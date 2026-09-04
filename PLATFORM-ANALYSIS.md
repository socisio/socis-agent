# SOCIS Agent — Platform Analysis

Deep analysis of the rebranded `socis-agent` platform (formerly `hermes-agent`),
covering: critical files, removable files, dependency/vulnerability posture, and
the `@nous-research/*` package question as it relates to UI and Desktop colors.

All figures below were measured directly against the current tree, not estimated.

---

## 1. Critical files — do not break these

"Critical" here means **dependency fan-in** (how many modules import it), not file
size. A large file with no dependents is far less risky than a small one imported
by 479 modules.

### Tier 1 — load-bearing core (breaking these breaks everything)

| File | Imported by | Role |
|---|---|---|
| `socis_agent_constants.py` | **479 files** | Path resolution (`~/.socis-agent/`), env var names, global constants. The single most depended-on module in the platform. |
| `socis_agent_state.py` | **360 files** | SQLite session/message persistence (`state.db`), FTS search, compression watermarks. |
| `utils.py` | **152 files** | Shared helpers (atomic writes, YAML/JSON round-trips, truthy parsing). |
| `toolsets.py` | **43 files** | Toolset registry — defines which tools exist and how they group. |
| `socis_agent_logging.py` | 19 files | Structured logging, profile-scoped log routing. |
| `socis_agent_bootstrap.py` | 11 files | Startup sequencing, early recovery. |

### Tier 2 — largest subsystems (high blast radius when changed)

| File | Size | Role |
|---|---|---|
| `gateway/run.py` | 1.6 MB | Multi-platform gateway event loop (Telegram/Discord/Slack/WhatsApp/Signal). |
| `cli.py` | 1.0 MB | Interactive CLI/TUI chat surface. |
| `socis_cli/web_server.py` | 808 KB | Dashboard HTTP/WS server, auth middleware, all REST routes. |
| `tui_gateway/server.py` | 764 KB | JSON-RPC backend the TUI and Desktop app both talk to. |
| `socis_cli/main.py` | 612 KB | CLI entry, subcommand dispatch, provider/model selection. |
| `agent/conversation_loop.py` | 512 KB | The core agent turn loop. |
| `agent/auxiliary_client.py` | 524 KB | Secondary-model client (compression, titles, reviews). |
| `agent/context_compressor.py` | 452 KB | Context-window compression. |
| `socis_cli/auth.py` | 420 KB | All OAuth/credential flows (see §4 — contains the one remaining `hermes-cli` value). |

### Tier 3 — entry points (defined in `pyproject.toml`)

```
socis        -> socis_cli.main:main      # main CLI
socis-agent  -> run_agent:main           # agent runtime
socis-acp    -> acp_adapter.entry:main   # editor protocol bridge (Zed etc.)
```

Plus the npm workspace root (`package.json`, name `socis-agent`) with workspaces:
`apps/*`, `ui-tui`, `ui-tui/packages/*`, `web`, `tests-js`.

### Tier 4 — branding-critical (changing these changes what users see)

| File | Controls |
|---|---|
| `SOUL.md` | Agent persona ("You are SOCIS Agent, built by SOCIS"). |
| `ui-tui/src/banner.ts` | TUI ASCII wordmark + hero mark art. |
| `ui-tui/src/theme.ts` | TUI color seeds (coral/navy). |
| `web/src/themes/presets.ts` | Dashboard themes. |
| `web/src/index.css` | Dashboard CSS token defaults. |
| `apps/desktop/src/themes/presets.ts` | **Desktop themes — still Nous-blue defaulted, see §4.** |
| `apps/desktop/src/styles.css` | **Desktop CSS tokens — still hardcodes `#0053fd`, see §4.** |
| `website/docusaurus.config.ts` | Docs site title/URL/social image. |

---

## 2. Files that can be removed

### Safe to remove now — orphaned, zero references

| Path | Size | Why |
|---|---|---|
| `docs/hermes-kanban-v1-spec.pdf` | 214 KB | Historical Hermes-era design PDF. Referenced only by the rebrand toolchain's exclusion list — nothing in the product reads it. |
| `scripts/rebrand/` | 36 KB | The rebrand toolchain itself (`rebrand_map.py`, `run_rebrand.py`). Its job is done; keep it only if you want the audit trail of how the rebrand was performed. |

### Safe to remove if you don't need the capability

