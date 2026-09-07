# Security MCP catalog — implementation tracking

Working document for adding security/SOC servers to `optional-mcps/`.
Candidate research and rationale live in `SECURITY-MCP-CANDIDATES.md`; this
file tracks what is actually being built, what is blocking it, and what has
shipped.

---

## Naming and identity

The catalog has **no separate display-name field** — `CatalogEntry.name` is
the directory name, and the desktop renders it title-cased with hyphens kept
(`aws-knowledge` → "Aws-Knowledge"). So the directory name *is* the branding
decision.

**Vendor servers keep their vendor name.** Anomali, Splunk, Elastic, PagerDuty
and Grafana are trademarks, and a user connecting to Splunk needs to see
"Splunk". Renaming them would be both confusing and legally unwise.

**Community MIT servers get functional SOCIS names.** The entry is ours — we
write the manifest, the description and the install experience — so it carries
a name that describes what an analyst gets, not who wrote the upstream server:

| SOCIS entry | Displays as | Wraps |
|---|---|---|
| `threat-intel` | Threat-Intel | mcp-threatintel (OTX + AbuseIPDB + GreyNoise + abuse.ch) |
| `endpoint-siem` | Endpoint-Siem | Wazuh MCP Server |
| `ioc-reputation` | Ioc-Reputation | mcp-virustotal |
| `attack-surface` | Attack-Surface | mcp-shodan |
| `domain-permutation` | Domain-Permutation | mcp-dnstwist |
| `cve-lookup` | Cve-Lookup | nvd-cve-mcp-server |
| `cti-platform` | Cti-Platform | OpenCTI |
| `intel-sharing` | Intel-Sharing | MISP |

### Attribution is not optional

MIT states its single condition plainly:

> *"The above copyright notice and this permission notice shall be included in
> all copies or substantial portions of the Software."*

Stripping author and repo is the one thing MIT does not permit. Two further
reasons beyond the legal one:

1. **`upstream-watch` needs it.** Without a recorded repo, the weekly job
   cannot tell us when one of these servers ships a security fix. We would be
   shipping unmaintained code to customer SOCs and not know it.
2. **It is the same standard already met.** The 759 vendored security skills
   carry a NOTICE crediting Mahipal Jangra under Apache-2.0. Doing less here
   would be inconsistent with a decision already taken.

**How both are satisfied:** the analyst-facing surface — entry name,
description, install flow, post-install text — is entirely SOCIS. Attribution
lives in the manifest's `source:` field and in `optional-mcps/NOTICE`, which
is where a reviewer or auditor looks and a user does not.

---

## Status

**10 of 13 built and parsing. 0 installed or tested.**

The other 3 are decided, not outstanding — MISP has no licence, Elastic has no
published endpoint, and `domain-permutation` is held pending a connection test.
All dependency audits are complete.

Catalog is at **75 entries: 65 inherited + 10 new**, `catalog_diagnostics()`
clean. See Handover at the end for the test order and what carries forward.

| # | Entry | Tier | Status | Next |
|---|---|---|---|---|
| 1 | Anomali ThreatStream | vendor | **WRITTEN** — parses; config verified against vendor docs | 406 unresolved — confirm transport/entitlement with Anomali |
| 2 | Splunk | vendor | **DONE** — parses; URL is per-stack, placeholder documented | customer supplies endpoint at install |
| 3 | Elastic | vendor | **WILL NOT SHIP** | no published endpoint — see final position below |
| 4 | PagerDuty | vendor | **DONE** — hosted, fixed URL, parses | — |
| 5 | Grafana | vendor | **ALREADY EXISTED** — inherited entry, hosted Grafana Cloud + OAuth | nothing to do; see the near-miss below |
| 6 | `threat-intel` | MIT | **DONE** — 28d, parses, deps clean | — |
| 7 | `endpoint-siem` (Wazuh) | MIT | **DONE** — 27d, parses | needs a running Wazuh MCP deployment to test |
| 8 | `ioc-reputation` (VirusTotal) | MIT | **DONE** — 105d, parses, **axios override applied** | — |
| 9 | `attack-surface` (Shodan) | MIT | **DONE** — 159d, parses, **axios override applied** | — |
| 10 | `domain-permutation` (dnstwist) | MIT | **HOLD — confirmed broken** | requires Docker; fails on any host without a running daemon |
| 11 | `cve-lookup` (NVD) | **first-party** | **DONE** — security-reviewed and fixed, parses | publish 1.1.0 to npm, then simplify to npx |
| 12 | `cti-platform` (OpenCTI) | MIT | **DONE** — MIT, 34d, parses | — |
| 13 | `intel-sharing` (MISP) | **NO LICENCE** | **WILL NOT SHIP** | nothing — see below |

---

## Vendor entries

### `pagerduty` — hosted, fixed endpoint

The only genuinely hosted entry so far. Fixed regional URLs:

| Region | URL |
|---|---|
| US | `https://mcp.pagerduty.com/mcp` |
| EU | `https://mcp.eu.pagerduty.com/mcp` |

Reached through `mcp-remote` rather than `type: http`, because PagerDuty uses
`Authorization: Token <token>` and the catalog's http+api_key path emits
`Bearer`. `TransportSpec` has no headers field to override it — the same
constraint that forces ThreatStream down the bridge route.

The credential is a literal `Token <token>` string, not a bare token, which is
easy to get wrong. The `post_install` says so explicitly.

**Write access.** It can create, modify and resolve incidents and change
on-call schedules. An agent acting on a mistaken instruction can page the wrong
people at 3am or close a live incident. The token inherits the issuing user's
permissions, so the guidance is a dedicated narrow-role user rather than an
admin account.

