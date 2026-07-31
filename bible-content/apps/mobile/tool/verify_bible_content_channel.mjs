import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'

import { verifyBibleContentChannel } from './bible_content_channel.mjs'

const channelPath = readArgument('--channel')
const publicKeyFile = readArgument('--public-key-file')
const keyId = readArgument('--key-id')
const artifactRoot = readArgument('--artifact-root')
const now = readArgument('--now')
const currentVersion = readArgument('--current-version')
const currentSha256 = readArgument('--current-sha256')

if (!channelPath || !publicKeyFile || !keyId) {
  throw new Error(
    'Usage: node apps/mobile/tool/verify_bible_content_channel.mjs ' +
      '--channel <channel-stable.json> --public-key-file <PEM> --key-id <id> ' +
      '[--artifact-root <directory>] [--now <ISO-8601>] ' +
      '[--current-version <integer> --current-sha256 <hash>]',
  )
}
if ((currentVersion == null) !== (currentSha256 == null)) {
  throw new Error(
    '--current-version and --current-sha256 must be supplied together',
  )
}

const trustedPublicKey = await fs.readFile(path.resolve(publicKeyFile), 'utf8')
const result = await verifyBibleContentChannel({
  channelPath: path.resolve(channelPath),
  ...(artifactRoot ? { artifactRoot: path.resolve(artifactRoot) } : {}),
  trustedPublicKeys: new Map([[keyId, trustedPublicKey]]),
  ...(now ? { now } : {}),
  ...(currentVersion
    ? {
        currentRelease: {
          contentVersion: Number(currentVersion),
          contentSha256: currentSha256,
        },
      }
    : {}),
})

console.log(JSON.stringify(result, null, 2))

function readArgument(name) {
  const index = process.argv.indexOf(name)
  if (index < 0) return null
  const value = process.argv[index + 1]
  if (!value || value.startsWith('--')) {
    throw new Error(`${name} requires a value`)
  }
  return value
}
