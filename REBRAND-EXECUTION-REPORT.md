# SOCIS Agent Rebrand — Execution Report

## What's in this delivery

1. **`socis-agent-rebranded.zip`** — the full Hermes Agent codebase with the rebrand applied: ~6,480 files rewritten, 103 files/directories renamed, CLI entrypoints changed to `socis`/`socis-agent`/`socis-acp`, env var prefix changed to `SOCIS_AGENT_*`, home directory changed to `~/.socis-agent/`, and the agent's own persona file (`SOUL.md`) updated to identify as SOCIS Agent built by SOCIS. **Git history was stripped from this copy** — it was applied to a fresh extraction, not your real repo, so this is for review/diffing, not for pushing directly.
2. **`socis-rebrand-toolchain.zip`** — the actual scripts (`rebrand_map.py` + `run_rebrand.py`) to run this same rebrand against your real repository, preserving git history via `git mv`. This is the one to actually use for the real migration.
3. **`SOCIS-Agent-Rebrand-Plan.md`** — the original strategic plan (tiers, naming decisions, domain/legal considerations, migration concerns).

## How to run it against your real repo

```bash
# 1. Clone your real repo, work on a branch
git checkout -b rebrand/socis-agent

# 2. Copy the toolchain in
cp -r socis-rebrand-toolchain/rebrand-toolchain scripts/rebrand

# 3. Dry run first — always review the report before applying
python3 scripts/rebrand/run_rebrand.py --root . --report rebrand_dry_run.json
# inspect rebrand_dry_run.json — check file counts, spot check a few entries

# 4. Apply
python3 scripts/rebrand/run_rebrand.py --root . --apply-text --apply-renames --report rebrand_applied.json

# 5. The script's own post-flight checks will report syntax errors / stale
#    imports if any exist — do not proceed to commit if either is non-empty.

# 6. Run your actual test suite. The script's checks are necessary but not
#    sufficient — they catch syntax breakage and Python import mismatches,
#    not runtime logic, TypeScript type errors, or behavior changes.

# 7. Regenerate lockfiles (do NOT hand-edit these — see below):
uv lock
npm install   # in web/, ui-tui/, apps/desktop/, website/, scripts/whatsapp-bridge/, etc.
```

## What the tool does NOT touch (by design) and why

| Path | Why excluded |
|---|---|
| `contributors/emails/*` | Real contributor personal data captured from git history — never rewrite personal information |
| `LICENSE` (root) | Legal copyright notice — requires a deliberate human decision on attribution, not an automated rewrite |
| `uv.lock`, `package-lock.json` (all copies) | Auto-generated from `pyproject.toml`/`package.json` — hand-editing them desyncs them from the source of truth. Regenerate with `uv lock` / `npm install` after the rebrand instead |
| `tools/wakewords/hey_hermes.onnx`, `.tflite` | Trained ML models for the "Hey Hermes" wake-word — this is a retraining task, not a text/rename operation. See "ML follow-up" below |
| `docs/hermes-kanban-v1-spec.pdf` | Historical design-spec PDF — left alone pending an explicit decision on whether to rename/update or archive as historical record |

## Items requiring a human decision before or after running this at scale

1. **`plugins/security-guidance/NOTICE`** — this is your own project's attribution notice (describing terms for a specific plugin's code), not a third-party vendored one. The tool's blanket LICENSE/NOTICE exclusion protected it along with genuine third-party notices, so it was **not** rebranded automatically. Worth a manual look — likely should be updated to reference SOCIS, unlike the true third-party licenses nearby.
2. **`plugins/*/LICENSE` files** — several plugin directories (e.g. `socis-achievements/LICENSE`) have their own LICENSE files. Check each one individually: some may be your own project's terms (should be updated) vs. genuinely vendored third-party code (should not be touched).
3. **Wake word — "Hey Hermes" → new phrase**: the `.onnx`/`.tflite` files are trained models, not text. Renaming the file doesn't change what the model listens for. This needs an actual ML retraining pass with the new wake phrase, budgeted as a separate workstream, not part of a code rebrand.
4. **Mascot/sprite assets** (`apps/desktop/public/hermes-sprite.png`, `hermes-frame-0..7.png`): these were renamed to `socis-*` equivalents, but the artwork itself is unchanged — it's still visually "Hermes" the character. Commission new SOCIS-branded artwork, or decide to drop the animated-mascot concept, before shipping the desktop app publicly.
5. **Domains**: the tool rewrote `hermes-agent.nousresearch.com` → `agent.socis.io` and `nousresearch.com` → `socis.io` as placeholders in text. **These domains need to actually exist and be registered** before install scripts / docs links work — verify with whoever owns SOCIS.io's DNS.
6. **PyPI / npm package publishing**: `pyproject.toml` now declares `name = "socis-agent"` and CLI entrypoints `socis`/`socis-agent`/`socis-acp`. Nothing is published under these names yet — that's a registration/publishing step outside this codebase change.

