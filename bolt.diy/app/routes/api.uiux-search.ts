import type { LoaderFunctionArgs } from '@remix-run/cloudflare';

type SearchResult = {
  title: string;
  url: string;
  description: string;
  age?: string;
  favicon?: string;
};

type SearchResponse = {
  provider: 'brave' | 'duckduckgo-lite';
  query: string;
  results: SearchResult[];
  warning?: string;
};

function decodeHtml(value: string) {
  return value
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&nbsp;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function normalizeDuckDuckGoUrl(rawHref: string) {
  try {
    const parsed = new URL(rawHref, 'https://lite.duckduckgo.com');

    if (parsed.hostname.endsWith('duckduckgo.com')) {
      if (parsed.pathname.startsWith('/l/')) {
        const target = parsed.searchParams.get('uddg');

        if (target) {
          return decodeURIComponent(target);
        }
      }

      // Skip DuckDuckGo navigation/help links. We only want external references.
      return '';
    }

    if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
      return parsed.toString();
    }
  } catch {
    // Ignore malformed search result URLs.
  }

  return '';
}

async function searchBrave(query: string, apiKey: string): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    count: '8',
    country: 'VN',
    search_lang: 'vi',
    safesearch: 'moderate',
  });

  const response = await fetch(`https://api.search.brave.com/res/v1/web/search?${params.toString()}`, {
    headers: {
      Accept: 'application/json',
      'X-Subscription-Token': apiKey,
    },
  });

  if (!response.ok) {
    throw new Error(`Brave Search failed (${response.status})`);
  }

  const data = (await response.json()) as any;

  const results: SearchResult[] = (data?.web?.results ?? [])
    .slice(0, 8)
    .map((item: any) => ({
      title: String(item?.title ?? 'Untitled result'),
      url: String(item?.url ?? ''),
      description: String(item?.description ?? ''),
      age: item?.age ? String(item.age) : undefined,
      favicon: item?.profile?.img ? String(item.profile.img) : undefined,
    }))
    .filter((item: SearchResult) => item.url);

  return {
    provider: 'brave',
    query,
    results,
  };
}

async function searchDuckDuckGo(query: string, warning?: string): Promise<SearchResponse> {
  const response = await fetch(`https://lite.duckduckgo.com/lite/?q=${encodeURIComponent(query)}`, {
    headers: {
      Accept: 'text/html,application/xhtml+xml',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36',
    },
  });

  if (!response.ok) {
    throw new Error(`DuckDuckGo fallback failed (${response.status})`);
  }

  const html = await response.text();
  const links = [
    ...html.matchAll(/<a[^>]*(?:class=["']result-link["'][^>]*)?href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi),
  ]
    .map((match) => ({
      url: normalizeDuckDuckGoUrl(match[1]),
      title: decodeHtml(match[2]),
    }))
    .filter((item) => item.url && item.title)
    .filter((item, index, all) => all.findIndex((candidate) => candidate.url === item.url) === index)
    .slice(0, 8);

  const snippets = [...html.matchAll(/<td[^>]*class=["']result-snippet["'][^>]*>([\s\S]*?)<\/td>/gi)].map((match) =>
    decodeHtml(match[1]),
  );

  const results: SearchResult[] = links.map((item, index) => ({
    title: item.title,
    url: item.url,
    description: snippets[index] ?? '',
  }));

  if (!results.length) {
    throw new Error('DuckDuckGo returned no parseable results');
  }

  return {
    provider: 'duckduckgo-lite',
    query,
    results,
    warning,
  };
}

export async function loader({ request, context }: LoaderFunctionArgs) {
  const url = new URL(request.url);
  const q = url.searchParams.get('q')?.trim();

  if (!q) {
    return Response.json({ error: 'Missing q', results: [] }, { status: 400 });
  }

  const cloudflareEnv = context?.cloudflare?.env as { BRAVE_SEARCH_API_KEY?: string } | undefined;
  const apiKey = cloudflareEnv?.BRAVE_SEARCH_API_KEY || process.env.BRAVE_SEARCH_API_KEY;

  if (apiKey) {
    try {
      return Response.json(await searchBrave(q, apiKey));
    } catch (error) {
      const warning = error instanceof Error ? error.message : 'Brave Search failed';

      try {
        return Response.json(await searchDuckDuckGo(q, warning));
      } catch (fallbackError) {
        const detail = fallbackError instanceof Error ? fallbackError.message : 'Fallback search failed';

        return Response.json(
          {
            error: `${warning}. ${detail}`,
            results: [],
          },
          { status: 502 },
        );
      }
    }
  }

  try {
    return Response.json(
      await searchDuckDuckGo(q, 'BRAVE_SEARCH_API_KEY is not configured; using the no-key DuckDuckGo Lite fallback.'),
    );
  } catch (error) {
    const detail = error instanceof Error ? error.message : 'Search failed';

    return Response.json(
      {
        error: `${detail}. Add BRAVE_SEARCH_API_KEY to bolt.diy/.env.local for the primary search provider.`,
        results: [],
      },
      { status: 503 },
    );
  }
}