**EU residency.** The US endpoint accepts EU traffic — it just routes through
US infrastructure. That is a silent way to breach a data-residency commitment,
so the manifest calls it out rather than leaving it to be discovered.

### `splunk` — per-stack endpoint, native Bearer

Vendor-official (Splunk LLC, Splunkbase 7931). Unlike PagerDuty there is no
shared endpoint: each customer's URL comes from the Splunk MCP Server app on
their own stack, so the manifest ships a `CHANGE-ME` placeholder and the
`post_install` walks through obtaining the real one.

Splunk uses `Authorization: Bearer`, which is what the catalog emits natively,
so this is a plain `type: http` entry with no bridge. Env var name verified
against `_env_key_for_server('splunk')` → `MCP_SPLUNK_API_KEY`; a mismatch
there installs cleanly and 401s at connect time.

Two things recorded in `post_install` that are easy to miss:

- **Searches honour existing Splunk RBAC.** The MCP server does not widen
  access. That is the right boundary — but a token issued from an
  over-privileged Splunk account gives the agent that account's reach, so it is
  worth confirming with the customer rather than assuming.
- **SPL costs money.** Searches consume Splunk resources and can count against
  licence quotas. An agent iterating over queries is expensive in a way an
  analyst running one search is not.

**OAuth is the better path where available.** Splunk Cloud 10.5.2506.3+
defaults to OAuth 2.1, removing the long-lived token entirely. The manifest
notes how to switch.

### `threatstream` — written, but do not trust it yet

Endpoint `https://optic.threatstream.com/mcp`, auth
`Authorization: Api-Key <user>:<key>`, via the `mcp-remote` bridge (the
catalog emits `Bearer` on the http path, and `TransportSpec` has no headers
field).

The `post_install` leads with the unresolved 406 rather than burying it. An
entry that appears in a catalog and then fails on first connection is worse
than one that is absent, so this ships only once Anomali confirms the
transport.

Worth noting why the bridge is the right shape here anyway: `auth.env` puts
the credential in `~/.socis-agent/.env`, prompted and masked. During testing
this exact credential was leaked in a screenshot of `mcp.json` — the config
file is a place secrets get shared by accident.

### NEAR MISS: `grafana` already existed and was overwritten

While writing a Grafana entry I created `optional-mcps/grafana/manifest.yaml`
without checking whether one was already there. **It was** — an inherited
entry for the hosted Grafana Cloud MCP (`https://mcp.grafana.com/mcp`, native
OAuth 2.1 + DCR, with a documented tool-exclusion list). `cat >` overwrote it
silently, and the entry count staying at 74 instead of rising to 75 was the
only signal.

Restored from the upstream Hermes copy, with the rebrand reapplied to match
the other 64 inherited manifests (`Hermes` → `SOCIS`, `hermes mcp login` →
`socis mcp login`; the `# Nous-approved` header is left alone throughout, so
it stays).

Two things this changes going forward:

1. **The inherited entry is the better one.** It uses the *hosted* Grafana
   Cloud server with OAuth, not the self-hosted `mcp-grafana` binary I was
   about to add. No credential to store, no `uv` dependency on the host. For
   self-hosted Grafana the OSS binary is still the answer, but that is a
   separate entry and should be named distinctly rather than replacing this.
2. **Check before writing.** All 65 inherited entries were verified afterwards
   for further collisions — there were none — but the check belongs before the
   write, not after.

### `intel-sharing` (MISP) — will not ship, no licence

    bornpresident/MISP-MCP-SERVER
    spdx_id: (none returned)
    pushed:  2025-04-09  (17 months)
    stars:   12

The GitHub licence endpoint returns no SPDX identifier, which means no
detectable LICENSE file. Absent an explicit grant a work is **all rights
reserved**, so packaging or redistributing it would be an infringement — the
same finding as `yargen-go-skill`, and the second time in this project that a
repository assumed to be open source turned out not to be.

This is why the licence check is a separate step from the age check. Both
repos looked adoptable: public, on GitHub, in a list of "open source MCP
servers". Neither carries a licence.

Secondary concerns that would have applied anyway: 17 months unmaintained and
12 stars, against `cti-platform`'s 40 — a thin base for something holding
credentials to a customer's threat-intel platform.

**If MISP integration is wanted**, the options are to ask the author to add a
licence (a one-line change, and people usually say yes), find an alternative
implementation, or use MISP's REST API through the `terminal` toolset with a
skill — MISP ships `PyMISP`, so this is well-trodden and needs no third-party
server at all.

### `cti-platform` (OpenCTI) — verified, one detail outstanding

    Spathodea-Network/opencti-mcp -> zxzinn/opencti-mcp   (moved again)
    spdx_id: MIT
    pushed:  2026-08-03  (34 days — clears the >=2 week rule)
    stars:   40
    HEAD:    7cd0c1e568dc712570970e91d76dfd36366433b9

Third repository in this set to have moved. The pattern is consistent enough
to be worth stating as a rule: **resolve the canonical path before pinning**,
because a redirect is controlled by whoever holds the old namespace and can be
re-pointed later, and `upstream-watch` must follow the real repository.

Resolved and written. Default branch is `master` (not `main` — which is why
the raw fetch initially returned nothing), entry point `build/index.js`,
credentials `OPENCTI_URL` and `OPENCTI_TOKEN`, both required.

`package.json` declares `"prepare": "npm run build"`, so `npm install` already
triggers tsc. The bootstrap keeps an explicit `npm run build` anyway, because
`prepare` does not run under `--ignore-scripts` or some CI defaults, and a
missing `build/index.js` fails at spawn with a bare module-not-found that
gives no hint about the cause.

Write capability noted in `post_install`: an OpenCTI API token carries the
user's full role, which can include creating and modifying entities, merging
objects and managing connectors. Merges are not cleanly reversible, and the
knowledge base is what detections are built on — so the guidance is a
dedicated read-only user.