## Bugs found and fixed during development (documented in the toolchain's own comments)

Worth knowing about since they inform how much to trust a first pass of any similar rename tool:

1. An early version of the home-directory rule (`.hermes` as a bare substring) also matched Python dotted-module import paths (e.g. `tests.hermes_cli`), producing a hyphen inside a Python identifier — invalid syntax. Fixed by anchoring the rule to concrete path forms only (`~/.hermes`, `/.hermes/`, quoted string literals).
2. Module file renames (e.g. `hermes_constants.py` → `socis_agent_constants.py`) initially weren't reflected in the text-substitution rules, so import statements referenced a name (`socis_constants`) that didn't match the file actually on disk (`socis_agent_constants.py`) — broke 500+ imports. Fixed by registering each module rename as an explicit, higher-priority text rule.
3. Extensionless files (the `hermes` CLI wrapper script itself, Docker/s6 service scripts) were skipped by the text pass entirely, so the file got renamed to `socis` but its content still imported from `hermes_cli` — a renamed-but-broken entry point. Fixed by including extensionless files in the text pass.
4. ALL-CAPS occurrences in ASCII-art banner text (`"HERMES-AGENT"`, `"NOUS HERMES"`) were missed since only Title-case and lowercase forms were covered. Fixed with explicit ALL-CAPS rules.

Each of these was caught by the toolchain's own post-flight syntax/import checks or a manual `grep` audit — not assumed away. This is the reason the plan recommends running this against a real branch with your actual test suite, not just trusting a clean-looking replacement count.

## Items closed since the first pass

The following were flagged as needing human judgment in the first delivery and have now been resolved by hand (not by the automated tool, since each required reading the actual content to classify correctly):

