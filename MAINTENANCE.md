# SOCIS Agent — Maintenance & Security Patching

This platform is a **rebrand of Hermes Agent** (Nous Research, MIT licensed).
That creates two *separate* patching problems, which are easy to conflate:

| | What it covers | Automated? |
|---|---|---|
| **A. Dependency vulnerabilities** | `electron`, `xmldom`, PyPI packages — third-party code we install | ✅ Yes |
| **B. Upstream source patches** | Bug/security fixes Nous makes to the Hermes code we forked | ❌ No — needs a process |

---

## A. Dependency vulnerabilities — already automated

Two CI workflows ship with the repo and will run once it's on GitHub:

- `.github/workflows/osv-scanner.yml` — scans against the OSV database
- `.github/workflows/supply-chain-audit.yml` — supply-chain checks

Plus, on demand:

```bash
npm audit                 # JS dependencies
npm audit fix             # safe, semver-compatible fixes only
uv lock --upgrade         # refresh Python deps within pyproject constraints
```

### Current status (as of the rebrand)

6 advisories, **all `dev`-only** — build tooling, not code shipped to users:

| Package | Severity | Fixable now? |
|---|---|---|
| `electron@40.10.2` | high ×2 | ❌ Needs major upgrade to 41.10.3+ — see below |
| `extract-zip@2.0.1` | high | ❌ Transitive under `electron` |
| `@xmldom/xmldom` | moderate ×2 | ⚠️ Transitive under `electron-builder`'s macOS signing chain |

**Why the Electron ones aren't a quick fix:** the advisory range is
`1.3.1 – 41.10.2`, so patch-bumping inside 40.x stays vulnerable. Clearing it
requires 41.10.3+ — a major runtime change touching native modules
(`node-pty`, `get-windows`) and the macOS signing/packaging chain. Do it as its
own project with a full `socis desktop` build test, not bundled with other work.

**Practical exposure:** the desktop app renders your own local UI and connects
to your own gateway; it isn't a browser loading untrusted sites. The advisories
concern custom-protocol session caching and sandboxed-iframe popups. Lower risk
than "2 high" implies — but not zero.

### The `.npmrc` supply-chain policy

`.npmrc` sets `min-release-age=14` — refusing any package published in the last
14 days, as a supply-chain-attack defense. Roughly 20 `min-release-age-exclude`
entries carve out exceptions, each documented with the CVE it fixes and a note
to *"remove when > 2wks old."* **Several are now stale.** Pruning expired ones
tightens the policy back up — do it as a separate change, after confirming a
build still succeeds.

⚠️ `engines.npm` is `<11.10.0 || >=11.17.0`. Versions 11.10–11.16 support
`min-release-age` but **not** `min-release-age-exclude`, so the age gate runs
with no exceptions and the install fails. Check with `npm --version`.

---

## B. Upstream source patches — needs a process

This is the gap. When Nous Research fixes a bug or security issue in Hermes
Agent, that fix does **not** reach this codebase automatically. Nothing in the
repo currently records where the fork came from.

### One-time setup: record the fork point

Determine which Hermes Agent release this was taken from (the inherited
versions were `0.21.0` Python / `0.17.0` desktop — likely the source tag), then
add upstream as a git remote:

```bash
git remote add upstream https://github.com/NousResearch/hermes-agent.git
git fetch upstream --tags
```

Record the fork point in this file so future maintainers know the baseline:

```
Forked from: NousResearch/hermes-agent @ v0.21.0 (Python) / 0.17.0 (desktop)
Fork date:   2026-09
```

Verified at the time of the rebrand: the inherited `pyproject.toml` read
`0.21.0` and `apps/desktop/package.json` read `0.17.0`. Upstream's published
releases at that point topped out at v0.19.0 (2026-07-20) plus dated patch
tags, so this fork was taken from `main` ahead of every tagged release —
expect `HEAD..upstream/main` to list a large number of commits.

