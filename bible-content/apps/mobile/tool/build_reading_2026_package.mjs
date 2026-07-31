import crypto from 'node:crypto'
import { execFile } from 'node:child_process'
import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { promisify } from 'node:util'
import { fileURLToPath, pathToFileURL } from 'node:url'
import zlib from 'node:zlib'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const mobileRoot = path.resolve(scriptDir, '..')
const sourceDir = path.join(mobileRoot, 'assets', 'bible_direction')
const sourceConfigPath = path.join(sourceDir, 'reading_2026.package-source.json')
const mobilePackageDir = path.join(sourceDir, 'packages')
const payloadName = 'reading_2026.rv1909.v1.package.json.gz'
const manifestName = 'reading_2026.rv1909.v1.manifest.json'
const filterAssetPattern = /_reading_2026\.rv1909\.v1\.json$/
const execFileAsync = promisify(execFile)

const desktopRoot = readArgument('--desktop-root')
const packageOnly = process.argv.includes('--package-only')
if (!desktopRoot && !packageOnly) {
  throw new Error(
    'Usage: node tool/build_reading_2026_package.mjs ' +
      '[--package-only | --desktop-root <SHINE Desktop root>]',
  )
}
const webRoot = readArgument('--web-root')

const resolvedDesktopRoot = desktopRoot ? path.resolve(desktopRoot) : null
const desktopPackageDir = resolvedDesktopRoot
  ? path.join(resolvedDesktopRoot, 'resources', 'reading-2026')
  : null
const rvRoot = path.join(mobileRoot, 'assets', 'bibles', 'rv1909')
const kjvRoot = path.join(mobileRoot, 'assets', 'bibles', 'kjv')
const sourceConfig = await readJson(sourceConfigPath)
const rvManifest = await readJson(path.join(rvRoot, 'manifest.json'))
const kjvManifest = resolvedDesktopRoot
  ? await readJson(path.join(kjvRoot, 'manifest.json'))
  : null

assertEqual(rvManifest.version?.id, 'RV1909', 'RV1909 manifest identity')
if (kjvManifest) assertEqual(kjvManifest.version?.id, 'KJV', 'KJV manifest identity')
assertEqual(rvManifest.contentSha256, sourceConfig.sourceCorpusSha256, 'RV1909 corpus hash')

const rvBooks = await loadBibleBooks(rvRoot, rvManifest)
const kjvBooks = kjvManifest ? await loadBibleBooks(kjvRoot, kjvManifest) : null
const bookOrder = new Map(rvBooks.map((entry) => [entry.book.book, entry.book.order]))
const fileNames = (await fs.readdir(sourceDir)).filter((name) => filterAssetPattern.test(name))
const filterBooks = []
let changedVerseCount = 0
let editCount = 0

for (const fileName of fileNames) {
  const sourcePath = path.join(sourceDir, fileName)
  const rawBytes = await fs.readFile(sourcePath)
  const book = parseJson(rawBytes, fileName)
  validateFilterBook(book, fileName, rvBooks)
  changedVerseCount += book.verses.length
  editCount += book.verses.reduce((total, verse) => total + verse.edits.length, 0)
  const canonicalBytes = canonicalJsonBytes(book)
  filterBooks.push({
    id: book.book,
    order: bookOrder.get(book.book),
    sourceFile: fileName,
    sourceContentSha256: book.sourceContentSha256,
    payloadSha256: sha256(canonicalBytes),
    changedVerseCount: book.verses.length,
    editCount: book.verses.reduce((total, verse) => total + verse.edits.length, 0),
    payload: book,
  })
}

filterBooks.sort((left, right) => left.order - right.order)
assertEqual(filterBooks.length, sourceConfig.expectedBookCount, 'Lectura 2026 book count')
assertEqual(filterBooks.every((entry, index) => entry.order === index + 1), true, 'Lectura 2026 canon order')

