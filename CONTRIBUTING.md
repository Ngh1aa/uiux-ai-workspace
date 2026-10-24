# Contributing

Thank you for improving uiux-ai-workspace. Start with [WORKFLOWS.md](WORKFLOWS.md) for design work
and [AGENTS.md](AGENTS.md) for the operating and evidence contract.

## License of contributions

Contributions are accepted under the same terms as the project (inbound = outbound):

- code, skills, prompts, flows, design tokens, CSS components and icons: [Apache-2.0](LICENSE);
- documentation in `docs/`, `design-system/docs/` and review screenshots:
  [CC BY 4.0](LICENSE-DOCS).

Sign off every commit to certify the [Developer Certificate of Origin](https://developercertificate.org/):

```sh
git commit -s -m "Describe the change"
```

The sign-off line (`Signed-off-by: Your Name <email>`) states that you wrote the change or have the
right to submit it under these licenses.

## Third-party content

- Check [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before copying anything that is not your own.
- **Never copy or adapt** files from Anthropic's source-available skills (`docx`, `pdf`, `pptx`,
  `xlsx`), from `doc-coauthoring` (no license) into this repository. Their terms forbid redistribution and derivative works. This applies to AI agents
  working in the repository as much as to people.
- Keep upstream code inside its submodule or vendor folder, unmodified, and put local adaptations
  outside it.
- Bundled fonts must keep their OFL license file next to the font files.
- Do not commit screenshots or text you do not have the right to share (third-party brand assets,
  paywalled articles, private user data).

## Checks before a pull request

```sh
python skills_UIUX/scripts/validate-skills.py
python skills_UIUX/scripts/validate-v2.py
python -m pytest -q skills_UIUX/tests
python scripts/check-links.py
python design-system/scripts/validate.py
```

`main` is protected: a pull request needs the `foundation` and `release-candidate` checks to pass.