Two of the three CVEs flagged in upstream's own security assessment
(issue #40889) were already fixed before this fork point:

| Dependency | Vulnerable | Ours |
|---|---|---|
| `PyJWT` | 2.12.1 | 2.13.0 ✓ |
| `starlette` | 1.0.1 | 1.3.1 ✓ |
| `requests` | 2.33.0 | 2.33.0 — pinned, see the `# CVE-2026-25645` note in `pyproject.toml` |

### Recurring: check for upstream fixes — automated

`.github/workflows/upstream-watch.yml` runs this every Monday and opens (or
updates) a single issue labelled `upstream-watch` listing security-relevant
upstream commits this fork does not have. Run it on demand from the Actions
tab.

It reports only. It does **not** cherry-pick: conflicts here are branding
conflicts, and resolving them automatically would either fail on every commit
or silently reintroduce Hermes naming. A human takes it from the issue.

To check by hand:

```bash
git fetch upstream
git log --oneline HEAD..upstream/main            # everything new upstream
git log --oneline HEAD..upstream/main --grep -i -E 'security|CVE|vuln|fix'
```

Keyword matching is a filter, not a classifier — some matches are irrelevant,
and a genuine fix may mention none of them (upstream's "body-size cap on
aiohttp webhook servers" is DoS hardening and matches nothing). Skim the full
log periodically, not just the filtered set.

### Applying a patch

Do **not** merge upstream wholesale — it would revert the rebrand. Cherry-pick:

```bash
git cherry-pick -n <upstream-sha>     # -n = stage without committing
# resolve conflicts: upstream says "hermes"/gold, ours says "socis"/coral
git diff --cached                      # review before committing
git commit
```

Conflicts are expected and are almost always branding. The rebrand touched:

- Six independent banner/palette definitions (see `PLATFORM-ANALYSIS.md` §8)
- Module names (`hermes_cli` → `socis_cli`) and env vars (`HERMES_*` → `SOCIS_AGENT_*`)
- Package names (`@hermes/*` → `@socis/*`)
- The color ramp: `#FFD700`→`#FF3366`, `#FFBF00`→`#F04162`,
  `#CD7F32`→`#C42248`, `#FFF8DC`→`#FFD9E1`, `#B8860B`→`#A81D3E`

**Do not rebrand during a cherry-pick.** Take upstream's logic, then apply the
rename separately so the two concerns stay reviewable.

### Things upstream patches must never overwrite

| Item | Why |
|---|---|
| `DEFAULT_NOUS_CLIENT_ID = "hermes-cli"` | Registered on **Nous's** OAuth server. Renaming breaks login (400). |
| `com.nousresearch.hermes` bundle ID | SOCIS has no equivalent macOS signing identity. |
| `@nous-research/ui`, `@nous-research/image-size` | Real published npm packages. |
| `hermes-estree`, `hermes-parser` | **Meta's** JS parser — name collision only, unrelated to Hermes Agent. |
| `portal.nousresearch.com`, `inference-api.nousresearch.com` | Real Nous infrastructure SOCIS doesn't operate. |
| Theme keys `'nous'`, `'nous-alt'`, `'default'` | Persisted user settings — renaming resets everyone's saved skin. |

---

## C. Versioning

Reset to **`0.1.0`** at rebrand — the inherited `0.21.0` / `0.17.0` / `1.0.0`
were Hermes's release history, not ours.

Every version declaration is kept in lockstep. When bumping, change **all** of:

```
package.json                              socis_cli/__init__.py   ← runtime source of truth
apps/desktop/package.json                 pyproject.toml
apps/shared/package.json                  uv.lock          (or regenerate: uv lock)
apps/bootstrap-installer/package.json     package-lock.json (or regenerate: npm install)
ui-tui/package.json
ui-tui/packages/socis-ink/package.json
web/package.json
website/package.json
```

`socis_cli/__init__.py`'s `__version__` is what the CLI banner, gateway API,
and provider headers report at runtime.

Suggested scheme (semver):
- **patch** `0.1.x` — bug fixes, dependency bumps, upstream cherry-picks
- **minor** `0.x.0` — new features, new providers/skills
- **major** `1.0.0` — when the platform is considered production-stable

⚠️ Lockfile versions must match their manifests or `npm ci` and
`uv sync --locked` fail. If they drift, `install.sh` falls back to a
**non-hash-verified** PyPI resolve — losing supply-chain verification silently.

---

## D. Pre-push checklist

```bash
# Regenerate lockfiles with the real tools (not hand-edits)
rm package-lock.json && npm install
uv lock && uv sync

# Verify
npm audit
python3 -c "import ast,os,sys
e=0
for r,d,f in os.walk('.'):
    d[:]=[x for x in d if x not in ('.git','node_modules','.venv','__pycache__')]
    for n in f:
        if n.endswith('.py'):
            try: ast.parse(open(os.path.join(r,n),encoding='utf-8').read())
            except SyntaxError: e+=1
print('python syntax errors:', e)"

# Full build
socis desktop
socis dashboard
```

---

## E. How upstream (Hermes Agent) handles these advisories

Checked against `NousResearch/hermes-agent` directly, September 2026.

### Electron: SUPERSEDED — a patch fix now exists

**Updated 2026-09-07.** The assessment below was correct when written and is
no longer the situation.

`npm audit` on the root workspace reports two HIGH advisories against
electron 40.10.2:

- **GHSA-r4w5-6pfg-jxp5** — `ProtocolResponse.url` reuses the default session
  cache instead of the registering session
- **GHSA-9f4c-93c8-jc8g** — a sandboxed iframe can bypass the `allow-popups`
  restriction via the OpenURL navigation path

Both affect the **running desktop app**, not just build tooling. That
distinction matters: the reasoning below correctly declined a bump when the
only fix was 42.x, a major upgrade against a pinned 40.x with no upstream
precedent. npm now reports the fix as **40.10.6** — a patch bump inside the
same minor line.

**Corrected after installing 40.10.6.** The bump fixed one of the two, not
both:

| Advisory | 40.10.6 | Fix available in |
|---|---|---|
| GHSA-r4w5-6pfg-jxp5 (session cache reuse) | **fixed** | 40.10.6 |
| GHSA-9f4c-93c8-jc8g (iframe allow-popups bypass) | still present | **44.2.0** |

`electron` in `apps/desktop/package.json` is now `40.10.6`, which was worth
doing on its own — it closed one HIGH advisory and resolved `extract-zip`
(GHSA-jmr9-qjv8-65gv) along with it, since 40.10.6 replaced that dependency
with `@electron-internal/extract-zip`.

**The iframe advisory has no fix inside 40.x.** npm reports the vulnerable
range as `40.0.0-alpha.2 - 41.10.2` and the remedy as `electron@44.2.0` — four
major versions up. So for this one the original reasoning below applies again
unchanged, and it stays an accepted risk rather than a pending task.

What accepting it means in practice: exploitation requires the app to load
hostile content inside a sandboxed iframe. SOCIS Desktop does render remote
content (the browser tool, preview panes), so this is not purely theoretical
— but a 40 → 44 jump would almost certainly break the native module staging
this repository has already spent a release cycle on, and upstream Hermes has
not moved either. Revisit when a 40.x or 41.x patch appears, or when the
desktop app is due a deliberate Electron upgrade with time to test it.

**`allowScripts` must be updated alongside any electron bump.** The root
`package.json` allowlist is keyed by `package@version`, so `electron@40.10.2`
did not cover `40.10.6`, and npm skipped the postinstall that downloads the
~150MB binary. Nothing fails at install time — it fails later in
electron-builder with a missing `node_modules/electron/dist`, which looks
nothing like a permissions problem. Verify with:

```bash
ls node_modules/electron/dist/    # expect Electron.app on macOS
```

`extract-zip` (GHSA-jmr9-qjv8-65gv, unvalidated symlink path traversal) resolved
with it — it was electron's download helper and only ran at `npm install`, so
that one was build-time only.

**Do not use `npm audit fix --force` for this.** It performs the same electron
bump but is free to touch anything else in the tree at the same time, and this
repository has already had one release cycle lost to an unexpected dependency
change. Bump the pin explicitly, then run plain `npm audit fix` for the rest.

Verify after the bump:

```bash
cd apps/desktop && npm install && npm audit
npm run build          # confirm the app still builds against 40.10.6
```

The original assessment, retained because the reasoning still applies whenever
the only available fix is a major version:

### Electron: upstream has not upgraded either

Issue [#45377](https://github.com/NousResearch/hermes-agent/issues/45377)
("electron@40.9.3 pulls in deprecated boolean@3.2.0 — upgrade to 42.x") was
opened **June 13, 2026** and is **still open** — labelled **P3, "Low — cosmetic,
nice to have."** No assignee, no linked PR, no branch.

Upstream's pin has moved `40.9.3` → `40.10.2` since: patch bumps inside 40.x,
never the major. So keeping `electron` at 40.x here matches a deliberate
upstream decision, not an oversight — the major upgrade touches native modules
(`node-pty`, `get-windows`) and the macOS signing chain, and upstream has
judged that cost higher than the benefit for a dev-only dependency.

### `@xmldom/xmldom`: we are ahead of upstream

Upstream carries no override for it. This tree pins the patched releases
(`0.8.15` / `0.9.12`, CVE-2026-83608/83609/83610) via `package.json`
`overrides`. Worth keeping through upstream syncs — a cherry-pick must not
drop it.

### Upstream's actual security model

Their effort goes to supply-chain poisoning and shipped code, not dev-tooling
CVEs:

1. **Curated advisory catalog** — `socis_cli/security_advisories.py` (upstream:
   `hermes_cli/`) flags known-compromised Python versions, surfaced at CLI
   startup, in `doctor`, and at gateway startup. Built after the May 2026
   `mistralai 2.4.6` worm. Advisories carry stable ids and can be acked into
   `config.security.acked_advisories`. Old entries are deliberately never
   removed, so fresh installs stay warned about versions that might linger in a
   private mirror.
2. **Lazy dependency install** (`tools/lazy_deps.py`) — extras install on first
   use rather than eagerly under `[all]`, so one quarantined transitive
   dependency can't collapse the whole resolve into a stripped tier.
3. **`min-release-age=14`** in `.npmrc` — the 14-day npm quarantine.
4. **CI guards** — `osv-scanner.yml`, `supply-chain-audit.yml`.

Their `SECURITY.md` names one load-bearing trust boundary and explicitly scopes
in-process heuristics *out* of the private-disclosure channel. Report privately
via GitHub Security Advisories or security@nousresearch.com; 90-day coordinated
disclosure. No bug bounty.

**Takeaway for this fork:** inherit the model, don't just inherit the code. The
advisory catalog in `socis_cli/security_advisories.py` is a live feature — as
upstream adds entries for newly-poisoned packages, those are exactly the
cherry-picks worth prioritising (see §B).
