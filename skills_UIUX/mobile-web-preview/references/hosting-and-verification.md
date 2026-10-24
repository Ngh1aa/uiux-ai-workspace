# Hosting and verifying a mobile browser prototype

## Select the existing target path

Keep the target's current framework. A static HTML/CSS/JS preview needs no new framework or dependency. An existing React/Expo app may reuse its web-compatible views; a SwiftUI/Compose codebase needs a separate browser presentation adapter, not an alleged native-to-HTML conversion.

For Expo, inspect the installed SDK and current official [web publishing guide](https://docs.expo.dev/guides/publishing-websites/). Export the web build with the target's package manager. GitHub Pages needs static output: explicitly choose `web.output=static` for prerendered routes, or a compatible single-page export with a working hash/query navigation strategy. Server output and API routes require a suitable server host. Validate the target's base URL/asset paths and actual export under the repository subpath. Do not change the native target stack metadata to describe the browser adapter.

For a static preview, relative asset paths and query/hash state links normally work under both a local subpath and a project Pages URL. Direct pathname navigation must correspond to exported HTML; GitHub Pages is not a general SPA fallback server. A service worker/PWA installation is optional and has its own cache/update QA.

## Publish only within current authorization

The [Pages workflow asset](../assets/github-pages.yml) assumes authorized deployment from the target's `main` and static files in `preview/`. Copy it into that target's `.github/workflows/` only when publication is in scope. Adapt the build/output directory to existing project commands; do not enable deployment for the Factory as a side effect. Configure Pages to use GitHub Actions and inspect existing hosting before changing it.

If the target already publishes a website, retain its workflow and include the mobile preview as a subdirectory of the existing static artifact, or use a separately authorized demo repository. Uploading only `preview/` as the entire site would replace that site's published content; do not use the standalone template to overwrite an existing website.

The template runs only on an explicit workflow dispatch, separates build from deployment and scopes `pages: write` / `id-token: write` to deployment. It does not install packages, manufacture QA or collect native evidence. Use the project's existing QA before dispatch. Consult [custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) for current hosting requirements. No secrets or backend services belong in a public static bundle.

## Bind the client handoff to actual evidence

1. Record the intended source SHA and current browser interaction/capture evidence.
2. Retrieve the real Pages deployment/build metadata from GitHub. Keep provider-reported deployed SHA/status separate from the intended SHA; never copy the latter into the former as proof.
3. Open the live URL in a real browser and compare it with that metadata. If no provider SHA is available, preserve UNKNOWN/PREPARED rather than inventing DEPLOYED_VERIFIED.
4. Open the actual URL on a phone-sized viewport and desktop. Verify critical tasks, assets, route reload and project subpaths again. A 2xx landing page alone is insufficient for interaction acceptance.
5. Complete [client handoff](../templates/client-handoff.md). Include the working URL, optional locally generated QR, platform presentation, data/reset behavior, source revision, known limitations and current observations. QR is just an alternate way to open the URL.

Sources checked: 2026-10-14. Linked documentation is guidance only; no upstream code or design kit is vendored by this capability.