### Elastic — not doing, for now

The MCP Apps endpoint is not in publicly searchable documentation. A manifest
pointing at a guessed URL would fail on first connect, which is worse than an
absent entry. It needs a URL from Elastic or from a customer deployment that
already runs it.

Not a gap worth chasing: `splunk` and `grafana` already cover SIEM and
log-datasource querying, and `grafana` reaches Elasticsearch datasources
directly. Add Elastic the day someone hands over the endpoint.

### TEST RESULT: `domain-permutation` requires Docker

First live test confirmed the hold was right, for a reason the manifest had
wrong. The server does not call a local `dnstwist` binary — it shells out to
Docker:

    Executing command: docker pull elceef/dnstwist
    failed to connect to the docker API at unix:///Users/.../docker.sock
    check if the path is correct and if the daemon is running

Every lookup failed. The original `post_install` said `pip install dnstwist`,
which was simply incorrect and would have sent users down the wrong path.
Corrected to state the Docker requirement plainly.

That makes three independent reasons this entry stays on hold: a pre-1.0 MCP
SDK, 18 months unmaintained, and a hard dependency on a running Docker daemon
for what is otherwise the least critical capability in the set.

### TEST RESULT: `threat-intel` and `cve-lookup` work

    Threat Intel MCP server running - configured: greynoise, feodo
    NVD CVE MCP Server started

`threat-intel` detected only the credentials that were actually set and
enabled those sources. That is the degrade-gracefully behaviour the manifest
was written for and that `ioc-enrichment` depends on — the skill queries
whatever is connected rather than failing when a source is absent.

### Final position on the three that will not ship

| Entry | Reason | Reversible? |
|---|---|---|
| MISP | No licence file — all rights reserved | Yes: ask the author to add one |
| Elastic | No published MCP Apps endpoint | Yes: the day a URL is available |
| `domain-permutation` | Pre-1.0 MCP SDK (`^0.4.0`), 18 months unmaintained | Yes: manifest is written; ship it if it connects |

None is unfinished work. Each is a decision with a recorded reason, so nobody
reopens it six months from now as a forgotten task.

### Superseded

- **Elastic** — the MCP Apps endpoint is not in publicly searchable docs.
  Needs a URL from Elastic or from a customer deployment.
- **Grafana** — `mcp-grafana` is a self-hosted Go binary, not a hosted service.
  It needs the stdio + install pattern rather than a URL, and the deployment
  shape should be confirmed before writing it.
- **Anomali ThreatStream** — still blocked on the 406.

---

## First-party entry: `cve-lookup`

`nvd-cve-mcp-server` is SOCIS's own (author `0x4hm3d`). It was reviewed like
any third-party entry, and the review found four things worth fixing — which
is the argument for reviewing your own code on the same terms as everyone
else's.

### What the review found

| | Finding | Fix |
|---|---|---|
| 1 | **No NVD API key support.** NVD limits anonymous callers to 5 requests per 30s; a free key gives 50. An analyst hits the anonymous limit during ordinary triage. | Optional `NVD_API_KEY`, sent as the `apiKey` header |
| 2 | **The rate limit degraded data silently.** On failure the server fell back to web scraping, which returns no CWE and no references. The only signal was `*Data source: NVD Web*` in the footer. | Report now opens with an `INCOMPLETE DATA` block naming the cause (429 vs genuine error) and what is missing |
| 3 | **`args.cve_id.toUpperCase()` with no type check** threw a raw `TypeError` that was returned to the model as the error text. | Type-checked with an actionable message; same for `keyword`, plus a 200-char cap and integer coercion on `limit` |
| 4 | **No lockfile**, floors at `axios ^1.7.9` / `sdk ^1.0.4`. | Floors raised to `^1.18.0` / `^1.24.0` |

Finding 2 was the significant one. Degraded data that looks like good data is
worse than an error, and in a CVE report an analyst has no way to know the CWE
field is empty because of a rate limit rather than because NVD has none.

### What the review found was already right

The CVE-ID regex `/^CVE-\d{4}-\d{4,}$/` runs **before** the ID reaches a URL,
and `getCVEFromWeb` interpolates it into a path. That regex is the control
preventing path traversal and SSRF, not input tidying. Tested against
`../../../etc/passwd`, `CVE-2024-3400/../../admin` and query injection — 10/10
rejected. The README now says so explicitly, so nobody relaxes it later.

Dependencies also used **caret ranges with no upper bound**, so `npm install`
picks up patches. That is precisely the mistake `ioc-reputation` and
`attack-surface` made, avoided here.

### Two decisions recorded

**The ≥2-week pin age was waived.** The rule exists because a freshly-pushed
commit is what a compromised third-party maintainer account produces. That
threat model does not apply to code SOCIS wrote, reviewed here, and pushed
itself — there is no upstream maintainer to compromise. **The waiver is
specific to first-party repositories** and must not be extended to community
servers, where the rule is doing real work.

**npm is deliberately not used.** The registry still carries 1.0.2, which
predates this review — no API key support, silent scraping fallback, raw
TypeError on bad input. Anyone installing from npm today gets the unfixed
server. Publish 1.1.0 and the manifest can drop the install block entirely for
`npx -y nvd-cve-mcp-server@1.1.0`, which is simpler for users. Until then, git.

---

## Dependency audit

Age alone does not tell you whether a pinned server is safe. `ioc-reputation`
cleared every process check — MIT, 105 days old, canonical path, verified entry
point — and still shipped a critical vulnerability, because the audit that
matters is of what it *installs*, not of the repository metadata.

### FINDING: `ioc-reputation` resolved a critically vulnerable axios

