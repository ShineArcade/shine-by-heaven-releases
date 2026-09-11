import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'
import { buildKjvContentChannel } from './kjv_content_channel.mjs'

const contentRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
const outputDir = argument('--out-dir')
const keyId = argument('--key-id')
const keyFile = argument('--private-key-file')
if (!outputDir || !keyId) throw new Error('Usage: --out-dir <directory> --key-id <id> [--private-key-file <PEM>]')
const privateKeyPem = keyFile ? await fs.readFile(path.resolve(keyFile), 'utf8') : process.env.SHINE_BIBLE_CONTENT_SIGNING_PRIVATE_KEY_PEM?.replaceAll('\\n', '\n')
if (!privateKeyPem) throw new Error('KJV signing key missing')
console.log(JSON.stringify(await buildKjvContentChannel({ repoRoot: contentRoot, outputDir: path.resolve(outputDir), privateKeyPem, keyId }), null, 2))
function argument(name) { const index = process.argv.indexOf(name); return index < 0 ? null : process.argv[index + 1] }