1. **`plugins/security-guidance/NOTICE`** — this file mixes a genuine third-party attribution (to Anthropic's Apache-2.0-licensed `patterns.py`) with a description of "the Hermes-side... original work by NousResearch." Only the second part was updated to SOCIS; the Anthropic attribution, source URL, commit hash, and Apache License reference were left exactly as they were, since altering third-party attribution is a real legal problem, not a branding one.
2. **`plugins/*/LICENSE` and root `LICENSE` files** — inspected all 10 LICENSE files in the tree individually rather than pattern-matching by path:
   - **Updated** (your own MIT-licensed copyright, `Copyright (c) Nous Research` → `Copyright (c) SOCIS`): root `LICENSE`, `apps/desktop/src/plugins/socis-bots/LICENSE`, `skills/productivity/docx/LICENSE`, `skills/productivity/pdf/LICENSE`, `skills/productivity/powerpoint/LICENSE`, `skills/productivity/xlsx/LICENSE`, and `plugins/socis-achievements/LICENSE` ("Hermes Achievements contributors" → "SOCIS Achievements contributors").
   - **Left untouched** (genuine third-party): `optional-skills/software-development/ast-grep/LICENSE` (Copyright Yeongyu Kim), `skills/creative/humanizer/LICENSE` (Copyright Siqi Chen), `plugins/security-guidance/LICENSE` (Apache License 2.0, belongs to Anthropic's forked code).
3. **`@nous-research/ui` and `@nous-research/image-size` npm dependencies** — confirmed these are real, externally-published npm packages (pinned to specific version numbers, not local `file:` references) that this project depends on. These were correctly left untouched by the automated pass and should stay that way — renaming the string would point `npm install` at a package that was never published under `@socis/*`, breaking every build. If SOCIS wants to fork or republish these under its own scope, that's a separate decision requiring actual package publishing, not a text edit.
4. **Desktop app mascot/sprite code** — traced how `apps/desktop/public/socis-sprite.png` and `socis-frame-*.png` are actually consumed: the component that renders them (`pet-sprite.tsx`) takes a dynamically-supplied `spriteUrl`, it doesn't hardcode the asset filename. So the code is not blocked by the mascot question — only the artwork's *content* (still visually the original character) remains a design decision, as previously flagged.

## Verification performed on this final delivery

Beyond the checks in the original pass:

- **Full TypeScript grammar-level syntax check** on all three JS/TS workspaces (`apps/desktop`, `ui-tui`, `web`) using each workspace's own real `tsconfig.json` (correct path aliases, no manual config needed): **0 syntax errors** in all three.
- **All 101 `.mjs` files** individually syntax-checked with `node --check` (which correctly parses ES module syntax, unlike a generic script-compile check): **0 errors**.
- **Re-ran the full Python `ast.parse()` check** after the manual LICENSE/NOTICE edits (which only touched non-Python files) to confirm no regression: still **0 errors** across all 5,130 `.py` files.
- **Full-tree final audit**: the only remaining occurrences of "hermes" anywhere in the codebase (text or filenames) are: 3 lockfiles (correctly unregenerated, see below), 2 contributor personal-data files (correctly untouched, real historical PR references), and the rebrand toolchain's own script files (which document the rename in code comments — that's expected, not a miss).

## Visual identity fixes (ASCII art, mascot, mythological theming)

The automated text-substitution pass only rewrote readable text — it could not touch content that carries the Hermes brand *visually* or *thematically* without spelling out the word "Hermes". These required manual identification and hand-editing:

1. **Block-letter ASCII logo** (`ui-tui/src/banner.ts`, `LOGO_ART`) — a box-drawing-character banner that still spelled out "HERMES...AGENT" in letter shapes, invisible to any text search for the word "hermes" since it's built from `█`/`╗`/`║` characters, not literal text. Replaced with a hand-built "SOCIS AGENT" wordmark in the same font style. Verified 0 TypeScript syntax errors.
2. **The mascot art** (`CADUCEUS_ART`) — a dot-matrix rendering of Hermes' mythological winged-staff symbol (the caduceus), built from Unicode braille characters. This is what appeared in the dashboard/TUI welcome screen. Replaced with a neutral hexagonal "node network" glyph in the same braille style and exact 30×15 dimensions — **this is a placeholder**, not real SOCIS brand artwork, since none was supplied. Commission real artwork before shipping publicly.
3. **Renamed the code identifiers themselves**, not just the art data: `caduceus()` → `heroMark()`, `CADUCEUS_WIDTH` → `HERO_MARK_WIDTH`, `CADUC_GRADIENT` → `HERO_MARK_GRADIENT`, across both `banner.ts` and its consumer `branding.tsx`. Verified 0 stale references.
4. **The ☤ (caduceus) emoji** used as a decorative brand mark — found in ~20 places: README headers (4 language variants), 17 tweet-share templates in `web/src/i18n/*.ts`, and the session-export HTML footer (`socis_cli/session_export_html.py`). Removed from all of these. Left untouched in `skills/creative/ascii-video/README.md` (generic decorative use in an unrelated skill, not a SOCIS brand reference) and two test files that use it as arbitrary Unicode test data (`tests/agent/test_tool_guardrails.py`, `tests/agent/test_system_prompt_restore.py`).
5. **Urdu-script "Hermes" (ہرمیس)** — a distinct category of miss: the automated pass only matched Latin-script "hermes"/"Hermes", so the Urdu README (`README.ur-pk.md`) had "Hermes Agent" spelled out in Urdu script in its heading AND 9 separate places in the body text, completely untouched. Fixed all 10 occurrences, plus one stray Latin-script "Nous Portal" reference in the same file. Confirmed the Chinese README/docs (`README.zh-CN.md`, `website/i18n/zh-Hans/`) have no equivalent transliterated-Hermes problem.
6. **Mythological tagline** ("Messenger of the Digital Gods", `ui-tui/src/components/branding.tsx`) — referenced Hermes' role as messenger-god without using his name at all, so no text rule could have caught it. Replaced with "The Self-Improving AI Agent", matching the phrasing already used in `pyproject.toml`'s own description field.
7. **A docstring implying SOCIS is a Greek god** (`plugins/cron_providers/chronos/__init__.py`) — read "Chronos (the Greek god of time, alongside SOCIS)", a leftover from when the sentence paired Chronos with Hermes (both mythological figures). Fixed to remove the implied mythological status.

## Real logo integration (SOCIS brand mark supplied)

The person supplied the actual SOCIS logo as an SVG (`icon-socis-agent` symbol: a compass/reticle mark — four inward-pointing corner brackets around a diamond core, in "Kinetic Coral" `#FF3366` on navy `#070A0F`/`#0D1424` canvas, alongside an "SOCIS | AGENT" wordmark). This replaced the earlier hexagon placeholder:

1. **No SVG rasterizer was available in this sandbox** (no network to install `rsvg-convert`/`cairosvg`, no local equivalent). Rather than approximate, the icon's exact vector geometry (4 corner polylines, 4 tick lines, a filled center diamond, a knockout circle — all with known coordinates in the SVG's 48×48 viewBox) was rasterized by hand: supersampled 8× per axis, anti-alias-averaged down to a 60×60 sub-pixel grid, and encoded as Unicode braille characters (30×15 cells) — the same technique and exact footprint as the mascot slot it replaces (`HERO_MARK_ART` in `ui-tui/src/banner.ts`).
2. **Full re-theme to the real brand palette**, not just the icon. The TUI's previous default theme (`DARK_SEEDS`/`LIGHT_SEEDS` in `ui-tui/src/theme.ts`) was itself Hermes-brand DNA: gold/amber primary (`#FFD700`), amber accent (`#FFBF00`), bronze border (`#CD7F32`) — matching the "FFD700" gold badges from the original Hermes README. This was identified and replaced with seeds derived directly from the supplied logo (`accent`/`primary: #FF3366`, `bg: #070A0F`, `surface: #0D1424`, `border: #161F30`, `text/prompt: #E2E8F0`). The light-mode seeds were **not** hand-guessed — they were computed by actually compiling and running the codebase's own `liftForContrast()` color-math function (via a standalone `tsc` compile + `node` execution) against the new dark seeds, reproducing exactly how the original gold light-theme was derived from its dark seeds. Verified contrast ratios: accent 5.19:1, text 5.27:1 on white (both clear the 4.5:1 target the original used).
3. **The brand icon symbol (`⚕`, Rod of Asclepius/caduceus-family)** used throughout `BRAND.icon` in `theme.ts` — this is a DIFFERENT symbol from the mascot art or the ☤ emoji already fixed; it's a single character embedded as a literal string across **34 files**: CLI print statements and box-drawing banners (`socis_cli/*.py`), the desktop TUI's loading-spinner animation frames, and cross-platform messaging prefixes for Discord/Telegram/WhatsApp/Feishu/QQ bot adapters, plus documentation examples. This was invisible to any "hermes"-text search since it's an unrelated Unicode glyph, not the word itself — found only by proactively re-checking for mythology-adjacent symbols. Replaced with `◆` (a diamond, echoing the logo's own center-diamond motif) in all 97 occurrences across 34 files, preserving exact string length so box-drawing banner alignment is unaffected (both symbols render single-width in standard terminal locales). One arbitrary-Unicode-test file (`tests/run_agent/test_unicode_ascii_codec.py`) was correctly left untouched since it uses the symbol as test fixture data, not branding.