Upstream declares:

    "axios": ">=1.4.0 <1.14.1"

That upper bound is not carelessness — it reads as a deliberate response to the
**2026-03-31 npm supply-chain attack**, in which the axios maintainer account
was compromised and versions 1.14.1 and 0.30.4 were published carrying a
cross-platform RAT. Both were pulled from the registry. Capping below 1.14.1
was the right call that week.

The side effect is that the range now resolves to at most **1.14.0**:

| Advisory | Impact | CVSS | Fixed in | 1.14.0 |
|---|---|---|---|---|
| CVE-2026-40175 / GHSA-fvcv-3m26-pcqx | prototype-pollution gadget → RCE / AWS IMDSv2 bypass | **9.9** | 1.15.0 | **vulnerable** |
| CVE-2025-62718 | proxy resolution path | — | 1.15.x | vulnerable |
| CVE-2026-67312 | uncontrolled recursion | moderate | 1.18.0 | vulnerable |
| CVE-2026-67315 | 0.0.0.0 not treated as loopback | moderate | 1.18.0 | vulnerable |

CVE-2026-40175 needs **zero direct user input**: if anything else in the
dependency tree pollutes `Object.prototype`, axios picks up the polluted
properties during config merge and can be steered into SSRF against cloud
metadata. In a SOC tool that already makes outbound HTTP requests on an
analyst's behalf, that is not a theoretical concern.

**Applied fix** — an explicit override in the manifest's bootstrap:

    - "npm install"
    - "npm install --save-exact axios@1.18.0"
    - "npm run build"

1.18.0 clears all four advisories and sits **above** the compromised 1.14.1, so
the upgrade does not walk back into the malicious release.

Re-verify at every pin bump. Upstream may widen the range themselves, at which
point the override becomes unnecessary rather than wrong — and an override kept
past its usefulness is its own maintenance hazard.

### FINDING: `attack-surface` had the same axios problem

    "axios": ">=1.7.8 <1.14.1"

Identical pattern, identical consequence — resolves to 1.14.0, vulnerable to
CVE-2026-40175 and the two 1.18.0 advisories. Same override applied.

Two of the three servers that use axios shipped it vulnerable. Worth assuming
any MCP server pinned during the March 2026 incident window has the same
shape.

### `threat-intel` is clean

    "@modelcontextprotocol/sdk": "^1.29.0"

One dependency, current major, caret range so npm resolves patches. Nothing to
override. The smallest dependency surface in the set — which is a point in its
favour beyond the four-sources-in-one coverage.

### CONCERN: `domain-permutation` depends on a pre-1.0 MCP SDK

    "@modelcontextprotocol/sdk": "^0.4.0"

For a 0.x package, `^0.4.0` means `>=0.4.0 <0.5.0` — so this is locked to the
0.4 line and cannot pick up anything newer. The current TypeScript SDK is
1.24.x.

MCP has gone through five protocol revisions since: 2024-11-05, 2025-03-26,
2025-06-18, 2025-11-25 and 2026-07-28. The last of those rewrote the wire
protocol — the `initialize` handshake is replaced by `server/discover`, state
moves into per-request `_meta`, and roots/sampling/logging are deprecated.

Modern clients do negotiate downward (the reference client advertises
acceptance back to 2024-10-07), so this **may** still connect in a degraded
mode. It also may not. It cannot be determined without testing.

**Recommendation: hold `domain-permutation` back from the first shipping set.**

The reasoning is cumulative rather than any single fault:

- 18 months without an upstream commit — no fixes are coming
- Locked to a pre-1.0 SDK, five protocol revisions behind
- Requires `dnstwist` installed separately on the host, so it is not
  self-contained even when it works
- The capability is the least critical in the set — typosquat discovery is
  useful, not load-bearing

Shipping an entry that probably half-works, in a catalog a customer browses
for security tooling, costs more in credibility than the feature returns. The
manifest is written and validated; it can ship the moment someone confirms it
connects. That is a better order than shipping it and finding out.

### FINDING: the dependency count is the real story

A live install of `attack-surface` — a wrapper around one HTTP API — resolved
**190 packages** and reported **14 advisories (1 critical, 9 high)**. The axios
pin cleared the critical and one high; 11 remained.

Reading the actual advisory list explains why, and it is not carelessness in
the server:

    hono                 ~30 advisories   web framework
    @hono/node-server                     HTTP server adapter
    koa                                   a SECOND web framework
    express-rate-limit                    a THIRD framework's middleware
    body-parser, path-to-regexp, qs       HTTP request handling
    file-type                             upload sniffing
    undici               16 advisories    HTTP client
    fast-uri, ip-address                  URI / IP parsing

**CORRECTED.** I first attributed this to `fastmcp`. It is not — the
**MCP TypeScript SDK itself** pulls the HTTP server stack, for its
Streamable-HTTP transport. Proof: `threat-intel` declares exactly ONE
dependency, `@modelcontextprotocol/sdk ^1.29.0`, and still resolves 96
packages with 6 advisories including `hono`, `body-parser`, `fast-uri`,
`ip-address` and `qs`.

So there is no "pick a leaner MCP framework" escape. Every Node MCP server on
the current SDK carries this, and `fastmcp` only adds on top of it. These
servers run **stdio** and never open a listener, so the server-side paths stay
unreachable — but the code is on disk and `npm audit` reports it.

**7 of the 11 advisory roots are server-side code that never executes here** —
serveStatic path traversal, CORS bypass, cookie injection, cache poisoning,
route ReDoS. Unreachable.

**4 are potentially reachable**: `undici` (the actual outbound HTTP client),
`fast-uri` and `ip-address` (SSRF via parsing quirks), `qs` (query building).

