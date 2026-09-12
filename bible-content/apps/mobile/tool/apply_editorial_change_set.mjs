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
for (const field of ['generatedAt', 'issuedAt', 'expiresAt']) {
  assert(typeof changeSet[field] === 'string' && Number.isFinite(Date.parse(changeSet[field])), field)
}
assert(Date.parse(changeSet.expiresAt) > Date.parse(changeSet.issuedAt), 'channel expiry')

const expandedChanges = changeSet.changes.flatMap(expandChange)
const changesByBook = Map.groupBy(expandedChanges, (change) => change.book)
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
  const directionName = await findDirectionName(directionRoot, bookId)
  assert(directionName, `direction file ${bookId}`)
  const corpus = await readJson(corpusPath)
  const directionPath = path.join(directionRoot, directionName)
  const direction = await readJson(directionPath)
  assert(direction.book === bookId, `direction book ${bookId}`)
  const changesByOccurrence = Map.groupBy(changes, occurrenceKey)
  const nextOccurrenceByKey = new Map()

  for (const change of changes) {
    validateChange(change)
    const chapter = corpus.chapters.find((entry) => entry.chapter === change.chapter)
    const verse = chapter?.verses.find((entry) => entry.verse === change.verse)
    assert(verse, `${bookId} ${change.chapter}:${change.verse}`)
    const matches = allOffsets(verse.text, change.expected)
    const key = occurrenceKey(change)
    const siblingChanges = changesByOccurrence.get(key)
    assert(
      matches.length === siblingChanges.length,
      `${bookId} ${change.chapter}:${change.verse} expected text`,
    )
    if (siblingChanges.length > 1) {
      const [first] = siblingChanges
      assert(
        siblingChanges.every((candidate) =>
          candidate.replacement === first.replacement &&
          candidate.category === first.category &&
          candidate.reason === first.reason &&
          JSON.stringify(candidate.evidence ?? null) === JSON.stringify(first.evidence ?? null)
        ),
        `${bookId} ${change.chapter}:${change.verse} repeated text requires identical reviewed changes`,
      )
    }
    const occurrenceIndex = nextOccurrenceByKey.get(key) ?? 0
    const startOffset = matches[occurrenceIndex]
    assert(
      Number.isSafeInteger(startOffset),
      `${bookId} ${change.chapter}:${change.verse} occurrence index`,
    )
    nextOccurrenceByKey.set(key, occurrenceIndex + 1)
    const edit = {
      startOffset,
      endOffset: startOffset + change.expected.length,
      expected: change.expected,
      replacement: change.replacement,
      category: change.category,
      reason: change.reason,
      ...(change.evidence === undefined ? {} : { evidence: change.evidence }),
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
      assert(existing.expected === edit.expected, `conflicting expected text ${bookId} ${change.chapter}:${change.verse}`)
      if (existing.replacement !== edit.replacement) {
        assert(
          typeof change.previousReplacement === 'string' &&
            existing.replacement === change.previousReplacement,
          `conflicting edit ${bookId} ${change.chapter}:${change.verse}`,
        )
      }
      Object.assign(existing, edit)
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
  const appliedChangeSet = path.relative(contentRoot, changeSetPath).replaceAll('\\', '/')
  if (
    direction.ownerReview?.contentVersion !== changeSet.contentVersion ||
    direction.ownerReview?.changeSet !== appliedChangeSet
  ) {
    direction.ownerReview = {
      contentVersion: changeSet.contentVersion,
      changeSet: appliedChangeSet,
      appliedEditCount: changes.length,
    }
  }
  await fs.writeFile(directionPath, `${JSON.stringify(direction)}\n`, 'utf8')
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
packageSource.generatedAt = changeSet.generatedAt
await fs.writeFile(packageSourcePath, `${JSON.stringify(packageSource, null, 2)}\n`, 'utf8')

const channelSourcePath = path.join(
  contentRoot,
  'apps',
  'mobile',
  'tool',
  'bible_content_channel.v1.source.json',
)
const channelSource = await readJson(channelSourcePath)
if (channelSource.contentVersion !== changeSet.contentVersion) {
  channelSource.contentVersion = changeSet.contentVersion
  channelSource.issuedAt = changeSet.issuedAt
  channelSource.expiresAt = changeSet.expiresAt
}
await fs.writeFile(channelSourcePath, `${JSON.stringify(channelSource, null, 2)}\n`, 'utf8')

console.log(JSON.stringify({
  contentVersion: changeSet.contentVersion,
  editorialRules: changeSet.changes.length,
  appliedChanges: expandedChanges.length,
  books: [...changesByBook.keys()],
}, null, 2))

async function findDirectionName(directionRoot, bookId) {
  const names = (await fs.readdir(directionRoot)).filter((name) =>
    name.endsWith('_reading_2026.rv1909.v1.json'),
  )
  for (const name of names) {
    const candidate = await readJson(path.join(directionRoot, name))
    if (candidate.book === bookId) return name
  }
  return null
}

function expandChange(change) {
  if (change.references === undefined) return [change]
  assert(Array.isArray(change.references) && change.references.length > 0, 'references')
  assert(change.chapter === undefined && change.verse === undefined, 'reference shape')
  return change.references.map((reference) => {
    assert(reference && typeof reference === 'object', 'reference')
    assert(Number.isSafeInteger(reference.chapter) && reference.chapter > 0, 'reference chapter')
    assert(Number.isSafeInteger(reference.verse) && reference.verse > 0, 'reference verse')
    return {
      ...change,
      chapter: reference.chapter,
      verse: reference.verse,
      references: undefined,
    }
  })
}

function validateChange(change) {
  assert(Number.isSafeInteger(change.chapter) && change.chapter > 0, 'chapter')
  assert(Number.isSafeInteger(change.verse) && change.verse > 0, 'verse')
  for (const field of ['expected', 'replacement', 'category', 'reason']) {
    assert(typeof change[field] === 'string' && change[field].length > 0, field)
  }
  if (change.previousReplacement !== undefined) {
    assert(
      typeof change.previousReplacement === 'string' && change.previousReplacement.length > 0,
      'previousReplacement',
    )
  }
  if (change.evidence !== undefined) {
    assert(Array.isArray(change.evidence) && change.evidence.length > 0, 'evidence')
    for (const item of change.evidence) {
      assert(item && typeof item === 'object', 'evidence item')
      assert(typeof item.label === 'string' && item.label.length > 0, 'evidence label')
      assert(typeof item.url === 'string' && /^https:\/\//.test(item.url), 'evidence URL')
    }
  }
}

function allOffsets(text, expected) {
  const offsets = []
  const wholeWord = /^\p{L}+$/u.test(expected)
  let cursor = 0
  while (cursor <= text.length) {
    const offset = text.indexOf(expected, cursor)
    if (offset < 0) break
    const before = offset > 0 ? text[offset - 1] : ''
    const after = text[offset + expected.length] ?? ''
    if (!wholeWord || (!/\p{L}/u.test(before) && !/\p{L}/u.test(after))) {
      offsets.push(offset)
    }
    cursor = offset + expected.length
  }
  return offsets
}

function occurrenceKey(change) {
  return `${change.chapter}:${change.verse}\u0000${change.expected}`
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
