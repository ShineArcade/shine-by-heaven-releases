import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'
import zlib from 'node:zlib'

export const EXPECTED_RV1909_SHA256 =
  'af7a0acc03b228719b549539dcd0dcaca3c40af51a4b3d6c96f51ec8510ec739'
export const CHANNEL_FORMAT = 'shine-public-bible-content-channel'
export const CHANNEL_SCHEMA_VERSION = 1
export const CHANNEL_ID = 'shine-public-bible-stable'

const SOURCE_FORMAT = 'shine-public-bible-content-channel-source'
const FILTER_ID = 'RV1909-LECTURA-2026'
const RV1909_ID = 'RV1909'
const EXPECTED_BOOK_COUNT = 66
const FILTER_ASSET_PATTERN = /_reading_2026\.rv1909\.v1\.json$/
const HASH_PATTERN = /^[a-f0-9]{64}$/
const SAFE_ARTIFACT_NAME = /^[A-Za-z0-9._-]+$/
const KEY_ID_PATTERN = /^[A-Za-z0-9._:-]{1,120}$/

export class ChannelVerificationError extends Error {
  constructor(code, message) {
    super(message)
    this.name = 'ChannelVerificationError'
    this.code = code
  }
}

export async function buildBibleContentChannel({
  repoRoot,
  outputDir,
  privateKeyPem,
  keyId,
  sourceConfigPath = path.join(
    repoRoot,
    'apps',
    'mobile',
    'tool',
    'bible_content_channel.v1.source.json',
  ),
}) {
  const resolvedRepoRoot = path.resolve(repoRoot)
  const resolvedOutputDir = path.resolve(outputDir)
  assertOutputDirectory(resolvedRepoRoot, resolvedOutputDir)
  assertKeyId(keyId)

  const privateKey = importEd25519PrivateKey(privateKeyPem)
  const sourceConfig = await readJson(sourceConfigPath)
  validateSourceConfig(sourceConfig)

  const rv1909 = await buildRv1909Artifact({
    repoRoot: resolvedRepoRoot,
    contentVersion: sourceConfig.rv1909ContentVersion,
  })
  const reading2026 = await buildReading2026Artifact({
    repoRoot: resolvedRepoRoot,
    rv1909Books: rv1909.books,
    rv1909BookHashes: rv1909.bookHashes,
  })

  const rvArtifactPath = `rv1909.v${rv1909.contentVersion}.package.json.gz`
  const filterArtifactPath =
    `reading_2026.rv1909.v${reading2026.contentVersion}.package.json.gz`
  const payload = {
    channelId: CHANNEL_ID,
    contentVersion: sourceConfig.contentVersion,
    issuedAt: sourceConfig.issuedAt,
    expiresAt: sourceConfig.expiresAt,
    distributionScope: 'public',
    updatePolicy: {
      versionAuthority: 'contentVersion',
      issuedAtRole: 'audit-only',
      equalVersionEqualHash: 'no-op',
      equalVersionDifferentHash: 'reject-conflict',
      lowerVersion: 'reject-downgrade',
      higherVersion: 'accept-after-verification',
    },
    artifacts: [
      {
        kind: 'bible-corpus',
        id: RV1909_ID,
        schemaVersion: 1,
        contentVersion: rv1909.contentVersion,
        sourceVersionId: RV1909_ID,
        sourceCorpusSha256: EXPECTED_RV1909_SHA256,
        contentSha256: rv1909.contentSha256,
        sizeBytes: rv1909.packageBytes.length,
        mimeType: 'application/json+gzip',
        artifactPath: rvArtifactPath,
        expectedBookCount: EXPECTED_BOOK_COUNT,
        includedBookCount: rv1909.books.length,
        rights: {
          license: rv1909.manifest.rights.license,
          copyright: rv1909.manifest.rights.copyright,
          rightsUrl: rv1909.manifest.rights.rightsUrl,
        },
      },
      {
        kind: 'reading-filter',
        id: FILTER_ID,
        schemaVersion: reading2026.manifest.schemaVersion,
        contentVersion: reading2026.contentVersion,
        sourceVersionId: RV1909_ID,
        sourceCorpusSha256: EXPECTED_RV1909_SHA256,
        contentSha256: reading2026.contentSha256,
        sizeBytes: reading2026.packageBytes.length,
        mimeType: 'application/json+gzip',
        artifactPath: filterArtifactPath,
        expectedBookCount: EXPECTED_BOOK_COUNT,
        includedBookCount: reading2026.bookCount,
        coverage: {
          changedVerseCount: reading2026.manifest.coverage.changedVerseCount,
          editCount: reading2026.manifest.coverage.editCount,
        },
        editorialPolicy: reading2026.manifest.editorialPolicy,
      },
    ],
  }
  validateChannelPayload(payload)

  const payloadBytes = canonicalJsonBytes(payload)
  const contentSha256 = sha256(payloadBytes)
  const signature = crypto.sign(null, payloadBytes, privateKey).toString('base64url')
  const channel = {
    format: CHANNEL_FORMAT,
    schemaVersion: CHANNEL_SCHEMA_VERSION,
    payload,
    contentSha256,
    signature: {
      algorithm: 'Ed25519',
      keyId,
      signedObject: 'payload',
      value: signature,
    },
  }

  await fs.mkdir(resolvedOutputDir, { recursive: true })
  await atomicWrite(path.join(resolvedOutputDir, rvArtifactPath), rv1909.packageBytes)
  await atomicWrite(
    path.join(resolvedOutputDir, filterArtifactPath),
    reading2026.packageBytes,
  )
  await atomicWrite(
    path.join(resolvedOutputDir, 'channel-stable.json'),
    Buffer.from(`${JSON.stringify(channel, null, 2)}\n`, 'utf8'),
  )

  const publicKey = crypto.createPublicKey(privateKey)
  const verification = await verifyBibleContentChannel({
    channelPath: path.join(resolvedOutputDir, 'channel-stable.json'),
    artifactRoot: resolvedOutputDir,
    trustedPublicKeys: new Map([[keyId, publicKey]]),
    now: new Date(sourceConfig.issuedAt),
  })

  return {
    channelPath: path.join(resolvedOutputDir, 'channel-stable.json'),
    contentVersion: payload.contentVersion,
    contentSha256,
    keyId,
    decision: verification.decision,
    artifacts: payload.artifacts.map((artifact) => ({
      id: artifact.id,
      contentVersion: artifact.contentVersion,
      contentSha256: artifact.contentSha256,
      sizeBytes: artifact.sizeBytes,
      artifactPath: artifact.artifactPath,
    })),
  }
}

