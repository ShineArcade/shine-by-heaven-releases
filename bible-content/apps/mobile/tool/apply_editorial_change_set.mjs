import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const contentRoot = path.resolve(scriptDir, '..', '..', '..')
const changeSetPath = path.resolve(
  readArgument('--change-set') ?? await latestChangeSetPath(),
)

const changeSet = await readJson(changeSetPath)
assert(changeSet.format === 'shine-reading-2026-editorial-change-set', 'format')
assert(changeSet.schemaVersion === 1, 'schemaVersion')
assert(changeSet.sourceVersionId === 'RV1909', 'sourceVersionId')
assert(changeSet.filterId === 'RV1909-LECTURA-2026', 'filterId')
assert(Number.isSafeInteger(changeSet.contentVersion), 'contentVersion')
assert(Array.isArray(changeSet.changes) && changeSet.changes.length > 0, 'changes')

const changesByBook = Map.groupBy(changeSet.changes, (change) => change.book)
for (const [bookId, changes] of changesByBook) {
  assert(/^[A-Z0-9]{3}$/.test(bookId), `book ${bookId}`)
  const corpusPath = path.join(
    contentRoot,
    'apps',
    'mobile',
    'assets',
    'bibles',
    'rv1909',
    'books',
    `${bookId}.json`,
  )
  const directionRoot = path.join(
    contentRoot,
    'apps',
    'mobile',
    'assets',
    'bible_direction',
  )
  const directionName = (await fs.readdir(directionRoot)).find((name) =>
    name.endsWith('_reading_2026.rv1909.v1.json') &&
    name.toLowerCase().startsWith(bookNamePrefix(bookId)),
  )
  assert(directionName, `direction file ${bookId}`)
  const corpus = await readJson(corpusPath)
  const directionPath = path.join(directionRoot, directionName)
  const direction = await readJson(directionPath)
  assert(direction.book === bookId, `direction book ${bookId}`)

  for (const change of changes) {
    validateChange(change)
    const chapter = corpus.chapters.find((entry) => entry.chapter === change.chapter)
    const verse = chapter?.verses.find((entry) => entry.verse === change.verse)
    assert(verse, `${bookId} ${change.chapter}:${change.verse}`)
    const matches = allOffsets(verse.text, change.expected)
    assert(matches.length === 1, `${bookId} ${change.chapter}:${change.verse} expected text`)
    const edit = {
      startOffset: matches[0],
      endOffset: matches[0] + change.expected.length,
      expected: change.expected,
      replacement: change.replacement,
      category: change.category,
      reason: change.reason,
    }
    let patch = direction.verses.find(
      (entry) => entry.chapter === change.chapter && entry.verse === change.verse,
    )
    if (!patch) {
      patch = {
        chapter: change.chapter,
        verse: change.verse,
        sourceTextSha256: sha256(verse.text),
        edits: [],
      }
      direction.verses.push(patch)
    }
    assert(patch.sourceTextSha256 === sha256(verse.text), 'source verse hash')
    const existing = patch.edits.find(
      (candidate) =>
        candidate.startOffset === edit.startOffset &&
        candidate.endOffset === edit.endOffset,
    )
    if (existing) {
      assert(
        existing.expected === edit.expected &&
          existing.replacement === edit.replacement,
        `conflicting edit ${bookId} ${change.chapter}:${change.verse}`,
      )
      continue
    }
    patch.edits.push(edit)
    patch.edits.sort((left, right) => left.startOffset - right.startOffset)
    for (let index = 1; index < patch.edits.length; index += 1) {
      assert(
        patch.edits[index].startOffset >= patch.edits[index - 1].endOffset,
        `overlap ${bookId} ${change.chapter}:${change.verse}`,
      )
    }
  }

  direction.verses.sort(
    (left, right) => left.chapter - right.chapter || left.verse - right.verse,
  )
  const edits = direction.verses.flatMap((entry) => entry.edits)
  direction.coverage.changedVerses = direction.verses.length
  direction.coverage.editCount = edits.length
  direction.coverage.categoryCounts = Object.fromEntries(
    [...Map.groupBy(edits, (edit) => edit.category)]
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([category, entries]) => [category, entries.length]),
  )
  direction.ownerReview = {
    contentVersion: changeSet.contentVersion,
    changeSet: path.relative(contentRoot, changeSetPath).replaceAll('\\', '/'),
    appliedEditCount: changes.length,
  }
  await fs.writeFile(directionPath, `${JSON.stringify(direction, null, 2)}\n`, 'utf8')
}

const packageSourcePath = path.join(
  contentRoot,
  'apps',
  'mobile',
  'assets',
  'bible_direction',
  'reading_2026.package-source.json',
)
const packageSource = await readJson(packageSourcePath)
packageSource.contentVersion = changeSet.contentVersion
packageSource.generatedAt = '2026-07-31T00:00:00.000Z'
await fs.writeFile(packageSourcePath, `${JSON.stringify(packageSource, null, 2)}\n`, 'utf8')

const channelSourcePath = path.join(
  contentRoot,
  'apps',
  'mobile',
  'tool',
  'bible_content_channel.v1.source.json',
)
const channelSource = await readJson(channelSourcePath)
channelSource.contentVersion = changeSet.contentVersion
channelSource.issuedAt = '2026-07-31T00:00:00.000Z'
channelSource.expiresAt = '2028-07-31T00:00:00.000Z'
await fs.writeFile(channelSourcePath, `${JSON.stringify(channelSource, null, 2)}\n`, 'utf8')

console.log(JSON.stringify({
  contentVersion: changeSet.contentVersion,
  appliedChanges: changeSet.changes.length,
  books: [...changesByBook.keys()],
}, null, 2))

function bookNamePrefix(bookId) {
  const names = { MAT: 'matthew_' }
  return names[bookId] ?? `${bookId.toLowerCase()}_`
}

function validateChange(change) {
  assert(Number.isSafeInteger(change.chapter) && change.chapter > 0, 'chapter')
  assert(Number.isSafeInteger(change.verse) && change.verse > 0, 'verse')
  for (const field of ['expected', 'replacement', 'category', 'reason']) {
    assert(typeof change[field] === 'string' && change[field].length > 0, field)
  }
}

function allOffsets(text, expected) {
  const offsets = []
  let cursor = 0
  while (cursor <= text.length) {
    const offset = text.indexOf(expected, cursor)
    if (offset < 0) break
    offsets.push(offset)
    cursor = offset + expected.length
  }
  return offsets
}

function sha256(value) {
  return crypto.createHash('sha256').update(value, 'utf8').digest('hex')
}

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, 'utf8'))
}

function readArgument(name) {
  const index = process.argv.indexOf(name)
  return index >= 0 ? process.argv[index + 1] : null
}

async function latestChangeSetPath() {
  const directory = path.join(contentRoot, 'editorial-changes')
  const candidates = (await fs.readdir(directory))
    .map((name) => ({ name, match: /^v([1-9][0-9]*)\.json$/.exec(name) }))
    .filter((entry) => entry.match)
    .sort((left, right) => Number(right.match[1]) - Number(left.match[1]))
  assert(candidates.length > 0, 'editorial change set inventory')
  return path.join(directory, candidates[0].name)
}

function assert(condition, label) {
  if (!condition) throw new Error(`Editorial change validation failed: ${label}`)
}
