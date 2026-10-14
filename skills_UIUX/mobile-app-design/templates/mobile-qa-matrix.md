# Mobile QA Matrix

Design/prototype observations and native runtime checks are separate. Start with critical tasks and declared devices; expand by feature/risk rather than multiplying every condition mechanically.

| Scenario | Platform / OS / device | Locale / theme / text scale | Initial state | Action | Expected outcome | Evidence + revision/hash | PASS/FAIL/NOT_RUN/UNKNOWN |
|---|---|---|---|---|---|---|---|

## Conditional coverage
- Primary task, save/pending/failure/retry and navigation return.
- Keyboard open/closed, safe areas/system bars and gesture Back/dismiss/cancel.
- Long/localized content, large text, dark mode, reduced motion.
- VoiceOver/TalkBack reading order, labels/actions and announcements.
- Permission denial/revocation, auth expiry and recovery when relevant.
- Offline/reconnect/conflict, interruption/resume/restoration when relevant.
- Deep links/notifications, tablet/foldable/multi-window, device capabilities when relevant.

Native checks bind source SHA, application/build identity, artifact hash, OS/device, test-tool version, scenario/assertions and capture hash. Screenshots alone do not prove behavior or accessibility. Record untested physical-device, performance and store-release coverage explicitly. Do not mark a planned test PASS.