export async function verifyBibleContentChannel({
  channelPath,
  artifactRoot = path.dirname(channelPath),
  trustedPublicKeys,
  currentRelease = null,
  now = new Date(),
}) {
  const channel = await readJson(channelPath)
  validateChannelEnvelope(channel)
  const payloadBytes = canonicalJsonBytes(channel.payload)
  const actualContentSha256 = sha256(payloadBytes)
  if (actualContentSha256 !== channel.contentSha256) {
    fail(
      'CHANNEL_HASH_MISMATCH',
      `Channel payload hash mismatch: expected ${channel.contentSha256}, received ${actualContentSha256}`,
    )
  }

  const publicKeyInput = lookupTrustedKey(trustedPublicKeys, channel.signature.keyId)
  const publicKey = importEd25519PublicKey(publicKeyInput)
  const signatureBytes = decodeBase64Url(channel.signature.value, 'signature.value')
  if (!crypto.verify(null, payloadBytes, publicKey, signatureBytes)) {
    fail('INVALID_SIGNATURE', 'Channel signature is not valid for the trusted key')
  }

  const verificationTime = normalizeDate(now, 'now')
  const issuedAt = parseIsoDate(channel.payload.issuedAt, 'payload.issuedAt')
  const expiresAt = parseIsoDate(channel.payload.expiresAt, 'payload.expiresAt')
  if (verificationTime < issuedAt) {
    fail('NOT_YET_VALID', 'Channel is not valid before its explicit issuedAt')
  }
  if (verificationTime >= expiresAt) {
    fail('EXPIRED', 'Channel has expired')
  }

  const artifactResults = []
  for (const artifact of channel.payload.artifacts) {
    artifactResults.push(
      await verifyArtifact({
        artifact,
        artifactRoot,
      }),
    )
  }

  const decision = decideChannelUpdate({
    offeredVersion: channel.payload.contentVersion,
    offeredSha256: channel.contentSha256,
    currentRelease,
  })
  return {
    decision,
    contentVersion: channel.payload.contentVersion,
    contentSha256: channel.contentSha256,
    keyId: channel.signature.keyId,
    artifacts: artifactResults,
  }
}