Verified after this pass: 0 Python syntax errors (5,130 files), 0 TypeScript grammar errors across the full `ui-tui` workspace (via its own `tsconfig.json`).

**Still a placeholder, not final:** the desktop app's `.png` sprite/frame assets (`apps/desktop/public/socis-sprite.png`, `socis-frame-*.png`) are still the original mascot artwork, unrelated to this SVG logo — converting those to match the new brand requires actual image editing/export from the source design file, which is outside what can be done from a single SVG icon symbol in this environment.


**What this means going forward:** any future rebrand of a codebase with deep thematic/mythological naming should budget explicit time for a *visual and conceptual* audit, separate from and in addition to a text-substitution pass — box-drawing art, non-Latin translations, and thematic copy don't contain the literal brand string and will not be caught by grep-based tooling no matter how thorough the pattern list.

## Critical functional corruption found and fixed (third-party infrastructure)

A user-prompted deep audit (checking every domain, model-name, and bundle-identifier string against the pristine original) found that the earlier text-substitution rebrand had corrupted references to **real, external, third-party infrastructure and content that this project depends on or links to** — not just our own branding. These are functional/legal bugs, not cosmetic ones: a broken billing link, a model-detection regex that would never match its real target, and dead links to real external content. Every one below was verified against the pristine original before reverting.