const payload = {
  format: 'shine-reading-filter-package',
  filterId: sourceConfig.filterId,
  schemaVersion: sourceConfig.schemaVersion,
  contentVersion: sourceConfig.contentVersion,
  sourceVersionId: sourceConfig.sourceVersionId,
  sourceCorpusSha256: sourceConfig.sourceCorpusSha256,
  editorialPolicy: sourceConfig.editorialPolicy,
  books: filterBooks.map((entry) => entry.payload),
}
const expandedBytes = canonicalJsonBytes(payload)
const packageBytes = zlib.gzipSync(expandedBytes, {
  level: zlib.constants.Z_BEST_COMPRESSION,
  mtime: 0,
})
const contentSha256 = sha256(packageBytes)
const manifest = {
  format: 'shine-reading-filter-manifest',
  filterId: sourceConfig.filterId,
  schemaVersion: sourceConfig.schemaVersion,
  contentVersion: sourceConfig.contentVersion,
  sourceVersionId: sourceConfig.sourceVersionId,
  sourceCorpusSha256: sourceConfig.sourceCorpusSha256,
  contentSha256,
  sizeBytes: packageBytes.length,
  expandedSizeBytes: expandedBytes.length,
  mimeType: 'application/vnd.shine.reading-filter+gzip',
  generatedAt: sourceConfig.generatedAt,
  editorialPolicy: sourceConfig.editorialPolicy,
  coverage: {
    expectedBookCount: sourceConfig.expectedBookCount,
    includedBookCount: filterBooks.length,
    changedVerseCount,
    editCount,
  },
  books: filterBooks.map(({ id, order, sourceFile, sourceContentSha256, payloadSha256, changedVerseCount: verses, editCount: edits }) => ({
    id,
    order,
    sourceFile,
    sourceContentSha256,
    payloadSha256,
    changedVerseCount: verses,
    editCount: edits,
  })),
  integrity: {
    bundledTrust: 'sha256-pinned',
    remoteUpdateSignature: {
      algorithm: 'Ed25519',
      required: true,
      keyId: null,
      signature: null,
      status: 'not-configured',
    },
  },
}
const manifestBytes = Buffer.from(`${JSON.stringify(manifest, null, 2)}\n`, 'utf8')

await writeIdenticalPackage(mobilePackageDir, packageBytes, manifestBytes)
if (resolvedDesktopRoot) {
  await writeIdenticalPackage(desktopPackageDir, packageBytes, manifestBytes)
  await buildDesktopBibleSeed({
    desktopRoot: resolvedDesktopRoot,
    rvRoot,
    rvManifest,
    kjvRoot,
    kjvManifest,
  })
}

const mobilePayload = await fs.readFile(path.join(mobilePackageDir, payloadName))
assertEqual(sha256(mobilePayload), contentSha256, 'Mobile package hash')
if (desktopPackageDir) {
  const desktopPayload = await fs.readFile(path.join(desktopPackageDir, payloadName))
  assertEqual(sha256(desktopPayload), contentSha256, 'Desktop package hash')
}
const webSync = webRoot
  ? await syncWebCandidate({
      webRoot: path.resolve(webRoot),
      mobileRoot,
    })
  : null

console.log(JSON.stringify({
  filterId: manifest.filterId,
  contentVersion: manifest.contentVersion,
  contentSha256,
  sizeBytes: manifest.sizeBytes,
  books: filterBooks.length,
  changedVerseCount,
  editCount,
  rv1909ContentSha256: rvManifest.contentSha256,
  kjvContentSha256: kjvManifest?.contentSha256 ?? null,
  mobilePackage: path.join(mobilePackageDir, payloadName),
  desktopPackage: desktopPackageDir
    ? path.join(desktopPackageDir, payloadName)
    : null,
  webSync,
}, null, 2))

async function syncWebCandidate({ webRoot: root, mobileRoot: sourceRoot }) {
  const importScript = path.join(root, 'scripts', 'import-bible-release.mjs')
  const buildScript = path.join(root, 'scripts', 'build-bible-site.mjs')
  await Promise.all([fs.access(importScript), fs.access(buildScript)])
  const importResult = await execFileAsync(
    process.execPath,
    [importScript, '--mobile-root', sourceRoot],
    { cwd: root, windowsHide: true },
  )
  const buildResult = await execFileAsync(
    process.execPath,
    [buildScript],
    { cwd: root, windowsHide: true },
  )
  return {
    status: 'candidate',
    import: parseCommandOutput(importResult.stdout),
    build: parseCommandOutput(buildResult.stdout),
  }
}