Unreachability is worth knowing but it is not a defence. It is the difference
between *exposed* and *shipping dead vulnerable code* — and a customer running
`npm audit` on a SOCIS install will not weigh that distinction generously.

**Fix applied.** `npm audit` reported every one as fixable without `--force`,
so the bootstrap now runs:

    npm install
    npm install axios@^1.18.0     # break the upstream cap first
    npm audit fix                 # then resolve the rest
    npm run build

Order matters: breaking the cap before `audit fix` lets audit see an
unconstrained range and bump axios further within `^1` if a newer fix lands.
A caret, not `--save-exact` — an exact pin would recreate the upper-bound trap
one version later, which is the mistake that caused this in the first place.
`npm run build` runs last, so an incompatible fix fails the install loudly
rather than shipping a broken server.

**The general point for future entries.** Dependency count is a security
property. A four-dependency package that resolves 190 is carrying a framework
it does not use, and every one of those is a package whose maintainer could be
compromised. Worth checking `npm ls --depth=0` and the resolved total before
adding any stdio MCP server to the catalog.

### Measured across every installed server

| Server | Packages | Advisories before | After `npm audit fix` |
|---|---|---|---|
| `attack-surface` | 194 | 14 (1 critical, 9 high) | **0** |
| `ioc-reputation` | 158 | 13 (9 high) | **0** |
| `cve-lookup` | 131 | **0** | 0 |
| `threat-intel` | 96 | 6 (3 high) | pending re-install |
| `domain-permutation` | 18 | 1 high — **unfixable** | see below |

`cve-lookup` reporting **0 with no remediation step** is the pattern working:
its dependencies are caret-ranged with no upper bounds, so npm resolves to
current and fixes arrive on their own. The two that needed remediation needed
it because upstream capped axios below a fix.

**The audit step is now in every git-installed manifest** — `threat-intel`,
`cve-lookup` and `cti-platform` were missing it, on the mistaken assumption
that a small dependency list meant a small surface.

### `domain-permutation`: a fifth reason, and a security one

    @modelcontextprotocol/sdk <1.24.0   HIGH
    DNS rebinding protection not enabled by default
    GHSA-w48q-cv73-mx4w
    fix available via `npm audit fix --force`
    Will install @modelcontextprotocol/sdk@1.30.0, which is a breaking change

Its 18-package footprint looked like an advantage until this. The pre-1.0 SDK
carries an unpatched high advisory whose **only** fix is a jump from `^0.4.0`
to 1.30.0 — across the 1.0 boundary and five protocol revisions, on a project
unmaintained for 18 months. `npm audit fix` without `--force` cannot touch it,
which is why that step is deliberately absent from this manifest rather than
added for consistency: it would run, report success, and change nothing.

A smaller attack surface that cannot be patched is not a smaller risk. This
now has five independent reasons to stay out of the catalog: pre-1.0 SDK, an
unfixable high advisory, 18 months unmaintained, a hard Docker dependency,
and the least critical capability in the set.

### Audit summary

| Entry | Dependencies | Verdict |
|---|---|---|
| `threat-intel` | MCP SDK ^1.29.0 | clean |
| `ioc-reputation` | axios (capped), dotenv, fastmcp, zod | **axios override applied** |
| `attack-surface` | axios (capped), dotenv, fastmcp, zod | **axios override applied** |
| `domain-permutation` | MCP SDK ^0.4.0 | **hold — pre-1.0 SDK, unmaintained** |
| `endpoint-siem` | 11 Python deps, all major-bounded | **clean — best-engineered of the set** |

### `endpoint-siem` (Wazuh) — audited, clean

SOCIS connects to a customer-run deployment rather than installing this, so
its dependency hygiene is the customer's to maintain. That is a genuine
reduction in our exposure and worth stating plainly to clients. It is not a
reason to skip the audit: we recommend the server, so its quality is our
concern even when patching is not.

Eleven Python dependencies, and **every upper bound is a MAJOR-version bound**:

    fastapi>=0.128.0,<1.0.0        pyjwt[crypto]>=2.9.0,<3.0.0
    uvicorn[standard]>=0.40.0,<1.0.0   python-multipart>=0.0.20,<1.0.0
    httpx>=0.28.1,<1.0.0           prometheus-client>=0.24.0,<1.0.0
    pydantic>=2.12.0,<3.0.0        psutil>=6.0.0,<8.0.0
    python-dotenv>=1.0.0,<2.0.0    tenacity>=9.0.0,<10.0.0
                                   cryptography>=50.0.0,<51.0.0

That distinction is the whole finding. A major bound lets every patch and
minor release through, so `pip install` resolves to the current version and
security fixes arrive on their own. A *patch-level* cap is what froze axios at
1.14.0 in `ioc-reputation` and `attack-surface`, below the fix for a CVSS 9.9
RCE chain. None of these caps sits below a known fix.

The project also explains its own reasoning in the file:

> *"Version ranges carry an upper bound so a new MAJOR release of a dependency
> cannot silently break a build. For fully reproducible images, generate a
> hash-locked file (pip-compile / uv pip compile) and install it in the
> Dockerfile with --require-hashes."*

Other signals of a maintained project rather than a weekend upload: `LICENSE`,
`SECURITY.md`, `.gitleaks.toml` (they scan their own repo for secrets),
`MCP_COMPLIANCE_VERIFICATION.md`, `WAZUH_COMPATIBILITY.md`, a `tests/`
directory, and both `compose.yml` and a `Dockerfile`.

**One thing to pass to customers:** no hash-locked file ships, so a `pip
install -r requirements.txt` today and the same command in three months
produce different trees. The project recommends `pip-compile` +
`--require-hashes` for production images. Worth doing on a host that talks to
a SIEM and can isolate endpoints — and worth mentioning during deployment,
since it is the customer's build, not ours.

