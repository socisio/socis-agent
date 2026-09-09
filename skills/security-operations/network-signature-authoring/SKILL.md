---
name: network-signature-authoring
description: "Write Suricata and Snort rules that fire, or answer questions on signature testing and PCAP replay."
version: 1.0.0
author: SOCIS
license: MIT
platforms: [linux, macos, windows]
category: security-operations
triggers:
  - "write a suricata rule"
  - "snort signature for this traffic"
  - "detect this c2 channel"
  - "network signature from pcap"
  - "why is my suricata rule not firing"
toolsets:
  - terminal
  - file
  - suricata
metadata:
  socis:
    tags: [Security, DetectionEngineering, Suricata, Snort, NetworkSecurity]
    related_skills: [detection-engineering, yara-authoring, attack-mapping]
---

# Network Signature Authoring

Suricata and Snort rules have a failure mode YARA does not: a rule can be
syntactically perfect, load without error, and never fire — because the traffic
never reaches the engine in the form the rule expects.

So the rule is not finished when it compiles. It is finished when you have
replayed the PCAP and watched it alert.

---

## Guardrails

1. **Test by replay, not by inspection.** A rule that looks right and has not
   been run against the PCAP is a guess. `suricata -T` proves it parses,
   nothing more.
2. **Never write a rule that alerts on your own monitoring traffic.** Sensor
   management, EDR check-ins and backup jobs all look like beaconing.
3. **Beware `any any -> any any`.** It is the right answer occasionally and the
   cause of most performance complaints otherwise.
4. **Customer PCAPs contain customer data** — credentials, session tokens,
   internal hostnames, sometimes personal data. Do not upload them anywhere,
   and be careful what you paste into a rule comment.
5. **TLS changed what is possible.** Most C2 is encrypted. Content matching on
   the payload will not work; JA3/JA4, SNI, certificate fields and traffic
   shape are what you have.
6. **Zero alerts has two causes, and they are opposite.** Either the rule is
   wrong, or the PCAP has no traffic of the kind the rule matches. A `.onion`
   DNS rule replayed against a capture containing only TCP to a SOCKS port
   produces no alerts and is *untested*, not broken. Establish what is in the
   capture FIRST (step 1) so a null result means something. Never report a
   rule as broken on a null replay without confirming the relevant protocol
   was present.
7. **A .rules file is a production artifact, not a notebook.** A header
   comment naming the author, date, reference and tested-against PCAP is
   standard. A narrative test report is not — it ships to the customer's
   sensor and it belongs in the case notes or the PR description. Observed: a
   twelve-line "yes it fired" write-up patched into a live rules file.

---

## Prerequisites

```bash
bash ~/.socis-agent/socis-agent/scripts/install.sh --ensure suricata
suricata --build-info | head -5
suricata -T -c /etc/suricata/suricata.yaml -S custom.rules   # syntax test
tcpdump -r sample.pcap -nn | head                            # look first
```

---

## Procedure

### 1. Read the traffic before writing anything

```bash
tcpdump -r sample.pcap -nn -A | less
tshark -r sample.pcap -q -z conv,tcp
tshark -r sample.pcap -Y "tls.handshake.type == 1" -T fields -e tls.handshake.extensions_server_name
```

Establish what is actually distinctive. Usually one of:

| Observable | Use when |
|---|---|
| URI path, user-agent, header order | plaintext HTTP |
| SNI, JA3/JA4, certificate subject/issuer | TLS — the common case |
| DNS query pattern, DGA shape, TXT abuse | tunnelling or resolution-based C2 |
| Packet size, interval, jitter | beaconing where content tells you nothing |
| Protocol misuse on a standard port | anything trying to look like something else |

**If the traffic is TLS, decide now.** Content matching is off the table, and
a rule written as though it were plaintext will parse, load, and never fire.

### 2. Write the rule

```
alert http $HOME_NET any -> $EXTERNAL_NET any ( \
    msg:"SOCIS Family C2 Beacon"; \
    flow:established,to_server; \
    http.method; content:"POST"; \
    http.uri; content:"/gate.php"; startswith; \
    http.user_agent; content:"Mozilla/4.0"; depth:12; \
    classtype:trojan-activity; \
    reference:url,internal-case-1234; \
    metadata:created_at 2026_09_06, tlp AMBER; \
    sid:1000001; rev:1; )
```

Rules of thumb that matter:

- **Pick the narrowest protocol keyword.** `alert http` beats `alert tcp` —
  the engine only evaluates it on parsed HTTP, which is both faster and more
  accurate.
