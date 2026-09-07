# Security MCP servers — findings for review

SOC, IR, DFIR, threat intel and enrichment. Nothing here is installed.
Check the links, mark what you want, and I'll write the manifests.

Offensive/pentest servers are deliberately excluded — see the note at the end.

**"Listed" is not "verified".** These are search results. Before pinning any
git server its source needs reading (credential handling, phone-home,
logging), and the catalog requires a real commit SHA — never a tag or branch.

---

## TIER 1 — vendor-official

Published and supported by the vendor. Lowest risk, add first.

| Tool | Link | Transport |
|---|---|---|
| **Anomali ThreatStream** | https://www.anomali.com/resources/videos/anomali-threatstream-mcp-server-installation-guide | http, `Api-Key user:key` |
| Splunk | https://github.com/CiscoDevNet/Splunk-MCP-Server-official | http + oauth |
| Elastic MCP Apps | https://www.elastic.co (search "Elastic MCP") | http |
| PagerDuty | https://www.pulsemcp.com/servers/pagerduty | http |
| Grafana | https://github.com/grafana/mcp-grafana | http |
| Datadog / Sentry / Cloudflare | already in catalog | http |

**ThreatStream — verified working.** Endpoint
`https://optic.threatstream.com/mcp`, auth `Api-Key <user>:<key>`, via
`npx mcp-remote` with **`--transport http-only`** (without it the SSE
sub-connection returns 406 and kills the process).

**35 tools**, and the capability is genuine: `get_actors`, `get_actor_details`,
`get_intelligence`, `ioc_knowledge_tool`, `semantic_search_tool`,
`get_threat_bulletins`, `get_investigations`, plus Anomali's PIR and
agentic-task workflow.

**But it costs ~66.2k tokens per call** — roughly half a 128k window on tool
schemas alone, before any conversation. That is the largest single entry in
this catalog by a wide margin, and the first symptom of overrunning it is
truncated tool output rather than any error naming context as the cause. The
manifest therefore pre-selects 12 read-only intelligence tools and leaves the
rest available but unchecked.

Worth remembering when assessing any large MCP server: **tool count is a
context cost, and it competes with the conversation.** `falcon-mcp` solves the
same problem with a `--dynamic` mode that loads schemas on demand; ThreatStream
has no equivalent, so the filtering has to happen at install time.

Note it needs the `mcp-remote` stdio bridge rather than a plain `type: http`
entry — the catalog's `TransportSpec` has no `headers` field, so a server
requiring a custom `Authorization` header cannot be expressed as a direct HTTP
transport. The bridge also keeps the key in `~/.socis-agent/.env` via
`auth.env` instead of sitting in a config file.

The test connection returned
`StreamableHTTPError: Failed to open SSE stream: Not Acceptable — 406`.
Worth confirming with Anomali whether that endpoint speaks Streamable HTTP, or
whether it wants different `Accept` headers, before packaging the entry.

---

## TIER 2 — SOC / SIEM / IR / threat intel (community, production-grade)

| Tool | Link | Notes |
|---|---|---|
| **Wazuh** | https://github.com/gensecaihq/Wazuh-MCP-Server | ~50 tools: triage, hunting, vuln mgmt, compliance (PCI/GDPR/HIPAA/NIST/ISO), active response. MIT, OAuth 2.1, Docker, air-gap capable. Strongest non-vendor option. |
| **OpenCTI** | https://github.com/Spathodea-Network/opencti-mcp | STIX entity search, indicators, reports, connector status. MIT. |
| **MISP** | https://github.com/bornpresident/MISP-MCP-SERVER | IOC lookup, event analysis, TI search. |
| Illumio | https://github.com/alexgoller/illumio-mcp-server | Microsegmentation: workloads, labels, traffic flows. |

**No MCP server found** for TheHive/Cortex, Velociraptor, Microsoft Sentinel,
or CrowdStrike standalone. Sentinel's vendor path is Security Copilot, not MCP.

---

## TIER 3 — enrichment / OSINT (read-only, low blast radius)

| Tool | Link | Covers |
|---|---|---|
| VirusTotal | https://github.com/BurtTheCoder/mcp-virustotal | Hash/URL/IP/domain reputation + relationships |
| Shodan | https://github.com/BurtTheCoder/mcp-shodan | Host/service fingerprinting, exposed infrastructure |
| dnstwist | https://github.com/BurtTheCoder/mcp-dnstwist | Typosquat / phishing-domain permutation |
| Maigret | https://github.com/BurtTheCoder/mcp-maigret | Username OSINT across platforms |
| OSV | https://github.com/gleicon/mcp-osv | Dependency vulnerabilities via OSV.dev |
| NVD CVE | npm `nvd-cve-mcp-server` (`npx -y nvd-cve-mcp-server`) | CVE detail, CVSS, CWE. Two tools: `get_cve_details`, `search_cve`. Keyless. |