### Audit complete

All five shipping servers with installable dependencies have now been
checked. Two needed an override, two were already correct, one is
best-in-class. `domain-permutation` remains on hold for a different reason
(pre-1.0 MCP SDK), not a dependency finding.

### The general lesson

Pinning a SHA freezes *the server's* code. It does **not** freeze what that
code pulls in at install time, and a caret range on a stale project resolves
to whatever npm offers on the day. Both need checking, and the second is the
one that gets skipped.

---


## Verification procedure (for future entries)

This is the process every entry above went through, kept because the next
person adding a server needs it — and because two of the checks below only
exist as a result of something this exercise got wrong.

### For every git-installed server

    # Resolve the CANONICAL path first — three of the repos here had moved,
    # and `curl` needs -L or the API silently returns nothing.
    curl -sL https://api.github.com/repos/OWNER/REPO | grep -E '"full_name"|"spdx_id"|"pushed_at"'

    git ls-remote https://github.com/OWNER/REPO HEAD

Paste the 40-char SHA. Catalog policy (see `optional-mcps/n8n/manifest.yaml`):
a **full commit SHA, never a tag or branch** — tags move, SHAs do not — and
the commit must be **at least 2 weeks old** at pin time, matching the
supply-chain rules already applied to pyproject and npm dependencies.

Also confirm the licence file actually exists in the repo. `yargen-go-skill`
looked adoptable and turned out to have **no LICENSE at all**, which means all
rights reserved. Assume nothing from a README.

### For every vendor server

The hosted endpoint URL and auth method. Most use OAuth 2.1 with dynamic
client registration, which SOCIS handles natively (see
`optional-mcps/datadog/manifest.yaml`).

---

## Pinned SHAs — verified

`git ls-remote HEAD`, captured 2026-09-06:

| Entry | Repo | HEAD SHA |
|---|---|---|
| `threat-intel` | aplaceforallmystuff/mcp-threatintel | `b71210b2e21766411de858844c1c864291630f30` |
| `endpoint-siem` | gensecaihq/Wazuh-MCP-Server | `af5a61e65589010dc4099827d9da4f91f6e5b20a` |
| `ioc-reputation` | BurtTheCoder/mcp-virustotal | `364ce0d0fb505644c52ed1a83c4f3d5f10abee1f` |
| `attack-surface` | BurtTheCoder/mcp-shodan | `59c70b91647a22b338bad04ac6269650af5a6f0f` |
| `domain-permutation` | BurtTheCoder/mcp-dnstwist | `af62d09328f762a3581cd354997299ed0a758c11` |

**Verified 2026-09-06:**

| Repo | Commit date | Age | Licence |
|---|---|---|---|
| aplaceforallmystuff/mcp-threatintel | 2026-08-09 | 28d PASS | MIT |
| gensecaihq/Wazuh-MCP-Server | 2026-08-10 | 27d PASS | MIT |
| **w0h1v**/mcp-virustotal | 2026-05-24 | 105d PASS | MIT |
| BurtTheCoder/mcp-shodan | — | — | — |
| BurtTheCoder/mcp-dnstwist | — | — | — |

### The BurtTheCoder repos have moved

`BurtTheCoder/mcp-virustotal` **redirects to `w0h1v/mcp-virustotal`.** That is
why the earlier API query came back empty in the shape being grepped — the
request was following a redirect to a different canonical name.

The project is MIT, 149 stars, last pushed 2026-05-24. Its manifest is
written, pinned to the canonical `w0h1v` path rather than the redirect.

**It reads as an account rename, not a transfer.** The decoded `package.json`
still declares `author: BurtTheCoder`, npm scope `@burtthecoder/mcp-virustotal`
and mcpName `io.github.BurtTheCoder/virustotal` — a new maintainer would almost
certainly have rewritten those. So the code is the same author's.

The canonical URL is still what goes in the manifest, because a redirect is
controlled by whoever holds the old namespace and can be re-pointed later, and
`upstream-watch` must follow the real repository or it watches nothing.
Attribution in NOTICE credits BurtTheCoder.

Entry point confirmed from `package.json`: `main: build/index.js`, built by
`tsc && chmod +x build/index.js`. An npm package `@burtthecoder/mcp-virustotal@1.0.25`
also exists with a matching scope — not a name-squat — but the git SHA pin is
kept, since a commit hash is content-addressed and an npm version tag is not.

Confirmed: all three moved. `w0h1v/mcp-shodan` (MIT, pushed 2026-03-31, 164
stars) and `w0h1v/mcp-dnstwist` (MIT, pushed 2025-03-03, 51 stars). Both use
`build/index.js` and `npm run build`, matching mcp-virustotal.

**`domain-permutation` is unmaintained** — 18 months since the last push. It
passes the age rule trivially, which is exactly why the age rule alone is not
enough: "old enough to be safe" and "still being looked after" are different
properties. Accepted here because it is a keyless read-only wrapper with a
small dependency surface, and `upstream-watch` will surface any advisory that
does appear. The same staleness in `endpoint-siem`, which holds SIEM
credentials, would have been disqualifying.

Note also `curl` needs `-L` against these paths — without it the redirect is
not followed and the API appears to return nothing, which is what made these
look blocked for two rounds.

The lesson from `yargen-go-skill` stands: "assumed MIT" and "actually
licensed" are different things, and so are "the URL everyone cites" and "the
repository that URL resolves to".

To settle it:

    curl -s -o /dev/null -w "%{http_code}\n" https://api.github.com/repos/BurtTheCoder/mcp-virustotal
    curl -s https://api.github.com/repos/BurtTheCoder/mcp-virustotal | grep -m1 '"license"' -A3

