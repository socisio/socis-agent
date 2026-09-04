# SOCIS CLI Reference

Live sources when anything looks stale: `socis --help`, `socis <command> --help`,
https://agent.socis.io/docs/reference/cli-commands

### Global Flags

```
socis [flags] [command]        (no subcommand = interactive chat)

  --version, -V             Show version
  -z, --oneshot PROMPT      One-shot: print ONLY the final response (for scripts/pipes)
  -m MODEL  --provider P    Model/provider override for this invocation
  -t, --toolsets LIST       Comma-separated toolsets for this invocation
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --tui / --cli             Force the Ink TUI / classic REPL
  --ignore-rules            Skip AGENTS.md/SOUL.md/memory/skill injection
  --safe-mode               Disable ALL customizations (troubleshooting)
  --pass-session-id         Include session ID in system prompt
```

### Chat

```
socis chat [flags]
  -q, --query TEXT          Single query, non-interactive
  --image PATH              Attach a local image to a single query
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --max-turns N             Cap tool-calling iterations
  --source TAG              Session source tag (default: cli)
```
(plus the global flags above)

### Configuration

```
socis setup [section]      Wizard (model|tts|terminal|gateway|tools|agent)
socis model                Interactive model/provider picker
socis fallback [add|remove|list]  Fallback provider chain
socis config [show|edit|get|set|unset|path|env-path|check|migrate]
socis login / logout       OAuth sign-in / clear stored auth
socis doctor [--fix]       Check dependencies and config
socis status [--all]       Component status
```

### Tools & Skills

```
socis tools [list|enable NAME|disable NAME]   Per-platform toolsets (curses UI with no args)

socis skills list|browse|search QUERY|inspect ID
socis skills install ID    Hub identifier OR a direct https://…/SKILL.md URL
socis skills config        Enable/disable skills per platform
socis skills check|update|uninstall|publish PATH
socis skills tap add REPO  Add a GitHub repo as a skill source
socis bundles              Skill bundles (one /<name> alias loads several skills)
```

### MCP Servers

```
socis mcp add NAME (--url or --command) | remove | list | test NAME
socis mcp catalog | install NAME     Curated catalog install
socis mcp configure NAME             Toggle tool selection
socis mcp serve                      Run SOCIS as an MCP server
```
Details (transport, tool discovery, catalog): `references/native-mcp.md`.

### Gateway (Messaging Platforms)

```
socis gateway run|install|start|stop|restart|status|setup
```

20+ platforms: Telegram, Discord, Slack, WhatsApp (Baileys + Business Cloud API), iMessage (Photon — `socis photon setup`), Signal, Email, SMS, Matrix, Mattermost, Teams, LINE, SimpleX, ntfy, Google Chat, Home Assistant, DingTalk, Feishu, WeCom, Weixin, API Server, Webhooks. Open WebUI connects via the API Server adapter. Most adapters ship under `plugins/platforms/`.
Docs: https://agent.socis.io/docs/user-guide/messaging/

### Sessions

```
socis sessions list|browse|rename ID TITLE|delete ID|export OUT|prune|stats
```

### Cron / Webhooks

```
socis cron list|create SCHED|edit ID|pause|resume|run ID|remove|status
    Schedules: '30m', 'every 2h', '0 9 * * *', ISO timestamp
socis webhook subscribe NAME|list|remove NAME|test NAME
```
Webhook payloads/routes: `references/webhooks.md`.

### Profiles

```
socis profile list|create NAME (--clone|--clone-all|--clone-from)|use|show|delete
socis profile rename A B | alias NAME | export NAME | import FILE
```

### Credentials & Pools

```
socis auth                 Interactive credential manager
socis auth add [PROVIDER]  Add OAuth or API-key credential (nous, openai-codex, qwen-oauth, …)
socis auth list|remove P IDX|reset PROVIDER|status
```
Multiple credentials per provider form a pool that rotates automatically and skips exhausted keys.

### Other

```
socis desktop / gui        Native desktop app
socis dashboard            Web admin panel + embedded chat (--stop / --status)
socis proxy                OpenAI-compatible local proxy backed by an OAuth provider
socis portal               Quick setup / sign in via Nous Portal
socis kanban <verb>        Multi-agent work-queue board
socis project              Named multi-folder workspaces
socis skin list|use|set    Switch/tweak skins (see references/themes.md)
socis pets <verb>          Pet mascots (see references/petdex.md)
socis memory setup|status|off|reset   Memory provider
socis secrets bitwarden|onepassword   External secret stores
socis moa                  Mixture-of-Agents slots
socis hooks / security / backup / import / checkpoints / console
socis logs [-f] [errors]   View agent/error logs
socis send                 One-off message through a gateway platform
socis pairing / plugins / insights / journey / computer-use
socis acp                  ACP server (IDE integration)
socis completion bash|zsh|fish
socis update / uninstall / claw migrate
```

Plugin- and provider-supplied subcommands (e.g. `socis photon setup`) only appear once their plugin is installed/active.

### Where to Find Things

| Looking for... | Location |
|---|---|
| Config options | `socis config edit` · [Configuration docs](https://agent.socis.io/docs/user-guide/configuration) |
| Tools / toolsets | `socis tools list` · [Tools reference](https://agent.socis.io/docs/reference/tools-reference) |
| Skills catalog | `socis skills browse` · [Skills catalog](https://agent.socis.io/docs/reference/skills-catalog) |
| Provider setup | `socis model` · [Providers guide](https://agent.socis.io/docs/integrations/providers) |
| Env variables | `socis config env-path` · [Env vars reference](https://agent.socis.io/docs/reference/environment-variables) |
| Gateway logs | `~/.socis-agent/logs/gateway.log` (or `socis logs`) |
| Sessions | `socis sessions browse` (reads state.db) |