export function decideChannelUpdate({
  offeredVersion,
  offeredSha256,
  currentRelease,
}) {
  assertPositiveInteger(offeredVersion, 'offeredVersion')
  assertHash(offeredSha256, 'offeredSha256')
  if (currentRelease == null) return 'APPLY'

  assertPositiveInteger(currentRelease.contentVersion, 'currentRelease.contentVersion')
  assertHash(currentRelease.contentSha256, 'currentRelease.contentSha256')
  if (offeredVersion < currentRelease.contentVersion) {
    fail(
      'DOWNGRADE',
      `Offered contentVersion ${offeredVersion} is below installed version ${currentRelease.contentVersion}`,
    )
  }
  if (offeredVersion === currentRelease.contentVersion) {
    if (offeredSha256 === currentRelease.contentSha256) return 'NO_OP'
    fail(
      'VERSION_CONFLICT',
      `contentVersion ${offeredVersion} has a different channel hash`,
    )
  }
  return 'APPLY'
}

export function signChannelPayload({ payload, privateKeyPem, keyId }) {
  validateChannelPayload(payload)
  assertKeyId(keyId)
  const privateKey = importEd25519PrivateKey(privateKeyPem)
  const payloadBytes = canonicalJsonBytes(payload)
  return {
    format: CHANNEL_FORMAT,
    schemaVersion: CHANNEL_SCHEMA_VERSION,
    payload,
    contentSha256: sha256(payloadBytes),
    signature: {
      algorithm: 'Ed25519',
      keyId,
      signedObject: 'payload',
      value: crypto.sign(null, payloadBytes, privateKey).toString('base64url'),
    },
  }
}

export function canonicalJsonBytes(value) {
  return Buffer.from(JSON.stringify(sortDeep(value)), 'utf8')
}

export function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex')
}

export function bibleContentIndexSha256(manifest) {
  if (!Array.isArray(manifest?.files) || manifest.files.length === 0) {
    throw new Error('Bible manifest files are required')
  }
  const verifiedIndex = manifest.files.map((file, index) => {
    assertNonEmptyString(file?.path, `manifest.files[${index}].path`)
    assertPositiveInteger(file?.sizeBytes, `manifest.files[${index}].sizeBytes`)
    assertHash(file?.sha256, `manifest.files[${index}].sha256`)
    return `${file.path}\u0000${file.sizeBytes}\u0000${file.sha256}\n`
  })
  verifiedIndex.sort()
  return sha256(Buffer.from(verifiedIndex.join(''), 'utf8'))
}

async function buildRv1909Artifact({ repoRoot, contentVersion }) {
  assertPositiveInteger(contentVersion, 'rv1909ContentVersion')
  const rvRoot = path.join(
    repoRoot,
    'apps',
    'mobile',
    'assets',
    'bibles',
    'rv1909',
  )
  const manifest = await readJson(path.join(rvRoot, 'manifest.json'))
  assertEqual(manifest.version?.id, RV1909_ID, 'RV1909 manifest version id')
  assertEqual(
    manifest.contentSha256,
    EXPECTED_RV1909_SHA256,
    'RV1909 corpus hash',
  )
  assertEqual(manifest.canon?.bookCount, EXPECTED_BOOK_COUNT, 'RV1909 book count')
  assertEqual(manifest.files?.length, EXPECTED_BOOK_COUNT, 'RV1909 file count')
  assertEqual(
    bibleContentIndexSha256(manifest),
    EXPECTED_RV1909_SHA256,
    'RV1909 computed corpus hash',
  )
  assertNonEmptyString(manifest.rights?.license, 'RV1909 rights.license')
  assertNonEmptyString(manifest.rights?.copyright, 'RV1909 rights.copyright')
  assertNonEmptyString(manifest.rights?.rightsUrl, 'RV1909 rights.rightsUrl')

  const books = []
  const bookHashes = new Map()
  for (const file of manifest.files) {
    const filePath = resolveContainedPath(rvRoot, file.path)
    const bytes = await fs.readFile(filePath)
    assertEqual(bytes.length, file.sizeBytes, `RV1909 ${file.path} size`)
    assertEqual(sha256(bytes), file.sha256, `RV1909 ${file.path} hash`)
    const book = parseJson(bytes, file.path)
    assertEqual(book.format, 'shine-mobile-bible-book', `${file.path} format`)
    assertEqual(book.schemaVersion, 1, `${file.path} schema`)
    assertEqual(book.versionId, RV1909_ID, `${file.path} version`)
    assertPositiveInteger(book.order, `${file.path} order`)
    assertNonEmptyString(book.book, `${file.path} book`)
    books.push(book)
    bookHashes.set(book.book, file.sha256)
  }
  books.sort((left, right) => left.order - right.order)
  assertCanonicalBookOrder(books, 'RV1909')

  const packagePayload = {
    format: 'shine-public-bible-corpus-package',
    schemaVersion: 1,
    contentVersion,
    sourceVersionId: RV1909_ID,
    sourceCorpusSha256: EXPECTED_RV1909_SHA256,
    version: manifest.version,
    canon: manifest.canon,
    versification: manifest.versification,
    rights: manifest.rights,
    provenance: {
      provider: manifest.provenance?.provider,
      sourceUrl: manifest.provenance?.sourceUrl,
      sourceArtifactSha256: manifest.provenance?.sourceArtifactSha256,
      sourceTreeSha256: manifest.provenance?.sourceTreeSha256,
    },
    books,
  }
  const packageBytes = deterministicGzip(canonicalJsonBytes(packagePayload))
  return {
    manifest,
    books,
    bookHashes,
    contentVersion,
    contentSha256: sha256(packageBytes),
    packageBytes,
  }
}

