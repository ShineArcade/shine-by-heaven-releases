import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { buildKjvContentChannel } from './kjv_content_channel.mjs'

const contentRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
const packageSource = JSON.parse(await fs.readFile(path.join(contentRoot, 'apps', 'mobile', 'assets', 'bible_direction', 'kjv', 'reading_2026.package-source.json'), 'utf8'))
const outputDir = await fs.mkdtemp(path.join(os.tmpdir(), 'shine-kjv-channel-'))
try {
  const { privateKey } = crypto.generateKeyPairSync('ed25519')
  const result = await buildKjvContentChannel({ repoRoot: contentRoot, outputDir, privateKeyPem: privateKey.export({ format: 'pem', type: 'pkcs8' }), keyId: 'shine-kjv-smoke' })
  if (result.contentVersion !== packageSource.contentVersion) throw new Error('Unexpected KJV content version')
  console.log(JSON.stringify({ ok: true, ...result }, null, 2))
} finally {
  await fs.rm(outputDir, { recursive: true, force: true })
}
