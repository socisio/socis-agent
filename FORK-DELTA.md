# Fork delta

Files this fork carries at paths upstream also uses. **70** of them.

A rebase-and-rebrand replays these by hand; everything else is copied or
rebuilt (2495 files under `optional-skills/security/` and
`optional-mcps/` replay by copy, generated docs are regenerated).

Measured 2026-09-11 against upstream `aa05e5c0f454`
by `scripts/fork_delta.py`, which runs monthly via `.github/workflows/fork-delta.yml`.
Regenerate rather than editing by hand.

## `(root)` (2)

- `MAINTENANCE.md`
- `PROJECT-TREE.md`

## `.github` (4)

- `.github/workflows/fork-delta.yml`
- `.github/workflows/release-desktop.yml`
- `.github/workflows/skill-names-check.yml`
- `.github/workflows/upstream-watch.yml`

## `apps` (18)

- `apps/bootstrap-installer/public/socis-mark.jpg`
- `apps/desktop/assets/icons/128x128.png`
- `apps/desktop/assets/icons/16x16.png`
- `apps/desktop/assets/icons/24x24.png`
- `apps/desktop/assets/icons/256x256.png`
- `apps/desktop/assets/icons/32x32.png`
- `apps/desktop/assets/icons/48x48.png`
- `apps/desktop/assets/icons/512x512.png`
- `apps/desktop/assets/icons/64x64.png`
- `apps/desktop/e2e/mock-server.ts`
- `apps/desktop/electron/update-count.test.ts`
- `apps/desktop/electron/update-count.ts`
- `apps/desktop/public/socis-mark.jpg`
- `apps/desktop/scripts/dev-mock.mjs`
- `apps/desktop/src/app/settings/plugins-settings.test.tsx`
- `apps/desktop/src/app/settings/plugins-settings.tsx`
- `apps/desktop/src/plugins/accent/picker.tsx`
- `apps/desktop/src/plugins/accent/plugin.tsx`

## `scripts` (8)

- `scripts/check-skill-names.py`
- `scripts/fork_delta.py`
- `scripts/sandbox/openssl.cnf`
- `scripts/sandbox/proxy.py`
- `scripts/sandbox/ssh-shim.sh`
- `scripts/sandbox/stage2-run.sh`
- `scripts/set-version.py`
- `scripts/vendor_security_skills.py`

## `skills` (8)

- `skills/security-operations/alert-triage/SKILL.md`
- `skills/security-operations/attack-mapping/SKILL.md`
- `skills/security-operations/detection-engineering/SKILL.md`
- `skills/security-operations/evidence-handling/SKILL.md`
- `skills/security-operations/incident-response/SKILL.md`
- `skills/security-operations/ioc-enrichment/SKILL.md`
- `skills/security-operations/network-signature-authoring/SKILL.md`
- `skills/security-operations/yara-authoring/SKILL.md`

## `socis_cli` (2)

- `socis_cli/data/plugin_index.json`
- `socis_cli/plugin_index.py`

## `tests` (19)

- `tests/agent/test_opencode_session_header.py`
- `tests/agent/test_skill_triggers.py`
- `tests/cron/test_cron_drift_alert_once.py`
- `tests/gateway/relay/test_descriptor_from_entry.py`
- `tests/gateway/test_max_tokens_propagation.py`
- `tests/gateway/test_session_boundary_hooks.py`
- `tests/install/install-update-e2e.sh`
- `tests/scripts/test_fork_delta.py`
- `tests/socis_cli/test_availability_guard.py`
- `tests/socis_cli/test_model_listing_priority.py`
- `tests/socis_cli/test_model_verification.py`
- `tests/socis_cli/test_nous_hermes_non_agentic.py`
- `tests/socis_cli/test_plugin_index_search.py`
- `tests/socis_cli/test_provider_credential_gate.py`
- `tests/tools/test_detection_yargen.py`
- `tests/tools/test_mcp_oauth_log_hygiene.py`
- `tests/tools/test_mitre_attack.py`
- `tests/tools/test_skill_view_not_found.py`
- `tests/tools/test_tool_schema_shapes.py`

## `tools` (7)

- `tools/cisa_kev.py`
- `tools/detection_tools.py`
- `tools/domain_permutations.py`
- `tools/mitre_attack.py`
- `tools/wakewords/hey_socis.onnx`
- `tools/wakewords/hey_socis.tflite`
- `tools/yara_strings.py`

## `website` (2)

- `website/src/pages/download/index.tsx`
- `website/src/pages/download/styles.module.css`
