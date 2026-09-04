SOCIS Agent — Repository Tree (Top-Level Summary)
====================================================
Generated from the fully rebranded, verified codebase.
File counts are recursive totals per top-level directory.

.
├── .github/              (44 files)   — CI workflows, issue/PR templates
├── acp_adapter/          (11 files)   — Agent Client Protocol bridge (Zed, etc.)
├── agent/                (216 files)  — Core agent runtime: model adapters, context engine,
│                                        compression, credential pool, memory manager
├── apps/                 (2,360 files) — Desktop app (Electron), bootstrap installer (Tauri),
│                                        shared TypeScript packages
├── assets/               (1 file)     — README banner image
├── cron/                 (15 files)   — Scheduled task engine
├── datagen-config-examples/ (4 files) — Example dataset generation configs
├── docker/               (18 files)   — Container entrypoints, s6 service supervision
├── docs/                 (23 files)   — Internal design docs, ADRs, RFCs
├── evals/                (46 files)   — Benchmark/evaluation harnesses
├── gateway/               (112 files) — Multi-platform message routing (Telegram, Discord,
│                                        Slack, WhatsApp, Signal, etc.)
├── locales/              (17 files)   — UI translation strings (17 languages)
├── mcp-research-data/    (5 files)    — Research benchmark data
├── native/                (5 files)   — Native C extension (CJK full-text search)
├── nix/                  (18 files)   — Nix packaging/deployment
├── optional-mcps/        (65 files)   — Optional MCP server manifests (third-party integrations)
├── optional-skills/      (718 files)  — Optional skill packs (not bundled by default)
├── plugins/              (353 files)  — Plugin system: model providers, memory backends,
│                                        messaging platforms, dashboard auth, etc.
├── providers/            (3 files)    — Provider abstraction base classes
├── scripts/              (91 files)   — Install script, CI helpers, dev tooling, rebrand toolchain
├── skills/               (330 files)  — Bundled skill packs (shipped by default)
├── socis_cli/            (324 files)  — CLI implementation (formerly hermes_cli)
├── tests/                (3,807 files) — Test suite
├── tests-js/             (12 files)   — JS/TS-specific tests
├── tools/                (165 files)  — Agent tool implementations (terminal, browser, file ops,
│                                        vision, TTS, wake-word, etc.)
├── tui_gateway/          (36 files)   — TUI backend gateway/RPC server
├── ui-tui/               (476 files)  — Terminal UI (React/Ink-based)
├── web/                  (188 files)  — Web dashboard (React/Vite)
├── website/              (812 files)  — Docusaurus documentation site (English + Chinese)
│
├── AGENTS.md                          — Contributor/agent development guide
├── CONTRIBUTING.md / .es.md           — Contribution guidelines
├── Dockerfile                         — Container build definition
├── LICENSE                            — MIT license (copyright: SOCIS)
├── README.md / .es.md / .zh-CN.md / .ur-pk.md  — Project README (4 languages)
├── REBRAND-EXECUTION-REPORT.md        — Full record of the Hermes→SOCIS rebrand work
├── SCREENSHOT-RETAKE-PUNCHLIST.md     — Docs screenshots/video still needing re-capture
├── SECURITY.md / .es.md               — Security policy
├── SOUL.md                            — Agent persona definition ("You are SOCIS Agent...")
├── cli.py                             — Main CLI entry logic
├── pyproject.toml                     — Python package definition (name: socis-agent)
├── run_agent.py                       — Agent runtime entry point
├── setup-socis.sh                     — Setup script
├── socis                              — CLI launcher binary/wrapper
├── socis_agent_*.py                   — Core state/logging/constants modules (formerly hermes_*.py)
└── uv.lock / package.json / package-lock.json — Dependency lockfiles
   (NOTE: lockfiles still reference pre-rebrand package name internally —
    regenerate with `uv lock` / `npm install` on a machine with network access)

Total: ~5,127 Python files, ~2,839 TypeScript/TSX files across the whole tree.

Note: the previous project's contributor attribution system (contributors/
folder with ~990 real contributor records, the contributor-check CI job,
and the add_contributor.py / audit_pr_attribution.py scripts) was removed
entirely per an explicit decision to start fresh rather than carry forward
the Hermes-era contributor community. release.py's contributor lookup was
left in place but cleared to an empty map, ready to be repopulated as SOCIS
Agent gains its own contributors — see the comment above `LEGACY_AUTHOR_MAP`
in scripts/release.py for how to add entries.