| Path | Size | What you lose |
|---|---|---|
| `evals/` | 496 KB | Benchmark harnesses (browser-use, compaction, read-tool, session-search). Dev-only; no runtime code imports them. |
| `mcp-research-data/` | 224 KB | Static research result JSON from MCP benchmarking. Dev-only. |
| `datagen-config-examples/` | 20 KB | Example dataset-generation configs. |
| `tests-js/` | 80 KB | JS-side workspace tests (entitlements, engine alignment). Remove only if you're dropping JS CI. |
| `optional-skills/` | ~12 MB | 718 files of opt-in skill packs. Not loaded unless a user explicitly opts in. Biggest single space win if you want a leaner repo. |
| `optional-mcps/` | ~65 files | Third-party MCP server manifests (Asana, Stripe, Figma, etc.). Same opt-in model. |

### Already removed in this rebrand

- `contributors/` (~990 files) + `contributor-check` CI job + `add_contributor.py` /
  `audit_pr_attribution.py` + `test_contributor_map.py` — removed per explicit decision.
- `website/static/img/nous-logo.png` — orphaned, unreferenced.
- `apps/desktop/public/nous-girl.jpg`, `apps/bootstrap-installer/public/nous-girl.jpg`
  — replaced with `socis-mark.jpg` (code references updated).

### Do **not** remove

- `contributors/`-style attribution is gone, but **`LICENSE` must stay** — MIT
  requires retaining the copyright notice.
- `plugins/security-guidance/LICENSE` + `NOTICE` — Apache-2.0 attribution to
  Anthropic for vendored code. Legally required.
- `optional-skills/software-development/ast-grep/LICENSE`,
  `skills/creative/humanizer/LICENSE` — third-party individual authors.
- `uv.lock`, `package-lock.json` — regenerate, don't delete (see §3).

---

## 3. Package / vulnerability posture

### Current state (measured from `package-lock.json`: 1,417 locked packages)

Your `socis doctor` run reported **2 moderate + 4 high** in the `web` workspace.
The build log showed **6 vulnerabilities (2 moderate, 4 high)** at root. Every
deprecated package flagged during install is a **transitive** dependency — none
are declared directly by this project, which means you cannot fix them by editing
your own `package.json`:

| Deprecated package | Version | Pulled in by | Direct fix possible? |
|---|---|---|---|
| `inflight@1.0.6` | leaks memory | `glob@7.2.3` | No — fix by upgrading `glob` |
| `glob@7.2.3` | EOL | `node-gyp`, `rimraf`, `cacache` | No — upstream must upgrade |
| `npmlog@5.0.1` | unsupported | `@mapbox/node-pre-gyp` | No |
| `are-we-there-yet@2.0.0` | unsupported | `npmlog` | No |
| `gauge@3.0.2` | unsupported | `npmlog` | No |
| `rimraf@2.6.3` / `3.0.2` | pre-v4 EOL | `temp`, `@mapbox/node-pre-gyp` | No |
| `boolean@3.2.0` | unsupported | dev-only | No |
| `rcedit@5.0.2` | unsupported | `electron-builder` (dev) | No |

**What this means:** these are almost entirely **build-time tooling**
(`node-gyp`, `electron-builder`, `@mapbox/node-pre-gyp`) — not runtime code
shipped to users. The `socis doctor` output said as much: *"build-tool advisory;
clears via lockfile bump."*

### Recommended actions, in order

1. **Regenerate the lockfile first.** It's currently out of sync (this is what
   caused your `npm ci` failure — `npm error Missing: @socis/ink@0.0.1 from lock
   file`). From the repo root, not a subfolder:
   ```bash
   rm package-lock.json && npm install
   ```
   This alone may clear several advisories by resolving newer patch versions.

2. **Then run the audit and see what's actually left:**
   ```bash
   npm audit
   npm audit fix          # safe, semver-compatible fixes only
   ```

3. **Only if needed**, `npm audit fix --force` — but review the diff first, since
   it can bump major versions of `electron-builder`/`vite` and break the build.

4. **Python side:** `pyproject.toml` pins `requires-python = ">=3.11,<3.14"` with
   112 dependency entries. Regenerate with:
   ```bash
   uv lock && uv sync
   ```
   (`uv.lock` still references the pre-rebrand `hermes-agent` package name
   internally — regenerating fixes that too.)

5. **Ongoing:** the repo already ships `.github/workflows/osv-scanner.yml` and
   `supply-chain-audit.yml`. Those will keep reporting once CI runs on your repo.

---

## 4. The `@nous-research/*` packages and your UI colors

This is the most consequential finding for your branding goal.

### What's actually depended on

| Package | Version | Used by |
|---|---|---|
| `@nous-research/ui` | `0.18.2` | `web`, `apps/desktop`, `apps/bootstrap-installer` |
| `@nous-research/image-size` | `2.0.3` (aliased as `image-size`) | `website` |