404 means the repo moved or was renamed — find the current location. 200 with
`"license": null` means no licence: all rights reserved, do not vendor.

**The original note on HEAD still applies to any future pin:** The policy exists because a
freshly-pushed commit is exactly what a compromised maintainer account
produces; two weeks is the window in which the community notices. Pinning HEAD
would defeat the point of pinning.

Two outstanding checks before any of these can be used:

    # commit date + declared licence, no clone needed
    curl -s https://api.github.com/repos/OWNER/REPO/commits/HEAD | grep -m1 '"date"'
    curl -s https://api.github.com/repos/OWNER/REPO/license   | grep -m1 '"spdx_id"'

If HEAD is younger than 2 weeks, pin the most recent commit that is not —
`git log --since` on a clone, or the commits API with `?until=`.

`spdx_id` must return a real identifier (`MIT`, `Apache-2.0`). `NOASSERTION`
or an error means no detectable licence, which is the `yargen-go-skill`
situation: all rights reserved, do not vendor or adapt.

---

## Known technical constraint: custom auth headers

`TransportSpec` has **no `headers` field**. A remote server requiring a custom
`Authorization` header therefore **cannot** be a `type: http` entry.

ThreatStream is the case in point — `Api-Key <user>:<key>`. It needs the
`mcp-remote` stdio bridge:

```yaml
transport:
  type: stdio
  command: npx
  args:
    - "-y"
    - "mcp-remote"
    - "https://optic.threatstream.com/mcp"
    - "--header"
    - "Authorization:${AUTH_HEADER}"

auth:
  type: api_key
  env:
    - name: AUTH_HEADER
      description: "Api-Key <username>:<api-key> from ThreatStream settings"
      required: true
```

This is better than a direct HTTP entry anyway: `auth.env` puts the credential
in `~/.socis-agent/.env` where it is prompted for and masked, rather than
sitting in plaintext in a config file that gets screenshotted.

Servers using OAuth or a plain bearer token can use `type: http` directly.

---

## Per-entry detail

### 1. Anomali ThreatStream — BLOCKED

- Vendor-official. Name kept.
- Endpoint `https://optic.threatstream.com/mcp`, auth `Api-Key <user>:<key>`
- Reached via `npx mcp-remote` (see constraint above)
- **Blocker:** test connection returned
  `StreamableHTTPError: Failed to open SSE stream: Not Acceptable — 406`.
  Either the endpoint does not speak Streamable HTTP, or it wants different
  `Accept` headers. Confirm with Anomali before packaging — shipping an entry
  that 406s on first use is worse than not shipping it.

### 6. `threat-intel` — highest value per unit of review

Wraps `aplaceforallmystuff/mcp-threatintel`. One entry, four sources:
AlienVault OTX, AbuseIPDB, GreyNoise, abuse.ch (URLhaus, MalwareBazaar,
ThreatFox, Feodo Tracker).