- **Always set `flow:`.** Without direction and state the rule evaluates on
  traffic it can never match, including the response side.
- **Use sticky buffers** (`http.uri`, `http.user_agent`, `tls.sni`) rather than
  raw `content` on the whole packet. Buffer-scoped matches are normalised and
  far cheaper.
- **Constrain with `depth`, `offset`, `startswith`.** An unanchored `content`
  scans the entire buffer on every packet.
- **SID from your own range.** 1000000–1999999 is the local range; anything
  else collides with ET or Talos.
- **`rev:` increments on every edit.** Engines cache by sid/rev, and a changed
  rule that keeps its rev may not reload.

### 3. Verify it parses

```bash
suricata -T -c /etc/suricata/suricata.yaml -S custom.rules
```

Parsing is necessary and nowhere near sufficient.

### 4. Replay — the step that decides

```bash
suricata -r sample.pcap -S custom.rules -l ./out/
cat ./out/fast.log
jq 'select(.event_type=="alert") | .alert.signature' ./out/eve.json
```

**No alert means one of two things, and they are opposite.** Either the rule
does not work, or this PCAP contains no traffic of the kind it matches. Settle
that before concluding anything:

```bash
# Is the protocol even present? No output = the rule was never exercised.
tshark -r sample.pcap -T fields -e dns.qry.name | sort -u | head
tshark -r sample.pcap -q -z io,phs        # protocol hierarchy
```

A `.onion` DNS rule replayed against a capture of TCP-to-SOCKS-proxy traffic
produces zero alerts and is **untested**, not broken. Discarding it there
throws away a working rule; shipping it because "replay ran" ships an
unverified one. Both are worse than saying "this capture cannot test it".

Once you have confirmed the relevant traffic IS in the capture, a null result
does mean the rule is wrong. Debug in this order:

1. Did Suricata parse the protocol at all? Check `eve.json` for `http` or
   `tls` events on that flow. If there are none, the traffic is on a
   non-standard port and needs a port definition or protocol detection.
2. Is `flow:` inverted? `to_server` on a response never matches.
3. Is the content in a different buffer than you assumed? `http.uri` excludes
   the host; `http.host` is separate.
4. Is it TLS? Then no payload content will ever match.

### 5. Test against benign traffic

```bash
suricata -r normal-day.pcap -S custom.rules -l ./fp-check/
wc -l ./fp-check/fast.log        # want 0
```

A rule that fires on ordinary browsing is worse than no rule. Use a capture
from the environment it will run in, not a synthetic one — every network has
its own strange-looking legitimate traffic.

### 6. Watch performance

```bash
suricata -r large.pcap -S custom.rules --engine-analysis
```

Look for rules flagged as having no fast-pattern or a weak one. A rule with a
1-2 byte fast pattern is evaluated constantly and will show up as packet loss
under load long before anyone connects it to the rule.

---

## Common failure modes

**Parses, never fires.** Wrong buffer, inverted `flow:`, or the traffic is
encrypted. Replay and check `eve.json` for protocol events.

**Fires on everything.** `any any -> any any` with a short generic content
match. Anchor the protocol, direction and buffer.

**Works on the PCAP, silent in production.** The PCAP was captured at a
different point in the network — often inside TLS termination, where
production sees the encrypted side.

**Packet loss after deployment.** A weak fast pattern, or `alert tcp` where
`alert http` would do. Run `--engine-analysis`.

**Alerts on your own tooling.** Vulnerability scanners and EDR agents generate
traffic that looks hostile. Exclude sensor and management ranges explicitly.

---

## On Snort

The syntax is close enough that most rules port with small changes, but
sticky-buffer names and some keywords differ between Snort 2, Snort 3 and
Suricata. Validate with the engine you will actually run:

```bash
snort -T -c snort.conf -R custom.rules
```

Do not assume a Suricata rule loads in Snort 3 because it looks similar.

---

## Verification

- [ ] Traffic examined before writing — distinctive observable identified
- [ ] Encrypted vs plaintext established, and the approach matches
- [ ] Narrowest protocol keyword used
- [ ] `flow:` set with correct direction and state
- [ ] Sticky buffers rather than raw packet content
- [ ] Matches anchored with `depth`, `offset` or `startswith`
- [ ] SID in the local range, `rev:` incremented
- [ ] `suricata -T` passes
- [ ] **Replayed against the PCAP and observed to alert**
- [ ] Replayed against benign traffic with zero hits
- [ ] `--engine-analysis` shows an adequate fast pattern
- [ ] Metadata complete: msg, classtype, reference, created_at, TLP
- [ ] No customer data in the rule text or comments