`@nous-research/ui` is imported by **48 source files**, with this surface area:

```
button (34)  spinner (25)  badge (24)  card (23)  input (21)  toast (18)
label (17)   use-toast (17)  select (12)  use-confirm-delete (9)
typography/h2 (8)  list-item (8)  switch (7)  confirm-dialog (7)
checkbox (6)  dialog (5)  segmented (3)  use-below-breakpoint (3)
stats (2)  command-block (2)  bottom-sheet (2)  tabs (1)  separator (1)
```

These are **real, externally-published npm packages** owned by Nous Research.
They are not renameable — pointing at `@socis/ui` would break every install,
because no such package exists on the registry.

### The good news: you do NOT need to fork them to control colors

The dashboard already **re-themes the Nous DS entirely through CSS variables**.
`web/src/index.css` remaps every design-system token onto your own palette:

```css
--color-primary:            var(--midground);
--color-primary-foreground: var(--background-base);
--color-card:      color-mix(in srgb, var(--midground-base) 4%, var(--background-base));
--color-accent:    color-mix(in srgb, var(--midground-base) 10%, var(--background-base));
--color-muted:     color-mix(in srgb, var(--midground-base) 8%,  var(--background-base));
```

Because every component reads these variables, changing `--midground-base` /
`--background-base` re-skins the entire component library. That's why the
dashboard fix (coral `#FFD9E1` on navy `#070A0F`) worked without touching the
package at all.

**Conclusion: keep `@nous-research/ui` as a dependency.** It's a rendering
library, not branding. Forking it would mean maintaining 25+ components for zero
visual benefit you can't already achieve through tokens.

### The real remaining problem: the Desktop app is still Nous-blue

The Desktop app has a **third, separate theme system** that was never rebranded —
distinct from both the TUI (`ui-tui/src/theme.ts`) and the dashboard
(`web/src/themes/`). It is still Nous-branded at the identity level:

| Location | Issue |
|---|---|
| `apps/desktop/src/themes/presets.ts:865` | `export const DEFAULT_SKIN_NAME = 'nous'` — the **default skin is literally named "nous"**. |
| `apps/desktop/src/themes/presets.ts:174` | `export const nousTheme` (`name: 'nous'`) — the default theme object. |
| `apps/desktop/src/themes/presets.ts:601` | `export const nousAltTheme` (`name: 'nous-alt'`) — a second Nous theme. |
| `apps/desktop/src/themes/presets.ts:168` | Comment: *"`#0053FD` is the brand color"* — Nous blue, described as the brand. |
| `apps/desktop/src/styles.css:174–214` | Hardcodes `#0053fd` **6 times** as `--theme-primary`, `--theme-midground`, `--ui-blue`, and in three `color-mix()` derivations. |
| `apps/desktop/src/themes/retint.ts`, `color.ts` | Comments referencing "Nous blue" as the reference brand color for contrast math. |

**To make the Desktop app match your coral/navy brand you need to:**

1. Replace the `#0053fd` seeds in `apps/desktop/src/styles.css` `:root` block with
   your palette (`#FF3366` primary / `#070A0F` background). The `.dark` block
   already inherits via variables, so only the light `:root` block needs changing.
2. Rename `nousTheme` → a brand-neutral name and update `DEFAULT_SKIN_NAME`.
   **Important:** like the dashboard themes, the internal `name: 'nous'` string is
   a *persisted user setting*. Renaming the key without an alias entry will
   silently reset every existing user's skin choice. The dashboard solved this
   with a `THEME_NAME_ALIASES` table in `web/src/themes/context.tsx` — the desktop
   app needs the same treatment, or you keep the key and change only the label.
3. Update the contrast-math comments in `retint.ts` / `color.ts` that use Nous
   blue as their worked example.

There is also a `retint.test.ts` with `const NOUS_BLUE = '#0053FD'` and assertions
pinned to that value — those tests will need updating alongside any seed change.

---

## 5. Summary of what's still open

| Item | Status |
|---|---|
| Desktop app theme (Nous blue `#0053fd`, `DEFAULT_SKIN_NAME = 'nous'`) | **Not done** — §4 above |
| Lockfile regeneration (`npm install`, `uv lock`) | **Not done** — needs network |
| npm vulnerabilities (2 moderate / 4 high, all build-tooling transitives) | **Not done** — clears via lockfile bump |
| 26 doc screenshots + 1 demo video showing old UI | **Not done** — see `SCREENSHOT-RETAKE-PUNCHLIST.md` |
| `hermes-cli` OAuth client ID | **Intentionally kept** — it's a credential registered on Nous's server, not branding. Only 2 lines, never user-visible. |
| `@nous-research/ui` dependency | **Intentionally kept** — real external package; colors are controlled via CSS tokens instead. |
| Wake-word models (`hey_hermes.onnx/.tflite`) | **Not done** — requires ML retraining, not a rename. |

