"""
Single source of truth for the Hermes Agent -> SOCIS Agent rebrand.

Every rename script in this directory imports from here so the whole
codebase, docs, and configs stay consistent. Do not hardcode "Hermes"
or "Nous" replacements anywhere else - add a rule here instead.

Ordering matters: replacements are applied in a fixed tier order (see
run_rebrand.py's build_replacement_table): domains, then home-dir path
forms, then env prefix, then module names, then general prose - longest
match first within each tier. Module names must beat the generic
bare-word "hermes"->"socis" rule or import statements will reference a
name that doesn't match what gets written to disk.

BUGS FOUND DURING DEVELOPMENT - fixed, kept here as history so they
aren't reintroduced:

1. A bare ".hermes" substring rule for the home directory also matched
   Python dotted-module paths like "tests.hermes_cli", rewriting them to
   "tests.socis-agent_cli" - a hyphen inside a Python identifier, which
   is a SyntaxError. Fix: home-dir replacement is anchored to concrete
   path forms only (HOME_DIR_PATH_FORMS below), never a bare ".hermes".

2. MODULE_RENAMES (renaming hermes_constants.py -> socis_agent_constants.py
   on disk) was not reflected in the text-substitution rules, which only
   knew the generic "hermes"->"socis" bare-word rule. Every
   `from hermes_constants import ...` became `from socis_constants
   import ...` (missing "_agent"), which no longer matched the renamed
   file - import breakage across 500+ files. Fix: MODULE_NAME_TEXT_REPLACEMENTS
   registers each renamed module as an explicit, higher-priority text rule.

3. Extensionless files (the `hermes` CLI wrapper script itself, s6 service
   scripts, Dockerfiles) were skipped by the text-substitution pass
   entirely because it only ran on a fixed extension allowlist. The file
   got renamed to `socis` but its CONTENT still said `from hermes_cli.main
   import main` - a renamed-but-broken entry point. Fix: extensionless
   files are included via is_text_candidate() in run_rebrand.py, while
   any file named LICENSE/NOTICE/COPYING anywhere in the tree (including
   vendored third-party ones under skills/, plugins/, etc.) is always
   excluded, since rewriting someone else's license text is a legal
   problem, not a cosmetic one.

4. ALL-CAPS occurrences ("HERMES-AGENT", "NOUS HERMES") in ASCII-art
   banner text were missed because only Title-case "Hermes" and
   lowercase "hermes" were covered. Fix: explicit ALL-CAPS rules added.
"""

# --- Env var prefix -----------------------------------------------------
ENV_PREFIX_OLD = "HERMES_"
ENV_PREFIX_NEW = "SOCIS_AGENT_"

# --- Home directory path forms (concrete forms only - see bug #1 above) ---
HOME_DIR_PATH_FORMS = [
    ("~/.hermes", "~/.socis-agent"),
    ("/.hermes/", "/.socis-agent/"),
    ('".hermes"', '".socis-agent"'),
    ("'.hermes'", "'.socis-agent'"),
    (".hermes/", ".socis-agent/"),
]

# --- CLI binaries (pyproject.toml [project.scripts]) -----------------------
CLI_ENTRYPOINTS = {
    "hermes": "socis",
    "hermes-agent": "socis-agent",
    "hermes-acp": "socis-acp",
}

# --- Package names ----------------------------------------------------
PYPI_PACKAGE_OLD = "hermes-agent"
PYPI_PACKAGE_NEW = "socis-agent"
NPM_SCOPE_OLD = "@hermes/"
NPM_SCOPE_NEW = "@socis/"

# --- Curated module renames, applied first, exact paths -------------------
MODULE_RENAMES = {
    "hermes_cli": "socis_cli",
    "hermes_bootstrap.py": "socis_agent_bootstrap.py",
    "hermes_constants.py": "socis_agent_constants.py",
    "hermes_logging.py": "socis_agent_logging.py",
    "hermes_time.py": "socis_agent_time.py",
    "hermes_startup_watchdog.py": "socis_agent_startup_watchdog.py",
    "hermes_state.py": "socis_agent_state.py",
    "hermes_state_common.py": "socis_agent_state_common.py",
    "hermes_state_holders.py": "socis_agent_state_holders.py",
    "hermes_state_portability.py": "socis_agent_state_portability.py",
    "hermes_state_registry.py": "socis_agent_state_registry.py",
    "hermes_state_schema.py": "socis_agent_state_schema.py",
    "hermes_state_search.py": "socis_agent_state_search.py",
    "ui-tui/packages/hermes-ink": "ui-tui/packages/socis-ink",
}

