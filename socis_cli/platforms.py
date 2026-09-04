"""
Shared platform registry for SOCIS Agent.

Single source of truth for platform metadata consumed by both
skills_config (label display) and tools_config (default toolset
resolution).  Import ``PLATFORMS`` from here instead of maintaining
duplicate dicts in each module.
"""

from collections import OrderedDict
from typing import NamedTuple


class PlatformInfo(NamedTuple):
    """Metadata for a single platform entry."""
    label: str
    default_toolset: str


# Ordered so that TUI menus are deterministic.
PLATFORMS: OrderedDict[str, PlatformInfo] = OrderedDict([
    ("cli",            PlatformInfo(label="🖥️  CLI",            default_toolset="socis-cli")),
    ("telegram",       PlatformInfo(label="📱 Telegram",        default_toolset="socis-telegram")),
    ("discord",        PlatformInfo(label="💬 Discord",         default_toolset="socis-discord")),
    ("slack",          PlatformInfo(label="💼 Slack",           default_toolset="socis-slack")),
    ("whatsapp",       PlatformInfo(label="📱 WhatsApp",        default_toolset="socis-whatsapp")),
    ("whatsapp_cloud", PlatformInfo(label="📱 WhatsApp Business (Cloud)", default_toolset="socis-whatsapp")),
    ("signal",         PlatformInfo(label="📡 Signal",          default_toolset="socis-signal")),
    ("bluebubbles",    PlatformInfo(label="💙 BlueBubbles",     default_toolset="socis-bluebubbles")),
    ("email",          PlatformInfo(label="📧 Email",           default_toolset="socis-email")),
    ("homeassistant",  PlatformInfo(label="🏠 Home Assistant",  default_toolset="socis-homeassistant")),
    ("mattermost",     PlatformInfo(label="💬 Mattermost",      default_toolset="socis-mattermost")),
    ("matrix",         PlatformInfo(label="💬 Matrix",          default_toolset="socis-matrix")),
    ("dingtalk",       PlatformInfo(label="💬 DingTalk",        default_toolset="socis-dingtalk")),
    ("feishu",         PlatformInfo(label="🪽 Feishu",          default_toolset="socis-feishu")),
    ("wecom",          PlatformInfo(label="💬 WeCom",           default_toolset="socis-wecom")),
    ("wecom_callback", PlatformInfo(label="💬 WeCom Callback",  default_toolset="socis-wecom-callback")),
    ("weixin",         PlatformInfo(label="💬 Weixin",          default_toolset="socis-weixin")),
    ("qqbot",          PlatformInfo(label="💬 QQBot",           default_toolset="socis-qqbot")),
    ("yuanbao",        PlatformInfo(label="🤖 Yuanbao",         default_toolset="socis-yuanbao")),
    ("webhook",        PlatformInfo(label="🔗 Webhook",         default_toolset="socis-webhook")),
    ("api_server",     PlatformInfo(label="🌐 API Server",      default_toolset="socis-api-server")),
    ("cron",           PlatformInfo(label="⏰ Cron",            default_toolset="socis-cron")),
])


def platform_label(key: str, default: str = "") -> str:
    """Return the display label for a platform key, or *default*.

    Checks the static PLATFORMS dict first, then the plugin platform
    registry for dynamically registered platforms.
    """
    info = PLATFORMS.get(key)
    if info is not None:
        return info.label
    # Check plugin registry
    try:
        from gateway.platform_registry import platform_registry
        entry = platform_registry.get(key)
        if entry:
            return f"{entry.emoji}  {entry.label}" if entry.emoji else entry.label
    except Exception:
        pass
    return default


def get_all_platforms() -> "OrderedDict[str, PlatformInfo]":
    """Return PLATFORMS merged with any plugin-registered platforms.

    Plugin platforms are appended after builtins.  This is the function
    that tools_config and skills_config should use for platform menus.
    """
    merged = OrderedDict(PLATFORMS)
    try:
        from gateway.platform_registry import platform_registry
        for entry in platform_registry.plugin_entries():
            if entry.name not in merged:
                merged[entry.name] = PlatformInfo(
                    label=f"{entry.emoji}  {entry.label}" if entry.emoji else entry.label,
                    default_toolset=f"socis-{entry.name}",
                )
    except Exception:
        pass
    return merged
