import fs from 'node:fs/promises'
import path from 'node:path'

import {
  CHANNEL_FORMAT,
  ChannelVerificationError,
  verifyBibleContentChannel,
} from './bible_content_channel.mjs'

const TRUST_STORE_FORMAT = 'shine-bible-content-trust-store'
const TRUST_STORE_SCHEMA_VERSION = 1
const CURRENT_POINTER_FORMAT = 'shine-bible-content-current-release'
const CURRENT_POINTER_SCHEMA_VERSION = 1
const KEY_ID_PATTERN = /^[A-Za-z0-9._:-]{1,120}$/
const HASH_PATTERN = /^[a-f0-9]{64}$/

export async function installBibleContentChannel({
  channelPath,
  installRoot,
  trustStore,
  now = new Date(),
  beforeActivate,
}) {
  const resolvedChannelPath = path.resolve(channelPath)
  const resolvedInstallRoot = path.resolve(installRoot)
  const sourceRoot = path.dirname(resolvedChannelPath)
  const lockPath = path.join(resolvedInstallRoot, '.install.lock')
  const stagingRoot = path.join(resolvedInstallRoot, '.staging')
  const releasesRoot = path.join(resolvedInstallRoot, 'releases')

  await fs.mkdir(resolvedInstallRoot, { recursive: true })
  const lock = await acquireInstallLock(lockPath)
  let stagePath
  try {
    const verificationTime = normalizeDate(now, 'now')
    const trustedPublicKeys = trustedKeysAt(trustStore, verificationTime)
    const current = await readCurrentRelease(resolvedInstallRoot)
    const sourceVerification = await verifyBibleContentChannel({
      channelPath: resolvedChannelPath,
      artifactRoot: sourceRoot,
      trustedPublicKeys,
      currentRelease: current
        ? {
            contentVersion: current.contentVersion,
            contentSha256: current.contentSha256,
          }
        : null,
      now: verificationTime,
    })

    if (sourceVerification.decision === 'NO_OP') {
      return {
        decision: 'NO_OP',
        current,
      }
    }

    const releaseName = releaseDirectoryName(sourceVerification)
    const releasePath = path.join(releasesRoot, releaseName)
    stagePath = path.join(
      stagingRoot,
      `${releaseName}.${process.pid}.${randomToken()}`,
    )
    await fs.mkdir(stagePath, { recursive: true })

    const channel = await readJson(resolvedChannelPath)
    await copyExclusive(resolvedChannelPath, path.join(stagePath, 'channel.json'))
    for (const artifact of channel.payload.artifacts) {
      await copyExclusive(
        path.join(sourceRoot, artifact.artifactPath),
        path.join(stagePath, artifact.artifactPath),
      )
    }

    const stagedVerification = await verifyBibleContentChannel({
      channelPath: path.join(stagePath, 'channel.json'),
      artifactRoot: stagePath,
      trustedPublicKeys,
      currentRelease: current
        ? {
            contentVersion: current.contentVersion,
            contentSha256: current.contentSha256,
          }
        : null,
      now: verificationTime,
    })
    if (
      stagedVerification.contentSha256 !== sourceVerification.contentSha256 ||
      stagedVerification.contentVersion !== sourceVerification.contentVersion
    ) {
      fail(
        'STAGING_CHANGED',
        'The staged release does not match the verified source release',
      )
    }

    if (beforeActivate) {
      await beforeActivate({
        stagePath,
        releasePath,
        verification: stagedVerification,
      })
    }

    await fs.mkdir(releasesRoot, { recursive: true })
    const existingRelease = await pathExists(releasePath)
    if (existingRelease) {
      const existingVerification = await verifyBibleContentChannel({
        channelPath: path.join(releasePath, 'channel.json'),
        artifactRoot: releasePath,
        trustedPublicKeys,
        now: verificationTime,
      })
      if (
        existingVerification.contentVersion !== stagedVerification.contentVersion ||
        existingVerification.contentSha256 !== stagedVerification.contentSha256
      ) {
        fail(
          'RELEASE_CONFLICT',
          'An existing release directory has incompatible verified content',
        )
      }
      await fs.rm(stagePath, { recursive: true, force: true })
      stagePath = null
    } else {
      await fs.rename(stagePath, releasePath)
      stagePath = null
    }

    const installedVerification = await verifyBibleContentChannel({
      channelPath: path.join(releasePath, 'channel.json'),
      artifactRoot: releasePath,
      trustedPublicKeys,
      now: verificationTime,
    })
    const nextCurrent = {
      format: CURRENT_POINTER_FORMAT,
      schemaVersion: CURRENT_POINTER_SCHEMA_VERSION,
      contentVersion: installedVerification.contentVersion,
      contentSha256: installedVerification.contentSha256,
      keyId: installedVerification.keyId,
      releaseDirectory: path.relative(resolvedInstallRoot, releasePath),
    }
    await atomicWriteJson(
      path.join(resolvedInstallRoot, 'current.json'),
      nextCurrent,
    )

    return {
      decision: 'APPLY',
      current: nextCurrent,
      previous: current,
    }
  } finally {
    if (stagePath) {
      await fs.rm(stagePath, { recursive: true, force: true })
    }
    await removeEmptyDirectory(stagingRoot)
    await lock.close()
    await fs.rm(lockPath, { force: true })
  }
}

