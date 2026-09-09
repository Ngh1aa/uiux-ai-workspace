import { useEffect, useMemo, useRef, useState } from 'react';
import {
  DesignIntelligencePanel,
  EMPTY_DESIGN_CONTEXT,
  type DesignSystemReport,
  type ReferenceReport,
} from './DesignIntelligencePanel';
import { readFactoryDraft, saveFactoryDraft, type DesignContextInput } from '~/lib/persistence/factoryDraft';
import { DesignPromptComposer } from './DesignPromptComposer';

type SearchResult = {
  title: string;
  url: string;
  description: string;
  age?: string;
  favicon?: string;
};

type SearchPayload = {
  provider?: string;
  query?: string;
  results?: SearchResult[];
  warning?: string;
  error?: string;
};

type JobState = {
  id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  run_id?: string;
  project_slug?: string;
  error?: string;
  output_tail?: string;
  mode?: 'build' | 'intelligence';
  active_stage?: string;
  completed_stages?: string[];
  engine?: 'template' | 'ai';
};

type Direction = {
  id: string;
  name: string;
  label: string;
  intent: string;
  composition: string;
  typography: string;
  media: string;
  avoid: string;
  signature: string;
};

const BRIDGE = 'http://127.0.0.1:8788';

const STAGES = [
  ['reference_analysis', 'Reference DNA'],
  ['research', 'Research'],
  ['ux_ia', 'UX / IA'],
  ['art_direction', 'Art direction'],
  ['design_contract', 'Contract'],
  ['design_system', 'System'],
  ['visual_composition', 'Composition'],
  ['implementation', 'Build'],
  ['browser_qa', 'Browser QA'],
  ['visual_qa', 'Visual critic'],
] as const;

const SKILL_SETS: Record<string, string[]> = {
  ecommerce: [
    'ecommerce-website',
    'visual-design-direction',
    'visual-taste-calibration',
    'design-system-and-components',
    'responsive-and-device-strategy',
  ],
  corporate: [
    'corporate-website',
    'brand-guidelines',
    'visual-design-direction',
    'conversion-and-content',
    'design-system-and-components',
  ],
  education: [
    'education-website',
    'information-architecture',
    'visual-design-direction',
    'accessibility',
    'responsive-and-device-strategy',
  ],
  agency: [
    'corporate-website',
    'conversion-and-content',
    'visual-taste-calibration',
    'asset-media-and-art-direction',
    'frontend-implementation',
  ],
};