---

## 6. Changes applied in this pass

### Desktop app theme — rebranded to SOCIS coral

The Desktop app's theme system (a third, separate one from the TUI and the web
dashboard) was still Nous-blue. Fixed with the **same two-seed discipline the
original theme documented**, rather than dropping the raw brand hex in:

| | Old (Nous) | New (SOCIS) | Contrast |
|---|---|---|---|
| Light seed | `#0053fd` | `#c42248` | 5.38:1 on `#f6f8fa` (old was 5.40) |
| Dark seed | `#4a84fe` | `#f04162` | 5.51:1 on `#010409` (old was 5.89) |
| Shared OKLCH hue | 263° | **15°** | both seeds, verified |

Raw brand coral `#FF3366` was **not** used directly: it measures only 3.33:1 on
the light sidebar, below WCAG AA. Both seeds were computed to sit at one hue
(preserving the theme's own invariant, which `retint.test.ts` asserts) while
each clearing AA in its own appearance. Soft surfaces (`secondary`, `accent`,
`userBubble`) were re-mixed from the new seeds at the upstream mix ratios.

Files changed:
- `apps/desktop/src/themes/presets.ts` — `nousTheme` re-seeded, label → `SOCIS`
- `apps/desktop/src/styles.css` — 5 hardcoded `#0053fd` → `#c42248`
- `apps/desktop/src/themes/retint.test.ts` — hue/seed assertions updated to 15° / new hexes
- `apps/desktop/src/themes/{color,retint}.ts` — worked-example comments updated
- `apps/desktop/src/plugins/accent/picker.tsx` — swatch list now leads with the SOCIS seeds
- `apps/bootstrap-installer/src/styles.css` — dark seeds re-synced to `nousTheme.darkColors` (it hardcodes a mirror because the installer has no theme runtime; it had drifted to the old Nous-Alt palette)

### Deliberately left unchanged, with reasons

| Item | Why |
|---|---|
| Theme registry keys `'nous'`, `'nous-alt'`, `DEFAULT_SKIN_NAME` | **Persisted user settings.** Renaming a key silently resets every user's saved skin. Labels/descriptions carry the branding instead. A comment now documents this at the registry. |
| `nousAltTheme` palette (mission-blue + cream) | Its identity is blue *end to end* — dark mode is cream text on a blue canvas, not a blue accent. Re-seeding to coral would put coral text on blue. Renamed label → `Cobalt Alt`; palette kept. |
| `--ui-blue: #0053fd` | A semantic palette slot beside `--ui-red`/`--ui-green`. Blue is meant to be blue. |
| `tier-art.tsx` blue well | Deliberately reproduces Nous Portal's own tier-card design so the billing page matches the real portal. |
| `docs.honcho.dev/.../hermes`, `banks/hermes/import` | Real third-party URLs/paths on servers we don't control. |

### Placeholder hostnames rebranded (31 files)

`hermes.example.com`, `hermes.local`, `hermes-agent.local`, `example.com/hermes`,
`/hermes-events` → SOCIS equivalents. These are example/dummy hosts, several
user-visible as **input placeholder text** (`urlPlaceholder` in 6 i18n locales).
Real third-party URLs were excluded from the pass.

This also fixed a **genuinely broken test**: `connection-config.test.ts:869`
asserted `normalizeRemoteBaseUrl('gw.example.com/socis/')` → `'http://gw.example.com/hermes'`
— input and expectation disagreed, left over from the earlier partial rebrand.

### Removed

- `docs/hermes-kanban-v1-spec.pdf` (214 KB, orphaned — no references)

### Verification after all changes

- **5,127 Python files** — 0 syntax errors
- **web / ui-tui / apps/desktop** — 0 TypeScript grammar errors each
- **6 key JSON configs** — all valid

---

## 7. The gold that survived four passes — root cause

The dashboard chat panel stayed gold after the TUI, web-dashboard, and desktop
theme fixes. Cause: **`cli.py` carries its own complete copy of the banner art
and color palette**, independent of `ui-tui/src/`. The dashboard's chat panel is
an embedded PTY rendering that Python CLI output, so it inherited the gold
regardless of any TypeScript-side theming.

Found in `cli.py`:
- `SOCIS_AGENT_AGENT_LOGO` — a second block-letter wordmark, **still spelling
  "HERMES-AGENT"**, in gold `#FFD700`/`#FFBF00`/`#CD7F32`
- `SOCIS_AGENT_CADUCEUS` — a second copy of the caduceus mascot, in gold
- ~50 further uses of the 5-color gold ramp across status bars, borders,
  completion menus, approval dialogs, and clarify prompts

### The ramp mapping applied

| Role | Gold (old) | Coral (new) | Contrast on `#070A0F` |
|---|---|---|---|
| Primary/headers | `#FFD700` | `#FF3366` | 5.59:1 |
| Secondary | `#FFBF00` | `#F04162` | 5.32:1 |
| Borders/tertiary | `#CD7F32` | `#C42248` | 3.46:1 |
| Body text | `#FFF8DC` | `#FFD9E1` | 15.35:1 |
| Dim/muted | `#B8860B` | `#A81D3E` | 2.75:1 |

The two lowest are used for **borders and dim text only** — their gold
originals (bronze, dark goldenrod) were equally low-contrast, so this preserves
the original design intent rather than changing it.

### Light-mode remap table also corrected

`cli.py`'s `_LIGHT_MODE_REMAP` darkens dark-mode colors for light terminals. A
naive find/replace updated its *keys* but left gold-derived *values*
(`#9A6B00`, `#8A5A00`), so coral would have remapped to goldenrod on light
terminals. Values recomputed: `#A3103A` (7.8:1 on white), `#9A1338` (8.3:1),
`#7A1330` (10.7:1), `#6B0F26` (12.2:1).

### Files changed in this pass

`cli.py`, `socis_cli/cli_commands_mixin.py`, `socis_cli/journey.py`,
`socis_cli/session_export_html.py`, `socis_cli/web_server.py` (comment),
`ui-tui/src/theme.ts`, `ui-tui/src/__tests__/theme.test.ts`.

Left alone: test fixtures in `loaders.test.ts`, `color.test.ts`, and
`createGatewayEventHandler.test.ts` that use gold hexes as arbitrary input to
color-math tests, not as brand values.

### Lesson

There were **five** independent banner/palette definitions in this codebase
(Python CLI, TypeScript TUI, web dashboard, desktop app, bootstrap installer).
Fixing one never fixed the others, and each was only discoverable by seeing the
wrong color in a running surface. A grep for the brand *word* never finds these
— only a grep for the brand *hex values* does.

---

## 8. The sixth banner — `socis_cli/banner.py`

After fixing `cli.py`, the dashboard chat panel was **still gold**. Root cause:
`socis_cli/banner.py` is a *separate, dedicated banner module* holding its own
third copy of the wordmark (still spelling "HERMES-AGENT") and the caduceus
mascot, plus its own `_GOLD` ANSI constant and `_skin_color()` fallbacks. This
is the module the dashboard's embedded terminal actually renders.

Also found and fixed in the same pass: **`socis_cli/skin_engine.py`**, which
defines the `"default"` skin — described in-code as *"Classic SOCIS — gold and
kawaii"*. Skins override theme colors at runtime, so even with every theme file
corrected, the active skin repainted everything gold. Both its dark block and
its `light_colors` overlay were re-seeded to the coral ramp, preserving the
documented contrast ladder (body 8.9:1 > fade 5.2 > label 3.7 > muted 3.3 >
title 2.7 on white).

Total banner/palette definitions found across this rebrand: **six**.

| # | Location | Surface |
|---|---|---|
| 1 | `ui-tui/src/banner.ts` + `theme.ts` | TUI (TypeScript) |
| 2 | `web/src/themes/presets.ts` + `index.css` | Web dashboard chrome |
| 3 | `apps/desktop/src/themes/presets.ts` + `styles.css` | Desktop app |
| 4 | `apps/bootstrap-installer/src/styles.css` | Installer |
| 5 | `cli.py` | Python CLI |
| 6 | `socis_cli/banner.py` + `skin_engine.py` | **Dashboard chat panel** |

### Why this took six rounds

Each definition was independent, and none was reachable by searching for the
brand *word* — the files were already correctly named `socis_*` and their
comments already said "SOCIS". Only searching for the **gold hex values**
(`#FFD700`, `#FFBF00`, `#CD7F32`, `#B8860B`, `#FFF8DC`, `#DAA520`) surfaced
them, and even then, a plain grep for those hexes missed `skin_engine.py`'s
runtime overrides until the rendered output was inspected again.

The durable check for anyone re-verifying this:

```bash
grep -rIn "FFD700\|FFBF00\|CD7F32\|B8860B\|FFF8DC\|DAA520" \
  --include="*.py" --include="*.ts" --include="*.tsx" . \
  --exclude-dir={.git,node_modules,.venv}
```

Expected remaining hits are only: the docs website CSS, test fixtures using gold
as arbitrary color-math input, and `_LIGHT_MODE_REMAP` table keys.

---

## 9. `install.sh` lockfile error — fixed

Running the installer produced:

```
The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.
```

**Cause:** the packaged `uv.lock` still declared the project as `hermes-agent`
(20 occurrences) while `pyproject.toml` says `socis-agent`. `install.sh` runs
`uv sync --extra all --locked`, and `--locked` fails when the lockfile doesn't
match the project — correctly, in this case.

**Why it mattered more than a cosmetic mismatch:** the error was *non-fatal* —
`install.sh` logs a warning and falls back to a multi-tier PyPI resolve. But
that fallback is explicitly **"no hash verification"**. `uv.lock` records a
SHA256 for every package; the fallback path drops that supply-chain guarantee.
So every fresh install was silently installing unverified packages.

**Fix:** renamed the self-referential project entry in `uv.lock`
(`source = { editable = "." }`) from `hermes-agent` to `socis-agent`. This is a
pure rename — no dependency hashes, versions, or resolution data changed.
Verified: TOML parses, 255 packages intact, editable entry now `socis-agent`,
and it matches `pyproject.toml`.

Note this was already correct in the user's *local* checkout (they had run
`uv lock` manually); only the packaged copy carried the stale name.

