import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'
import zlib from 'node:zlib'
import { fileURLToPath } from 'node:url'

const contentRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
const packageRoot = path.join(contentRoot, 'apps', 'mobile', 'assets', 'bible_direction', 'kjv', 'packages')
const packagePath = path.join(packageRoot, 'reading_2026.kjv.v1.package.json.gz')
const manifest = JSON.parse(await fs.readFile(path.join(packageRoot, 'reading_2026.kjv.v1.manifest.json'), 'utf8'))
const compressed = await fs.readFile(packagePath)
const payload = JSON.parse(zlib.gunzipSync(compressed).toString('utf8'))
const registry = JSON.parse(await fs.readFile(path.join(contentRoot, 'editorial-review', 'registry.kjv.json'), 'utf8'))
const packageSource = JSON.parse(await fs.readFile(path.join(contentRoot, 'apps', 'mobile', 'assets', 'bible_direction', 'kjv', 'reading_2026.package-source.json'), 'utf8'))

assert(payload.filterId === 'KJV-READING-2026', 'filter id')
assert(payload.sourceVersionId === 'KJV', 'source id')
assert(payload.contentVersion === packageSource.contentVersion && manifest.contentVersion === packageSource.contentVersion, 'content version')
assert(payload.books.length === 66, '66 books')
assert(crypto.createHash('sha256').update(compressed).digest('hex') === manifest.contentSha256, 'package hash')
assert(manifest.sourceCorpusSha256 === '4e2c28113d053e64dacef2792a8d3bcfb32367320f549ef2c2f03b3122902939', 'immutable corpus')
assert(registry.requiredFullTest === true && registry.activeContentVersion === packageSource.contentVersion && registry.applied.length >= 77, 'mandatory registry')
assert(registry.pending.every((entry) => entry.reason && entry.references.length && entry.evidence.length), 'pending records')
for (const book of payload.books) {
  for (const verse of book.verses) {
    const ordered = [...verse.edits].sort((left, right) => left.startOffset - right.startOffset)
    for (let index = 1; index < ordered.length; index += 1) assert(ordered[index].startOffset >= ordered[index - 1].endOffset, `overlap ${book.book}.${verse.chapter}.${verse.verse}`)
    assert(verse.edits.every((edit) => edit.reason && edit.category), `traceability ${book.book}.${verse.chapter}.${verse.verse}`)
  }
}
console.log(JSON.stringify({ ok: true, contentVersion: packageSource.contentVersion, books: 66, editCount: manifest.coverage.editCount, appliedReviews: registry.applied.length, pendingTerms: registry.pending.length, contentSha256: manifest.contentSha256 }, null, 2))
function assert(condition, label) { if (!condition) throw new Error(`KJV Reading 2026 verification failed: ${label}`) }