The four `BurtTheCoder/*` servers are one author — a single source review
covers all of them, which makes them a cheap block to approve together.

### Aggregators — one server, many sources

Searched the shortlist (AbuseIPDB, URLScan, GreyNoise, Censys, OTX,
MalwareBazaar, HIBP, crt.sh). Most have no dedicated MCP server, but two
aggregators cover the majority in one install — which is better anyway: one
source to review, one manifest, one credential set.

| Server | Link | Covers |
|---|---|---|
| **mcp-threatintel** | https://github.com/aplaceforallmystuff/mcp-threatintel | AlienVault OTX, AbuseIPDB, GreyNoise, abuse.ch (URLhaus, MalwareBazaar, ThreatFox, Feodo Tracker). npm `mcp-threatintel-server`. **Tools enable per key present**, and Feodo works with no key at all — so it degrades gracefully, which is exactly what a skill like `ioc-enrichment` needs. |
| Sandbox + IOC enrichment | search `malwarebazaar model-context-protocol` on GitHub topics | Detonation via Hybrid Analysis / tria.ge / ANY.RUN, plus MalwareBazaar, ThreatFox, URLhaus, Feodo, URLScan, VirusTotal. BYOK, async, ATT&CK mapping. Note the guardrail: **do not detonate customer files in a public sandbox.** |

**No dedicated MCP found** for Censys, crt.sh / certificate transparency,
IPinfo or SecurityTrails. crt.sh in particular needs none — it is an
unauthenticated HTTP endpoint the `web` toolset can already query.

**HIBP** appears only inside `badchars/darknet-mcp-server` (66 tools: breach
data, stealer logs, Tor .onion access, ransomware tracking, IntelX). Genuine
CTI value, but that scope — dark-web access and credential dumps — deserves
the same deliberate decision as the offensive tier, not a default install.
Link: https://github.com/badchars/darknet-mcp-server

---

## Detection rules — writing them, not scanning with them

Searched specifically for MCP servers that **generate** Sigma, YARA and
Snort/Suricata rules. **None exists**, and the strongest evidence that none
should is who else concluded the same:

**Florian Roth — author of yarGen and THOR — shipped a SKILL, not an MCP:**
https://github.com/Neo23x0/yargen-go-skill

> *"An LLM Agent Skill for automated YARA rule generation using yarGen-Go.
> Embeds expertise from the creator of the original yarGen tool into your AI
> assistant's context."*

He explicitly targets MCP-based agents and still chose a skill. Rule
generation splits three ways, and none of it wants a network service holding
credentials:

| Step | Belongs to |
|---|---|
| Extract candidate strings, filter goodware | **CLI** — yarGen, YaraML |
| Decide which strings are durable, write the condition | **the LLM** |
| Validate it compiles and does not over-match | **CLI** — `yarac`, `sigma check`, `suricata -T` |

That is `terminal` + a skill, which SOCIS already has.

### Generation tooling worth installing on the host

| Format | Tool | Link |
|---|---|---|
| YARA | yarGen-Go (Go; REST API + web UI) | https://github.com/Neo23x0/yarGen-Go |
| YARA | yarGen (Python; has an `--ai` output mode) | https://github.com/Neo23x0/yarGen |
| YARA | YaraML (Sophos, ML-based, Apache-2.0) | search `sophos YaraML` |
| YARA | yaraQA — rule quality / FP checker | search `Neo23x0/yaraQA` |
| Sigma | sigma-cli + pySigma — author, `sigma check`, convert per SIEM | https://github.com/SigmaHQ/sigma |
| Suricata/Snort | `suricata -T` / `snort -T` validate; no generator — the LLM writes from PCAP or IOC | — |

Rule *sources* (not servers), useful as reference corpora:

- SigmaHQ/sigma — https://github.com/SigmaHQ/sigma
- JPMinty/Detection_Engineering_Signatures (YARA + Sigma + Snort) — https://github.com/JPMinty/Detection_Engineering_Signatures
- yara-sigma-webui (YARA→Sigma converter) — https://github.com/wahidhendrawan/yara-sigma-webui

### Gap in our own skills

`detection-engineering` (bundled) covers **Sigma** properly — authoring, the
conversion trap, tuning, known-positive tests. It covers **neither YARA nor
Snort/Suricata**. Two skills would close that:

- **`yara-authoring`** — sample → yarGen → string triage → condition logic →
  `yarac` + yaraQA → FP test against a goodware corpus
- **`network-signature-authoring`** — PCAP/IOC → Suricata rule → `suricata -T`
  → replay against the PCAP to confirm it actually fires

### Licence check on `yargen-go-skill` — do NOT copy it

