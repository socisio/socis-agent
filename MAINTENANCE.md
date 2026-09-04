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
Forked from: NousResearch/hermes-agent @ v0.21.0
Fork date:   2026-09
```

### Recurring: check for upstream fixes

```bash
git fetch upstream
git log --oneline HEAD..upstream/main            # everything new upstream
git log --oneline HEAD..upstream/main --grep -i -E 'security|CVE|vuln|fix'
```

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