---

## 10. `socis desktop` — the `npm ci` failure

```
npm error `npm ci` can only install packages when your package.json and
package-lock.json are in sync.
npm error Missing: @socis/ink@0.0.1 from lock file
npm error Missing: socis@0.17.0 from lock file          (+5 more)
```

**Root cause:** the packaged `package-lock.json` still carried the pre-rebrand
workspace names (`@hermes/ink`, `hermes`, `hermes-tui`, `@hermes/shared`,
`@hermes/bootstrap-installer`, `@hermes/root-tests`, root `hermes-agent`) plus
the stale path `ui-tui/packages/hermes-ink`. Every `package.json` said
`@socis/*`, so `npm ci` correctly refused.

Same class of bug as the `uv.lock` issue in §9 — fixing the Python lockfile
earlier did not touch the npm one.

**Not a bug in the installer.** `_run_npm_install()` in `socis_cli/main.py`
tries `npm ci` first and falls back to `npm install --no-save`. The `--no-save`
is deliberate; its docstring explains why:

> an out-of-sync lockfile gets rewritten by the fallback, which drifts the
> committed lockfile and makes every future `npm ci` fail — a self-reinforcing
> cycle

So the failure was the tooling *correctly refusing* to mask a broken lockfile,
and the build still completed via the fallback. The fix belongs in the
lockfile, not the installer.

