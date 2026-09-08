// Resolve electronDist at runtime (#38673, #47917): electron-builder 26.8.x can
// re-unpack a broken Electron.app; reusing the installed dist dodges that.
// npm workspace hoisting is non-deterministic — require.resolve finds electron
// wherever it landed. Dist present → -c.electronDist=<abs>/dist; absent → let
// electron-builder fetch via @electron/get (electronVersion + ELECTRON_MIRROR).

import fs from "node:fs"
import path from "node:path"
import { spawnSync } from "node:child_process"
import { createRequire } from "node:module"

const require = createRequire(import.meta.url)

/**
 * Fail if devDependencies.electron and build.electronVersion disagree.
 *
 * These are read by different consumers and nothing kept them in step:
 * scripts/rebuild-native.mjs rebuilds native modules against
 * devDependencies.electron, while electron-builder packages against
 * build.electronVersion. They drifted silently — devDependencies said 40.10.6
 * and build said 40.10.2, so a security bump to the former never reached the
 * shipped app, and the build log's `electron=40.10.2` was the only clue.
 *
 * The worse failure is an ABI mismatch: native modules rebuilt for one
 * Electron and packaged with another produce a binary that installs cleanly
 * and crashes on first use of node-pty. That has already cost this project a
 * release cycle once.
 */
function assertElectronVersionsAgree() {
  const pkgPath = path.join(process.cwd(), "package.json")
  let pkg
  try {
    pkg = JSON.parse(fs.readFileSync(pkgPath, "utf8"))
  } catch {
    return // not fatal here; other guards cover a missing/unreadable manifest
  }
  const dev = (pkg.devDependencies?.electron ?? "").replace(/^[\^~]/, "")
  const built = pkg.build?.electronVersion ?? ""
  if (!dev || !built) return
  if (dev !== built) {
    console.error(
      `[run-electron-builder] electron version mismatch:\n` +
        `  devDependencies.electron = ${dev}   (used by rebuild-native.mjs)\n` +
        `  build.electronVersion    = ${built}   (used by electron-builder)\n` +
        `Set both to the same version. A mismatch ships native modules built\n` +
        `for one Electron inside an app running another.`
    )
    process.exit(1)
  }
  console.log(`[run-electron-builder] electron ${dev} (devDeps and build agree)`)
}

function electronDistDir() {
  try {
    return path.join(path.dirname(require.resolve("electron/package.json")), "dist")
  } catch {
    return null
  }
}

function distBinary(dist) {
  if (process.platform === "darwin") {
    return path.join(dist, "Electron.app", "Contents", "MacOS", "Electron")
  }
  if (process.platform === "win32") {
    return path.join(dist, "electron.exe")
  }
  return path.join(dist, "electron")
}

function electronBuilderCli() {
  const pkgJson = require.resolve("electron-builder/package.json")
  const bin = require(pkgJson).bin
  const rel = typeof bin === "string" ? bin : bin["electron-builder"]
  return path.join(path.dirname(pkgJson), rel)
}

// Check this BEFORE resolving electronDist or spawning the builder — a
// mismatch is cheap to detect and expensive to discover after packaging.
assertElectronVersionsAgree()

const dist = electronDistDir()
// Local `socis desktop` builds only ever package (--dir or dist), never
// publish a GitHub release — no CI workflow drives this script. But the npm
// lifecycle env sets CI=1 (so esbuild's postinstall doesn't try interactive
// animations), and electron-builder treats CI=1 as a signal to implicitly
// resolve a publish target. That resolution reads <projectDir>/.git/config
// directly — projectDir here is apps/desktop, which has no .git of its own
// (only the repo root does) and no "repository" field in its package.json —
// so it fails with "Cannot detect repository by .git/config". Pin publish to
// "never" so electron-builder skips that lookup entirely.
const args = ["--publish", "never"]
if (dist && fs.existsSync(distBinary(dist))) {
  args.push(`-c.electronDist=${dist}`)
} else {
  console.warn(
    "[run-electron-builder] no local electron dist; electron-builder will fetch " +
      "via @electron/get (electronVersion + ELECTRON_MIRROR)."
  )
}
args.push(...process.argv.slice(2))

const result = spawnSync(process.execPath, [electronBuilderCli(), ...args], {
  stdio: "inherit",
})
if (result.error) {
  console.error(`[run-electron-builder] spawn failed: ${result.error.message}`)
  process.exit(1)
}
process.exit(result.status == null ? 1 : result.status)
