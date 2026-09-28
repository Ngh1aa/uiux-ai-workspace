# Safe Read Contract — A4.1

A4.1 defines the fail-closed read boundary used by the canonical Flow OS runtime.

Executable enforcement lives in:

```text
uiux-factory/core/runtime/flow_os/safe_read.py
```

This document owns the declarative contract only.

## Goal

A READ permission means "read approved project/runtime knowledge safely". It does **not** mean arbitrary filesystem access.

Every project/source read exposed to a model or provider must be anchored to an explicit trusted root and revalidated at the moment the bytes are loaded.

## Required guarantees

A Safe Read must:

1. resolve below an explicit allowlisted root;
2. reject lexical and resolved root escape;
3. reject symlink paths instead of inheriting target trust implicitly;
4. reject credential-bearing paths such as `.env`, `.env.local`, `.npmrc`, `.pypirc`, `.netrc`, common service-account/credential files and private-key file types;
5. permit non-secret environment templates such as `.env.example`, `.env.sample` and `.env.template`;
6. reject runtime/internal dependency trees that a model should not inspect directly (`.git`, `.uiux-agent-runs`, `node_modules`);
7. require a regular file for text reads;
8. enforce a bounded per-file byte budget;
9. reject NUL/binary content and invalid UTF-8 rather than decoding with replacement characters;
10. reject obvious private-key material even when stored under an otherwise innocent filename;
11. fail closed when a previously accepted context path changes into an unsafe path before provider load.

## Canonical read paths

The same Safe Read implementation must govern:

```text
read_text tool
context-manifest project/source inspection
provider skill/source context loading
safe project directory listing
```

Provider context loading must not trust a checkpoint-provided root by itself. The active harness supplies the allowed roots, currently:

```text
project_root
skills_UIUX root
```

A stored `read_root` is provenance metadata; it is valid only when it matches the active allowlist.

## Checkpoint compatibility

Older checkpoints may not contain `read_root`. They may be migrated only by testing their stored path against the current harness-provided allowlisted roots through Safe Read. If no safe root accepts the path, the run must stop rather than load the file.

## Listing behavior

Safe directory listing is intentionally narrower than raw filesystem listing. It omits:

- blocked credential-bearing files;
- blocked internal/dependency directories;
- symlink entries.

This prevents discovery from becoming a side channel around the read boundary.

## Scope boundary

A4.1 protects model/provider **read** surfaces. It does not claim to solve:

- write/worktree isolation — A4.2;
- isolated target command execution — A4.3;
- typed evidence/gate semantics — A4.4;
- expanded file edit/search tools — A4.5;
- OS-level race-proof sandboxing against a hostile concurrent local process.

Write tools keep their existing authority checks until A4.2/A4.5 hardening.

## Verification

A4.1 is only PASSED when regression tests prove at minimum:

- normal UTF-8 project reads still work;
- traversal/root escape is rejected;
- secret/internal paths are rejected;
- binary/invalid UTF-8/private-key content is rejected;
- byte limits are enforced;
- symlink reads are rejected;
- safe listing hides denied entries;
- context manifests record a trusted read root;
- provider context revalidates allowed roots;
- old checkpoints can migrate only through the current allowlist;
- a post-manifest symlink swap is rejected;
- the complete Factory CI remains green on `main` after merge.