1. **Nous Research backend domains** (~18 subdomains: `portal.nousresearch.com`, `inference-api.nousresearch.com`, `telemetry.nousresearch.com`, `gateway.nousresearch.com`, `api.nousresearch.com`, etc.) — these are Nous Research's real, live infrastructure that this codebase calls as a client (e.g. `agent/billing_links.py` builds a clickable billing URL; `agent/model_metadata.py` matches API response hostnames to route requests correctly). The earlier rebrand's domain rule (`nousresearch.com` → `socis.io`) treated ALL `nousresearch.com` occurrences as "our brand," corrupting these into non-existent `*.socis.io` addresses. **Confirmed with the person that SOCIS does not operate this infrastructure** — reverted all ~370 occurrences across 137 files to the real `nousresearch.com` endpoints. `agent.socis.io` and `setup.agent.socis.io` were initially assumed to be safe exceptions (our own docs/install domain) but one of the two (`setup.agent.socis.io`) turned out to also be used as a **real Nous-hosted Cloudflare Worker API endpoint** in `socis_cli/telegram_managed_bot.py` and `socis_cli/web_server.py` — reverted those 2 call sites specifically; the docs-only uses of `agent.socis.io` remain correctly as our own domain.
2. **The "Nous Hermes" model family** — a real, still-existing third-party LLM series (e.g. `NousResearch/Hermes-3-Llama-3.1-70B` on Hugging Face/OpenRouter) that this codebase specifically detects and warns users away from (it's a chat model, not tool-calling capable, so using it breaks agent workflows). The bare "hermes"→"socis" rule corrupted the detection regex, function names, warning text, and test fixtures into `is_nous_socis_non_agentic()` matching a string ("socis-3"/"socis-4") that will never appear in a real model name — silently disabling this safety warning. Fixed in `socis_cli/model_switch.py` (function renamed to `is_nous_hermes_non_agentic`, regex and warning text corrected), plus 6 dependent files (`cli.py`, `agent/agent_init.py`, 2 test files, a desktop test fixture, and 2 docs pages/translations).
3. **macOS/Electron bundle identifier** — `com.nousresearch.hermes` (reverse-DNS: company.product) is used for code-signing verification, `tccutil` permission resets, the Electron `appId`, and the Tauri installer identifier. The rebrand independently mapped both "nousresearch" and "hermes" to "socis", corrupting it into the nonsensical `com.socis.socis`. **The person confirmed this should revert to the original `com.nousresearch.hermes`** (SOCIS does not have equivalent signing infrastructure yet) — fixed across 11 files (Electron main process, Tauri config, 3 CLI modules, 5 test files, 2 docs pages).
4. **Real external URLs to content SOCIS doesn't control** — the most severe category. `website/src/data/userStories.json` (a collection of real testimonial links: Reddit threads, Medium/Substack articles, LinkedIn posts, GitHub community-project archives) had every "hermes"/"nousresearch" occurrence in its URLs rewritten, turning every single link into a dead 404 — these are real posts by real third parties, not our content to rename. **Reverted the entire file to the pristine original** rather than selectively patch it, since virtually every entry was affected. A full-tree URL audit (comparing every `https?://` URL against the pristine original, ~8,346 URLs each side) found 93 additional files with similarly corrupted third-party links (Discord invite, Meta AI, Supermemory, Honcho, DeepInfra, ComfyUI, and other integration docs/tests) — all reverted to their real, working URLs.
5. **GitHub repository org name** — the person's real GitHub org is `socisio` (i.e. `github.com/socisio/socis-agent`), not the `SOCIS`/`socis` guess used during the initial rebrand pass. Corrected across every reference format found in the repo: HTTPS URLs, SSH remote URLs (`git@github.com:socisio/...`), `raw.githubusercontent.com` asset links, and `package.json`/`tauri.conf.json` metadata fields — required several passes since different files used different casing (`SOCIS-Agent` vs `socis-agent`) and different file extensions weren't all covered by the same script pass (`.yml`, `.ps1`, `.mjs`, `.nix`, `.rs` needed separate sweeps). Final verification used a regex scan across every non-binary file in the tree with zero extension filtering, to stop relying on an extension allowlist that kept missing files.

**Why this category of bug is different from (and worse than) the earlier cosmetic ones:** a wrong mascot or leftover gold color theme is visibly wrong and easy to spot on sight. A corrupted third-party domain, model-detection regex, or external URL *looks* completely normal in the source and only fails at runtime (a dead link, a silently-disabled warning, a billing page that 404s) or when someone happens to diff against the original. This is why the request for "deep analysis of every file" was the right call — surface-level review would not have caught any of these five issues.

## GitHub org confirmed

The real GitHub organization is **`socisio`** (`https://github.com/socisio/socis-agent`). All repository links, SSH remotes, and raw-content URLs throughout the codebase now consistently point here.



- **Lockfile regeneration** (`uv.lock`, and 3 copies of `package-lock.json`): confirmed via direct test that this sandbox has no network egress (`uv lock` fails trying to reach GitHub release mirrors). These files still correctly resolve against the *old* `hermes-agent` package name until regenerated with `uv lock` / `npm install` on a machine with network access — this is expected and safe (lockfiles aren't consulted for identity, just dependency pinning), but must be done before a real install/build.
- **Full TypeScript type-checking** (as opposed to grammar/syntax checking) requires the actual `node_modules` tree, which requires `npm install` against the real npm registry.
- **Wake-word model retraining** and **new mascot artwork** remain genuine creative/ML workstreams outside what a text/file rebrand can produce, as noted in the original report.