# Text-replacement equivalents of the module renames above (bare names, no
# extension, so they match inside import statements). Must beat the
# generic bare-word rule. More specific "hermes_state_X" variants listed
# before the shorter "hermes_state" so the shorter one doesn't fire first.
MODULE_NAME_TEXT_REPLACEMENTS = [
    ("hermes_cli", "socis_cli"),
    ("hermes_bootstrap", "socis_agent_bootstrap"),
    ("hermes_constants", "socis_agent_constants"),
    ("hermes_logging", "socis_agent_logging"),
    ("hermes_time", "socis_agent_time"),
    ("hermes_startup_watchdog", "socis_agent_startup_watchdog"),
    ("hermes_state_common", "socis_agent_state_common"),
    ("hermes_state_holders", "socis_agent_state_holders"),
    ("hermes_state_portability", "socis_agent_state_portability"),
    ("hermes_state_registry", "socis_agent_state_registry"),
    ("hermes_state_schema", "socis_agent_state_schema"),
    ("hermes_state_search", "socis_agent_state_search"),
    ("hermes_state", "socis_agent_state"),
    ("hermes-ink", "socis-ink"),
    ("hermes_home", "socis_agent_home"),
]

# --- Company / product prose -------------------------------------------
# Longest-first within this list; bare forms last since they're the
# broadest match and will also catch unrelated substrings (see
# EXCLUDE_PATHS for the specific real-world case: contributor emails).
PROSE_REPLACEMENTS = [
    ("Hermes Agent", "SOCIS Agent"),
    ("hermes-agent", "socis-agent"),
    ("Hermes Desktop", "SOCIS Agent Desktop"),
    ("Nous Research", "SOCIS"),
    ("NousResearch", "SOCIS"),
    ("nousresearch", "socis"),
    ("Hey Hermes", "Hey SOCIS"),
    ("hey_hermes", "hey_socis"),
    ("NOUS HERMES", "SOCIS"),
    ("HERMES-AGENT", "SOCIS-AGENT"),
    ("HERMES", "SOCIS"),
    ("Hermes", "SOCIS"),
    ("hermes", "socis"),
]

# --- Domains --------------------------------------------------------------
DOMAIN_REPLACEMENTS = [
    ("hermes-agent.nousresearch.com", "agent.socis.io"),
    ("setup.hermes-agent.nousresearch.com", "setup.agent.socis.io"),
    ("nousresearch.com", "socis.io"),
]

# Paths to NEVER touch (text or renames) even if they textually match:
# binary ML models, vendored code, git internals, lockfiles, real
# contributor personal data from git history, legal attribution
# requiring a human decision, and this toolchain's own source.
EXCLUDE_PATHS = [
    ".git/",
    "node_modules/",
    "uv.lock",
    "package-lock.json",
    "tools/wakewords/hey_hermes.onnx",
    "tools/wakewords/hey_hermes.tflite",
    "contributors/emails/",
    "LICENSE",
    "scripts/rebrand/",
    "docs/hermes-kanban-v1-spec.pdf",
]

TEXT_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".md", ".mdx",
    ".json", ".jsonl", ".yaml", ".yml", ".toml", ".sh", ".ps1", ".cmd",
    ".cfg", ".ini", ".txt", ".html", ".css", ".nix", ".service",
    ".example", ".rs", ".c", ".h", ".svg", ".plist", ".manifest", ".tmpl",
    ".lock",
}

# Any file with this exact basename, anywhere in the tree (ours or a
# vendored third party's), is skipped by the text pass entirely.
EXTENSIONLESS_LICENSE_NAMES = {"LICENSE", "NOTICE", "COPYING", "LICENSE.txt", "NOTICE.txt"}
