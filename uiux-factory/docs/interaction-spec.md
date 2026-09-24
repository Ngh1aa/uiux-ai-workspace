# UIUX Factory: prompt-first entry

The Bolt `/uiux` welcome view asks for one brief. Suggestions only fill the editor; they never submit or overwrite a run. Brand, uploaded images and references are optional and use the existing Brand/System panel. Returning to the brief preserves input.

State: idle → submitting → queued/running → completed/failed. Busy jobs disable submission. Errors remain beside the input with the brief retained. Enter inserts a newline; Ctrl/Cmd+Enter submits outside IME composition. Reference Enter adds the URL without submitting the brief. Form labels remain stable while editing. Mobile stacks actions below the editor with 44px primary controls.

Health exposes only whether cloud configuration exists and provider names. This is not a live inference/billing verification. The welcome CTA uses AI when configured; otherwise it prepares Brand/Reference DNA and DESIGN.md and clearly states that cloud generation is unavailable. The advanced studio retains an explicit template mode.

No art-direction preset is inserted into the brief until the user selects one. Saved drafts retain prompt, context, references, explicit direction choice and engine. Completed stage indicators come from backend `completed_stages`, never guessed from pipeline order. Browser checks do not imply a visual score.

Current limits: cloud credentials are configured locally in Factory; this screen does not capture credentials. Jobs live in bridge memory, while run artifacts remain on disk. Restarting the bridge clears live job tracking. Canvas/Point & Edit is not included in this release.