async function buildReading2026Artifact({
  repoRoot,
  rv1909Books,
  rv1909BookHashes,
}) {
  const directionRoot = path.join(
    repoRoot,
    'apps',
    'mobile',
    'assets',
    'bible_direction',
  )
  const packageRoot = path.join(directionRoot, 'packages')
  const sourceConfig = await readJson(
    path.join(directionRoot, 'reading_2026.package-source.json'),
  )
  const manifest = await readJson(
    path.join(packageRoot, 'reading_2026.rv1909.v1.manifest.json'),
  )
  const packageBytes = await fs.readFile(
    path.join(packageRoot, 'reading_2026.rv1909.v1.package.json.gz'),
  )

  assertEqual(sourceConfig.filterId, FILTER_ID, 'filter source id')
  assertEqual(sourceConfig.sourceVersionId, RV1909_ID, 'filter source version')
  assertEqual(
    sourceConfig.sourceCorpusSha256,
    EXPECTED_RV1909_SHA256,
    'filter source corpus hash',
  )
  assertPositiveInteger(sourceConfig.contentVersion, 'filter contentVersion')
  assertEqual(manifest.filterId, sourceConfig.filterId, 'filter manifest id')
  assertEqual(
    manifest.contentVersion,
    sourceConfig.contentVersion,
    'filter manifest contentVersion',
  )
  assertEqual(
    manifest.sourceCorpusSha256,
    EXPECTED_RV1909_SHA256,
    'filter manifest source corpus hash',
  )
  assertEqual(packageBytes.length, manifest.sizeBytes, 'filter package size')
  assertEqual(sha256(packageBytes), manifest.contentSha256, 'filter package hash')
  assertEqual(
    manifest.coverage?.expectedBookCount,
    EXPECTED_BOOK_COUNT,
    'filter expected book count',
  )
  assertEqual(
    manifest.coverage?.includedBookCount,
    EXPECTED_BOOK_COUNT,
    'filter included book count',
  )

  const rvById = new Map(rv1909Books.map((book) => [book.book, book]))
  const sourceNames = (await fs.readdir(directionRoot))
    .filter((name) => FILTER_ASSET_PATTERN.test(name))
  assertEqual(sourceNames.length, EXPECTED_BOOK_COUNT, 'filter source asset count')
  const sourceBooks = []
  for (const sourceName of sourceNames) {
    const sourceBook = await readJson(path.join(directionRoot, sourceName))
    validateFilterSourceBook({
      sourceBook,
      sourceName,
      rvBook: rvById.get(sourceBook.book),
      rvBookSha256: rv1909BookHashes.get(sourceBook.book),
    })
    sourceBooks.push(sourceBook)
  }
  sourceBooks.sort(
    (left, right) => rvById.get(left.book).order - rvById.get(right.book).order,
  )

  const expandedBytes = zlib.gunzipSync(packageBytes)
  assertEqual(
    expandedBytes.length,
    manifest.expandedSizeBytes,
    'filter expanded size',
  )
  const packagePayload = parseJson(expandedBytes, 'filter package payload')
  assertEqual(packagePayload.filterId, FILTER_ID, 'filter package id')
  assertEqual(packagePayload.sourceVersionId, RV1909_ID, 'filter package source')
  assertEqual(
    packagePayload.sourceCorpusSha256,
    EXPECTED_RV1909_SHA256,
    'filter package corpus hash',
  )
  assertEqual(
    packagePayload.contentVersion,
    sourceConfig.contentVersion,
    'filter package contentVersion',
  )
  assertEqual(packagePayload.books?.length, EXPECTED_BOOK_COUNT, 'filter package books')
  assertEqual(
    canonicalJsonBytes(packagePayload.books).equals(canonicalJsonBytes(sourceBooks)),
    true,
    'filter package/source parity',
  )

  return {
    manifest,
    contentVersion: sourceConfig.contentVersion,
    contentSha256: manifest.contentSha256,
    packageBytes,
    bookCount: sourceBooks.length,
  }
}

