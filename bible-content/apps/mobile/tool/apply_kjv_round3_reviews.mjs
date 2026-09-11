import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'
import zlib from 'node:zlib'
import { fileURLToPath } from 'node:url'

const contentRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
const mobileRoot = path.join(contentRoot, 'apps', 'mobile')
const corpusRoot = path.join(mobileRoot, 'assets', 'bibles', 'kjv')
const directionRoot = path.join(mobileRoot, 'assets', 'bible_direction', 'kjv')
const reviewsRoot = path.join(contentRoot, 'editorial-review', 'kjv-source')
const reportNames = [
  'KJV_ROUND2_RARE_WORDS_REVIEW_2026-09-04.json',
  'KJV_ROUND2_PRIORITY_REVIEW_2026-09-04.json',
]

const reports = await Promise.all(reportNames.map((name) => readJson(path.join(reviewsRoot, name))))
const proposals = reports.flatMap((report) => report.records).filter((record) => record.disposition === 'proposed-edit')
const byBook = Map.groupBy(proposals, (record) => record.reference.split('.')[0])
let added = 0

for (const [book, records] of byBook) {
  const directionPath = await findDirection(book)
  const direction = await readJson(directionPath)
  for (const record of records) {
    const [, chapterText, verseText] = record.reference.split('.')
    const chapter = Number(chapterText)
    const verse = Number(verseText)
    let patch = direction.verses.find((entry) => entry.chapter === chapter && entry.verse === verse)
    if (!patch) {
      patch = { chapter, verse, sourceTextSha256: record.sourceTextSha256, edits: [] }
      direction.verses.push(patch)
    }
    if (patch.sourceTextSha256 !== record.sourceTextSha256) throw new Error(`Source hash mismatch ${record.reference}`)
    const edit = {
      startOffset: record.startOffset,
      endOffset: record.endOffset,
      expected: record.expected,
      replacement: record.proposedReplacement,
      category: record.category,
      reason: record.reason,
      evidence: [{ label: 'Reviewed lexical evidence', url: record.evidenceUrl }],
    }
    const exact = patch.edits.find((candidate) => candidate.startOffset === edit.startOffset && candidate.endOffset === edit.endOffset)
    if (exact) {
      if (exact.expected !== edit.expected || exact.replacement !== edit.replacement) throw new Error(`Conflicting edit ${record.reference}`)
      continue
    }
    if (patch.edits.some((candidate) => edit.startOffset < candidate.endOffset && edit.endOffset > candidate.startOffset)) {
      throw new Error(`Overlapping edit ${record.reference}`)
    }
    patch.edits.push(edit)
    patch.edits.sort((left, right) => left.startOffset - right.startOffset)
    added += 1
  }
  direction.verses.sort((left, right) => left.chapter - right.chapter || left.verse - right.verse)
  direction.editorialStatus = 'approved-minimal-comprehension-v3'
  direction.ownerReview = { contentVersion: 3, review: 'KJV round 3 complete-verse review', requiredFullTest: true }
  await writeJson(directionPath, direction)
}

const packageSourcePath = path.join(directionRoot, 'reading_2026.package-source.json')
const packageSource = await readJson(packageSourcePath)
packageSource.contentVersion = 3
packageSource.generatedAt = '2026-09-10T00:00:00.000Z'
packageSource.editorialPolicy.version = 3
await writeJson(packageSourcePath, packageSource)