**Fix applied:** rewrote only the workspace entries — names, paths, the
`node_modules/*` link entries, and their `resolved` targets.

Deliberately **not** renamed (real third-party packages that merely contain
"hermes"):

| Package | Why untouched |
|---|---|
| `hermes-estree@0.25.1` | Meta's JavaScript parser — name collision only |
| `hermes-parser@0.25.1` | Meta's parser toolchain |
| `@nous-research/ui@0.18.2` | Real published component library |
| `@nous-research/image-size@2.0.3` | Real published package |

**Validated** the same way `npm ci` does: all 7 workspaces have lockfile
entries whose names match their `package.json`; all 7 `node_modules/*` link
entries exist and resolve to in-lock targets; JSON valid; 1,417 entries intact;
`lockfileVersion: 3` preserved.

⚠️ **Caveat:** this lockfile was repaired programmatically, not regenerated by
npm. It satisfies every check `npm ci` performs, but the authoritative fix is
still to run `rm package-lock.json && npm install` once on a networked machine
and commit the result before pushing.

### Are the `socis` package names a problem?

No. All eight are `private: true` internal workspace packages resolved through
`file:` paths (`file:../apps/shared`, `file:./packages/socis-ink`) — never
fetched from any registry. Verified: zero `socis`-named packages have an
`http` resolved URL. The Python `socis-agent` is likewise
`source = {editable = "."}`, installed from the checkout.

(`socis-agent` is not on PyPI. Irrelevant for git-checkout installs; only
matters if `pip install socis-agent` should ever work.)

