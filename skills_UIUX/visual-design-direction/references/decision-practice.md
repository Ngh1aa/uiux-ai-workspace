# Decision practice: learn, critique, repair, transfer

Use for deliberate practice requested by a learner or a skill maintainer. This is
not another delivery orchestrator: real project work follows `START-HERE.md`,
`WORKFLOWS.md` and the target's brief and acceptance criteria. Completing exercises does not establish
seniority, clinical/domain expertise or human usability.

## Start with an observable baseline

Open [Decision lab](../examples/decision-lab/index.html) through a local server.
Choose one of five synthetic briefs and hide the annotations. Keep the task, facts,
state and viewport fixed. Inspect both variants, perform the review/back task and
write observations **before** reading the explanation. The fragile variant has a
deliberate input-loss defect; do not copy it into production.

Use existing skills only when their decision is active:

| Practice | Owning skill | Exercise and deliverable | Review / redo condition |
|---|---|---|---|
| 1. Frame the job | `audience-intent-and-top-tasks` | Pick one brief. Name actor, entry context, decision, consequence of error and one assumption needing evidence. | Redo if the goal is a visual adjective or the audience is everyone. |
| 2. Model the workflow | `ux-structure-and-flow-design`, `state-feedback-and-error-recovery` | Map current state → next actor/action → feedback → failure/recovery. Add an interrupted/back path. | Redo if pending looks complete, input is lost or the journey ends without recovery. |
| 3. Organize information | `information-architecture` | Prioritize the same facts for entry, comparison and review. Justify grouping/labels without a fixed menu count. | Explain one rejected grouping; test findability when evidence warrants it. |
| 4. Ground the domain | `industry-playbooks`, `design-reference-research-and-benchmark` | Select the matching playbook or a relevant primary reference. Write ADOPT/ADAPT/REJECT for one workflow and one reference transfer. | Unknown industry must produce a research plan, not an unrelated preset. |
| 5. Explore direction | `visual-design-direction` | Render two meaningful representative alternatives with the same facts/state/CTA. Declare type, density and object relationships. | A color/font swap alone does not answer the structural question. Do not force novelty into a familiar form. |
| 6. Critique craft | `ui-craft-and-visual-qa`, `visual-taste-calibration` | Open desktop and narrow/enlarged-text renders. Annotate observed hierarchy, type, spacing, comparison and states. | Each issue needs a location, consequence, owner and proposed repair. Check seven signs by purpose, not prohibition. |
| 7. Repair and retest | Existing implementation owner + `ui-craft-and-visual-qa` | Fix one root cause; rerun the same scenario and preserve before/after artifacts. | A passing build is not a visual review; a screenshot is not proof back retains input. |
| 8. Transfer and calibrate | `visual-taste-calibration` + benchmark protocol | Repeat on a different domain with its own objects/risks. Compare decisions with a held-out rubric. | Redo if the old metaphor/policy transfers unchanged or an unmeasured result becomes a success claim. |

## Five practice briefs

- **Healthcare record/support:** tell pending from confirmed; identify the next actor,
  preserve patient context and use a verified contact. Do not invent clinic/clinical rules.
- **Commerce selection/review:** compare variant, actual cost and unknown delivery;
  retain filters/cart context and distinguish payment pending from order confirmation.
- **Portfolio evidence/contact:** distinguish contribution, prototype, research class
  and measured impact; make the actual artifact easy to find.
- **Enterprise request:** distinguish approval from provisioning and expiry from
  revocation; make scope, duration and recovery ownership readable.
- **Industrial scope:** expose inputs/outputs/exclusions and scope revision; do not
  imply equipment compatibility or commissioning from an illustrative diagram.

## Critique rubric and feedback record

Score each dimension 0–3 using evidence, or `UNVERIFIED` when evidence is missing:
task/state/action/recovery; information relationships; domain/evidence accuracy;
typography/spacing/composition; responsive/accessibility; rationale/transfer.
0 = observed blocker, 1 = material friction, 2 = sound with specific remaining
issues, 3 = clear execution for the declared task. Scores are practice feedback,
not a certification or user-study measurement. An unresolved task blocker prevents
acceptance regardless of the average. Media can be N/A when unnecessary.

Record:
`exercise + task → attempt artifact → observed issue/location → interpretation →
trade-off → owner/fix → same-scenario retest → evidence class → next practice`.

Example feedback: “In healthcare/fragile at 390px, I changed the note, opened review
and returned. The original note replaced the edit. The state owner resets on back.
Repair that owner and rerun the same sequence; changing card radius cannot fix it.”
Only use this wording as an observed result after actually exercising the specimen.

Revisit a weak dimension later on a **new brief** without annotations or copied
answers. A later independent attempt and practitioner feedback are stronger evidence
of learning than a checked lesson list. There is no fixed schedule or automatic
mastery status in this package.

## Source and evidence boundary

The lab's original cases and comments are authored teaching material. Domain workflow
candidates come from `data/domain-workflows.json`; primary standard sources live in
`ux-laws-and-heuristics/references/principle-sources.md`. Read one relevant source,
not every skill. For model/skill outcome trials use the existing eval harness and
controlled comparison protocol. A teaching
pair changes multiple axes and cannot isolate the effect of a font, layout or skill.