const manifest = await readJson(path.join(corpusRoot, 'manifest.json'))
const corpusBookFiles = (await fs.readdir(path.join(corpusRoot, 'books'))).filter((name) => name.endsWith('.json'))
const corpusBooksByCode = new Map()
for (const name of corpusBookFiles) {
  const book = await readJson(path.join(corpusRoot, 'books', name))
  corpusBooksByCode.set(book.book, book)
}
const orderByBook = new Map([...corpusBooksByCode].map(([code, book]) => [code, book.order]))
const directionFiles = (await fs.readdir(path.join(directionRoot, 'books'))).filter((name) => name.endsWith('.json'))
const books = await Promise.all(directionFiles.map((name) => readJson(path.join(directionRoot, 'books', name))))
books.sort((left, right) => orderByBook.get(left.book) - orderByBook.get(right.book))
if (books.length !== 66) throw new Error(`Expected 66 KJV books, received ${books.length}`)
const payload = {
  books,
  contentVersion: 3,
  editorialPolicy: packageSource.editorialPolicy,
  filterId: packageSource.filterId,
  format: 'shine-reading-filter-package',
  normalizationId: packageSource.normalizationId,
  schemaVersion: 1,
  sourceCorpusSha256: packageSource.sourceCorpusSha256,
  sourceVersionId: 'KJV',
}
const raw = Buffer.from(canonicalJson(payload), 'utf8')
const compressed = zlib.gzipSync(raw, { level: 9, mtime: 0 })
const packagesRoot = path.join(directionRoot, 'packages')
await fs.mkdir(packagesRoot, { recursive: true })
const packagePath = path.join(packagesRoot, 'reading_2026.kjv.v1.package.json.gz')
await fs.writeFile(packagePath, compressed)
const coverage = {
  expectedBookCount: 66,
  includedBookCount: 66,
  changedVerseCount: books.reduce((sum, book) => sum + book.verses.length, 0),
  editCount: books.reduce((sum, book) => sum + book.verses.reduce((subtotal, verse) => subtotal + verse.edits.length, 0), 0),
}
const outputManifest = {
  format: 'shine-reading-filter-manifest', filterId: packageSource.filterId, schemaVersion: 1,
  contentVersion: 3, sourceVersionId: 'KJV', sourceCorpusSha256: packageSource.sourceCorpusSha256,
  normalizationId: packageSource.normalizationId, contentSha256: sha256(compressed), sizeBytes: compressed.length,
  expandedSizeBytes: raw.length, mimeType: 'application/vnd.shine.reading-filter+gzip',
  generatedAt: '2026-09-10', editorialPolicy: packageSource.editorialPolicy, coverage,
  books: books.map((book) => ({
    id: book.book, order: orderByBook.get(book.book),
    sourceFile: directionFiles.find((name) => name.startsWith(book.book.toLowerCase())) ?? null,
    sourceContentSha256: book.sourceContentSha256,
    payloadSha256: sha256(Buffer.from(canonicalJson(book), 'utf8')),
    changedVerseCount: book.verses.length,
    editCount: book.verses.reduce((sum, verse) => sum + verse.edits.length, 0),
  })),
}
await writeJson(path.join(packagesRoot, 'reading_2026.kjv.v1.manifest.json'), outputManifest)