async function buildDesktopBibleSeed({
  desktopRoot: root,
  rvRoot: spanishRoot,
  rvManifest: spanishManifest,
  kjvRoot: englishRoot,
  kjvManifest: englishManifest,
}) {
  const temporaryRoot = path.join(root, 'build', 'generated-builtin-bibles')
  const seedBiblesRoot = path.join(root, 'shine-data-seed', 'bibles')
  assertSafeGeneratedPath(root, temporaryRoot)
  assertSafeGeneratedPath(root, seedBiblesRoot)
  await fs.rm(temporaryRoot, { recursive: true, force: true })
  await fs.rm(seedBiblesRoot, { recursive: true, force: true })
  await fs.mkdir(temporaryRoot, { recursive: true })

  const versions = [
    { root: spanishRoot, manifest: spanishManifest, languageGroup: 'spanish' },
    { root: englishRoot, manifest: englishManifest, languageGroup: 'english' },
  ]
  const results = []
  for (const version of versions) {
    const versionId = version.manifest.version.id
    const bookFiles = {}
    for (const file of version.manifest.files) {
      const bookId = path.basename(file.path, '.json').toUpperCase()
      const relativePath = `bible/${versionId}/${bookId}.json`
      const sourcePath = path.join(version.root, ...file.path.split('/'))
      const targetPath = path.join(temporaryRoot, ...relativePath.split('/'))
      const bytes = await fs.readFile(sourcePath)
      assertEqual(bytes.length, file.sizeBytes, `${versionId}/${bookId} size`)
      assertEqual(sha256(bytes), file.sha256, `${versionId}/${bookId} hash`)
      await fs.mkdir(path.dirname(targetPath), { recursive: true })
      await fs.writeFile(targetPath, bytes)
      bookFiles[bookId] = relativePath
    }
    results.push({
      ok: true,
      version: versionId,
      versionTitle: version.manifest.version.displayName,
      language: version.manifest.version.language,
      languageGroup: version.languageGroup,
      sourcePackId: `builtin-${versionId.toLowerCase()}`,
      contentVersion: '1',
      contentSha256: version.manifest.contentSha256,
      preserveExactText: true,
      bookFiles,
    })
  }
  const sourceManifest = {
    format: 'shine-bible-version-pack-source',
    version: 1,
    id: 'shine-builtin-rv1909-kjv',
    locale: 'multilingual',
    scope: 'canon',
    contentVersion: '1',
    versions: ['RV1909', 'KJV'],
    bookCount: 66,
    errorCount: 0,
    results,
    errors: [],
    generatedBy: 'SHINE deterministic built-in Bible packaging',
  }
  await fs.writeFile(
    path.join(temporaryRoot, 'bible_manifest.json'),
    `${JSON.stringify(sourceManifest, null, 2)}\n`,
    'utf8',
  )

  const importModulePath = path.join(root, 'scripts', 'bible-library-import.mjs')
  const { installBibleLibrary } = await import(`${pathToFileURL(importModulePath).href}?v=${Date.now()}`)
  const result = await installBibleLibrary({
    sourceRoot: temporaryRoot,
    shineDataDir: path.join(root, 'shine-data-seed'),
  })
  assertEqual(
    JSON.stringify(result.catalog.versions.map((entry) => entry.id).sort()),
    JSON.stringify(['KJV', 'RV1909']),
    'Desktop built-in Bible versions',
  )
  assertEqual(result.catalog.books.length, 66, 'Desktop built-in canon')
  const portableSourceRoot = '$SHINE_DATA/bibles/source'
  const sourceManifestPath = path.join(root, 'shine-data-seed', 'bibles', 'source', 'manifest.json')
  const portableSourceManifest = await readJson(sourceManifestPath)
  portableSourceManifest.activeSourceDir = portableSourceRoot
  portableSourceManifest.imports = (portableSourceManifest.imports ?? []).map((entry) => ({
    ...entry,
    importedFrom: 'builtin-package',
  }))
  await fs.writeFile(sourceManifestPath, `${JSON.stringify(portableSourceManifest, null, 2)}\n`, 'utf8')
  const catalogPath = path.join(root, 'shine-data-seed', 'bibles', 'library', 'catalog.json')
  const catalog = await readJson(catalogPath)
  catalog.sourceRoot = portableSourceRoot
  if (catalog.sourceManifest) {
    catalog.sourceManifest.imports = (catalog.sourceManifest.imports ?? []).map((entry) => ({
      ...entry,
      importedFrom: 'builtin-package',
    }))
  }
  await fs.writeFile(catalogPath, `${JSON.stringify(catalog, null, 2)}\n`, 'utf8')
  await fs.rm(temporaryRoot, { recursive: true, force: true })
}