Why this one first: **tools enable per key present**, and Feodo Tracker works
with no key at all. So it degrades gracefully — which is exactly what the
`ioc-enrichment` skill assumes ("ask whatever is connected, note what is
missing, continue"). Four `auth.env` entries, all optional.

Published to npm as `mcp-threatintel-server`, so it may not need `install:
git` at all — `npx -y mcp-threatintel-server` would do, which removes the SHA
pin question entirely. **Verify whether the npm package is published by the
same author before relying on it** — npm name-squatting on a GitHub project is
a known supply-chain pattern.

### 7. `endpoint-siem` — Wazuh

~50 tools: alert triage, threat hunting, vulnerability management, compliance
mapping (PCI DSS, GDPR, HIPAA, NIST CSF, ISO 27001), active response. MIT,
OAuth 2.1 + bearer, Docker-first, **air-gap capable**.

Two things to settle before writing the manifest:

1. **Docker or Python?** The project is containerised. If the recommended
   deployment is `docker compose up`, that does not fit `install: git` +
   `bootstrap` cleanly and the manifest should point at an already-running
   instance over HTTP instead.
2. **Active response is a write capability.** These tools can isolate hosts
   and kill processes on a customer's estate. The manifest's `post_install`
   must say so explicitly, and the credential guidance should recommend a
   read-only Wazuh API user unless the customer has deliberately chosen
   otherwise.

### 8–10. BurtTheCoder set — one review covers three

`mcp-virustotal`, `mcp-shodan`, `mcp-dnstwist` share an author. One source
review clears all three, which makes them cheap to approve as a block. All
read-only lookups against public APIs — the lowest blast radius in the list.

Guardrail to carry into `post_install` for VirusTotal: **do not submit
customer files or internal URLs.** Submission publishes them.

### 11. `cve-lookup` — NVD

npm `nvd-cve-mcp-server`, keyless, two tools: `get_cve_details`, `search_cve`.
Simplest entry in the list — likely `npx -y nvd-cve-mcp-server` with
`auth: {type: none}` and no install block at all. Still needs a licence check
on the npm package.

---

## Deliberately excluded

**Offensive / pentest servers.** They run `nmap`, `sqlmap`, `metasploit` and
`hydra` against whatever target the model is handed. In an MSSP touching
client environments a prompt-injected or mistaken target means attacking the
wrong host, and scope enforcement is the server's responsibility with widely
varying quality between repos. If a PT arm ever needs them they belong in a
separate, explicitly-labelled category an operator installs deliberately.
Recorded here so the decision is not silently reversed later.

**HexStrike AI** (150+ tools, autonomous) — highest-risk profile in the
ecosystem. Not appropriate for a client-facing product.

**`badchars/darknet-mcp-server`** (66 tools: HIBP, stealer logs, Tor .onion
access, IntelX). Genuine CTI value, but dark-web access and credential dumps
deserve the same deliberate decision as the offensive tier, not a default
install.

---

## Definition of done, per entry

- [ ] Upstream licence file **read** (not the README's claim about it)
- [ ] Source reviewed: credential handling, phone-home, logging
- [ ] Commit SHA pinned, ≥2 weeks old — or npm package verified as same-author
- [ ] `manifest.yaml` validates:
      `python3 -c "from socis_cli.mcp_catalog import list_catalog, catalog_diagnostics; list_catalog(); print(catalog_diagnostics() or 'OK')"`
- [ ] Entry appears in `socis mcp list` and in the desktop Catalog
- [ ] Install tested end to end on a clean profile
- [ ] Credentials land in `~/.socis-agent/.env`, not in any config file
- [ ] `post_install` states exactly which credential, what scope, and any
      write capability the server has
- [ ] Attribution added to `optional-mcps/NOTICE`
- [ ] Repo added to `upstream-watch` so its advisories surface weekly

A malformed manifest is reported through `catalog_diagnostics()` rather than
crashing the catalog — so check it explicitly. A silent parse failure looks
exactly like a missing entry.

---

## NOTICE requirement

`optional-mcps/NOTICE` exists and covers every pinned entry, following the
pattern of `optional-skills/security/NOTICE`. It records:

- Upstream project name, URL and copyright holder
- Full licence text (MIT is short — include it verbatim)
- Statement of what SOCIS changed (packaging and naming, not the server code)
- Explicit note that these servers are **vendored/pinned as-is and not
  individually audited by SOCIS beyond the review recorded above**

That last line matters. These run with credentials to a customer's security
platform, and a client is entitled to know the difference between "SOCIS
wrote this" and "SOCIS packaged this".

---

## Handover

### Shipping — 10 entries

| Entry | Displays as | Type | Credential |
|---|---|---|---|
| `threat-intel` | Threat-Intel | community MIT, pinned | 4 optional keys |
| `ioc-reputation` | Ioc-Reputation | community MIT, pinned | VirusTotal key |
| `attack-surface` | Attack-Surface | community MIT, pinned | Shodan key |
| `cti-platform` | Cti-Platform | community MIT, pinned | OpenCTI URL + token |
| `cve-lookup` | Cve-Lookup | first-party | optional NVD key |
| `endpoint-siem` | Endpoint-Siem | remote, customer-run | bearer token |
| `splunk` | Splunk | vendor, per-stack | bearer token |
| `pagerduty` | Pagerduty | vendor, hosted | `Token <token>` |
| `threatstream` | Threatstream | vendor, hosted | `Api-Key user:key` |
| `grafana` | Grafana | vendor, hosted (inherited) | OAuth |

Catalog: **75 entries — 65 inherited + 10 new.** `catalog_diagnostics()` clean.

### Test order

1. **`threat-intel`** first. No infrastructure needed, and abuse.ch Feodo works
   with no credential at all, so tools respond immediately. Free keys for the
   other three sources take a few minutes.
2. **`cve-lookup`** next — keyless, first-party, two tools.
3. **`ioc-reputation`** / **`attack-surface`** — one API key each. These are
   the two carrying the axios override; confirm `npm install` completes and
   the pinned 1.18.0 is what lands.
4. **`pagerduty`** if you have an account — the only hosted entry with a fixed
   URL, so it exercises the mcp-remote bridge without needing a deployment.
5. The rest need infrastructure: `endpoint-siem` a Wazuh MCP deployment,
   `splunk` the Splunk MCP app on a stack, `cti-platform` an OpenCTI instance.

Validate before any of it:

    python3 -c "from socis_cli.mcp_catalog import list_catalog, catalog_diagnostics; \
                print(len(list_catalog()), 'entries'); print(catalog_diagnostics() or 'OK')"

A malformed manifest reports through `catalog_diagnostics()` rather than
crashing the catalog, so check it explicitly — a silent parse failure looks
identical to a missing entry.

### Write capabilities — confirm before any customer deployment

Three entries can change state in a customer's environment:

| Entry | What it can do |
|---|---|
| `endpoint-siem` | Isolate hosts, kill processes, run active-response scripts |
| `pagerduty` | Create, modify and resolve incidents; change on-call schedules |
| `cti-platform` | Create and merge entities, manage connectors — merges are not cleanly reversible |

Each `post_install` says so and recommends a read-only credential. That
guidance is only worth anything if someone reads it during onboarding, so it
belongs in the deployment checklist rather than only in the manifest.

### Carrying forward

- **`upstream-watch` must cover the pinned repos.** Five servers are pinned to
  a commit; without the workflow following them, a security fix upstream never
  surfaces. The repos are in NOTICE.
- **Re-verify overrides at every pin bump.** The axios override in
  `ioc-reputation` and `attack-surface` becomes unnecessary — not wrong, but
  noise — if upstream widens its range. An override kept past its usefulness
  is its own maintenance hazard.
- **`cve-lookup` should move to npm.** Publish 1.1.0 and the manifest drops the
  install block for `npx -y nvd-cve-mcp-server@1.1.0`: no clone, no build. It
  also closes the trap where someone finds 1.0.2 on npm and installs the
  version without the security fixes.

### What this exercise found that process alone would not

Every server here passed a licence check and an age check. Two still shipped a
CVSS 9.9 remote-code-execution chain, because the audit that mattered was of
what the code *installs*, not of the repository's metadata. Pinning a SHA
freezes the server; it does not freeze its dependency tree.

Two repositories assumed to be open source had no licence at all. Three had
moved to different owners. One inherited entry was silently overwritten and
only the entry count revealed it.

None of that is exotic. It is what an hour of checking finds in any set of
community servers, and it is the argument for doing the checking before these
reach a customer's SIEM rather than after.