const DIRECTIONS: Record<string, Direction[]> = {
  ecommerce: [
    {
      id: 'editorial-commerce',
      name: 'Editorial Commerce',
      label: 'Premium / expressive',
      intent: 'Make product discovery feel like a strong editorial story rather than a marketplace template.',
      composition: 'Oversized type, asymmetric product staging, controlled density shifts, quiet transactional pages.',
      typography: 'Large display headlines paired with restrained, highly legible product information.',
      media: 'Product imagery becomes the composition. Fewer decorative cards, larger crop decisions.',
      avoid: 'Card soup, excessive pills, generic SaaS gradients, identical hero shells.',
      signature: 'Editorial product theatre with asymmetric merchandising and purple used as precise wayfinding.',
    },
    {
      id: 'immersive-market',
      name: 'Immersive Market',
      label: 'Bold / campaign-led',
      intent: 'Create a memorable storefront driven by campaign moments and strong visual transitions.',
      composition: 'Full-width campaign bands, layered category discovery, large media anchors, cinematic pacing.',
      typography: 'Confident display scale with short copy and compact utility typography.',
      media: 'Hero imagery, material closeups, campaign collages, editorial product cutouts.',
      avoid: 'Over-animated sections, weak contrast, decorative effects without commerce purpose.',
      signature: 'Campaign-led commerce where each major scroll chapter has a distinct visual anchor.',
    },
    {
      id: 'precision-retail',
      name: 'Precision Retail',
      label: 'Clean / product-first',
      intent: 'Feel premium through precision, spacing and product clarity instead of decoration.',
      composition: 'Strict grid, large product media, thin separators, compact navigation, generous negative space.',
      typography: 'Neutral modern grotesk, sharp hierarchy, strong numeric and price treatment.',
      media: 'Clean product photography with consistent crop logic and subtle material detail.',
      avoid: 'Soft generic cards, bloated shadows, unnecessary gradients, decorative badges.',
      signature: 'Gallery-like retail precision with disciplined spacing and product objects carrying the brand.',
    },
  ],
  corporate: [
    {
      id: 'editorial-authority',
      name: 'Editorial Authority',
      label: 'Premium / credible',
      intent: 'Turn corporate proof, capability and leadership into a confident editorial experience.',
      composition:
        'Strong type hierarchy, asymmetric proof blocks, selective full-bleed media, structured data moments.',
      typography: 'Editorial display type paired with sober body typography and precise metadata.',
      media: 'Real projects, people, infrastructure or domain artifacts as evidence, never generic decoration.',
      avoid: 'Logo walls without context, generic icon cards, corporate blue gradients everywhere.',
      signature: 'Editorial credibility where evidence and outcomes determine composition.',
    },
    {
      id: 'systems-confidence',
      name: 'Systems Confidence',
      label: 'Technical / modern',
      intent: 'Express capability through systems thinking, data, diagrams and controlled interaction.',
      composition: 'Modular technical canvas, diagrams, metric rails, service architecture, selective dark surfaces.',
      typography: 'Modern sans with technical labels, tabular numbers and compact supporting copy.',
      media: 'Diagrams, infrastructure views, product UI and real system evidence.',
      avoid: 'Fake dashboards, meaningless glowing orbs, abstract tech visuals unrelated to the business.',
      signature: 'Technical clarity with one coherent systems language across pages.',
    },
    {
      id: 'quiet-luxury',
      name: 'Quiet Confidence',
      label: 'Minimal / executive',
      intent: 'Build authority with restraint, proportion and strong content sequencing.',
      composition: 'Wide margins, fewer sections, large evidence moments, clean dividers, controlled asymmetry.',
      typography: 'Refined display scale, comfortable reading measure, calm metadata.',
      media: 'One strong image or artifact per chapter instead of many small visuals.',
      avoid: 'Dense grids, decorative icons, loud gradients, excessive motion.',
      signature: 'Executive restraint where spacing and evidence create premium character.',
    },
  ],
  education: [
    {
      id: 'human-campus',
      name: 'Human Campus',
      label: 'Warm / aspirational',
      intent: 'Make the school feel alive, trustworthy and emotionally relevant to parents and students.',
      composition:
        'Story-led admissions hero, program journeys, campus moments, student outcomes, clear inquiry paths.',
      typography: 'Warm display voice with exceptionally readable information typography.',
      media: 'Authentic campus, students, learning moments and facilities as primary evidence.',
      avoid: 'Stock children imagery, childish UI, generic rounded school cards.',
      signature: 'A living campus narrative where human evidence guides every key decision.',
    },
    {
      id: 'academic-editorial',
      name: 'Academic Editorial',
      label: 'Prestige / structured',
      intent: 'Balance institutional prestige with clarity around programs, pathways and outcomes.',
      composition:
        'Editorial masthead, structured program navigation, publication-like content rhythm, proof-rich sections.',
      typography: 'Distinctive academic display type paired with neutral digital reading type.',
      media: 'Architecture, academic artifacts, publications, labs and real achievements.',
      avoid: 'Overly playful visuals, university-template sameness, shallow badge collections.',
      signature: 'Academic prestige expressed through editorial hierarchy and real learning evidence.',
    },
    {
      id: 'future-learning',
      name: 'Future Learning',
      label: 'Modern / progressive',
      intent: 'Communicate a progressive learning model without looking like a generic technology startup.',
      composition: 'Interactive pathways, program maps, learning-model diagrams, bold student work and outcomes.',
      typography: 'Contemporary sans with expressive headings and crisp information density.',
      media: 'Student projects, labs, curriculum diagrams and hands-on learning evidence.',
      avoid: 'SaaS dashboards, neon tech clichés, abstract AI imagery disconnected from education.',
      signature: 'Progressive learning visualized through pathways, projects and real student outcomes.',
    },
  ],
  agency: [
    {
      id: 'work-first',
      name: 'Work First',
      label: 'Case-study driven',
      intent: 'Make the agency memorable through the work itself, not marketing claims.',
      composition: 'Project-led hero, oversized case-study media, sparse capability framing, sharp outcome typography.',
      typography: 'Bold editorial type with compact utility labels and strong project metadata.',
      media: 'Real project screens, campaign assets, motion frames and outcomes.',
      avoid: 'Service card grids, fake awards, generic creative-agency gradients.',
      signature: 'A portfolio-first editorial system where each project changes the visual rhythm.',
    },
    {
      id: 'creative-system',
      name: 'Creative System',
      label: 'Distinctive / modular',
      intent: 'Show a recognizable creative point of view through a repeatable but flexible visual grammar.',
      composition: 'Modular compositions, art-directed typography, strong transitions, variable project layouts.',
      typography: 'Expressive display treatment supported by a disciplined information layer.',
      media: 'Mixed media, interface crops, abstract brand artifacts and project process evidence.',
      avoid: 'One layout repeated for every case study, random motion, visual noise without narrative.',
      signature: 'A modular creative grammar that changes by project while preserving one unmistakable agency voice.',
    },
    {
      id: 'strategic-minimal',
      name: 'Strategic Minimal',
      label: 'Senior / restrained',
      intent: 'Position the agency as a senior strategic partner through clarity and proof.',
      composition:
        'Few high-value sections, strong point-of-view statements, outcome-led case studies, minimal chrome.',
      typography: 'Large confident statements with calm supporting copy and precise metrics.',
      media: 'Selective project evidence, diagrams and results rather than decorative imagery.',
      avoid: 'Trendy effects, crowded portfolios, vague capability language.',
      signature: 'Senior strategic clarity with outcomes and point of view carrying the visual identity.',
    },
  ],
};

function inferDomain(prompt: string) {
  const value = prompt.toLowerCase();

  if (
    ['ecommerce', 'e-commerce', 'thương mại điện tử', 'marketplace', 'shop', 'shopee', 'checkout'].some((term) =>
      value.includes(term),
    )
  ) {
    return 'ecommerce';
  }

  if (
    ['trường', 'school', 'education', 'tuyển sinh', 'học sinh', 'phụ huynh', 'academy'].some((term) =>
      value.includes(term),
    )
  ) {
    return 'education';
  }

  if (['agency', 'marketing', 'seo', 'quảng cáo', 'studio', 'creative'].some((term) => value.includes(term))) {
    return 'agency';
  }

  return 'corporate';
}

function domainLabel(domain: string) {
  return (
    {
      ecommerce: 'E-commerce',
      corporate: 'Corporate / B2B',
      education: 'Education',
      agency: 'Agency / Studio',
    }[domain] ?? 'Corporate / B2B'
  );
}

function hostname(url: string) {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}

