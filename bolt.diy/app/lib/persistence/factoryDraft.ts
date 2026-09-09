import { z } from 'zod';

const contextSchema = z.object({
  brand_name: z.string(),
  personality: z.array(z.string()),
  avoid: z.array(z.string()),
  guideline: z.string(),
  existing_code: z.string(),
  existing_website: z.string(),
  assets: z.array(z.object({ name: z.string(), kind: z.enum(['logo', 'screenshot']), data_url: z.string() })),
});

const draftSchema = z.object({
  version: z.literal(1),
  prompt: z.string(),
  webResearch: z.boolean(),
  manualReferences: z.array(z.string()),
  selectedDirection: z.string(),
  directionChosen: z.boolean().default(false),
  centerMode: z.enum(['direction', 'preview', 'system']),
  designContext: contextSchema,
  tokensText: z.string(),
  engine: z.enum(['template', 'ai']).default('template'),
});

export type DesignContextInput = z.infer<typeof contextSchema>;
export type FactoryDraft = z.infer<typeof draftSchema>;

const STORAGE_KEY = 'uiux-factory-design-context-v3';

export function readFactoryDraft(): FactoryDraft | null {
  try {
    const result = draftSchema.safeParse(JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null'));
    return result.success ? result.data : null;
  } catch {
    return null;
  }
}

export function saveFactoryDraft(draft: FactoryDraft): boolean {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
    return true;
  } catch {
    return false;
  }
}