function validateFilterSourceBook({
  sourceBook,
  sourceName,
  rvBook,
  rvBookSha256,
}) {
  if (!rvBook) throw new Error(`${sourceName} references an unknown RV1909 book`)
  assertEqual(sourceBook.schemaVersion, 1, `${sourceName} schema`)
  assertEqual(sourceBook.editionId, FILTER_ID, `${sourceName} edition`)
  assertEqual(sourceBook.sourceVersionId, RV1909_ID, `${sourceName} source version`)
  assertEqual(
    sourceBook.sourceContentSha256,
    rvBookSha256,
    `${sourceName} source book hash`,
  )
  const verseKeys = new Set()
  for (const patch of sourceBook.verses ?? []) {
    const verseKey = `${patch.chapter}:${patch.verse}`
    if (verseKeys.has(verseKey)) {
      throw new Error(`${sourceName} duplicates verse ${verseKey}`)
    }
    verseKeys.add(verseKey)
    const chapter = rvBook.chapters.find((entry) => entry.chapter === patch.chapter)
    const verse = chapter?.verses.find((entry) => entry.verse === patch.verse)
    if (!verse) throw new Error(`${sourceName} references missing verse ${verseKey}`)
    assertEqual(
      patch.sourceTextSha256,
      sha256(Buffer.from(verse.text, 'utf8')),
      `${sourceName} ${verseKey} source text hash`,
    )
    let previousEnd = -1
    for (const edit of patch.edits ?? []) {
      if (
        !Number.isInteger(edit.startOffset) ||
        !Number.isInteger(edit.endOffset) ||
        edit.startOffset < 0 ||
        edit.endOffset <= edit.startOffset ||
        edit.endOffset > verse.text.length
      ) {
        throw new Error(`${sourceName} ${verseKey} has invalid offsets`)
      }
      if (edit.startOffset < previousEnd) {
        throw new Error(`${sourceName} ${verseKey} has overlapping edits`)
      }
      assertEqual(
        verse.text.slice(edit.startOffset, edit.endOffset),
        edit.expected,
        `${sourceName} ${verseKey} expected text`,
      )
      assertNonEmptyString(edit.replacement, `${sourceName} ${verseKey} replacement`)
      assertNonEmptyString(edit.category, `${sourceName} ${verseKey} category`)
      assertNonEmptyString(edit.reason, `${sourceName} ${verseKey} reason`)
      previousEnd = edit.endOffset
    }
  }
}

async function verifyArtifact({ artifact, artifactRoot }) {
  if (!SAFE_ARTIFACT_NAME.test(artifact.artifactPath)) {
    fail('UNSAFE_ARTIFACT_PATH', `Unsafe artifact path ${artifact.artifactPath}`)
  }
  const filePath = path.join(path.resolve(artifactRoot), artifact.artifactPath)
  const bytes = await fs.readFile(filePath).catch((error) => {
    fail('MISSING_ARTIFACT', `Cannot read ${artifact.artifactPath}: ${error.message}`)
  })
  if (bytes.length !== artifact.sizeBytes) {
    fail('ARTIFACT_SIZE_MISMATCH', `${artifact.id} size does not match the channel`)
  }
  if (sha256(bytes) !== artifact.contentSha256) {
    fail('ARTIFACT_HASH_MISMATCH', `${artifact.id} hash does not match the channel`)
  }

  let payload
  try {
    payload = parseJson(zlib.gunzipSync(bytes), artifact.artifactPath)
  } catch (error) {
    fail('INVALID_ARTIFACT', `${artifact.id} cannot be decoded: ${error.message}`)
  }
  if (artifact.kind === 'bible-corpus') {
    if (
      payload.format !== 'shine-public-bible-corpus-package' ||
      payload.sourceVersionId !== RV1909_ID ||
      payload.sourceCorpusSha256 !== EXPECTED_RV1909_SHA256 ||
      payload.contentVersion !== artifact.contentVersion ||
      payload.books?.length !== EXPECTED_BOOK_COUNT
    ) {
      fail('INVALID_ARTIFACT', 'RV1909 package metadata is incompatible')
    }
  } else if (
    payload.format !== 'shine-reading-filter-package' ||
    payload.filterId !== FILTER_ID ||
    payload.sourceVersionId !== RV1909_ID ||
    payload.sourceCorpusSha256 !== EXPECTED_RV1909_SHA256 ||
    payload.contentVersion !== artifact.contentVersion ||
    payload.books?.length !== EXPECTED_BOOK_COUNT
  ) {
    fail('INVALID_ARTIFACT', 'Lectura 2026 package metadata is incompatible')
  }
  return {
    id: artifact.id,
    contentSha256: artifact.contentSha256,
    sizeBytes: artifact.sizeBytes,
    bookCount: payload.books.length,
  }
}