export function trustedKeysAt(trustStore, now = new Date()) {
  validateTrustStore(trustStore)
  const verificationTime = normalizeDate(now, 'now')
  const trusted = new Map()
  for (const key of trustStore.keys) {
    if (key.status !== 'active') continue
    const validFrom = normalizeDate(key.validFrom, `key ${key.keyId} validFrom`)
    const validUntil = normalizeDate(key.validUntil, `key ${key.keyId} validUntil`)
    if (verificationTime < validFrom || verificationTime >= validUntil) continue
    trusted.set(key.keyId, key.publicKeyPem)
  }
  return trusted
}

export async function readCurrentRelease(installRoot) {
  const pointerPath = path.join(path.resolve(installRoot), 'current.json')
  try {
    const current = await readJson(pointerPath)
    validateCurrentPointer(current)
    const releasePath = path.resolve(installRoot, current.releaseDirectory)
    const releasesRoot = path.resolve(installRoot, 'releases')
    if (!isWithin(releasesRoot, releasePath)) {
      fail(
        'INVALID_CURRENT_POINTER',
        'Current release directory must remain inside releases',
      )
    }
    return current
  } catch (error) {
    if (error?.code === 'ENOENT') return null
    throw error
  }
}

function validateTrustStore(value) {
  if (
    !isPlainObject(value) ||
    value.format !== TRUST_STORE_FORMAT ||
    value.schemaVersion !== TRUST_STORE_SCHEMA_VERSION ||
    !Array.isArray(value.keys) ||
    value.keys.length === 0
  ) {
    fail('INVALID_TRUST_STORE', 'Trust store envelope is invalid')
  }
  const seen = new Set()
  for (const key of value.keys) {
    if (
      !isPlainObject(key) ||
      !KEY_ID_PATTERN.test(key.keyId ?? '') ||
      key.algorithm !== 'Ed25519' ||
      !['active', 'revoked'].includes(key.status) ||
      typeof key.publicKeyPem !== 'string' ||
      key.publicKeyPem.length < 40 ||
      typeof key.validFrom !== 'string' ||
      typeof key.validUntil !== 'string'
    ) {
      fail('INVALID_TRUST_STORE', 'Trust store contains an invalid key record')
    }
    if (seen.has(key.keyId)) {
      fail('INVALID_TRUST_STORE', `Duplicate trust key ${key.keyId}`)
    }
    seen.add(key.keyId)
    const validFrom = normalizeDate(key.validFrom, `key ${key.keyId} validFrom`)
    const validUntil = normalizeDate(key.validUntil, `key ${key.keyId} validUntil`)
    if (validFrom >= validUntil) {
      fail('INVALID_TRUST_STORE', `Invalid validity interval for ${key.keyId}`)
    }
  }
}

function validateCurrentPointer(value) {
  const keys = Object.keys(value ?? {}).sort()
  const expected = [
    'contentSha256',
    'contentVersion',
    'format',
    'keyId',
    'releaseDirectory',
    'schemaVersion',
  ].sort()
  if (
    !isPlainObject(value) ||
    JSON.stringify(keys) !== JSON.stringify(expected) ||
    value.format !== CURRENT_POINTER_FORMAT ||
    value.schemaVersion !== CURRENT_POINTER_SCHEMA_VERSION ||
    !Number.isSafeInteger(value.contentVersion) ||
    value.contentVersion < 1 ||
    !HASH_PATTERN.test(value.contentSha256 ?? '') ||
    !KEY_ID_PATTERN.test(value.keyId ?? '') ||
    typeof value.releaseDirectory !== 'string' ||
    value.releaseDirectory.length === 0
  ) {
    fail('INVALID_CURRENT_POINTER', 'Current release pointer is invalid')
  }
}

async function acquireInstallLock(lockPath) {
  try {
    return await fs.open(lockPath, 'wx')
  } catch (error) {
    if (error?.code === 'EEXIST') {
      fail('INSTALL_BUSY', 'Another Bible content installation is active')
    }
    throw error
  }
}

async function copyExclusive(source, destination) {
  await fs.copyFile(source, destination, 1)
}

async function atomicWriteJson(filePath, value) {
  const temporaryPath = `${filePath}.${process.pid}.${randomToken()}.tmp`
  await fs.writeFile(
    temporaryPath,
    Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8'),
    { flag: 'wx' },
  )
  await fs.rename(temporaryPath, filePath)
}

async function removeEmptyDirectory(directoryPath) {
  try {
    await fs.rmdir(directoryPath)
  } catch (error) {
    if (!['ENOENT', 'ENOTEMPTY', 'EEXIST'].includes(error?.code)) throw error
  }
}

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, 'utf8'))
}

function releaseDirectoryName(verification) {
  return `v${verification.contentVersion}-${verification.contentSha256}`
}

function randomToken() {
  return Math.random().toString(16).slice(2)
}

function normalizeDate(value, field) {
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.valueOf())) {
    fail('INVALID_TIME', `${field} must be a valid date`)
  }
  return date
}

function isWithin(root, candidate) {
  const relative = path.relative(root, candidate)
  return (
    relative === '' ||
    (!relative.startsWith('..') && !path.isAbsolute(relative))
  )
}

function isPlainObject(value) {
  return (
    value !== null &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    Object.getPrototypeOf(value) === Object.prototype
  )
}

async function pathExists(filePath) {
  try {
    await fs.access(filePath)
    return true
  } catch (error) {
    if (error?.code === 'ENOENT') return false
    throw error
  }
}

function fail(code, message) {
  throw new ChannelVerificationError(code, message)
}