async function loadBibleBooks(root, manifest) {
  const entries = []
  for (const file of manifest.files) {
    const bytes = await fs.readFile(path.join(root, ...file.path.split('/')))
    assertEqual(bytes.length, file.sizeBytes, `${manifest.version.id}/${file.path} size`)
    assertEqual(sha256(bytes), file.sha256, `${manifest.version.id}/${file.path} hash`)
    const book = parseJson(bytes, `${manifest.version.id}/${file.path}`)
    entries.push({ bytes, book, sha256: file.sha256 })
  }
  entries.sort((left, right) => left.book.order - right.book.order)
  return entries
}

function validateFilterBook(book, fileName, rvBooks) {
  assertEqual(book.schemaVersion, 1, `${fileName} schema`)
  assertEqual(book.editionId, 'RV1909-LECTURA-2026', `${fileName} edition`)
  assertEqual(book.sourceVersionId, 'RV1909', `${fileName} source version`)
  const source = rvBooks.find((entry) => entry.book.book === book.book)
  if (!source) throw new Error(`${fileName} references unknown book ${book.book}`)
  assertEqual(book.sourceContentSha256, source.sha256, `${fileName} source book hash`)
  const verseKeys = new Set()
  for (const versePatch of book.verses) {
    const key = `${versePatch.chapter}:${versePatch.verse}`
    if (verseKeys.has(key)) throw new Error(`${fileName} duplicates ${key}`)
    verseKeys.add(key)
    const chapter = source.book.chapters.find((entry) => entry.chapter === versePatch.chapter)
    const verse = chapter?.verses.find((entry) => entry.verse === versePatch.verse)
    if (!verse) throw new Error(`${fileName} references missing verse ${key}`)
    assertEqual(sha256(Buffer.from(verse.text, 'utf8')), versePatch.sourceTextSha256, `${fileName} ${key} verse hash`)
    let previousEnd = -1
    for (const edit of versePatch.edits) {
      if (!Number.isInteger(edit.startOffset) || !Number.isInteger(edit.endOffset) || edit.startOffset < 0 || edit.endOffset <= edit.startOffset || edit.endOffset > verse.text.length) {
        throw new Error(`${fileName} ${key} has invalid offsets`)
      }
      if (edit.startOffset < previousEnd) throw new Error(`${fileName} ${key} has overlapping edits`)
      assertEqual(verse.text.slice(edit.startOffset, edit.endOffset), edit.expected, `${fileName} ${key} expected text`)
      if (!edit.replacement || !edit.category || !edit.reason) throw new Error(`${fileName} ${key} has incomplete editorial metadata`)
      previousEnd = edit.endOffset
    }
  }
}

async function writeIdenticalPackage(targetDir, packageBytes, manifestBytes) {
  await fs.mkdir(targetDir, { recursive: true })
  await fs.writeFile(path.join(targetDir, payloadName), packageBytes)
  await fs.writeFile(path.join(targetDir, manifestName), manifestBytes)
}

function canonicalJsonBytes(value) {
  return Buffer.from(JSON.stringify(sortDeep(value)), 'utf8')
}

function sortDeep(value) {
  if (Array.isArray(value)) return value.map(sortDeep)
  if (!value || typeof value !== 'object') return value
  return Object.fromEntries(
    Object.keys(value).sort().map((key) => [key, sortDeep(value[key])]),
  )
}

function parseJson(bytes, label) {
  try {
    return JSON.parse(Buffer.from(bytes).toString('utf8'))
  } catch {
    throw new Error(`${label} is not valid UTF-8 JSON`)
  }
}

function parseCommandOutput(stdout) {
  const text = String(stdout ?? '').trim()
  if (!text) return null
  const lines = text.split(/\r?\n/)
  for (let index = 0; index < lines.length; index += 1) {
    const candidate = lines.slice(index).join('\n')
    try {
      return JSON.parse(candidate)
    } catch {
      // Command wrappers may print a prefix before the final JSON payload.
    }
  }
  return { output: text }
}

async function readJson(filePath) {
  return parseJson(await fs.readFile(filePath), filePath)
}

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex')
}

function assertEqual(actual, expected, label) {
  if (actual !== expected) {
    throw new Error(`${label} mismatch: expected ${expected}, received ${actual}`)
  }
}

function assertSafeGeneratedPath(root, target) {
  const resolvedRoot = path.resolve(root)
  const resolvedTarget = path.resolve(target)
  if (!resolvedTarget.startsWith(`${resolvedRoot}${path.sep}`)) {
    throw new Error(`Generated target escapes Desktop root: ${resolvedTarget}`)
  }
}

function readArgument(name) {
  const index = process.argv.indexOf(name)
  return index >= 0 ? process.argv[index + 1] : null
}