function validateSourceConfig(source) {
  assertExactKeys(
    source,
    [
      'format',
      'schemaVersion',
      'channelId',
      'contentVersion',
      'issuedAt',
      'expiresAt',
      'rv1909ContentVersion',
    ],
    'channel source',
  )
  assertEqual(source.format, SOURCE_FORMAT, 'channel source format')
  assertEqual(source.schemaVersion, 1, 'channel source schema')
  assertEqual(source.channelId, CHANNEL_ID, 'channel source id')
  assertPositiveInteger(source.contentVersion, 'channel source contentVersion')
  assertPositiveInteger(
    source.rv1909ContentVersion,
    'channel source rv1909ContentVersion',
  )
  const issuedAt = parseIsoDate(source.issuedAt, 'channel source issuedAt')
  const expiresAt = parseIsoDate(source.expiresAt, 'channel source expiresAt')
  if (expiresAt <= issuedAt) {
    throw new Error('channel source expiresAt must be after issuedAt')
  }
}

function validateChannelEnvelope(channel) {
  assertExactKeys(
    channel,
    ['format', 'schemaVersion', 'payload', 'contentSha256', 'signature'],
    'channel',
  )
  assertEqual(channel.format, CHANNEL_FORMAT, 'channel format')
  assertEqual(channel.schemaVersion, CHANNEL_SCHEMA_VERSION, 'channel schema')
  assertHash(channel.contentSha256, 'channel contentSha256')
  validateChannelPayload(channel.payload)
  assertExactKeys(
    channel.signature,
    ['algorithm', 'keyId', 'signedObject', 'value'],
    'channel signature',
  )
  assertEqual(channel.signature.algorithm, 'Ed25519', 'signature algorithm')
  assertEqual(channel.signature.signedObject, 'payload', 'signature object')
  assertKeyId(channel.signature.keyId)
  if (!/^[A-Za-z0-9_-]{86}$/.test(channel.signature.value)) {
    fail('INVALID_CHANNEL', 'signature.value is not an Ed25519 base64url value')
  }
}

function validateChannelPayload(payload) {
  assertExactKeys(
    payload,
    [
      'channelId',
      'contentVersion',
      'issuedAt',
      'expiresAt',
      'distributionScope',
      'updatePolicy',
      'artifacts',
    ],
    'channel payload',
  )
  assertEqual(payload.channelId, CHANNEL_ID, 'channel id')
  assertPositiveInteger(payload.contentVersion, 'channel contentVersion')
  const issuedAt = parseIsoDate(payload.issuedAt, 'channel issuedAt')
  const expiresAt = parseIsoDate(payload.expiresAt, 'channel expiresAt')
  if (expiresAt <= issuedAt) {
    fail('INVALID_CHANNEL', 'channel expiresAt must be after issuedAt')
  }
  assertEqual(payload.distributionScope, 'public', 'channel distribution scope')
  assertExactKeys(
    payload.updatePolicy,
    [
      'versionAuthority',
      'issuedAtRole',
      'equalVersionEqualHash',
      'equalVersionDifferentHash',
      'lowerVersion',
      'higherVersion',
    ],
    'channel updatePolicy',
  )
  assertEqual(
    payload.updatePolicy.versionAuthority,
    'contentVersion',
    'version authority',
  )
  assertEqual(payload.updatePolicy.issuedAtRole, 'audit-only', 'issuedAt role')
  assertEqual(
    payload.updatePolicy.equalVersionEqualHash,
    'no-op',
    'equal version/equal hash policy',
  )
  assertEqual(
    payload.updatePolicy.equalVersionDifferentHash,
    'reject-conflict',
    'equal version/different hash policy',
  )
  assertEqual(
    payload.updatePolicy.lowerVersion,
    'reject-downgrade',
    'lower version policy',
  )
  assertEqual(
    payload.updatePolicy.higherVersion,
    'accept-after-verification',
    'higher version policy',
  )
  if (!Array.isArray(payload.artifacts) || payload.artifacts.length !== 2) {
    fail('INVALID_CHANNEL', 'channel must contain exactly two artifacts')
  }
  validateRv1909Artifact(payload.artifacts[0])
  validateReading2026Artifact(payload.artifacts[1])
}