I suggested adapting Florian Roth's skill. **That was wrong, and the check is
why.**

The repository (https://github.com/Neo23x0/yargen-go-skill) contains only
`references/`, `scripts/`, `README.md` and `SKILL.md` — **there is no LICENSE
file.** Its licence section reads:

> *"This skill is designed for use with yarGen-Go by Florian Roth. See the
> yarGen-Go repository for licensing details"*

It defers to a **different repository's** licence, which does not grant rights
over this one. Under the Berne Convention, absent an explicit licence a work
is **all rights reserved** — copying, adapting or redistributing it would be
an infringement, whatever the yarGen-Go licence says.

It is also very new: 4 stars, 7 commits, 1 fork.

**What we can do instead**

- **Reference it.** Linking and citing is always fine, and it is genuinely the
  best public statement of the "skill, not MCP" position.
- **Write our own from public docs.** CLI flags, database strategy and the
  goodware-filtering method are facts and procedures published in the yarGen
  and yarGen-Go READMEs. Facts are not copyrightable; the *expression* in his
  SKILL.md is. Ours must be written independently, in our own words and
  structure — the same standard applied to the vendored security skills.
- **Ask.** He is reachable (@cyb3rops). If SOCIS wants to ship an adaptation,
  a one-line permission or an added MIT licence settles it. Worth doing before
  building on his work rather than after.

For contrast, the 759 vendored security skills were **Apache-2.0**, which is
why vendoring them was straightforward — retain the notice, state the changes.
No licence is a different situation entirely.

---

## Directories, to browse for anything missed

- awesome-mcp-servers (security) — https://github.com/TensorBlock/awesome-mcp-servers/blob/main/docs/security.md
- PulseMCP — https://www.pulsemcp.com/servers
- Glama — https://glama.ai/mcp/servers

---

## Offensive / pentest servers — excluded

Removed at your request, and I agree with the call. For the record so the
decision is not silently revisited: these run `nmap`, `sqlmap`, `metasploit`
and `hydra` against whatever target the model is handed. In an MSSP touching
client environments, a prompt-injected or mistaken target means attacking the
wrong host, and scope enforcement is the server's responsibility with widely
varying quality. If a PT arm ever needs them they belong in a separate,
explicitly-labelled category that an operator installs deliberately — never a
default, never alongside the SOC tooling.

---

## Should we vendor these into the SOCIS repo?

You asked whether, if the MCPs are MIT, we can copy them into the repo and
"make them ours" — as we did with the 759 security skills.

**My recommendation: no, not by default.** The two cases look similar and are
not.

**Skills are inert.** A `SKILL.md` is markdown. Vendoring one costs a licence
notice and nothing else — worst case it gives bad advice, which a human reads
and rejects.

**MCP servers are executable code holding credentials to a customer's SIEM.**
Vendoring one means:

1. **You inherit the security burden.** Upstream ships a fix for an auth bypass
   or a log-injection bug; your vendored copy never receives it. You now have
   to watch every upstream repo yourself — the same problem `MAINTENANCE.md`
   documents for the Hermes fork, multiplied per server.
2. **You implicitly vouch for it.** A client sees `socisio/socis-agent` shipping
   the code that talks to their Wazuh. Reasonably, they hold you responsible
   for what it does.
3. **You get no reproducibility benefit you don't already have.** The catalog
   already pins a full commit SHA that must be ≥2 weeks old. That is the
   guarantee vendoring would buy — and it is already there, without ownership.
4. **MIT does not make it free of obligations.** You must retain the copyright
   notice and licence text, and state your modifications. Cheap, but not zero,
   and it must be right for every server.

**The one real argument for vendoring is air-gap.** SOC and OT customers
genuinely run without outbound internet, and `install: git` cannot clone
there. If that is a requirement, the answer is selective:

- Vendor only the two or three servers those specific customers need
- Keep them in a clearly-marked directory with upstream URL, pinned SHA,
  licence and a "last synced" date
- Add them to the `upstream-watch` workflow so their advisories surface
- Re-sync deliberately, as a reviewed change

**Middle path worth considering instead:** ship the manifests (tiny, ours,
no third-party code) and provide an offline bundle — a tarball of the pinned
servers built by CI for air-gapped installs. Same outcome, and the repo stays
free of other people's code.

---

## How to give me your picks

Mark each install or skip. For Tier 2 servers, one command gives me the pin:

    git ls-remote https://github.com/OWNER/REPO HEAD

Paste the 40-char SHA. I'll confirm it is ≥2 weeks old, read the source, and
write the manifest.

Suggested first cut: **ThreatStream** (already in use, vendor-official),
**Splunk**, **Wazuh**, and the **BurtTheCoder enrichment set**. Add
OpenCTI/MISP once you know which TIP your clients run.
