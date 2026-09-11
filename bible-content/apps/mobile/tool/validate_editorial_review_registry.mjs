import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const contentRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
const registry = JSON.parse(await fs.readFile(path.join(contentRoot, 'editorial-review', 'registry.json'), 'utf8'))
const changeSet = JSON.parse(await fs.readFile(path.join(contentRoot, registry.activeChangeSet), 'utf8'))

assert(registry.format === 'shine-reading-2026-editorial-review-registry', 'registry format')
assert(registry.schemaVersion === 1, 'registry schema')
assert(registry.sourceVersionId === 'RV1909', 'source version')
assert(registry.requiredFullTest === true, 'mandatory full test')
assert(registry.fullTestCommand === 'node bible-content/apps/mobile/tool/smoke_bible_content_flow.mjs', 'full test command')
assert(changeSet.contentVersion >= 1 && changeSet.changes.length > 0, 'active change set')

const ids = new Set()
for (const item of registry.pending) {
  assert(item.status === 'pending-review', `${item.id} status`)
  assert(typeof item.id === 'string' && item.id.length > 0 && !ids.has(item.id), `${item.id} unique id`)
  ids.add(item.id)
  assert(['old-testament', 'new-testament'].includes(item.scope), `${item.id} scope`)
  assert(typeof item.term === 'string' && item.term.length > 0, `${item.id} term`)
  assert(Array.isArray(item.proposedOptions) && item.proposedOptions.length > 0, `${item.id} options`)
  assert(typeof item.reason === 'string' && item.reason.length > 0, `${item.id} reason`)
  assert(Array.isArray(item.references) && item.references.length > 0, `${item.id} references`)
  assert(Array.isArray(item.evidence) && item.evidence.every((entry) => /^https:\/\//.test(entry.url)), `${item.id} evidence`)
}

for (const change of changeSet.changes) {
  assert(typeof change.category === 'string' && change.category.length > 0, 'applied category')
  assert(typeof change.reason === 'string' && change.reason.length > 0, 'applied reason')
}

console.log(JSON.stringify({
  ok: true,
  contentVersion: changeSet.contentVersion,
  appliedRules: changeSet.changes.length,
  pendingTerms: registry.pending.length,
  pendingReferences: registry.pending.reduce((total, item) => total + item.references.length, 0),
  mandatoryFullTest: registry.fullTestCommand,
}, null, 2))

function assert(condition, label) {
  if (!condition) throw new Error(`Editorial review registry validation failed: ${label}`)
}
