/**
 * after-pack.mjs — electron-builder afterPack hook.
 *
 * Stamps the SOCIS icon + identity onto the packed Windows SOCIS.exe via
 * rcedit (delegated to set-exe-identity.mjs). This runs for EVERY packed build
 * — first install, `socis desktop`, the installer's --update rebuild, and a
 * dev's manual `npm run pack` — so the branded exe can never silently revert
 * to the stock "Electron" icon/name (the bug when the stamp lived only in
 * install.ps1, which the update path doesn't use).
 *
 * On macOS it also applies an ad-hoc code signature. Apple Silicon REFUSES to
 * launch an arm64 binary with no signature at all — Finder reports it as
 * `"SOCIS" is damaged and can't be opened`, which reads like a corrupt
 * download but is purely a missing signature. `socis desktop` already ad-hoc
 * signs (socis_cli/main.py), but CI release builds call electron-builder
 * directly with CSC_IDENTITY_AUTO_DISCOVERY=false and never did — so every
 * published .dmg was unopenable on Apple Silicon. Doing it here covers every
 * packing path, exactly like the Windows stamp above.
 *
 * Ad-hoc is not Developer ID: users still see Gatekeeper's "unidentified
 * developer" prompt on first open (right-click -> Open). It only makes the app
 * launchable at all. Set CSC_LINK/CSC_KEY_PASSWORD for real signing.
 *
 * Best-effort throughout: a stamp or signature failure must never fail an
 * otherwise-good build, so we log and resolve rather than throw.
 *
 * electron-builder passes a context with:
 *   - electronPlatformName: 'win32' | 'darwin' | 'linux'
 *   - appOutDir:            the unpacked app directory for this target
 *   - packager.appInfo.productFilename: the exe basename (e.g. 'SOCIS')
 */

import { execFile } from 'node:child_process'
import { existsSync, readdirSync } from 'node:fs'
import path from 'node:path'
import { promisify } from 'node:util'

import { Arch } from 'electron-builder'

import { stampExeIdentity } from './set-exe-identity.mjs'

const execFileAsync = promisify(execFile)

/**
 * Ad-hoc sign the .app so Apple Silicon will run it.
 *
 * --deep is required: every nested helper, framework and .node binary needs a
 * signature too, and an unsigned nested Mach-O invalidates the outer bundle.
 * It signs inside-out, so the outer bundle seals last.
 *
 * Skipped when a real identity is configured — re-signing ad-hoc on top of a
 * Developer ID signature would strip it.
 */
async function adhocSignMac(appPath) {
  if (process.env.CSC_LINK || process.env.CSC_NAME) {
    console.log('[after-pack] real signing identity present; skipping ad-hoc sign')
    return
  }
  await execFileAsync('codesign', ['--force', '--deep', '--sign', '-', appPath])
  // Verify rather than assume: a silent codesign failure here ships a .dmg
  // that no Apple Silicon user can open.
  await execFileAsync('codesign', ['--verify', '--deep', '--strict', appPath])
  console.log(`[after-pack] ad-hoc signed ${path.basename(appPath)}`)
}


/**
 * Fail the build if the PACKED app carries a node-pty prebuild for the wrong
 * architecture.
 *
 * This has to run here, not in stage-native-deps.mjs. That script rmSync's its
 * destination before staging, so by the time it validates, only the arch it
 * just wrote can be present — the check is vacuous. The damage happens later:
 * if two arches are packed from the same shared dist/ directory, one target's
 * staging can land in the other's bundle. Only the packed output shows it.
 *
 * The symptom this prevents shipping:
 *   Error: Failed to load native module: pty.node
 *   Cannot find module './prebuilds/darwin-arm64//pty.node'
 * — an app that builds, installs, launches, and then dies.
 */
function assertPrebuildArch(context) {
  const platform = context.electronPlatformName
  const arch = typeof context.arch === 'number' ? Arch[context.arch] : undefined
  if (!platform || !arch || arch === 'universal') return

  // electron-builder unpacks per asarUnpack; node-pty lands under app.asar.unpacked.
  const roots = [
    path.join(context.appOutDir, `${context.packager?.appInfo?.productFilename || 'SOCIS'}.app`,
              'Contents', 'Resources', 'app.asar.unpacked', 'dist', 'node_modules', 'node-pty'),
    path.join(context.appOutDir, 'resources', 'app.asar.unpacked', 'dist', 'node_modules', 'node-pty')
  ]
  const root = roots.find((r) => existsSync(path.join(r, 'prebuilds')))
  if (!root) return  // no prebuilds dir — build/Release path, nothing to compare

  const expected = `${platform}-${arch}`
  const found = readdirSync(path.join(root, 'prebuilds'), { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
  const strays = found.filter((n) => n !== expected)
  if (strays.length > 0) {
    throw new Error(
      `[after-pack] packed app contains node-pty prebuilds for the WRONG arch.\n` +
      `  target: ${expected}\n  found:  ${found.join(', ')}\n` +
      `This ships an app that crashes on launch. Build each arch in its own ` +
      `electron-builder invocation instead of passing several --arch flags.`
    )
  }
  console.log(`[after-pack] verified node-pty prebuild matches ${expected}`)
}

export default async function afterPack(context) {
  assertPrebuildArch(context)

  if (context.electronPlatformName === 'darwin') {
    const productName = context.packager?.appInfo?.productFilename || 'SOCIS'
    const app = path.join(context.appOutDir, `${productName}.app`)
    try {
      await adhocSignMac(app)
    } catch (err) {
      console.warn(
        `[after-pack] ad-hoc signing failed (${err.message}); the .app will NOT ` +
        'launch on Apple Silicon ("is damaged" in Finder)'
      )
    }
    return
  }

  if (context.electronPlatformName !== 'win32') {
    return
  }

  const productName = context.packager?.appInfo?.productFilename || 'SOCIS'
  const exe = path.join(context.appOutDir, `${productName}.exe`)
  const desktopRoot = path.resolve(import.meta.dirname, '..')

  try {
    await stampExeIdentity(exe, desktopRoot)
  } catch (err) {
    // Never fail the build over a cosmetic stamp.
    console.warn(`[after-pack] exe identity stamp failed (${err.message}); SOCIS.exe keeps the stock Electron icon`)
  }
}
