import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'

export const KJV_CHANNEL_FORMAT = 'shine-public-kjv-reading-channel'
export const KJV_CHANNEL_ID = 'shine-public-kjv-reading-stable'
export const KJV_SOURCE_SHA256 = '4e2c28113d053e64dacef2792a8d3bcfb32367320f549ef2c2f03b3122902939'

export async function buildKjvContentChannel({ repoRoot, outputDir, privateKeyPem, keyId }) {
  const manifestPath = path.join(repoRoot, 'apps', 'mobile', 'assets', 'bible_direction', 'kjv', 'packages', 'reading_2026.kjv.v1.manifest.json')
  const packagePath = path.join(repoRoot, 'apps', 'mobile', 'assets', 'bible_direction', 'kjv', 'packages', 'reading_2026.kjv.v1.package.json.gz')
  const manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'))
  const bytes = await fs.readFile(packagePath)
  assert(manifest.sourceCorpusSha256 === KJV_SOURCE_SHA256, 'source corpus hash')
  assert(manifest.contentSha256 === sha256(bytes), 'artifact hash')
  assert(manifest.coverage.includedBookCount === 66, 'book count')
  const artifactName = `reading_2026.kjv.v${manifest.contentVersion}.package.json.gz`
  const payload = {
    channelId: KJV_CHANNEL_ID,
    contentVersion: manifest.contentVersion,
    issuedAt: '2026-09-10T00:00:00.000Z',
    expiresAt: '2028-09-10T00:00:00.000Z',
    distributionScope: 'public',
    updatePolicy: {
      versionAuthority: 'contentVersion', equalVersionEqualHash: 'no-op',
      equalVersionDifferentHash: 'reject-conflict', lowerVersion: 'reject-downgrade',
      higherVersion: 'accept-after-verification',
    },
    artifacts: [{
      kind: 'reading-filter', id: 'KJV-READING-2026', schemaVersion: 1,
      contentVersion: manifest.contentVersion, sourceVersionId: 'KJV',
      sourceCorpusSha256: KJV_SOURCE_SHA256, contentSha256: manifest.contentSha256,
      sizeBytes: bytes.length, mimeType: 'application/json+gzip', artifactPath: artifactName,
      expectedBookCount: 66, includedBookCount: 66, coverage: manifest.coverage,
      editorialPolicy: manifest.editorialPolicy,
    }],
  }
  const payloadBytes = Buffer.from(canonicalJson(payload), 'utf8')
  const privateKey = crypto.createPrivateKey(privateKeyPem)
  const channel = {
    format: KJV_CHANNEL_FORMAT, schemaVersion: 1, payload,
    contentSha256: sha256(payloadBytes),
    signature: { algorithm: 'Ed25519', keyId, signedObject: 'payload', value: crypto.sign(null, payloadBytes, privateKey).toString('base64url') },
  }
  await fs.mkdir(outputDir, { recursive: true })
  await fs.writeFile(path.join(outputDir, artifactName), bytes)
  await fs.writeFile(path.join(outputDir, 'kjv-channel-stable.json'), `${JSON.stringify(channel, null, 2)}\n`, 'utf8')
  await verifyKjvContentChannel({ channelPath: path.join(outputDir, 'kjv-channel-stable.json'), artifactRoot: outputDir, trustedPublicKeys: new Map([[keyId, crypto.createPublicKey(privateKey)]]), now: new Date(payload.issuedAt) })
  return { channelPath: path.join(outputDir, 'kjv-channel-stable.json'), contentVersion: payload.contentVersion, contentSha256: channel.contentSha256, artifactName, artifactSha256: manifest.contentSha256 }
}

export async function verifyKjvContentChannel({ channelPath, artifactRoot = path.dirname(channelPath), trustedPublicKeys, now = new Date() }) {
  const channel = JSON.parse(await fs.readFile(channelPath, 'utf8'))
  assert(channel.format === KJV_CHANNEL_FORMAT && channel.schemaVersion === 1, 'channel envelope')
  assert(channel.payload.channelId === KJV_CHANNEL_ID, 'channel id')
  assert(new Date(channel.payload.expiresAt) > now, 'channel expiry')
  const payloadBytes = Buffer.from(canonicalJson(channel.payload), 'utf8')
  assert(sha256(payloadBytes) === channel.contentSha256, 'payload hash')
  const publicKey = trustedPublicKeys.get(channel.signature.keyId)
  assert(publicKey, 'trusted key')
  assert(crypto.verify(null, payloadBytes, publicKey, Buffer.from(channel.signature.value, 'base64url')), 'signature')
  assert(channel.payload.artifacts.length === 1, 'artifact count')
  const artifact = channel.payload.artifacts[0]
  assert(artifact.id === 'KJV-READING-2026' && artifact.sourceCorpusSha256 === KJV_SOURCE_SHA256, 'artifact identity')
  const bytes = await fs.readFile(path.join(artifactRoot, artifact.artifactPath))
  assert(bytes.length === artifact.sizeBytes && sha256(bytes) === artifact.contentSha256, 'artifact bytes')
  return { ok: true, contentVersion: channel.payload.contentVersion, contentSha256: channel.contentSha256, artifactSha256: artifact.contentSha256 }
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(',')}}`
  return JSON.stringify(value)
}
function sha256(value) { return crypto.createHash('sha256').update(value).digest('hex') }
function assert(condition, label) { if (!condition) throw new Error(`KJV content channel validation failed: ${label}`) }