## 11. Build-log warnings cleared

| Warning | Fix |
|---|---|
| `__dirname` unsupported by Vite's native config loader | → `import.meta.dirname` (12 uses in `apps/desktop/vite.config.ts`, 2 in `web/vite.config.ts`) |
| `advancedChunks` deprecated | → `codeSplitting` (rolldown rename, same shape). Also disambiguated the neighbouring comment, which otherwise read as if the boolean `codeSplitting: false` and the new groups object were the same option. |
| `INEFFECTIVE_DYNAMIC_IMPORT` | **Left as-is, documented.** The `await import()` in `use-prompt-actions/utils.ts` exists to break an *initialization cycle*, not to code-split. Converting it to a static import would silence the warning and reintroduce the cycle. Added a comment saying so. |
| `@electron/rebuild` "excess dependency" | **Left as-is.** electron-builder's suggestion is wrong here: `scripts/rebuild-native.mjs` imports it directly and `stage-native-deps.mjs` invokes its binary for per-arch native staging (`node-pty`, `get-windows`). Removing it breaks the desktop build. |

---

## 12. Version reset to 0.1.0

The platform carried **three different inherited versions**, all from Hermes's
release history rather than SOCIS's:

| Manifest | Was | Now |
|---|---|---|
| `package.json` (root) | 1.0.0 | **0.1.0** |
| `apps/desktop/package.json` | 0.17.0 | **0.1.0** |
| `pyproject.toml` + `socis_cli/__init__.py` | 0.21.0 | **0.1.0** |
| `apps/shared`, `web`, `website` | 0.0.0 | **0.1.0** |
| `apps/bootstrap-installer`, `ui-tui`, `socis-ink` | 0.0.1 | **0.1.0** |

Also synced: `package-lock.json` (root + all workspace entries) and `uv.lock`'s
editable project entry — a version mismatch there re-breaks `npm ci` and
`uv sync --locked`.

`socis_cli/__init__.py`'s `__version__` is the runtime source of truth (CLI
banner, gateway API `/version`, provider User-Agent headers).

**Safe to lower:** verified the updater compares *dependency* pins, not the
project's own version against a remote — it tracks git commits. Desktop test
fixtures using `'0.17.0'` as mock data were updated for consistency; a
historical bug-reference comment (`#49903: on desktop v0.17.0`) was left alone.

Verified: 5,127 Python files / 0 errors, 3 TS workspaces / 0 errors, all
JSON+TOML valid, and every version declaration reports a single consistent
`0.1.0`.

## 13. Security patching — two distinct problems

Added `MAINTENANCE.md`. The key insight: **dependency CVEs and upstream source
patches are different problems**, and only the first is automated.

**A. Dependency vulnerabilities** — already covered by the repo's own
`osv-scanner.yml` and `supply-chain-audit.yml`, plus `npm audit` /
`uv lock --upgrade`. Current 6 advisories are all `dev`-only build tooling.

**B. Upstream source patches** — the real gap. When Nous Research fixes a bug in
Hermes Agent, nothing brings it here, and the repo records no fork point.
`MAINTENANCE.md` documents adding `upstream` as a git remote, how to find
security-relevant commits, and how to cherry-pick them (`git cherry-pick -n`,
resolve branding conflicts, never merge wholesale — that would revert the
rebrand).

