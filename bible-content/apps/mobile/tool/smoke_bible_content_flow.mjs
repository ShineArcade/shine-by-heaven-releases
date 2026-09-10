import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import zlib from 'node:zlib'
import { fileURLToPath } from 'node:url'

import { buildBibleContentChannel } from './bible_content_channel.mjs'

const toolRoot = path.dirname(fileURLToPath(import.meta.url))
const contentRoot = path.resolve(toolRoot, '..', '..', '..')
const temporaryRoot = await fs.mkdtemp(path.join(os.tmpdir(), 'shine-bible-content-smoke-'))

try {
  const { privateKey } = crypto.generateKeyPairSync('ed25519')
  const result = await buildBibleContentChannel({
    repoRoot: contentRoot,
    outputDir: temporaryRoot,
    privateKeyPem: privateKey.export({ format: 'pem', type: 'pkcs8' }),
    keyId: 'shine-bible-content-smoke',
  })
  const source = JSON.parse(await fs.readFile(
    path.join(contentRoot, 'apps', 'mobile', 'tool', 'bible_content_channel.v1.source.json'),
    'utf8',
  ))
  assert(result.contentVersion === source.contentVersion, 'channel contentVersion')
  const filter = result.artifacts.find((artifact) => artifact.id === 'RV1909-LECTURA-2026')
  assert(filter?.contentVersion === source.contentVersion, 'filter contentVersion')
  const packageBytes = await fs.readFile(path.join(temporaryRoot, filter.artifactPath))
  const payload = JSON.parse(zlib.gunzipSync(packageBytes).toString('utf8'))
  const secondKings = payload.books.find((book) => book.book === '2KI')
  const verse = secondKings?.verses?.find((entry) => entry.chapter === 3 && entry.verse === 21)
  const edit = verse?.edits?.find((entry) =>
    entry.expected === 'desde todos los que ceñían talabarte arriba',
  )
  assert(
    edit?.replacement === 'desde todos los que tenían edad para portar armas en adelante',
    '2KI.3.21 replacement',
  )
  assert(typeof edit.reason === 'string' && edit.reason.length > 0, '2KI.3.21 reason')
  assert(Array.isArray(edit.evidence) && edit.evidence.length === 2, '2KI.3.21 evidence')
  console.log(JSON.stringify({
    ok: true,
    channelContentVersion: result.contentVersion,
    filterContentVersion: filter.contentVersion,
    filterContentSha256: filter.contentSha256,
    verifiedReference: '2KI.3.21',
  }, null, 2))
} finally {
  await fs.rm(temporaryRoot, { recursive: true, force: true })
}

function assert(condition, label) {
  if (!condition) throw new Error(`Bible content flow smoke failed: ${label}`)
}