const pendingDefinitions = [
  ['suffer', ['allow', 'endure'], 'The KJV verb can mean permit or endure.'],
  ['suffered', ['allowed', 'endured'], 'The past form also changes meaning by context.'],
  ['peculiar', ['special possession', 'distinctive'], 'Often denotes belonging, not oddness.'],
  ['meat', ['food', 'meat'], 'It often means food generally, but not in every occurrence.'],
  ['corn', ['grain'], 'The historical word is grain rather than modern maize in biblical settings.'],
  ['coast', ['region', 'border', 'coast'], 'Geography determines the correct modern term.'],
  ['coasts', ['regions', 'borders', 'coasts'], 'The plural has the same geographic ambiguity.'],
  ['bowels', ['inner being', 'compassion', 'internal organs'], 'Literal and figurative senses must remain distinct.'],
  ['let', ['allow', 'hinder'], 'This false friend can express opposite actions.'],
  ['charity', ['love'], 'The theological context and rhetorical force require per-verse review.'],
  ['peradventure', ['perhaps'], 'Candidate is clear but every occurrence remains reserved for the next reviewed batch.'],
  ['haply', ['perhaps', 'by chance'], 'The adverb changes nuance by context.'],
  ['betwixt', ['between'], 'Candidate is reserved until its complete phrase is reviewed.'],
  ['whence', ['from where'], 'Question, source, and causal uses require separate phrasing.'],
  ['hither', ['here', 'to this place'], 'Movement and idiom determine the natural wording.'],
  ['thither', ['there', 'to that place'], 'Movement and idiom determine the natural wording.'],
  ['whither', ['where', 'to where'], 'Question and relative-clause uses differ.'],
  ['raiment', ['clothing', 'garments'], 'Narrative and ceremonial contexts may prefer different terms.'],
  ['froward', ['perverse', 'stubborn', 'contrary'], 'The moral nuance varies by passage.'],
  ['emerods', ['tumors', 'swellings'], 'The historical medical diagnosis is disputed.'],
  ['thee', ['you'], 'The pronoun system encodes number and grammatical role and cannot be replaced in isolation.'],
  ['thou', ['you'], 'The pronoun system must be modernized as a coordinated grammar layer, if ever.'],
  ['thy', ['your'], 'Possessive grammar must be changed consistently with the full pronoun system.'],
  ['thine', ['yours', 'your'], 'Its form depends on grammatical position.'],
  ['ye', ['you'], 'It carries plural information that a careless global replacement can erase.'],
  ['hath', ['has'], 'Verb agreement depends on the coordinated pronoun system.'],
  ['doth', ['does'], 'Verb agreement depends on the coordinated pronoun system.'],
  ['shalt', ['shall', 'will'], 'Modal force and agreement require contextual review.'],
  ['wilt', ['will'], 'Verb agreement depends on the coordinated pronoun system.'],
]
const corpusBooks = [...corpusBooksByCode.values()]
const pending = pendingDefinitions.map(([term, proposedOptions, reason]) => ({
  id: `kjv-${term}`, status: 'pending-review', scope: 'old-and-new-testament', term, proposedOptions, reason,
  references: corpusBooks.flatMap((book) => book.chapters.flatMap((chapter) => chapter.verses
    .filter((verse) => new RegExp(`(?<![\\p{L}\\p{M}])${term}(?![\\p{L}\\p{M}])`, 'iu').test(normalizeKjv(verse.text)))
    .map((verse) => ({ book: book.book, chapter: chapter.chapter, verse: verse.verse })))),
  evidence: [{ label: 'KJV lexical and complete-verse review', url: 'https://www.merriam-webster.com/' }],
})).filter((entry) => entry.references.length > 0)
await writeJson(path.join(contentRoot, 'editorial-review', 'registry.kjv.json'), {
  format: 'shine-reading-2026-editorial-review-registry', schemaVersion: 1,
  updatedAt: '2026-09-10T00:00:00.000Z', sourceVersionId: 'KJV', activeContentVersion: 3,
  requiredFullTest: true, fullTestCommand: 'node bible-content/apps/mobile/tool/verify_kjv_reading_2026.mjs',
  applied: proposals.map((record) => ({ reference: record.reference, expected: record.expected, replacement: record.proposedReplacement, category: record.category, reason: record.reason, evidenceUrl: record.evidenceUrl })),
  pending,
})

console.log(JSON.stringify({ added, applied: proposals.length, pendingTerms: pending.length, pendingReferences: pending.reduce((sum, item) => sum + item.references.length, 0), ...coverage, contentSha256: outputManifest.contentSha256 }, null, 2))

async function findDirection(book) {
  const names = (await fs.readdir(path.join(directionRoot, 'books'))).filter((name) => name.endsWith('.json'))
  for (const name of names) {
    const candidate = path.join(directionRoot, 'books', name)
    const document = await readJson(candidate)
    if (document.book === book) return candidate
  }
  throw new Error(`Missing KJV direction ${book}`)
}
function normalizeKjv(value) {
  const normalized = String(value ?? '').replace(/\\\+(?:w|add|nd)\*?\s*/giu, '').replace(/\s+([,.;:!?])/gu, '$1').replace(/\s+/gu, ' ').trim()
  if (/\\\+[a-z0-9-]+\*?/iu.test(normalized)) throw new Error('Unsupported KJV marker')
  return normalized
}
function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(',')}}`
  return JSON.stringify(value)
}
function sha256(value) { return crypto.createHash('sha256').update(value).digest('hex') }
async function readJson(filePath) { return JSON.parse(await fs.readFile(filePath, 'utf8')) }
async function writeJson(filePath, value) { await fs.mkdir(path.dirname(filePath), { recursive: true }); await fs.writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8') }