function validateRv1909Artifact(artifact) {
  assertExactKeys(
    artifact,
    [
      'kind',
      'id',
      'schemaVersion',
      'contentVersion',
      'sourceVersionId',
      'sourceCorpusSha256',
      'contentSha256',
      'sizeBytes',
      'mimeType',
      'artifactPath',
      'expectedBookCount',
      'includedBookCount',
      'rights',
    ],
    'RV1909 artifact',
  )
  validateCommonArtifact(artifact)
  assertEqual(artifact.kind, 'bible-corpus', 'RV1909 artifact kind')
  assertEqual(artifact.id, RV1909_ID, 'RV1909 artifact id')
  assertExactKeys(
    artifact.rights,
    ['license', 'copyright', 'rightsUrl'],
    'RV1909 rights',
  )
  assertNonEmptyString(artifact.rights.license, 'RV1909 rights license')
  assertNonEmptyString(artifact.rights.copyright, 'RV1909 rights copyright')
  assertNonEmptyString(artifact.rights.rightsUrl, 'RV1909 rights URL')
}

function validateReading2026Artifact(artifact) {
  assertExactKeys(
    artifact,
    [
      'kind',
      'id',
      'schemaVersion',
      'contentVersion',
      'sourceVersionId',
      'sourceCorpusSha256',
      'contentSha256',
      'sizeBytes',
      'mimeType',
      'artifactPath',
      'expectedBookCount',
      'includedBookCount',
      'coverage',
      'editorialPolicy',
    ],
    'Lectura 2026 artifact',
  )
  validateCommonArtifact(artifact)
  assertEqual(artifact.kind, 'reading-filter', 'Lectura 2026 artifact kind')
  assertEqual(artifact.id, FILTER_ID, 'Lectura 2026 artifact id')
  assertExactKeys(
    artifact.coverage,
    ['changedVerseCount', 'editCount'],
    'Lectura 2026 coverage',
  )
  assertPositiveInteger(
    artifact.coverage.changedVerseCount,
    'Lectura 2026 changed verse count',
  )
  assertPositiveInteger(artifact.coverage.editCount, 'Lectura 2026 edit count')
  assertExactKeys(
    artifact.editorialPolicy,
    ['id', 'version', 'description'],
    'Lectura 2026 editorial policy',
  )
  assertNonEmptyString(artifact.editorialPolicy.id, 'editorial policy id')
  assertPositiveInteger(artifact.editorialPolicy.version, 'editorial policy version')
  assertNonEmptyString(
    artifact.editorialPolicy.description,
    'editorial policy description',
  )
}

function validateCommonArtifact(artifact) {
  assertEqual(artifact.schemaVersion, 1, `${artifact.id} schema`)
  assertPositiveInteger(artifact.contentVersion, `${artifact.id} contentVersion`)
  assertEqual(artifact.sourceVersionId, RV1909_ID, `${artifact.id} source version`)
  assertEqual(
    artifact.sourceCorpusSha256,
    EXPECTED_RV1909_SHA256,
    `${artifact.id} source corpus hash`,
  )
  assertHash(artifact.contentSha256, `${artifact.id} content hash`)
  assertPositiveInteger(artifact.sizeBytes, `${artifact.id} size`)
  assertEqual(artifact.mimeType, 'application/json+gzip', `${artifact.id} mime type`)
  if (!SAFE_ARTIFACT_NAME.test(artifact.artifactPath)) {
    fail('INVALID_CHANNEL', `${artifact.id} has an unsafe artifact path`)
  }
  assertEqual(
    artifact.expectedBookCount,
    EXPECTED_BOOK_COUNT,
    `${artifact.id} expected book count`,
  )
  assertEqual(
    artifact.includedBookCount,
    EXPECTED_BOOK_COUNT,
    `${artifact.id} included book count`,
  )
}

function deterministicGzip(bytes) {
  const compressed = zlib.gzipSync(bytes, {
    level: zlib.constants.Z_BEST_COMPRESSION,
    mtime: 0,
  })
  // RFC 1952 permits 255 ("unknown") and removes platform-specific OS output.
  compressed[9] = 255
  return compressed
}

function importEd25519PrivateKey(value) {
  let key
  try {
    key = crypto.createPrivateKey(value)
  } catch (error) {
    throw new Error(`Cannot import signing private key: ${error.message}`)
  }
  if (key.asymmetricKeyType !== 'ed25519') {
    throw new Error('Signing key must be Ed25519')
  }
  return key
}

function importEd25519PublicKey(value) {
  let key
  try {
    key = value?.type === 'public' ? value : crypto.createPublicKey(value)
  } catch (error) {
    fail('INVALID_TRUST_KEY', `Cannot import trusted public key: ${error.message}`)
  }
  if (key.asymmetricKeyType !== 'ed25519') {
    fail('INVALID_TRUST_KEY', 'Trusted key must be Ed25519')
  }
  return key
}

