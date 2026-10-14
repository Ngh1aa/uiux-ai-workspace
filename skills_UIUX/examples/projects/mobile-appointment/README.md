# Synthetic mobile browser prototype example

This is a small appointment-review fixture for the mobile workflow, not a real client app, native build, participant study or live deployment. `preview/` contains one renderer/state model for service/slot selection, confirmation, local demo bookings, cancellation, offline recovery and empty states.

From this directory, serve the static files with an available HTTP server, for example `python -m http.server 4173`, then open `http://127.0.0.1:4173/preview/`. Useful state links are `preview/?screen=confirm&service=portfolio&slot=16:00` and `preview/?screen=bookings&state=empty`. Use **Đặt lại demo** to clear local fixtures.

The `.uiux-profile.json` describes platform identity/design scope. It grants no output or publication authority. To produce a browser demo packet, run the canonical `prepare-external-task.py` with `--platform-family mobile_app --requested-output browser-prototype` and this target root.

For an actual target app, adapt [mobile-web-preview](../../../mobile-web-preview/SKILL.md) to its design system and code owners. The [Pages workflow asset](../../../mobile-web-preview/assets/github-pages.yml) can be copied into an authorized target project after QA. Nothing in this example enables Pages or publishes the Factory automatically.

Real-browser regression lives in `uiux-factory/qa/tests/mobile-preview-contract.spec.mjs` and runs with `npm run test:mobile-preview` in the existing QA workspace. It tests phone/desktop widths, interaction/reload/Back, labelled demo data, recovery, subpath assets and query-state validation. Screenshots prove the browser fixture rendered; they do not certify native UX or actual user outcomes.
