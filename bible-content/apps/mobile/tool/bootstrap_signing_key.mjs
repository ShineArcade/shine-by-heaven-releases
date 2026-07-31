import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'

const privatePath = process.argv[2]
const publicPath = process.argv[3]
if (!privatePath || !publicPath) {
  throw new Error('Usage: node bootstrap_signing_key.mjs <private.pem> <public.pem>')
}

const { privateKey, publicKey } = crypto.generateKeyPairSync('ed25519')
await fs.mkdir(path.dirname(path.resolve(privatePath)), { recursive: true })
await fs.mkdir(path.dirname(path.resolve(publicPath)), { recursive: true })
await fs.writeFile(
  path.resolve(privatePath),
  privateKey.export({ type: 'pkcs8', format: 'pem' }),
  { mode: 0o600 },
)
await fs.writeFile(
  path.resolve(publicPath),
  publicKey.export({ type: 'spki', format: 'pem' }),
)

console.log(JSON.stringify({
  publicKeySha256: crypto
    .createHash('sha256')
    .update(publicKey.export({ type: 'spki', format: 'der' }))
    .digest('hex'),
}))
