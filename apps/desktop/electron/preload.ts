import { contextBridge, ipcRenderer, webFrame, webUtils } from 'electron'

// Which translucency the OS can back. Asked synchronously because the renderer
// needs it before its first paint, and answered by main because deciding it
// needs `os.release()` — a sandboxed preload may only require electron, events,
// timers and url, so importing node:os here throws before contextBridge runs
// and takes the ENTIRE bridge down with it (window.socisDesktop undefined =>
// "Desktop IPC bridge is unavailable"). No reply means no glass, which degrades
// to an ordinary opaque window rather than a page thinned over nothing.
const translucencySupport = ipcRenderer.sendSync('socis:translucency:support')
const hudWindowing = ipcRenderer.sendSync('socis:hud:windowing')
const hudNativeDrag = hudWindowing?.nativeDrag === true
const launchFlags = ipcRenderer.sendSync('socis:launch-flags')

contextBridge.exposeInMainWorld('socisDesktop', {
  glassSupported: translucencySupport?.glass === true,
  translucencySupported: translucencySupport?.translucency === true,
  // Launch-flag fact: the app was started with --local, so the renderer may
  // show the local-models surfaces. Static for the window's lifetime.
  localModelsEnabled: launchFlags?.localModels === true,
  getConnection: profile => ipcRenderer.invoke('socis:connection', profile),
  // Registry-scoped backend resolution: { connectionId, profile } → descriptor.
  getConnectionFor: payload => ipcRenderer.invoke('socis:connection:for', payload),
  getProfileRoutes: profiles => ipcRenderer.invoke('socis:plugin-profile-routes', profiles),
  revalidateConnection: () => ipcRenderer.invoke('socis:connection:revalidate'),
  touchBackend: profile => ipcRenderer.invoke('socis:backend:touch', profile),
  getPoolLimits: () => ipcRenderer.invoke('socis:pool-limits:get'),
  setPoolLimits: limits => ipcRenderer.invoke('socis:pool-limits:set', limits),
  getGatewayWsUrl: profile => ipcRenderer.invoke('socis:gateway:ws-url', profile),
  // Registry-scoped fresh WS URL: { connectionId, profile } → result shape of
  // getGatewayWsUrl, minted against that connection's backend.
  getGatewayWsUrlFor: payload => ipcRenderer.invoke('socis:gateway:ws-url-for', payload),
  // Union agent roster across every registered connection.
  getAgentRoster: () => ipcRenderer.invoke('socis:agents:roster'),
  openSessionWindow: (sessionId, opts) => ipcRenderer.invoke('socis:window:openSession', sessionId, opts),
  openSessionInTerminal: (sessionId, opts) => ipcRenderer.invoke('socis:window:openInTerminal', sessionId, opts),
  openWindow: () => ipcRenderer.invoke('socis:window:openInstance'),
  openBrowserWindow: tabId => ipcRenderer.invoke('socis:window:openBrowser', tabId),
  onBrowserPopoutClosed: callback => {
    const listener = (_event, tabId) => callback(tabId)
    ipcRenderer.on('socis:browser-popout:closed', listener)

    return () => ipcRenderer.removeListener('socis:browser-popout:closed', listener)
  },
  claimAmbientCue: key => ipcRenderer.invoke('socis:ambient:claim', key),
  wakeIndicator: {
    getState: () => ipcRenderer.invoke('socis:wake-indicator:get'),
    setState: state => ipcRenderer.send('socis:wake-indicator:set', state),
    onState: callback => {
      const listener = (_event, state) => callback(state)
      ipcRenderer.on('socis:wake-indicator:state', listener)

      return () => ipcRenderer.removeListener('socis:wake-indicator:state', listener)
    }
  },
  petOverlay: {
    // Main renderer → main process: window lifecycle + drag. `request` is
    // `{ bounds, screen }`; resolves with the screen bounds it actually used.
    open: request => ipcRenderer.invoke('socis:pet-overlay:open', request),
    close: () => ipcRenderer.invoke('socis:pet-overlay:close'),
    setBounds: bounds => ipcRenderer.send('socis:pet-overlay:set-bounds', bounds),
    setIgnoreMouse: ignore => ipcRenderer.send('socis:pet-overlay:ignore-mouse', ignore),
    // Flip the overlay focusable (and focus it) while the composer needs keys.
    setFocusable: focusable => ipcRenderer.send('socis:pet-overlay:set-focusable', focusable),
    // Main renderer → overlay (forwarded by main): push the latest pet state.
    pushState: payload => ipcRenderer.send('socis:pet-overlay:state', payload),
    // Overlay → main renderer (forwarded by main): pop back in / composer submit.
    control: payload => ipcRenderer.send('socis:pet-overlay:control', payload),
    // Overlay subscribes to state pushes.
    onState: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('socis:pet-overlay:state', listener)

      return () => ipcRenderer.removeListener('socis:pet-overlay:state', listener)
    },
    // Main renderer subscribes to overlay control messages.
    onControl: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('socis:pet-overlay:control', listener)

      return () => ipcRenderer.removeListener('socis:pet-overlay:control', listener)
    }
  },
  // HUD mode: the chrome-free floating chat. A full app renderer (own gateway)
  // sized as a floating bar, so it mounts the real composer. Main owns the
  // window; `onChanged` keeps every window's toggle truthful.
  hud: {
    nativeDrag: hudNativeDrag,
    windowing: {
      clientPlacement: hudWindowing?.clientPlacement !== false,
      controlDrag: hudWindowing?.controlDrag === true,
      nativeDrag: hudNativeDrag,
      solid: hudWindowing?.solid === true,
      workspaceTransfer: hudWindowing?.workspaceTransfer === true
    },
    open: request => ipcRenderer.invoke('socis:hud:open', request),
    close: () => ipcRenderer.invoke('socis:hud:close'),
    setIgnoreMouse: ignore => ipcRenderer.send('socis:hud:ignore-mouse', ignore),
    beginMove: () => ipcRenderer.send('socis:hud:begin-move'),
    endMove: () => ipcRenderer.send('socis:hud:end-move'),
    moveBy: delta => ipcRenderer.send('socis:hud:move-by', delta),
    setWorkspaceTransfer: transferring => ipcRenderer.send('socis:hud:workspace-transfer', transferring),
    setBounds: bounds => ipcRenderer.send('socis:hud:set-bounds', bounds),
    resetLayout: () => ipcRenderer.invoke('socis:hud:reset-layout'),
    // Whether the band covers the window below the bar. Main pairs it with the
    // user's translucency setting to decide the native frost (macOS vibrancy /
    // Windows 11 DWM backdrop) — see hudFrostFor.
    setFrost: showing => ipcRenderer.invoke('socis:hud:frost', showing),
    // The HUD tells main which session it is on; main hands that back to the
    // app window when the HUD closes, so the app can re-home onto it.
    setSession: sessionId => ipcRenderer.send('socis:hud:session', sessionId),
    onGoto: callback => {
      const listener = (_event, sessionId) => callback(sessionId)
      ipcRenderer.on('socis:hud:goto', listener)

      return () => ipcRenderer.removeListener('socis:hud:goto', listener)
    },
    onChanged: callback => {
      const listener = (_event, state) => callback(state)
      ipcRenderer.on('socis:hud:changed', listener)

      return () => ipcRenderer.removeListener('socis:hud:changed', listener)
    },
    // Linux only, and silent elsewhere: where the cursor is, in page
    // coordinates, or null when it has left the window. Stands in for the
    // mousemove that `setIgnoreMouseEvents(true, { forward: true })` delivers on
    // macOS and Windows but not here.
    onCursor: callback => {
      const listener = (_event, point) => callback(point)
      ipcRenderer.on('socis:hud:cursor', listener)

      return () => ipcRenderer.removeListener('socis:hud:cursor', listener)
    },
    // Main's game-overlay watch: whether a fullscreen app (a game) is under
    // the HUD, so the renderer can step back to the low-opacity overlay
    // treatment while one owns the screen.
    onGameOverlay: callback => {
      const listener = (_event, state) => callback(state)
      ipcRenderer.on('socis:hud:game-overlay', listener)

      return () => ipcRenderer.removeListener('socis:hud:game-overlay', listener)
    }
  },
  // Quick Entry: the global-hotkey mini composer window. Main owns the OS
  // shortcut + the persisted preference; the quick window only captures text
  // and hands it back, and the primary renderer submits it through the normal
  // prompt path.
  quickEntry: {
    getSettings: () => ipcRenderer.invoke('socis:quick-entry:settings:get'),
    setSettings: patch => ipcRenderer.invoke('socis:quick-entry:settings:set', patch),
    submit: payload => ipcRenderer.send('socis:quick-entry:submit', payload),
    dismiss: () => ipcRenderer.send('socis:quick-entry:dismiss'),
    // Primary renderer → main → quick window: gateway connection state + the
    // recent-session options the target picker offers. Main caches the latest
    // payload so a freshly spawned quick window starts from truth.
    pushState: payload => ipcRenderer.send('socis:quick-entry:state', payload),
    // Quick window subscribes to those pushes.
    onState: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('socis:quick-entry:state', listener)

      return () => ipcRenderer.removeListener('socis:quick-entry:state', listener)
    },
    // Main → primary renderer: a submit captured by the quick window.
    onSubmit: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('socis:quick-entry:submit', listener)

      return () => ipcRenderer.removeListener('socis:quick-entry:submit', listener)
    },
    // Main → quick window: you were just summoned (reset draft + refocus).
    onShown: callback => {
      const listener = () => callback()
      ipcRenderer.on('socis:quick-entry:shown', listener)

      return () => ipcRenderer.removeListener('socis:quick-entry:shown', listener)
    }
  },
  getBootProgress: () => ipcRenderer.invoke('socis:boot-progress:get'),
  getConnectionConfig: profile => ipcRenderer.invoke('socis:connection-config:get', profile),
  saveConnectionConfig: payload => ipcRenderer.invoke('socis:connection-config:save', payload),
  applyConnectionConfig: payload => ipcRenderer.invoke('socis:connection-config:apply', payload),
  testConnectionConfig: payload => ipcRenderer.invoke('socis:connection-config:test', payload),
  // Opt-in OS-keychain encryption for stored gateway secrets (default off —
  // see secret-storage-policy.ts). get never touches the OS keychain.
  getSecretStorageEncryption: () => ipcRenderer.invoke('socis:secret-storage:get'),
  setSecretStorageEncryption: (on: boolean) => ipcRenderer.invoke('socis:secret-storage:set', on),
  // v2 multi-connection registry: named agent sources (local / remote / cloud / ssh).
  connections: {
    list: () => ipcRenderer.invoke('socis:connections:list'),
    save: payload => ipcRenderer.invoke('socis:connections:save', payload),
    remove: id => ipcRenderer.invoke('socis:connections:remove', id),
    setPrimary: id => ipcRenderer.invoke('socis:connections:set-primary', id),
    setLaunchMode: mode => ipcRenderer.invoke('socis:connections:set-launch-mode', mode),
    setLastUsed: id => ipcRenderer.invoke('socis:connections:set-last-used', id),
    test: id => ipcRenderer.invoke('socis:connections:test', id),
    updateManaged: id => ipcRenderer.invoke('socis:connections:update-managed', id),
    // Fan out `socis update` to every eligible registered connection.
    // Optional excludeIds skips rows the caller updates through another path.
    updateAll: options => ipcRenderer.invoke('socis:connections:update-all', options),
    // Registry lifecycle push (main → renderer): a connection was removed or
    // materially edited, so secondaries scoped to it must be disposed (and,
    // for edits, re-dialed at the new target).
    onChanged: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('socis:connections:changed', listener)

      return () => ipcRenderer.removeListener('socis:connections:changed', listener)
    }
  },
  sshConfigHosts: () => ipcRenderer.invoke('socis:ssh-config:hosts'),
  sshResolveHost: host => ipcRenderer.invoke('socis:ssh-config:resolve', host),
  probeConnectionConfig: remoteUrl => ipcRenderer.invoke('socis:connection-config:probe', remoteUrl),
  oauthLoginConnectionConfig: remoteUrl => ipcRenderer.invoke('socis:connection-config:oauth-login', remoteUrl),
  oauthLogoutConnectionConfig: remoteUrl => ipcRenderer.invoke('socis:connection-config:oauth-logout', remoteUrl),
  // SOCIS Cloud: one portal login powers discovery + silent per-agent sign-in
  // (cloud-auto-discovery Phase 3).
  cloud: {
    status: () => ipcRenderer.invoke('socis:cloud:status'),
    login: () => ipcRenderer.invoke('socis:cloud:login'),
    logout: () => ipcRenderer.invoke('socis:cloud:logout'),
    discover: org => ipcRenderer.invoke('socis:cloud:discover', org),
    agentSignIn: dashboardUrl => ipcRenderer.invoke('socis:cloud:agent-sign-in', dashboardUrl)
  },
  profile: {
    get: () => ipcRenderer.invoke('socis:profile:get'),
    remember: name => ipcRenderer.invoke('socis:profile:remember', name),
    set: name => ipcRenderer.invoke('socis:profile:set', name)
  },
  api: request => ipcRenderer.invoke('socis:api', request),
  notify: payload => ipcRenderer.invoke('socis:notify', payload),
  requestMicrophoneAccess: () => ipcRenderer.invoke('socis:requestMicrophoneAccess'),
  readWindowBelow: () => ipcRenderer.invoke('socis:window:readBelow'),
  readFileDataUrl: filePath => ipcRenderer.invoke('socis:readFileDataUrl', filePath),
  readFileDataUrlForAttach: filePath => ipcRenderer.invoke('socis:readFileDataUrlForAttach', filePath),
  dataUrlReadMax: {
    get: () => ipcRenderer.invoke('socis:data-url-read-max:get'),
    set: maxMb => ipcRenderer.invoke('socis:data-url-read-max:set', maxMb)
  },
  readFileText: filePath => ipcRenderer.invoke('socis:readFileText', filePath),
  readPluginSource: (filePath: string) => ipcRenderer.invoke('socis:readPluginSource', filePath),
  selectPaths: options => ipcRenderer.invoke('socis:selectPaths', options),
  selectSavePath: options => ipcRenderer.invoke('socis:selectSavePath', options),
  writeClipboard: text => ipcRenderer.invoke('socis:writeClipboard', text),
  readClipboard: () => ipcRenderer.invoke('socis:readClipboard'),
  saveGatewayFile: payload => ipcRenderer.invoke('socis:saveGatewayFile', payload),
  saveImageFromUrl: url => ipcRenderer.invoke('socis:saveImageFromUrl', url),
  contextMenuEdit: command => ipcRenderer.invoke('socis:context-menu:edit', command),
  contextMenuCopyImage: () => ipcRenderer.invoke('socis:context-menu:copy-image'),
  contextMenuSpellcheck: action => ipcRenderer.invoke('socis:context-menu:spellcheck', action),
  contextMenuGuestAddWord: payload => ipcRenderer.invoke('socis:context-menu:guest-add-word', payload),
  onContextMenuSpellcheck: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('socis:context-menu-spellcheck', listener)

    return () => ipcRenderer.removeListener('socis:context-menu-spellcheck', listener)
  },
  saveImageBuffer: (data, ext, name) => ipcRenderer.invoke('socis:saveImageBuffer', { data, ext, name }),
  capturePreview: payload => ipcRenderer.invoke('socis:capturePreview', payload),
  saveClipboardImage: () => ipcRenderer.invoke('socis:saveClipboardImage'),
  getPathForFile: file => {
    try {
      return webUtils.getPathForFile(file) || ''
    } catch {
      return ''
    }
  },
  normalizePreviewTarget: (target, baseDir) => ipcRenderer.invoke('socis:normalizePreviewTarget', target, baseDir),
  watchPreviewFile: url => ipcRenderer.invoke('socis:watchPreviewFile', url),
  watchDirectory: dir => ipcRenderer.invoke('socis:watchDirectory', dir),
  stopPreviewFileWatch: id => ipcRenderer.invoke('socis:stopPreviewFileWatch', id),
  setActiveWork: payload => ipcRenderer.send('socis:active-work', payload),
  setTitleBarTheme: payload => ipcRenderer.send('socis:titlebar-theme', payload),
  setNativeTheme: mode => ipcRenderer.send('socis:native-theme', mode),
  setTranslucency: payload => ipcRenderer.send('socis:translucency', payload),
  setKeepAwake: on => ipcRenderer.send('socis:keep-awake', on),
  setDisableF12: blocked => ipcRenderer.send('socis:devtools:disable-f12', blocked),
  setPreviewShortcutActive: active => ipcRenderer.send('socis:previewShortcutActive', Boolean(active)),
  openExternal: url => ipcRenderer.invoke('socis:openExternal', url),
  mcpOauth: {
    // One-shot loopback listener for MCP OAuth against remote backends: bind
    // on this machine, hand redirectUri to mcp.servers.oauth.start, then wait
    // for the provider redirect and relay code/state via oauth.callback.
    listen: () => ipcRenderer.invoke('socis:mcp-oauth:listen'),
    wait: (id, timeoutMs) => ipcRenderer.invoke('socis:mcp-oauth:wait', id, timeoutMs),
    cancel: id => ipcRenderer.invoke('socis:mcp-oauth:cancel', id)
  },
  openPreviewInBrowser: url => ipcRenderer.invoke('socis:openPreviewInBrowser', url),
  reachPreviewUrl: url => ipcRenderer.invoke('socis:preview:reach', url),
  setActiveConnectionRoute: route => ipcRenderer.send('socis:connection:active-route', route),
  fetchLinkTitle: url => ipcRenderer.invoke('socis:fetchLinkTitle', url),
  resolveFavicon: url => ipcRenderer.invoke('socis:resolveFavicon', url),
  sanitizeWorkspaceCwd: cwd => ipcRenderer.invoke('socis:workspace:sanitize', cwd),
  settings: {
    getDefaultProjectDir: () => ipcRenderer.invoke('socis:setting:defaultProjectDir:get'),
    setDefaultProjectDir: dir => ipcRenderer.invoke('socis:setting:defaultProjectDir:set', dir),
    pickDefaultProjectDir: () => ipcRenderer.invoke('socis:setting:defaultProjectDir:pick')
  },
  zoom: {
    // Current zoom of this window, as { level, percent }.
    get: () => ipcRenderer.invoke('socis:zoom:get'),
    // Synchronous zoom factor (1 = 100%). Coordinate math needs it in the
    // same tick as the event it converts, so no IPC round-trip here.
    factor: () => webFrame.getZoomFactor(),
    setPercent: percent => ipcRenderer.send('socis:zoom:set-percent', percent),
    // Fires on every zoom change, including the Ctrl/Cmd +/-/0 shortcuts,
    // so the settings UI can stay in sync with the keyboard.
    onChanged: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('socis:zoom:changed', listener)

      return () => ipcRenderer.removeListener('socis:zoom:changed', listener)
    }
  },
  revealLogs: () => ipcRenderer.invoke('socis:logs:reveal'),
  getRecentLogs: () => ipcRenderer.invoke('socis:logs:recent'),
  // Fire-and-forget: persists a renderer error-boundary catch (with component
  // stack) to desktop.log so crashes survive the window (#79428).
  reportRendererError: report => ipcRenderer.send('socis:logs:renderer-error', report),
  readDir: dirPath => ipcRenderer.invoke('socis:fs:readDir', dirPath),
  gitRoot: startPath => ipcRenderer.invoke('socis:fs:gitRoot', startPath),
  revealPath: targetPath => ipcRenderer.invoke('socis:fs:reveal', targetPath),
  openDir: dirPath => ipcRenderer.invoke('socis:fs:openDir', dirPath),
  desktopPluginsRoot: () => ipcRenderer.invoke('socis:fs:desktopPluginsRoot'),
  logsRoot: () => ipcRenderer.invoke('socis:fs:logsRoot'),
  agentPluginsRoot: () => ipcRenderer.invoke('socis:fs:agentPluginsRoot'),
  renamePath: (targetPath, newName) => ipcRenderer.invoke('socis:fs:rename', targetPath, newName),
  writeTextFile: (filePath, content) => ipcRenderer.invoke('socis:fs:writeText', filePath, content),
  trashPath: targetPath => ipcRenderer.invoke('socis:fs:trash', targetPath),
  git: {
    worktreeList: repoPath => ipcRenderer.invoke('socis:git:worktreeList', repoPath),
    worktreeAdd: (repoPath, options) => ipcRenderer.invoke('socis:git:worktreeAdd', repoPath, options),
    worktreeRemove: (repoPath, worktreePath, options) =>
      ipcRenderer.invoke('socis:git:worktreeRemove', repoPath, worktreePath, options),
    branchSwitch: (repoPath, branch) => ipcRenderer.invoke('socis:git:branchSwitch', repoPath, branch),
    branchList: repoPath => ipcRenderer.invoke('socis:git:branchList', repoPath),
    baseBranchList: repoPath => ipcRenderer.invoke('socis:git:baseBranchList', repoPath),
    repoStatus: repoPath => ipcRenderer.invoke('socis:git:repoStatus', repoPath),
    fileDiff: (repoPath, filePath) => ipcRenderer.invoke('socis:git:fileDiff', repoPath, filePath),
    scanRepos: (roots, options) => ipcRenderer.invoke('socis:git:scanRepos', roots, options),
    review: {
      list: (repoPath, scope, baseRef) => ipcRenderer.invoke('socis:git:review:list', repoPath, scope, baseRef),
      diff: (repoPath, filePath, scope, baseRef, staged) =>
        ipcRenderer.invoke('socis:git:review:diff', repoPath, filePath, scope, baseRef, staged),
      stage: (repoPath, filePath) => ipcRenderer.invoke('socis:git:review:stage', repoPath, filePath),
      unstage: (repoPath, filePath) => ipcRenderer.invoke('socis:git:review:unstage', repoPath, filePath),
      revert: (repoPath, filePath) => ipcRenderer.invoke('socis:git:review:revert', repoPath, filePath),
      revParse: (repoPath, ref) => ipcRenderer.invoke('socis:git:review:revParse', repoPath, ref),
      commit: (repoPath, message, push) => ipcRenderer.invoke('socis:git:review:commit', repoPath, message, push),
      commitContext: repoPath => ipcRenderer.invoke('socis:git:review:commitContext', repoPath),
      push: repoPath => ipcRenderer.invoke('socis:git:review:push', repoPath),
      shipInfo: repoPath => ipcRenderer.invoke('socis:git:review:shipInfo', repoPath),
      prList: (repoPath, branches, numbers) =>
        ipcRenderer.invoke('socis:git:review:prList', repoPath, branches, numbers),
      fetchPrComment: (repoPath, url) => ipcRenderer.invoke('socis:git:review:fetchPrComment', repoPath, url),
      createPr: repoPath => ipcRenderer.invoke('socis:git:review:createPr', repoPath)
    }
  },
  terminal: {
    attach: id => ipcRenderer.invoke('socis:terminal:attach', id),
    cwd: id => ipcRenderer.invoke('socis:terminal:cwd', id),
    dispose: id => ipcRenderer.invoke('socis:terminal:dispose', id),
    resize: (id, size) => ipcRenderer.invoke('socis:terminal:resize', id, size),
    start: options => ipcRenderer.invoke('socis:terminal:start', options),
    write: (id, data) => ipcRenderer.invoke('socis:terminal:write', id, data),
    onData: (id, callback) => {
      const channel = `socis:terminal:${id}:data`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)

      return () => ipcRenderer.removeListener(channel, listener)
    },
    onExit: (id, callback) => {
      const channel = `socis:terminal:${id}:exit`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)

      return () => ipcRenderer.removeListener(channel, listener)
    }
  },
  onClosePreviewRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('socis:close-preview-requested', listener)

    return () => ipcRenderer.removeListener('socis:close-preview-requested', listener)
  },
  onPreviewNav: callback => {
    const listener = (_event, command) => callback(command)
    ipcRenderer.on('socis:preview-nav', listener)

    return () => ipcRenderer.removeListener('socis:preview-nav', listener)
  },
  onOpenFolderRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('socis:open-folder-requested', listener)

    return () => ipcRenderer.removeListener('socis:open-folder-requested', listener)
  },
  onOpenUpdatesRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('socis:open-updates', listener)

    return () => ipcRenderer.removeListener('socis:open-updates', listener)
  },
  onDeepLink: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('socis:deep-link', listener)

    return () => ipcRenderer.removeListener('socis:deep-link', listener)
  },
  signalDeepLinkReady: () => ipcRenderer.invoke('socis:deep-link-ready'),
  probePluginRepo: payload => ipcRenderer.invoke('socis:plugin:probe', payload),
  installDesktopPlugin: payload => ipcRenderer.invoke('socis:plugin:installDesktop', payload),
  onWindowStateChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('socis:window-state-changed', listener)

    return () => ipcRenderer.removeListener('socis:window-state-changed', listener)
  },
  onFocusSession: callback => {
    const listener = (_event, sessionId) => callback(sessionId)
    ipcRenderer.on('socis:focus-session', listener)

    return () => ipcRenderer.removeListener('socis:focus-session', listener)
  },
  onNotificationAction: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('socis:notification-action', listener)

    return () => ipcRenderer.removeListener('socis:notification-action', listener)
  },
  onNotificationActivate: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('socis:notification-activate', listener)

    return () => ipcRenderer.removeListener('socis:notification-activate', listener)
  },
  onPreviewFileChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('socis:preview-file-changed', listener)

    return () => ipcRenderer.removeListener('socis:preview-file-changed', listener)
  },
  onBackendExit: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('socis:backend-exit', listener)

    return () => ipcRenderer.removeListener('socis:backend-exit', listener)
  },
  // Soft gateway-mode apply finished tearing down the primary backend. Renderer
  // should wipe session lists + re-dial without a window reload.
  onConnectionApplied: callback => {
    const listener = () => callback()
    ipcRenderer.on('socis:connection:applied', listener)

    return () => ipcRenderer.removeListener('socis:connection:applied', listener)
  },
  onPowerResume: callback => {
    const listener = () => callback()
    ipcRenderer.on('socis:power-resume', listener)

    return () => ipcRenderer.removeListener('socis:power-resume', listener)
  },
  // AC ↔ battery transitions; renderers slow their backstop polls on battery.
  getOnBattery: () => ipcRenderer.invoke('socis:power-battery:get'),
  onBatteryChanged: callback => {
    const listener = (_event, onBattery) => callback(Boolean(onBattery))
    ipcRenderer.on('socis:power-battery', listener)

    return () => ipcRenderer.removeListener('socis:power-battery', listener)
  },
  onBootProgress: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('socis:boot-progress', listener)

    return () => ipcRenderer.removeListener('socis:boot-progress', listener)
  },
  // First-launch bootstrap progress -- emitted by the install.ps1 stage
  // runner in main.ts (apps/desktop/electron/bootstrap-runner.ts).
  // Renderer's install overlay subscribes to live events and queries the
  // current snapshot via getBootstrapState() to recover after a devtools
  // reload mid-bootstrap.
  getBootstrapState: () => ipcRenderer.invoke('socis:bootstrap:get'),
  continueBootstrapLocal: () => ipcRenderer.invoke('socis:bootstrap:continue-local'),
  recycleBackend: profile => ipcRenderer.invoke('socis:backend:recycle', profile),
  resetBootstrap: () => ipcRenderer.invoke('socis:bootstrap:reset'),
  repairBootstrap: () => ipcRenderer.invoke('socis:bootstrap:repair'),
  cancelBootstrap: () => ipcRenderer.invoke('socis:bootstrap:cancel'),
  onBootstrapEvent: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('socis:bootstrap:event', listener)

    return () => ipcRenderer.removeListener('socis:bootstrap:event', listener)
  },
  getVersion: () => ipcRenderer.invoke('socis:version'),
  relaunchApp: () => ipcRenderer.invoke('socis:app:relaunch'),
  getRemoteDisplayReason: () => ipcRenderer.invoke('socis:get-remote-display-reason'),
  uninstall: {
    summary: () => ipcRenderer.invoke('socis:uninstall:summary'),
    run: mode => ipcRenderer.invoke('socis:uninstall:run', { mode })
  },
  updates: {
    check: () => ipcRenderer.invoke('socis:updates:check'),
    apply: opts => ipcRenderer.invoke('socis:updates:apply', opts),
    getBranch: () => ipcRenderer.invoke('socis:updates:branch:get'),
    setBranch: name => ipcRenderer.invoke('socis:updates:branch:set', name),
    onProgress: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('socis:updates:progress', listener)

      return () => ipcRenderer.removeListener('socis:updates:progress', listener)
    }
  },
  themes: {
    fetchMarketplace: id => ipcRenderer.invoke('socis:vscode-theme:fetch', id),
    searchMarketplace: query => ipcRenderer.invoke('socis:vscode-theme:search', query)
  },
  // Find-in-page (Ctrl/Cmd+F): delegates to Electron's
  // webContents.findInPage on the IPC sender's window so a Cmd+F pressed
  // in a secondary session window searches THAT window, not the primary.
  // `onFoundInPage` returns the unsubscribe fn; the renderer wires it via
  // `initFindInPageListener` in store/find-in-page.ts and tears it down
  // when the FindBar unmounts.
  findInPage: (query, options) => ipcRenderer.invoke('socis:find-in-page', query, options),
  stopFindInPage: () => ipcRenderer.invoke('socis:stop-find-in-page'),
  onFoundInPage: callback => {
    const listener = (_event, result) => callback(result)
    ipcRenderer.on('socis:found-in-page', listener)

    return () => ipcRenderer.removeListener('socis:found-in-page', listener)
  },
  // Main-process `before-input-event` forwards Ctrl/Cmd+F here so renderer
  // can open the FindBar even when the GTK compositor has already grabbed
  // the chord at the windowing layer (#81727).
  onOpenFindBarRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('socis:open-find-bar', listener)

    return () => ipcRenderer.removeListener('socis:open-find-bar', listener)
  }
})