It also lists what upstream patches must never overwrite: the `hermes-cli`
OAuth client ID, the `com.nousresearch.hermes` bundle ID, `@nous-research/*`
packages, `hermes-estree`/`hermes-parser` (Meta's parser — name collision only),
real Nous infrastructure URLs, and the persisted theme keys.

**Correcting an earlier assumption in this document:** §11 and earlier framing
treated `@socis/ink` as a vendored fork with an upstream to track. It isn't a
separately-forked library — the *entire platform* is the fork. `@socis/ink` and
`@socis/shared` are just internal workspace packages within it, containing code
inherited from Hermes like everything else. The upstream-sync process in
`MAINTENANCE.md` covers them the same as any other directory.

---

## 14. The "agent-browser" and "web workspace" vulnerability reports

`socis doctor` reported *"Browser tools (agent-browser) has 1 npm vulnerability"*
and *"web workspace has 2 npm vulnerabilities"*. Both labels are misleading.

**"Browser tools (agent-browser)" is a mislabeled root audit.** From
`socis_cli/doctor.py`:

```python
(PROJECT_ROOT, "Browser tools (agent-browser)", ["--workspaces=false"]),
```

That runs `npm audit --workspaces=false` at the **project root** — auditing the
root `package.json`, not `agent-browser`. `agent-browser` isn't a dependency of
this repo at all (verified: absent from every `package.json` and from
`package-lock.json`); it's a separate package users install globally via
`npm install -g agent-browser`. Its own vulnerabilities live in its own
dependency tree and cannot be fixed from here.

**Fixed:** relabelled to `"root workspace (build tooling)"`.

**"web workspace" is hoisting attribution.** `npm audit --workspace web`
resolves against the shared hoisted `node_modules`, so root-level packages get
counted against `web`. Traced the actual chains:

```
@xmldom/xmldom  ← plist ← @electron/osx-sign / app-builder-lib  (macOS signing)
extract-zip     ← electron ← apps/desktop
```

Nothing in `web`'s 37 direct dependencies reaches either. The only packages
installed under `web/node_modules/` are Babel tooling. **The web workspace has
no real vulnerabilities of its own.**

### What was actually fixable

| Advisory | Fixable | Action |
|---|---|---|
| `@xmldom/xmldom` (moderate ×2) | ✅ Yes | Patched releases exist — **0.8.15** and **0.9.12** (CVE-2026-83608/83609/83610). Added scoped `overrides`. |
| `electron` (high ×2) | ❌ No | Advisory range is `1.3.1–41.10.2`; clearing needs ≥41.10.3 — a major upgrade touching native modules and macOS signing. |
| `extract-zip` (high) | ❌ No | Pinned by `electron`; clears with the Electron upgrade. |

Added to `package.json` `overrides`, matching the file's existing scoped-range
style (`nanoid@^3`, `undici@^6`) — needed because `plist` requests **both**
major lines:

```json
"@xmldom/xmldom@^0.8": "0.8.15",
"@xmldom/xmldom@^0.9": "0.9.12"
```

Also added a `min-release-age-exclude` entry in `.npmrc`, since these are recent
releases and the 14-day supply-chain gate would otherwise block them.

⚠️ **Takes effect on the next `npm install`** — overrides are applied at
resolution time. Run `rm package-lock.json && npm install`, then `npm audit`
should drop from 6 advisories to 3 (the Electron chain only).

---

## 15. Installer banners — a seventh branding location

The install scripts run *before* any Python or TypeScript loads, so they carry
their own banners. Three problems were found:

| File | Issue |
|---|---|
| `scripts/install.sh` | `⚕` (Rod of Asclepius — Hermes' caduceus), magenta instead of brand coral, and a broken box: the borders were 57 chars while the text lines had been shortened by the earlier "Nous Research" → "SOCIS" rename, leaving visibly ragged edges |
| `scripts/install.ps1` | `*` placeholder where the caduceus had been stripped, magenta, same ragged box |
| `setup-socis.sh` | `⚕` caduceus in the one-line header |

### `install.sh`

Replaced the box with the SOCIS wordmark in block letters, rendered in the
brand coral gradient (`#FF3366` → `#F04162` → `#C42248`) via true-color escapes,
plus the `◆` mark. Built a **37-column** variant rather than reusing the TUI's
91-column `LOGO_ART` — an installer runs in an unknown terminal, and the CLI
banner already documents a ~95-char requirement it can't assume here.

Three colour variables (`CORAL`, `CORAL_MID`, `CORAL_DEEP`) were added beside
the existing ANSI set.

### `install.ps1` — constrained to ASCII

`tests/test_install_ps1_ascii_only.py` enforces that this file stays pure
ASCII: Windows consoles can be on a non-UTF-8 code page when the script is
piped through `iex`, which turns box-drawing characters into mojibake. So the
PowerShell banner uses ASCII block letters, not Unicode.

Colour is `Red` — the closest of PowerShell's fixed 16 console colours to
`#FF3366`. True-colour escapes aren't reliable across PowerShell 5.1 hosts.

Verified: **0 non-ASCII bytes**, so the regression test still passes. Also
removed a backtick from a comment (PowerShell's escape character — harmless
inside `#`, but a needless hazard).

### Left alone

- `scripts/install.cmd` — a thin wrapper that immediately hands off to
  PowerShell; its plain text is appropriate.
- `docker/entrypoint.sh` — a deprecated shim, no banner.

Verified: all shell scripts pass `bash -n`, `install.ps1` is ASCII-clean, 5,127
Python files parse.

**Running total: seven independent banner/branding definitions** — the six in
§8 plus the installer scripts. Consistent with the lesson there: these are
invisible to a search for the brand *word*, and in this case also invisible to
a search for the gold *hex values*, since the installers used named ANSI
colours rather than hex.
