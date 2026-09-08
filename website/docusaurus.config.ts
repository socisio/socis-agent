import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'SOCIS Agent',
  tagline: 'The self-improving AI agent',
  favicon: 'img/favicon.ico',

  url: process.env.DOCUSAURUS_URL || 'https://agent.socis.io',

  // baseUrl is baked into every emitted asset path, so it MUST match the
  // path the site is actually served from — otherwise the HTML loads and
  // every stylesheet and script 404s, rendering the site unstyled.
  //
  // Two deploy targets, two values:
  //   agent.socis.io           -> /docs/              (default, below)
  //   socisio.github.io        -> /socis-agent/docs/  (project sites are
  //                               served under /<repo>/, and the Pages
  //                               workflow sets DOCUSAURUS_BASE_URL)
  //
  // The github.io copy exists so the CIMD OAuth client-metadata document has
  // a redirect-free origin; an authorization server MUST NOT follow redirects
  // when fetching it.
  baseUrl: process.env.DOCUSAURUS_BASE_URL || '/docs/',

  organizationName: 'socisio',
  projectName: 'socis-agent',

  onBrokenLinks: 'throw',

  // Anchors are slugs GENERATED from heading text, so rewording a heading
  // silently breaks every link pointing at it — the page still loads, it
  // just doesn't scroll, which is invisible in CI and easy to miss in
  // review. The rebrand did exactly this ("SOCIS Desktop" -> "SOCIS Agent
  // Desktop", "Nous Research" -> "SOCIS") and left 5 dead anchors.
  //
  // Both are 'throw' rather than 'warn': a warning in a 5-minute build that
  // already prints thousands of lines is not a signal anyone acts on.
  onBrokenAnchors: 'throw',

  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  // English only. Building both locales doubles the output (~800 MB) because
  // Docusaurus emits a complete standalone site per locale — every one of the
  // ~1,150 pages, plus its own copy of the JS/CSS bundles and the static/
  // directory — under build/zh-Hans/.
  //
  // The Chinese source still lives in i18n/zh-Hans/ and is not deleted. To
  // publish it again, add 'zh-Hans' back to `locales` and restore the
  // localeDropdown navbar item below.
  //
  // Do NOT instead build both and upload only build/ minus build/zh-Hans/ —
  // the locale dropdown would link to pages that 404.
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
    localeConfigs: {
      en: {
        label: 'English',
      },
    },
  },

  themes: [
    '@docusaurus/theme-mermaid',
  ],

  plugins: [
    [
      '@docusaurus/plugin-client-redirects',
      {
        // Static-host redirects for renamed doc pages (GitHub Pages can't
        // do server-side redirects). Paths are relative to baseUrl (/docs/).
        redirects: [
          {
            // Renamed in #44470 (Automation Blueprints terminology rebrand)
            from: '/guides/automation-templates',
            to: '/guides/automation-blueprints',
          },
          {
            // Moved when the Plugins subcategory was created under
            // Developer Guide > Extending (docs restructure, July 2026)
            from: '/guides/build-a-socis-plugin',
            to: '/developer-guide/plugins',
          },
          {
            // Users guess these short paths from abbreviated links and hit
            // raw 404s (consumer-onboarding audit finding #1, Aug 2026).
            from: '/quickstart',
            to: '/getting-started/quickstart',
          },
          {
            from: '/installation',
            to: '/getting-started/installation',
          },
        ],
      },
    ],
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',  // Docs at the root of /docs/
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/socisio/socis-agent/edit/main/website/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/socis-agent-banner.png',
    // Search is currently disabled.
    //
    // This block previously carried Hermes Agent's Algolia DocSearch
    // credentials verbatim — the appId and search-only apiKey it carried
    // belong to Nous Research's Algolia application, not ours. The rebrand
    // renamed indexName from 'hermes docs' to 'socis docs' but left the
    // credentials, so DocSearch queried an index that does not exist in that
    // application and the search box silently returned nothing.
    //
    // To re-enable, apply for DocSearch (free for open-source docs) at
    // https://docsearch.algolia.com/apply — Algolia crawls agent.socis.io and
    // issues OUR appId, search-only apiKey and index name. Restore the block
    // with those values. Do not reuse another project's credentials.
    //
    // The alternative is @easyops-cn/docusaurus-search-local, which this site
    // used before: it works with no third-party account, at the cost of a
    // large client-side index every visitor downloads before their first
    // result.
    colorMode: {
      defaultMode: 'dark',
      respectPrefersColorScheme: true,
    },
    docs: {
      sidebar: {
        hideable: true,
        autoCollapseCategories: true,
      },
    },
    navbar: {
      title: 'SOCIS Agent',
      logo: {
        alt: 'SOCIS Agent',
        src: 'img/logo.png',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/skills',
          label: 'Skills',
          position: 'left',
        },
        {
          to: '/download',
          label: 'Download',
          position: 'left',
        },
        {
          href: 'https://github.com/socisio/socis-agent',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            { label: 'Getting Started', to: '/getting-started/quickstart' },
            { label: 'User Guide', to: '/user-guide/cli' },
            { label: 'Developer Guide', to: '/developer-guide/architecture' },
            { label: 'Reference', to: '/reference/cli-commands' },
          ],
        },
        {
          title: 'Community',
          items: [
            { label: 'GitHub Issues', href: 'https://github.com/socisio/socis-agent/issues' },
            { label: 'Skills Hub', href: 'https://agentskills.io' },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'Desktop Download', to: '/download' },
            { label: 'GitHub', href: 'https://github.com/socisio/socis-agent' },
            { label: 'SOCIS', href: 'https://socis.io' },
          ],
        },
      ],
      copyright: `Built by <a href="https://socis.io">SOCIS</a> · MIT License · ${new Date().getFullYear()}`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'yaml', 'json', 'python', 'toml'],
    },
    mermaid: {
      theme: {light: 'neutral', dark: 'dark'},
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
