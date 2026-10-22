---
name: human-ai-interaction-design
description: Design AI-assisted experiences with clear mental models, capability boundaries, confidence, feedback/control, correction and graceful failure. Use when a product exposes generative, predictive or agentic AI to end users.
---

# Human-AI Interaction Design

## Goal and scope

Give users an accurate mental model of what the AI can and cannot do, keep them in control of outcomes they are accountable for, and make wrong output cheap to notice, fix or undo. The design target is calibrated trust: users rely on the system when it is right and catch it when it is wrong. Over-trust and under-trust are both failures.

**When not to use**

- Evaluating the reliability of UI/UX coding agents in this repository: use `agent-evaluation-and-reliability`.
- Remembered preferences, saved filters and recommendations that are rules, not models: use `personalization-and-preference-ux`.
- Organization-level credibility, claims and proof pages: use `trust-credibility-and-transparency`.
- Generic loading, empty and error states with no AI-specific uncertainty: use `state-feedback-and-error-recovery`.
- Data collection, retention and consent mechanics for training data: use `security-and-privacy`, then return here for the in-product explanation.

**Prerequisites**

- The user task and who is accountable for its outcome (the user, a reviewer, the organization).
- Error cost: what happens when the AI is wrong and nobody notices.
- Model behavior evidence: known failure modes, evaluation results, latency range, whether outputs vary per run.

## Decisions

**Should this be AI at all? (PAIR: User needs + defining success)**
- Use AI when the task tolerates probabilistic output, rules cannot capture it, or personalization at scale matters. Prefer deterministic logic when users need predictable, auditable, identical results (tax totals, permissions, legal deadlines).
- Decide automate versus augment: automate tasks users find tedious and low-stakes; augment tasks users value doing or are accountable for. If users say "I want to check this", design augmentation.

**Autonomy level by error cost**

| Error cost | Reversible? | Default autonomy |
|---|---|---|
| Low | Yes | Act, show result, offer undo |
| Medium | Yes | Suggest, one-step accept, easy edit |
| High or irreversible (money, health, legal, sending to others, deleting) | No | Draft or plan only; explicit human confirmation of the specific action; log who approved |

Agentic actions with side effects show the plan before execution, name each external effect, and support stop mid-run.

**Capability and limits (HAX G1, G2)**
- Say what it does and how well at the moment of use, not in onboarding only. State scope ("Summarizes up to the last 30 days of tickets") and known weak spots ("May miss handwritten notes").
- Never imply human-level understanding, personhood or certainty the system lacks. Disclose AI identity when users could reasonably think they talk to a person (EU AI Act Article 50 transparency obligations; verify current application dates and scope).

**Confidence and explanation (HAX G11, PAIR Explainability + Trust)**
- Show confidence only if it changes what the user does. Prefer categorical or action-oriented signals ("Needs review", highlighted uncertain spans) over raw percentages; show a number only if it is calibrated and users were tested on reading it.
- Explanations should be source or reason based ("From: Q3 contract, section 4") so users can verify. A citation must point to the passage that supports the claim.

**Input guidance**
- Show examples of good requests, scoped to what works. Starter prompts must succeed reliably; a showcased prompt that fails teaches the wrong model.

**Feedback and control (HAX G7, G8, G9, G15, G17)**
- Invocation, dismissal and correction must each be one step. Editing output inline beats regenerate-only.
- Feedback controls state what happens to the feedback (improves this session, reviewed by team, used for training, or nothing). Do not collect thumbs-down with no consequence and imply it trains the model.
- Provide global controls: turn the feature off, clear memory, opt out of training where offered.

**Failure as a normal state (PAIR Errors + Graceful Failure, HAX G10)**
- Design refusal, low-confidence, timeout, partial result and "out of scope" states with a next step (rephrase, narrow scope, manual path, human contact).
- When in doubt, scope down or ask a clarifying question rather than guessing silently.

**Change over time (HAX G12 to G14, G18)**
- Remember recent context within a session when it helps; adapt cautiously; notify users when model behavior or data use changes.

## Workflow

1. Define user need and why AI is appropriate; record the deterministic alternative and the automate/augment choice.
2. Explain capability and limits at the moment they matter: scope line, weak-spot note, AI identity disclosure.
3. Design input guidance/examples without overclaiming; verify every starter example succeeds.
4. Decide when confidence, rationale or source context is useful; reject displays that do not change user action.
5. Provide feedback, correction, regenerate/undo and human override where appropriate, sized to the autonomy table.
6. Design uncertainty, refusal and failure as normal states, each with a recovery path.
7. Clarify data use and whether user feedback changes the system, in plain language next to the control.
8. Test with real model output, including bad output, not with hand-written ideal responses.

**Anti-patterns**

- Mockups populated with perfect AI output; the shipped model is never shown failing in design review.
- "98% confident" badges from uncalibrated scores.
- Citations that link to a whole document, or to sources that do not contain the claim.
- Chat as the only interface for a structured task (filling a form, choosing a date).
- Agent sends emails or makes purchases from a single vague prompt with no plan preview.
- Regenerate as the only fix, so a nearly-right answer cannot be edited.
- Thumbs up/down that goes nowhere, presented as "helps improve our AI".
- Anthropomorphic persona that apologizes and promises ("I'll remember that") when no memory exists.
- AI feature cannot be turned off, or reappears after dismissal.
- Generic "Something went wrong" for refusals, so users retry the same request forever.

**Resources**

- Need the HAX guideline map, state inventory or the worked before/after example? Read [human-AI pattern reference](references/human-ai-pattern-reference.md).

**Output**

Deliver an AI experience specification containing:

1. Appropriateness note: need, deterministic alternative, automate or augment, accountable party.
2. Autonomy decision per AI action, using the error-cost table.
3. Interaction table with this header:

| AI moment | User goal | Autonomy | Capability/limit copy | Confidence or source display | Control (accept/edit/undo/stop) | Failure state and next step | Data-use note | Guideline ref |
|---|---|---|---|---|---|---|---|---|

4. State inventory: idle, thinking/streaming, success, partial, low confidence, refusal, out of scope, error, stopped by user.
5. Test plan using real model outputs, including at least one known-bad output per AI moment.

## Quality gate

Pass only if every statement is true:

- [ ] AI identity/capability is not misleading: scope and known limits appear at point of use; AI is disclosed where a person could be assumed.
- [ ] Users retain meaningful control: every AI output can be edited or undone, and every agentic run can be previewed and stopped.
- [ ] Failures provide a path forward: refusal, low-confidence, timeout and out-of-scope states each name a next step.
- [ ] Confidence is not false precision: any numeric confidence is calibrated and user-tested, otherwise it is categorical or removed.
- [ ] High-impact use has appropriate human review: irreversible or high-cost actions require explicit confirmation of the specific action.
- [ ] Every feedback control states what happens to the feedback.
- [ ] Design was reviewed with real model output, including failure cases.

**Baseline / sources**

- Google PAIR People + AI Guidebook: user needs and defining success, data collection and evaluation, mental models, explainability and trust, feedback and control, errors and graceful failure.
- Microsoft Guidelines for Human-AI Interaction (Amershi et al., CHI 2019), 18 guidelines, and the HAX Toolkit.
- Apple Human Interface Guidelines, machine learning and generative AI sections (verify current guidance).
- EU AI Act Article 50 transparency obligations (verify current application dates).
- NIST AI Risk Management Framework (AI RMF 1.0) for risk framing.
