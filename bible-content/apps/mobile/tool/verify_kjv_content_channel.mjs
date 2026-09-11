import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { verifyKjvContentChannel } from './kjv_content_channel.mjs'

const channelPath = argument('--channel')
const publicKeyFile = argument('--public-key-file')
const keyId = argument('--key-id')
if (!channelPath || !publicKeyFile || !keyId) throw new Error('Missing required KJV verification arguments')
const publicKey = crypto.createPublicKey(await fs.readFile(path.resolve(publicKeyFile), 'utf8'))
console.log(JSON.stringify(await verifyKjvContentChannel({ channelPath: path.resolve(channelPath), trustedPublicKeys: new Map([[keyId, publicKey]]), now: new Date(argument('--now') ?? Date.now()) }), null, 2))
function argument(name) { const index = process.argv.indexOf(name); return index < 0 ? null : process.argv[index + 1] }