function lookupTrustedKey(trustedPublicKeys, keyId) {
  const value =
    trustedPublicKeys instanceof Map
      ? trustedPublicKeys.get(keyId)
      : trustedPublicKeys?.[keyId]
  if (!value) fail('UNKNOWN_KEY', `No trusted public key for ${keyId}`)
  return value
}

function decodeBase64Url(value, label) {
  try {
    const bytes = Buffer.from(value, 'base64url')
    if (bytes.toString('base64url') !== value) throw new Error('not canonical')
    return bytes
  } catch {
    fail('INVALID_CHANNEL', `${label} is not canonical base64url`)
  }
}

function normalizeDate(value, label) {
  if (value instanceof Date && Number.isFinite(value.getTime())) return value
  return parseIsoDate(value, label)
}

function parseIsoDate(value, label) {
  if (typeof value !== 'string') {
    fail('INVALID_CHANNEL', `${label} must be an ISO-8601 string`)
  }
  const date = new Date(value)
  if (!Number.isFinite(date.getTime()) || date.toISOString() !== value) {
    fail('INVALID_CHANNEL', `${label} must be canonical UTC ISO-8601`)
  }
  return date
}

function assertOutputDirectory(repoRoot, outputDir) {
  if (
    outputDir === repoRoot ||
    outputDir === path.parse(outputDir).root
  ) {
    throw new Error('Output directory must not be the repository or filesystem root')
  }
}

function assertCanonicalBookOrder(books, label) {
  assertEqual(books.length, EXPECTED_BOOK_COUNT, `${label} canonical book count`)
  const seen = new Set()
  for (let index = 0; index < books.length; index += 1) {
    assertEqual(books[index].order, index + 1, `${label} canonical order`)
    if (seen.has(books[index].book)) {
      throw new Error(`${label} duplicates book ${books[index].book}`)
    }
    seen.add(books[index].book)
  }
}

function assertPositiveInteger(value, label) {
  if (!Number.isInteger(value) || value < 1) {
    fail('INVALID_CHANNEL', `${label} must be a positive integer`)
  }
}

function assertHash(value, label) {
  if (typeof value !== 'string' || !HASH_PATTERN.test(value)) {
    fail('INVALID_CHANNEL', `${label} must be a lowercase SHA-256`)
  }
}

function assertKeyId(value) {
  if (typeof value !== 'string' || !KEY_ID_PATTERN.test(value)) {
    throw new Error('keyId must contain 1-120 safe characters')
  }
}

function assertNonEmptyString(value, label) {
  if (typeof value !== 'string' || value.trim() === '') {
    throw new Error(`${label} must be a non-empty string`)
  }
}

function assertExactKeys(value, keys, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    fail('INVALID_CHANNEL', `${label} must be an object`)
  }
  const actual = Object.keys(value).sort()
  const expected = [...keys].sort()
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    fail(
      'INVALID_CHANNEL',
      `${label} keys mismatch: expected ${expected.join(', ')}, received ${actual.join(', ')}`,
    )
  }
}

function assertEqual(actual, expected, label) {
  if (actual !== expected) {
    throw new Error(`${label} mismatch: expected ${expected}, received ${actual}`)
  }
}

function resolveContainedPath(root, relativePath) {
  const resolvedRoot = path.resolve(root)
  const resolved = path.resolve(resolvedRoot, ...String(relativePath).split('/'))
  if (!resolved.startsWith(`${resolvedRoot}${path.sep}`)) {
    throw new Error(`Path escapes source root: ${relativePath}`)
  }
  return resolved
}

async function atomicWrite(filePath, bytes) {
  const temporaryPath = `${filePath}.${process.pid}.${crypto.randomUUID()}.tmp`
  await fs.writeFile(temporaryPath, bytes)
  await fs.rename(temporaryPath, filePath)
}

async function readJson(filePath) {
  return parseJson(await fs.readFile(filePath), filePath)
}

function parseJson(bytes, label) {
  try {
    return JSON.parse(Buffer.from(bytes).toString('utf8'))
  } catch {
    throw new Error(`${label} is not valid UTF-8 JSON`)
  }
}

function sortDeep(value) {
  if (Array.isArray(value)) return value.map(sortDeep)
  if (!value || typeof value !== 'object') return value
  return Object.fromEntries(
    Object.keys(value)
      .sort()
      .map((key) => [key, sortDeep(value[key])]),
  )
}

function fail(code, message) {
  throw new ChannelVerificationError(code, message)
}
