import React, { useEffect, useState } from "react";
import Layout from "@theme/Layout";
import styles from "./styles.module.css";

const REPO = "socisio/socis-agent";
const RELEASES_URL = `https://github.com/${REPO}/releases`;
const API_URL = `https://api.github.com/repos/${REPO}/releases/latest`;

interface Asset {
  name: string;
  browser_download_url: string;
  size: number;
}

interface Release {
  tag_name: string;
  html_url: string;
  published_at: string;
  assets: Asset[];
}

type PlatformKey = "mac" | "win" | "linux";

interface PlatformSpec {
  key: PlatformKey;
  label: string;
  /** Order matters: the first match becomes the primary download button. */
  patterns: RegExp[];
  hint: string;
}

const PLATFORMS: PlatformSpec[] = [
  {
    key: "mac",
    label: "macOS",
    patterns: [/\.dmg$/i, /mac.*\.zip$/i],
    hint: "Apple Silicon and Intel builds are published separately — pick the one matching your Mac.",
  },
  {
    key: "win",
    label: "Windows",
    patterns: [/\.exe$/i, /\.msi$/i],
    hint: "The .exe is the standard installer; the .msi suits managed/enterprise deployment.",
  },
  {
    key: "linux",
    label: "Linux",
    patterns: [/\.AppImage$/i, /\.deb$/i, /\.rpm$/i],
    hint: "AppImage runs anywhere; .deb for Debian/Ubuntu, .rpm for Fedora/RHEL.",
  },
];

function formatSize(bytes: number): string {
  if (!bytes) return "";
  const mb = bytes / (1024 * 1024);
  return mb >= 1 ? `${mb.toFixed(1)} MB` : `${(bytes / 1024).toFixed(0)} KB`;
}

/** Guess the visitor's platform so the right card can lead. */
function detectPlatform(): PlatformKey | null {
  if (typeof navigator === "undefined") return null;
  const ua = navigator.userAgent;
  if (/Mac/i.test(ua)) return "mac";
  if (/Win/i.test(ua)) return "win";
  if (/Linux|X11/i.test(ua)) return "linux";
  return null;
}

export default function Download(): JSX.Element {
  const [release, setRelease] = useState<Release | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [detected, setDetected] = useState<PlatformKey | null>(null);

  useEffect(() => {
    setDetected(detectPlatform());

    let cancelled = false;
    fetch(API_URL, { headers: { Accept: "application/vnd.github+json" } })
      .then((r) => {
        // 404 is the expected response before the first release is published.
        if (r.status === 404) throw new Error("no-release");
        if (!r.ok) throw new Error(`GitHub API returned ${r.status}`);
        return r.json();
      })
      .then((data: Release) => {
        if (!cancelled) {
          setRelease(data);
          setLoading(false);
        }
      })
      .catch((e: Error) => {
        if (!cancelled) {
          setError(e.message);
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const assetsFor = (spec: PlatformSpec): Asset[] => {
    if (!release) return [];
    return spec.patterns.flatMap((re) =>
      release.assets.filter(
        (a) => re.test(a.name) && !a.name.endsWith(".blockmap"),
      ),
    );
  };

  return (
    <Layout
      title="Download"
      description="Download SOCIS Agent Desktop for macOS, Windows, and Linux."
    >
      <main className={styles.page}>
        <header className={styles.header}>
          <h1 className={styles.title}>SOCIS Agent Desktop</h1>
          <p className={styles.subtitle}>
            The self-improving AI agent, as a native desktop app.
          </p>
          {release && (
            <p className={styles.version}>
              Latest release{" "}
              <a href={release.html_url} target="_blank" rel="noreferrer">
                {release.tag_name}
              </a>
            </p>
          )}
        </header>

        {loading && <p className={styles.status}>Loading latest release…</p>}

        {error === "no-release" && (
          <div className={styles.notice}>
            <p>
              No desktop release has been published yet. You can still install
              the CLI, which includes the desktop app:
            </p>
            <pre className={styles.code}>
              curl -fsSL https://agent.socis.io/install.sh | bash
            </pre>
            <p>
              Then run <code>socis desktop</code> to build and launch it
              locally.
            </p>
          </div>
        )}

        {error && error !== "no-release" && (
          <div className={styles.notice}>
            <p>
              Couldn&apos;t reach the GitHub API ({error}). You can browse
              releases directly:
            </p>
            <p>
              <a href={RELEASES_URL} target="_blank" rel="noreferrer">
                {RELEASES_URL}
              </a>
            </p>
          </div>
        )}

        {release && (
          <div className={styles.grid}>
            {PLATFORMS.map((spec) => {
              const assets = assetsFor(spec);
              const isDetected = detected === spec.key;
              return (
                <section
                  key={spec.key}
                  className={`${styles.card} ${isDetected ? styles.cardDetected : ""}`}
                >
                  <h2 className={styles.cardTitle}>
                    {spec.label}
                    {isDetected && (
                      <span className={styles.badge}>Your system</span>
                    )}
                  </h2>

                  {assets.length === 0 ? (
                    <p className={styles.empty}>
                      No build published for this platform in {release.tag_name}.
                    </p>
                  ) : (
                    <ul className={styles.assetList}>
                      {assets.map((a) => (
                        <li key={a.name}>
                          <a
                            className={styles.assetLink}
                            href={a.browser_download_url}
                          >
                            {a.name}
                          </a>
                          <span className={styles.assetSize}>
                            {formatSize(a.size)}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}

                  <p className={styles.hint}>{spec.hint}</p>
                </section>
              );
            })}
          </div>
        )}

        <footer className={styles.footer}>
          <p>
            Builds are unsigned. macOS may show an &ldquo;unidentified
            developer&rdquo; warning (right-click → Open to bypass) and Windows
            may show a SmartScreen prompt (More info → Run anyway).
          </p>
          <p>
            Prefer the terminal? See the{" "}
            <a href="/docs/getting-started/quickstart">CLI quickstart</a>. All
            releases are listed on{" "}
            <a href={RELEASES_URL} target="_blank" rel="noreferrer">
              GitHub
            </a>
            .
          </p>
        </footer>
      </main>
    </Layout>
  );
}
