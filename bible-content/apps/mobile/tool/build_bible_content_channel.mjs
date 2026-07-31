import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

import { buildBibleContentChannel } from './bible_content_channel.mjs'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(scriptDir, '..', '..', '..')
const outputDir = readArgument('--out-dir')
const keyId = readArgument('--key-id')
const privateKeyFile = readArgument('--private-key-file')
const privateKeyEnvName =
  readArgument('--private-key-env') ??
  'SHINE_BIBLE_CONTENT_SIGNING_PRIVATE_KEY_PEM'
const sourceConfigPath = readArgument('--source-config')

if (!outputDir || !keyId) {
  throw new Error(
    'Usage: node apps/mobile/tool/build_bible_content_channel.mjs ' +
      '--out-dir <directory> --key-id <id> ' +
      '[--private-key-file <PEM> | --private-key-env <name>] ' +
      '[--source-config <JSON>]',
  )
}
if (privateKeyFile && process.argv.includes('--private-key-env')) {
  throw new Error('Choose either --private-key-file or --private-key-env')
}

const privateKeyPem = privateKeyFile
  ? await fs.readFile(path.resolve(privateKeyFile), 'utf8')
  : readPrivateKeyEnvironment(privateKeyEnvName)

const result = await buildBibleContentChannel({
  repoRoot,
  outputDir: path.resolve(outputDir),
  privateKeyPem,
  keyId,
  ...(sourceConfigPath
    ? { sourceConfigPath: path.resolve(sourceConfigPath) }
    : {}),
})

console.log(JSON.stringify(result, null, 2))

function readPrivateKeyEnvironment(name) {
  const value = process.env[name]
  if (!value) {
    throw new Error(
      `Signing key is missing. Set ${name} or pass --private-key-file.`,
    )
  }
  return value.includes('\\n') ? value.replaceAll('\\n', '\n') : value
}

function readArgument(name) {
  const index = process.argv.indexOf(name)
  if (index < 0) return null
  const value = process.argv[index + 1]
  if (!value || value.startsWith('--')) {
    throw new Error(`${name} requires a value`)
  }
  return value
}