export function DesignExperienceV2() {
  const [savedDraft] = useState(readFactoryDraft);
  const [prompt, setPrompt] = useState(savedDraft?.prompt ?? '');
  const [showWelcome, setShowWelcome] = useState(true);
  const [aiReady, setAiReady] = useState(false);
  const engineTouched = useRef(false);
  const [webResearch, setWebResearch] = useState(savedDraft?.webResearch ?? true);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchProvider, setSearchProvider] = useState('');
  const [searchWarning, setSearchWarning] = useState('');
  const [searchError, setSearchError] = useState('');
  const [researching, setResearching] = useState(false);
  const [manualReference, setManualReference] = useState('');
  const [manualReferences, setManualReferences] = useState<string[]>(savedDraft?.manualReferences ?? []);
  const [selectedDirection, setSelectedDirection] = useState(savedDraft?.selectedDirection ?? '');
  const [directionChosen, setDirectionChosen] = useState(savedDraft?.directionChosen ?? false);
  const [rightTab, setRightTab] = useState<'direction' | 'research' | 'skills' | 'quality'>('direction');
  const [centerMode, setCenterMode] = useState<'direction' | 'preview' | 'system'>(
    savedDraft?.centerMode ?? 'direction',
  );
  const [designContext, setDesignContext] = useState<DesignContextInput>(
    savedDraft?.designContext ?? EMPTY_DESIGN_CONTEXT,
  );
  const [tokensText, setTokensText] = useState(savedDraft?.tokensText ?? '');
  const [draftWarning, setDraftWarning] = useState('');
  const [intelligenceError, setIntelligenceError] = useState('');
  const [systemReport, setSystemReport] = useState<DesignSystemReport | null>(null);
  const [referenceReport, setReferenceReport] = useState<ReferenceReport | null>(null);
  const [artifactJobId, setArtifactJobId] = useState('');
  const [analyzedInput, setAnalyzedInput] = useState('');
  const [starting, setStarting] = useState(false);
  const [engine, setEngine] = useState<'template' | 'ai'>(savedDraft?.engine ?? 'template');
  const [job, setJob] = useState<JobState | null>(null);
  const [activeStage, setActiveStage] = useState('research');
  const [previewUrl, setPreviewUrl] = useState('');
  const [bridgeOnline, setBridgeOnline] = useState<boolean | null>(null);
  const pollTimer = useRef<number | null>(null);

  const domain = useMemo(() => inferDomain(prompt), [prompt]);
  const directions = DIRECTIONS[domain] ?? DIRECTIONS.corporate;
  const activeDirection = directions.find((item) => item.id === selectedDirection) ?? directions[0];
  const skills = SKILL_SETS[domain] ?? SKILL_SETS.corporate;
  const isRunning = starting || job?.status === 'running' || job?.status === 'queued';
  const contextKey = JSON.stringify({
    designContext,
    tokensText,
    manualReferences,
    prompt,
    direction: activeDirection.id,
  });
  const submittedInput = useRef('');

  useEffect(() => {
    // Debounce synchronous browser storage while the user types or uploads assets.
    const timer = window.setTimeout(() => {
      const saved = saveFactoryDraft({
        version: 1,
        prompt,
        webResearch,
        manualReferences,
        selectedDirection,
        directionChosen,
        centerMode,
        designContext,
        tokensText,
        engine,
      });
      setDraftWarning(
        saved
          ? ''
          : 'Trình duyệt không lưu được bản nháp (có thể đã hết dung lượng). Context hiện tại vẫn dùng được cho lần chạy này.',
      );
    }, 300);
    return () => window.clearTimeout(timer);
  }, [
    prompt,
    webResearch,
    manualReferences,
    selectedDirection,
    directionChosen,
    centerMode,
    designContext,
    tokensText,
    engine,
  ]);

  useEffect(() => {
    setSelectedDirection((current) => {
      const stillExists = directions.some((item) => item.id === current);
      return stillExists ? current : directions[0].id;
    });
  }, [domain]);

  useEffect(() => {
    void checkBridge();

    return () => {
      if (pollTimer.current) {
        window.clearTimeout(pollTimer.current);
      }
    };
  }, []);

  async function checkBridge() {
    try {
      const response = await fetch(`${BRIDGE}/health`);
      setBridgeOnline(response.ok);

      const health = (await response.json()) as { ai?: { configured?: boolean } };
      const ready = response.ok && health.ai?.configured === true;
      setAiReady(ready);

      if (!engineTouched.current && !savedDraft) {
        setEngine(ready ? 'ai' : 'template');
      }
    } catch {
      setBridgeOnline(false);
      setAiReady(false);
    }
  }

  function addReference() {
    const value = manualReference.trim();

    if (!value || manualReferences.includes(value)) {
      return;
    }

    try {
      const url = new URL(value);

      if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password || manualReferences.length >= 4) {
        throw new Error('invalid');
      }
    } catch {
      setSearchError('Dùng URL HTTP(S) hợp lệ, tối đa 4 reference.');
      setRightTab('research');

      return;
    }

    setManualReferences((current) => [...current, value]);
    setManualReference('');
  }

  async function runResearch() {
    setResearching(true);
    setSearchError('');
    setSearchWarning('');

    try {
      const query = [
        prompt,
        `Website design references for ${domainLabel(domain)}.`,
        'Focus on excellent information architecture, art direction, layout, typography, responsive patterns and visual differentiation.',
      ].join(' ');

      const response = await fetch(`/api/uiux-search?q=${encodeURIComponent(query)}`);
      const payload = (await response.json()) as SearchPayload;

      if (!response.ok) {
        throw new Error(payload.error || 'Web research failed');
      }

      setSearchResults(payload.results ?? []);
      setSearchProvider(payload.provider ?? 'web');
      setSearchWarning(payload.warning ?? '');
      setRightTab('research');

      return payload.results ?? [];
    } catch (error) {
      setSearchError(error instanceof Error ? error.message : 'Web research failed');
      setRightTab('research');

      return [];
    } finally {
      setResearching(false);
    }
  }

  function compilePrompt() {
    if (!directionChosen) {
      return `${prompt.trim()}\n\nChoose the UX and visual direction from this brief and the supplied brand context. Do not impose a preset style. Preserve factual content and brand constraints; identify unknowns.`;
    }

    const references = manualReferences.length
      ? manualReferences.map((url, index) => `${index + 1}. ${url}`).join('\n')
      : 'None supplied manually.';

    return `${prompt.trim()}\n\n## SELECTED DESIGN DIRECTION\nName: ${activeDirection.name}\nIntent: ${activeDirection.intent}\nComposition: ${activeDirection.composition}\nTypography: ${activeDirection.typography}\nMedia: ${activeDirection.media}\nAvoid: ${activeDirection.avoid}\nSignature: ${activeDirection.signature}\n\n## MANUAL REFERENCES\n${references}\n\n## DESIGN EXECUTION PRIORITY\nResearch before decoration. Preserve page-role diversity. Avoid generic card-grid composition. Create a visible, memorable visual signature. Treat mobile transformation as a design decision. The selected direction is a commitment unless evidence proves it conflicts with usability or accessibility.`;
  }

  async function startDesign(mode: 'build' | 'intelligence' = 'build', requestedEngine: 'template' | 'ai' = engine) {
    if (isRunning) {
      return;
    }

    if (!prompt.trim()) {
      setIntelligenceError('Hãy mô tả website bạn muốn tạo trước khi bắt đầu.');
      setShowWelcome(true);
      setCenterMode('direction');

      return;
    }

    setStarting(true);
    setIntelligenceError('');
    submittedInput.current = contextKey;

    let tokens: Record<string, unknown>;

    try {
      const parsed: unknown = tokensText.trim() ? JSON.parse(tokensText) : {};

      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('Design system JSON phải là một object.');
      }

      tokens = parsed as Record<string, unknown>;
    } catch (error) {
      setIntelligenceError(error instanceof Error ? error.message : 'JSON không hợp lệ.');
      setCenterMode('system');
      setStarting(false);

      return;
    }

    let evidence = searchResults;

    if (mode === 'build' && webResearch && evidence.length === 0) {
      evidence = await runResearch();
    }

    const manualEvidence: SearchResult[] = manualReferences.map((url) => ({
      title: `Manual reference — ${hostname(url)}`,
      url,
      description:
        'Reference URL supplied directly by the user. Use for design-language study only; do not copy the source.',
    }));

    try {
      const response = await fetch(`${BRIDGE}/${mode === 'intelligence' ? 'intelligence' : 'run'}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          engine: requestedEngine,
          prompt: compilePrompt(),
          domain,
          use_skills: true,
          web_research: webResearch,
          search_results: [...manualEvidence, ...evidence],
          design_context: { ...designContext, tokens, reference_urls: manualReferences },
        }),
      });
      const payload = (await response.json()) as JobState & { error?: string };

      if (!response.ok) {
        throw new Error(payload.error || 'Unable to start UIUX Factory');
      }

      setJob(payload);
      setShowWelcome(false);
      setActiveStage('reference_analysis');
      setCenterMode(mode === 'intelligence' ? 'system' : 'preview');

      if (mode === 'build') {
        setPreviewUrl('');
      }

      schedulePoll(payload.id);
    } catch (error) {
      setJob({
        id: 'failed-to-start',
        status: 'failed',
        error: error instanceof Error ? error.message : 'Bridge unavailable',
      });
      setIntelligenceError(error instanceof Error ? error.message : 'Bridge unavailable');
    } finally {
      setStarting(false);
    }
  }

  async function loadIntelligence(id: string) {
    const base = `${BRIDGE}/jobs/${id}/artifacts`;
    const responses = await Promise.all([fetch(`${base}/design-system.json`), fetch(`${base}/reference-dna.json`)]);

    if (responses.some((response) => !response.ok)) {
      throw new Error('Chưa tải được artifact của lần phân tích.');
    }

    setSystemReport((await responses[0].json()) as DesignSystemReport);
    setReferenceReport((await responses[1].json()) as ReferenceReport);
    setArtifactJobId(id);
    setAnalyzedInput(submittedInput.current);
  }

  function schedulePoll(id: string) {
    pollTimer.current = window.setTimeout(async () => {
      try {
        const response = await fetch(`${BRIDGE}/jobs/${id}`);

        if (response.status === 404) {
          setJob({
            id,
            status: 'failed',
            error: 'Phiên chạy không còn trong bridge. Artifact đã ghi vẫn nằm trong thư mục runs.',
          });
          return;
        }

        if (!response.ok) {
          throw new Error('Không đọc được trạng thái Factory.');
        }

        const payload = (await response.json()) as JobState;
        setJob(payload);
        setBridgeOnline(true);

        const output = (payload.output_tail ?? '').toLowerCase();
        const matchedStage = [...STAGES].reverse().find(([stage]) => {
          const readable = stage.replaceAll('_', ' ');
          return output.includes(stage) || output.includes(readable);
        });

        if (payload.active_stage || matchedStage) {
          setActiveStage(payload.active_stage ?? matchedStage![0]);
        }

        if (payload.status === 'running' || payload.status === 'queued') {
          schedulePoll(id);
          return;
        }

        if (payload.status === 'completed') {
          await loadIntelligence(id);
        }

        if (payload.status === 'completed' && payload.mode === 'intelligence') {
          setCenterMode('system');
          setActiveStage('design_system');
        } else if (payload.status === 'completed' && payload.project_slug) {
          setPreviewUrl(`${BRIDGE}/preview/${payload.project_slug}/`);
          setActiveStage('visual_qa');
          setRightTab('quality');
        }
      } catch (error) {
        setBridgeOnline(false);
        setIntelligenceError(error instanceof Error ? error.message : 'Mất kết nối Factory.');
        schedulePoll(id);
      }
    }, 1400);
  }

  const currentStageIndex = STAGES.findIndex(([stage]) => stage === activeStage);
  const welcome = showWelcome && centerMode === 'direction';

  return (
    <div className={`dx-shell ${welcome ? 'dx-welcome-mode' : ''}`}>
      <aside className="dx-rail">
        <div className="dx-brand">
          <div className="dx-mark">UX</div>
          <div>
            <strong>UIUX Factory</strong>
            <span>Design Intelligence V3</span>
          </div>
        </div>

        <nav className="dx-nav">
          <button
            className="is-active"
            onClick={() => {
              setShowWelcome(true);
              setCenterMode('direction');
            }}
          >
            <span>✦</span>Design
          </button>
          <button
            onClick={() => {
              setShowWelcome(false);
              setRightTab('research');
            }}
          >
            <span>⌕</span>Research
          </button>
          <button
            onClick={() => {
              setShowWelcome(false);
              setRightTab('direction');
            }}
          >
            <span>◒</span>Directions
          </button>
          <button onClick={() => setCenterMode('system')}>
            <span>◇</span>Brand & System
          </button>
          <button
            onClick={() => {
              setShowWelcome(false);
              setRightTab('skills');
            }}
          >
            <span>⌘</span>Skills
          </button>
          <button
            onClick={() => {
              setShowWelcome(false);
              setRightTab('quality');
            }}
          >
            <span>◎</span>Quality
          </button>
        </nav>

        <div className="dx-rail-spacer" />

        <div className="dx-runtime">
          <span className={`dx-status-dot ${bridgeOnline ? 'is-online' : ''}`} />
          <div>
            <strong>{bridgeOnline ? 'Factory connected' : 'Factory offline'}</strong>
            <span>MetaGPT · skills_UIUX</span>
          </div>
          <button onClick={checkBridge}>↻</button>
        </div>
      </aside>

      <main className="dx-main">
        <header className="dx-topbar">
          <div>
            <span className="dx-kicker">Design studio</span>
            <strong>{designContext.brand_name || 'Untitled website'}</strong>
          </div>
          <div className="dx-top-actions">
            <button
              className="dx-return-brief"
              onClick={() => {
                setShowWelcome(true);
                setCenterMode('direction');
              }}
            >
              Yêu cầu thiết kế
            </button>
            <span className="dx-mode">✦ Taste mode</span>
            <span className="dx-domain">{domainLabel(domain)}</span>
          </div>
        </header>

        {welcome ? (
          <section className="dx-welcome" aria-labelledby="dx-welcome-title">
            <div className="dx-welcome-heading">
              <span className="dx-kicker">Từ ý tưởng đến giao diện</span>
              <h1 id="dx-welcome-title">
                Bạn mang ý tưởng.
                <br />
                <em>Cùng biến nó thành website.</em>
              </h1>
              <p>Mô tả điều bạn muốn. Factory sẽ chọn kỹ năng phù hợp, xây hướng thiết kế và kiểm tra kết quả.</p>
            </div>
            <DesignPromptComposer
              prompt={prompt}
              onChange={setPrompt}
              onSubmit={() => void startDesign(aiReady ? 'build' : 'intelligence', aiReady ? 'ai' : 'template')}
              busy={isRunning}
              submitLabel={aiReady ? 'Bắt đầu thiết kế' : 'Chuẩn bị bản thiết kế'}
              error={intelligenceError || draftWarning}
            >
              <div className="dx-brief-context-actions">
                <button type="button" onClick={() => setCenterMode('system')}>
                  ＋ Thương hiệu / hình ảnh
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowWelcome(false);
                    setCenterMode('direction');
                  }}
                >
                  Chọn hướng thiết kế
                </button>
              </div>
              <details className="dx-brief-references">
                <summary>
                  Website tham khảo {manualReferences.length ? `(${manualReferences.length})` : '(tùy chọn)'}
                </summary>
                <div className="dx-reference-row">
                  <input
                    aria-label="Website tham khảo"
                    placeholder="https://website-ban-thich.com"
                    value={manualReference}
                    onChange={(event) => setManualReference(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter') {
                        event.preventDefault();
                        addReference();
                      }
                    }}
                  />
                  <button type="button" onClick={addReference}>
                    Thêm
                  </button>
                </div>
                <div className="dx-ref-chips">
                  {manualReferences.map((url) => (
                    <button
                      type="button"
                      key={url}
                      onClick={() => setManualReferences((items) => items.filter((item) => item !== url))}
                      aria-label={`Bỏ ${url}`}
                    >
                      {hostname(url)} ×
                    </button>
                  ))}
                </div>
              </details>
            </DesignPromptComposer>
            <div className="dx-prompt-examples" aria-label="Gợi ý yêu cầu">
              <span>Thử một ý tưởng</span>
              {[
                [
                  'Website doanh nghiệp',
                  'Thiết kế website cho công ty tư vấn doanh nghiệp, dành cho khách hàng B2B. Cảm giác chuyên nghiệp, đáng tin. Có dịch vụ, năng lực, dự án và liên hệ.',
                ],
                [
                  'Studio sáng tạo',
                  'Thiết kế website studio kiến trúc, dành cho chủ nhà tìm đơn vị thiết kế. Tối giản, ấm áp, hình ảnh dự án nổi bật. Có dự án, dịch vụ và tư vấn.',
                ],
                [
                  'Thương hiệu bán lẻ',
                  'Thiết kế website giới thiệu thương hiệu nội thất, dành cho người yêu không gian sống tinh tế. Cần bộ sưu tập, câu chuyện thương hiệu và đặt lịch tư vấn.',
                ],
              ].map(([label, value]) => (
                <button key={label} disabled={isRunning} onClick={() => setPrompt(value)}>
                  {label} <span aria-hidden="true">↗</span>
                </button>
              ))}
            </div>
            <div className="dx-ai-readiness" role="status">
              <span className={`dx-status-dot ${aiReady ? 'is-online' : ''}`} />
              <p>
                {aiReady
                  ? 'AI đã cấu hình · Chọn kỹ năng theo brief · Kiểm tra desktop và mobile'
                  : bridgeOnline
                    ? 'Chưa kết nối AI cloud. Bạn vẫn có thể phân tích thương hiệu, reference và chuẩn bị DESIGN.md.'
                    : 'Đang chờ kết nối Factory. Brief của bạn được giữ trên trình duyệt.'}
              </p>
              <button onClick={checkBridge} aria-label="Kiểm tra lại kết nối AI">
                Kiểm tra lại
              </button>
            </div>
          </section>
        ) : (
          <div className="dx-grid">
            <section className="dx-chat">
              <div className="dx-chat-scroll">
                <div className="dx-agent-message">
                  <div className="dx-agent-avatar">✦</div>
                  <div>
                    <div className="dx-message-meta">
                      <strong>Design Director</strong>
                      <span>Direction-first workflow</span>
                    </div>
                    <p>
                      Cho tôi brief. Tôi sẽ nghiên cứu thị trường, route skill thật, đề xuất direction rõ ràng rồi mới
                      build.
                    </p>
                  </div>
                </div>

                <div className="dx-plan-card">
                  <div className="dx-plan-title">
                    <span>PLAN MODE</span>
                    <b>Before code</b>
                  </div>
                  <ol>
                    <li className={searchResults.length ? 'is-done' : 'is-active'}>
                      <span>01</span>
                      <div>
                        <strong>Research evidence</strong>
                        <small>
                          {searchResults.length
                            ? `${searchResults.length} web references collected`
                            : 'Study market and reference patterns'}
                        </small>
                      </div>
                    </li>
                    <li className={directionChosen ? 'is-done' : ''}>
                      <span>02</span>
                      <div>
                        <strong>Choose art direction</strong>
                        <small>{directionChosen ? activeDirection.name : 'Tự đề xuất theo brief'}</small>
                      </div>
                    </li>
                    <li className={job?.mode === 'build' && job.status === 'completed' ? 'is-done' : ''}>
                      <span>03</span>
                      <div>
                        <strong>Compose & build</strong>
                        <small>Page-role specific composition</small>
                      </div>
                    </li>
                    <li className={job?.mode === 'build' && job.status === 'completed' ? 'is-done' : ''}>
                      <span>04</span>
                      <div>
                        <strong>{job?.engine === 'ai' ? 'Kiểm tra trình duyệt' : 'Critique rendered output'}</strong>
                        <small>
                          {job?.engine === 'ai' ? 'BrowserQA · cần duyệt hình trực quan' : 'BrowserQA + VisualCritic'}
                        </small>
                      </div>
                    </li>
                  </ol>
                </div>

                {job && (
                  <div className="dx-agent-message dx-run-message">
                    <div className="dx-agent-avatar">↻</div>
                    <div>
                      <div className="dx-message-meta">
                        <strong>Factory run</strong>
                        <span>{job.status}</span>
                      </div>
                      <p>
                        {job.status === 'failed'
                          ? job.error
                          : job.status === 'completed'
                            ? job.mode === 'intelligence'
                              ? 'Brand DNA và Reference DNA đã sẵn sàng để review.'
                              : 'Bản build đã sẵn sàng. Kiểm tra preview và quality panel.'
                            : `Đang chạy ${STAGES[currentStageIndex]?.[1] ?? 'pipeline'}…`}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              <div className="dx-prompt-zone">
                <div className="dx-reference-row">
                  <input
                    value={manualReference}
                    onChange={(event) => setManualReference(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter') {
                        event.preventDefault();
                        addReference();
                      }
                    }}
                    placeholder="Paste reference URL…"
                  />
                  <button onClick={addReference}>＋ Reference</button>
                </div>

                {manualReferences.length > 0 && (
                  <div className="dx-ref-chips">
                    {manualReferences.map((url) => (
                      <button
                        key={url}
                        onClick={() => setManualReferences((items) => items.filter((item) => item !== url))}
                        title="Remove reference"
                      >
                        {hostname(url)} <span>×</span>
                      </button>
                    ))}
                  </div>
                )}

                <DesignPromptComposer
                  prompt={prompt}
                  onChange={setPrompt}
                  onSubmit={() => void startDesign()}
                  busy={isRunning}
                  submitLabel={engine === 'ai' ? 'Tạo giao diện bằng AI' : 'Tạo prototype mẫu'}
                  error={centerMode === 'system' ? undefined : intelligenceError || draftWarning}
                >
                  <label className="dx-engine-select">
                    <span id="dx-engine-label">Chế độ tạo giao diện</span>
                    <select
                      aria-labelledby="dx-engine-label"
                      value={engine}
                      disabled={isRunning}
                      onChange={(event) => {
                        engineTouched.current = true;
                        setEngine(event.target.value === 'ai' ? 'ai' : 'template');
                      }}
                    >
                      <option value="template">Prototype có sẵn · không gọi AI cloud</option>
                      <option value="ai">AI tùy biến · Groq / Gemini đã cấu hình</option>
                    </select>
                  </label>
                  <div className="dx-composer-actions">
                    <div>
                      <span className="dx-chip is-on">✦ skills_UIUX</span>
                      <button
                        type="button"
                        className={`dx-chip ${webResearch ? 'is-on' : ''}`}
                        onClick={() => setWebResearch((value) => !value)}
                      >
                        ⌕ Web research
                      </button>
                      <button type="button" className="dx-chip" onClick={runResearch} disabled={researching}>
                        {researching ? 'Researching…' : 'Research now'}
                      </button>
                    </div>
                  </div>
                </DesignPromptComposer>
              </div>
            </section>

            <section className="dx-stage">
              <div className="dx-stage-toolbar">
                <div className="dx-view-tabs">
                  <button
                    className={centerMode === 'direction' ? 'is-active' : ''}
                    onClick={() => setCenterMode('direction')}
                  >
                    Direction studio
                  </button>
                  <button
                    className={centerMode === 'system' ? 'is-active' : ''}
                    onClick={() => setCenterMode('system')}
                  >
                    Brand & System
                  </button>
                  <button
                    className={centerMode === 'preview' ? 'is-active' : ''}
                    onClick={() => setCenterMode('preview')}
                  >
                    Live preview
                  </button>
                </div>
                <div className="dx-stage-note">Research → Direction → Build → Critique</div>
              </div>

              <div className="dx-stage-body">
                {centerMode === 'system' ? (
                  <DesignIntelligencePanel
                    context={designContext}
                    onChange={setDesignContext}
                    tokensText={tokensText}
                    onTokensChange={setTokensText}
                    onAnalyze={() => void startDesign('intelligence')}
                    busy={isRunning}
                    error={intelligenceError || draftWarning || (job?.status === 'failed' ? (job.error ?? '') : '')}
                    system={systemReport}
                    references={referenceReport}
                    artifactBase={`${BRIDGE}/jobs/${artifactJobId}/artifacts`}
                    stale={!!analyzedInput && analyzedInput !== contextKey}
                  />
                ) : centerMode === 'direction' ? (
                  <div className="dx-direction-studio">
                    <div className="dx-studio-head">
                      <span>ART DIRECTION</span>
                      <h1>
                        Choose the visual idea <em>before</em> code.
                      </h1>
                      <p>
                        Ba hướng có cùng UX goal nhưng khác visual grammar. Chọn một hướng để biến thành commitment
                        trong prompt, Art Direction và Visual Composition.
                      </p>
                    </div>

                    <div className="dx-direction-grid">
                      {directions.map((direction, index) => {
                        const selected = directionChosen && activeDirection.id === direction.id;

                        return (
                          <button
                            key={direction.id}
                            className={`dx-direction-card dx-direction-${index + 1} ${selected ? 'is-selected' : ''}`}
                            onClick={() => {
                              setSelectedDirection(direction.id);
                              setDirectionChosen(true);
                            }}
                          >
                            <div className="dx-direction-preview">
                              <span className="dx-preview-label">{direction.label}</span>
                              <div className="dx-preview-type">
                                <b>Aa</b>
                                <i>01 — {String(index + 1).padStart(2, '0')}</i>
                              </div>
                              <div className="dx-preview-lines">
                                <span />
                                <span />
                                <span />
                              </div>
                              <div className="dx-preview-object">
                                <span />
                              </div>
                            </div>
                            <div className="dx-direction-copy">
                              <div>
                                <span>0{index + 1}</span>
                                {selected && <b>SELECTED</b>}
                              </div>
                              <h3>{direction.name}</h3>
                              <p>{direction.intent}</p>
                              <small>{direction.signature}</small>
                            </div>
                          </button>
                        );
                      })}
                    </div>

                    <div className="dx-direction-detail">
                      <div>
                        <span>Composition</span>
                        <p>{activeDirection.composition}</p>
                      </div>
                      <div>
                        <span>Typography</span>
                        <p>{activeDirection.typography}</p>
                      </div>
                      <div>
                        <span>Media</span>
                        <p>{activeDirection.media}</p>
                      </div>
                      <div>
                        <span>Avoid</span>
                        <p>{activeDirection.avoid}</p>
                      </div>
                    </div>
                  </div>
                ) : previewUrl ? (
                  <div className="dx-browser">
                    <div className="dx-browser-bar">
                      <div>
                        <span />
                        <span />
                        <span />
                      </div>
                      <p>{previewUrl}</p>
                      <button onClick={() => window.open(previewUrl, '_blank')}>↗</button>
                    </div>
                    <iframe title="Generated website preview" src={previewUrl} />
                  </div>
                ) : (
                  <div className="dx-preview-empty">
                    <div>✦</div>
                    <h2>
                      {isRunning ? 'Designing the selected direction…' : 'Build a direction to see the live website.'}
                    </h2>
                    <p>
                      {activeDirection.name} · {activeDirection.signature}
                    </p>
                  </div>
                )}
              </div>

              <div className="dx-stagebar">
                {STAGES.map(([key, label]) => {
                  const done = job?.completed_stages?.includes(key) ?? false;
                  const active = isRunning && key === activeStage;

                  return (
                    <div key={key} className={`${done ? 'is-done' : ''} ${active ? 'is-active' : ''}`}>
                      <span />
                      <b>{label}</b>
                    </div>
                  );
                })}
              </div>
            </section>

            <aside className="dx-inspector">
              <div className="dx-inspector-tabs">
                <button
                  className={rightTab === 'direction' ? 'is-active' : ''}
                  onClick={() => setRightTab('direction')}
                >
                  Direction
                </button>
                <button className={rightTab === 'research' ? 'is-active' : ''} onClick={() => setRightTab('research')}>
                  Research
                </button>
                <button className={rightTab === 'skills' ? 'is-active' : ''} onClick={() => setRightTab('skills')}>
                  Skills
                </button>
                <button className={rightTab === 'quality' ? 'is-active' : ''} onClick={() => setRightTab('quality')}>
                  Quality
                </button>
              </div>

              <div className="dx-inspector-body">
                {rightTab === 'direction' && (
                  <div className="dx-panel-stack">
                    <div className="dx-panel-head">
                      <span>COMMITMENT</span>
                      <h3>{activeDirection.name}</h3>
                      <p>
                        Direction này được inject vào project goal để ArtDirector và Composer không quay về layout mặc
                        định.
                      </p>
                    </div>
                    <div className="dx-commitment">
                      <span>Visual signature</span>
                      <strong>{activeDirection.signature}</strong>
                    </div>
                    <div className="dx-mini-list">
                      <div>
                        <span>Intent</span>
                        <p>{activeDirection.intent}</p>
                      </div>
                      <div>
                        <span>Avoid</span>
                        <p>{activeDirection.avoid}</p>
                      </div>
                    </div>
                    <button
                      className="dx-primary-side"
                      onClick={() => void startDesign()}
                      disabled={isRunning || !prompt.trim()}
                    >
                      Build this direction
                    </button>
                  </div>
                )}

                {rightTab === 'research' && (
                  <div className="dx-panel-stack">
                    <div className="dx-panel-head">
                      <span>WEB EVIDENCE</span>
                      <h3>Reference board</h3>
                      <p>
                        {searchProvider
                          ? `Provider: ${searchProvider}`
                          : 'Collect current market references before design.'}
                      </p>
                    </div>
                    <button className="dx-primary-side" onClick={runResearch} disabled={researching}>
                      {researching ? 'Searching…' : 'Search current market'}
                    </button>
                    {searchWarning && <div className="dx-warning">{searchWarning}</div>}
                    {searchError && <div className="dx-error">{searchError}</div>}
                    <div className="dx-research-list">
                      {searchResults.map((result) => (
                        <a key={result.url} href={result.url} target="_blank" rel="noreferrer">
                          <span>{hostname(result.url)}</span>
                          <strong>{result.title}</strong>
                          <p>{result.description}</p>
                        </a>
                      ))}
                    </div>
                  </div>
                )}

                {rightTab === 'skills' && (
                  <div className="dx-panel-stack">
                    <div className="dx-panel-head">
                      <span>SKILL BRAIN</span>
                      <h3>Real skill graph</h3>
                      <p>UI chỉ hiển thị skill liên quan; runtime vẫn xác minh path + SHA từ repo skills_UIUX thật.</p>
                    </div>
                    <div className="dx-skill-list">
                      {skills.map((skill, index) => (
                        <div key={skill}>
                          <span>{String(index + 1).padStart(2, '0')}</span>
                          <div>
                            <strong>{skill}</strong>
                            <small>SKILL.md · verified runtime</small>
                          </div>
                          <i>✓</i>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {rightTab === 'quality' && (
                  <div className="dx-panel-stack">
                    <div className="dx-panel-head">
                      <span>RENDERED QUALITY</span>
                      <h3>Pass the website, not the promise</h3>
                      <p>
                        {(job?.engine ?? engine) === 'ai'
                          ? 'AI draft được kiểm tra lỗi trình duyệt và responsive. Chưa có điểm thẩm mỹ; cần duyệt screenshot.'
                          : 'Build success is not enough. BrowserQA and VisualCritic judge the rendered result.'}
                      </p>
                    </div>
                    <div className="dx-score">
                      <strong>90+</strong>
                      <span>target score · chưa phải kết quả đo</span>
                    </div>
                    <div className="dx-quality-list">
                      <div>
                        <span>Hierarchy</span>
                        <b>≥ 90</b>
                      </div>
                      <div>
                        <span>Typography</span>
                        <b>≥ 90</b>
                      </div>
                      <div>
                        <span>Spacing</span>
                        <b>≥ 90</b>
                      </div>
                      <div>
                        <span>Responsive</span>
                        <b>100</b>
                      </div>
                      <div>
                        <span>Accessibility</span>
                        <b>100</b>
                      </div>
                      <div>
                        <span>Generic AI feel</span>
                        <b>LOW</b>
                      </div>
                    </div>
                    <div className="dx-quality-note">
                      Next upgrade: point-and-edit annotations + targeted repair of the selected element.
                    </div>
                  </div>
                )}
              </div>
            </aside>
          </div>
        )}
      </main>
    </div>
  );
}
