# Docs Screenshot Retake Punch List

These 26 screenshots (11 dashboard + 10 kanban-tutorial + 5 dashboard-models/
tui-orchestrator) plus 1 demo video all show the **old UI** — sidebar text
reading "HERMES AGENT", "Update Hermes", "Nous Research", "HERMES TEAL" is
visible in every one checked. They need to be retaken from the actual
running, rebranded platform. Below is exactly what page/state each one
needs to show, so retaking them is a checklist rather than guesswork.

## How to retake these

1. Run the rebranded platform locally: `socis dashboard` (or `socis serve`),
   open the web dashboard in a browser.
2. Navigate to each page listed below, get it into the described state.
3. Screenshot at a reasonable width (the originals look like ~1280–1400px
   wide browser screenshots — match that for consistent sizing across docs).
4. Save with the **exact same filename** into the same folder
   (`website/static/img/dashboard/` or `website/static/img/kanban-tutorial/`)
   to overwrite the old file — no doc-page edits needed since the `.md`
   files already reference these paths correctly.

## Dashboard screenshots (`website/static/img/dashboard/`)

| Filename | Page / State to capture |
|---|---|
| `admin-config.png` | Config admin page — section filters on the left, auto-discovered fields on the right |
| `admin-sessions.png` | Sessions admin page — stats bar, prune button, and per-row rename/export/delete controls visible |
| `admin-skills-hub.png` | Skills admin page — the "Browse" hub view showing search, install, update options |
| `admin-mcp.png` | MCP admin page — your configured servers with enable/disable toggles, plus the install catalog |
| `admin-webhooks.png` | Webhooks admin page — subscriptions list with enable/disable toggles |
| `admin-pairing.png` | Pairing admin page (whatever state it's normally shown in) |
| `admin-channels.png` | Channels admin page — every messaging platform listed with status, enable toggles, per-platform setup forms |
| `admin-system-top.png` | System admin page, top section — host stats and **Nous Portal** status (this section legitimately still says "Nous Portal" since that's the real third-party service name, not a rebrand miss) |
| `admin-system-curator.png` | System admin page — skill curator, gateway, memory, and credential pool sections |
| `admin-system-ops.png` | System admin page — operations, checkpoints, and shell hooks sections |
| `admin-hook-create.png` | The "New shell hook" creation modal, open and populated with example fields |

## Kanban tutorial screenshots (`website/static/img/kanban-tutorial/`)

| Filename | Page / State to capture |
|---|---|
| `01-board-overview.png` | Kanban board overview — the main board view |
| `02-board-flat.png` | Kanban board with "Lanes by profile" toggle turned **off** |
| `03-drawer-schema-task.png` | Solo-dev view — a completed schema task's drawer open |
| `06-drawer-crash-recovery.png` | Drawer showing a crash-and-recovery state: 1 crashed task + 1 completed task |
| `07-fleet-transcribes.png` | Fleet view filtered to transcription tasks |
| `08-pipeline-auth.png` | Pipeline view for a multi-role feature (e.g. an "auth" pipeline) |
| `09-drawer-pipeline-review.png` | A reviewer's drawer view of a pipeline task |
| `10-drawer-in-flight.png` | Drawer showing a claimed, in-flight (currently running) task |
| `11-drawer-gave-up.png` | Drawer showing the circuit-breaker state: 2 `spawn_failed` + 1 `gave_up` |

**Not currently referenced anywhere in the docs** (found on disk but no
`.md` file links to it — likely orphaned from an earlier tutorial draft):
- `04b-drawer-retry-history-scrolled.png` — probably safe to leave as-is or
  delete; only retake if you rediscover a doc page that's supposed to use it.

## Additional screenshots found in a second pass (`website/static/img/docs/`)

| Filename | Page / State to capture |
|---|---|
| `dashboard-models/overview.png` | Models page overview — main model card, models-used stats row, and the per-model usage cards below |
| `dashboard-models/picker-dialog.png` | The model picker dialog, open |
| `dashboard-models/auxiliary-expanded.png` | The "Show auxiliary" panel expanded |
| `dashboard-models/use-as-dropdown.png` | The "Use as" dropdown menu, open on one of the model cards |
| `tui-session-orchestrator/session-orchestrator.png` | TUI Session Orchestrator view with one live session and a "+ new" row visible |

## Video file also needs re-recording (not just a screenshot)

**`website/static/img/docs/tui-session-orchestrator/session-orchestrator-demo.mp4`**
— referenced in `website/docs/user-guide/tui.md`, embedded as an autoplay
demo video showing the TUI Session Orchestrator in action. Since this
predates the TUI banner/mascot fixes, it almost certainly shows the old
"HERMES AGENT" banner and/or the caduceus mascot animation on screen at some
point. This needs to be **re-recorded** from the current, rebranded TUI —
there's no way to patch a video file's visible content after the fact the
way a still screenshot could theoretically be touched up. Same workflow as
the screenshots: run the rebranded `socis` TUI, record the same interaction
(one live session, then start a new one via the "+ new" row), save over the
same filename.



After retaking, re-run this check from the repo root to confirm no old
"hermes"/"nous" branding survives in these images — this uses OCR-free
heuristics (just re-running the same audit approach), so it's not perfect,
but a quick visual scan of each file is the reliable way to confirm:

```bash
# Just re-open each file and eyeball the sidebar/header text once retaken.
# There's no reliable way to grep pixel content, so this is a manual check.
ls website/static/img/dashboard/ website/static/img/kanban-tutorial/
```
