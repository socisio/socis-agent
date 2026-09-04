import { describe, expect, it } from 'vitest'

import {
  normalizeSOCISOpenString,
  pathFromSOCISDeepLink,
  pathFromOpenDeepLink,
  resolveSOCISOpenPath
} from './socis-open-target'

describe('normalizeSOCISOpenString', () => {
  it('accepts hash-router paths and strips a leading hash', () => {
    expect(normalizeSOCISOpenString('/index-network/intent/1')).toBe('/index-network/intent/1')
    expect(normalizeSOCISOpenString('#/index-network/intent/1')).toBe('/index-network/intent/1')
  })

  it('maps plugin-scoped socis:// deep links to the same path', () => {
    expect(normalizeSOCISOpenString('socis://index-network/intent/1')).toBe('/index-network/intent/1')
    expect(normalizeSOCISOpenString('socis://index-network/intent/1?focus=true')).toBe(
      '/index-network/intent/1?focus=true'
    )
  })

  it('maps socis://open/… deep links by stripping the open host', () => {
    expect(normalizeSOCISOpenString('socis://open/index-network/intent/1')).toBe('/index-network/intent/1')
    expect(normalizeSOCISOpenString('socis://open/settings/plugins')).toBe('/settings/plugins')
  })

  it('rejects reserved socis kinds and unsafe paths', () => {
    expect(normalizeSOCISOpenString('socis://blueprint/morning-brief')).toBeNull()
    expect(normalizeSOCISOpenString('socis://plugin/install')).toBeNull()
    expect(normalizeSOCISOpenString('https://example.com/x')).toBeNull()
    expect(normalizeSOCISOpenString('/../etc/passwd')).toBeNull()
    expect(normalizeSOCISOpenString('index-network')).toBeNull()
  })
})

describe('resolveSOCISOpenPath', () => {
  it('merges structured path + params', () => {
    expect(resolveSOCISOpenPath({ path: '/index-network/intent/1', params: { focus: 'true' } })).toBe(
      '/index-network/intent/1?focus=true'
    )
  })

  it('resolves href the same as a bare string', () => {
    expect(resolveSOCISOpenPath({ href: 'socis://index-network/intent/1' })).toBe('/index-network/intent/1')
  })
})

describe('pathFromSOCISDeepLink', () => {
  it('builds the navigate path from a plugin-scoped deep-link payload', () => {
    expect(pathFromSOCISDeepLink('index-network', 'intent/1')).toBe('/index-network/intent/1')
  })

  it('builds the navigate path from socis://open/… payloads', () => {
    expect(pathFromOpenDeepLink('index-network/intent/1')).toBe('/index-network/intent/1')
    expect(pathFromSOCISDeepLink('open', 'agent/42')).toBe('/agent/42')
  })

  it('ignores reserved kinds', () => {
    expect(pathFromSOCISDeepLink('blueprint', 'morning-brief')).toBeNull()
    expect(pathFromSOCISDeepLink('plugin', 'install')).toBeNull()
  })
})
