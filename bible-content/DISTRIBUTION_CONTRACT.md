# SHINE Reading 2026 distribution contract

Status date: 2026-09-04

## Authority

`ShineArcade/shine-by-heaven-releases` is the only publication authority for
shared Bible reading-layer updates. Consumer repositories must not be treated
as independent editorial authorities.

For RV1909, reviewed changes live under `editorial-changes/`. A push to `main`
causes GitHub Actions to apply the latest monotonic change set, rebuild the
deterministic package, sign the channel with the protected Ed25519 key, verify
the exact bytes, commit the generated pointer and publish an immutable release.

## Current consumers

| Consumer | Source | Behavior |
| --- | --- | --- |
| Mobile | signed `channel-stable.json` | Release builds check the channel and retain the last verified revision on failure. |
| Desktop | signed `channel-stable.json` | Startup checks the channel; install is atomic, monotonic and reversible to the bundled fallback. |
| Website | signed `channel-stable.json` | Every production build synchronizes the channel before generating public Bible pages. |

The canonical endpoint is:

`https://raw.githubusercontent.com/ShineArcade/shine-by-heaven-releases/main/bible-content/channel/channel-stable.json`

The website deployment hook may be triggered after a successful channel
publication. Mobile and Desktop do not require source-file copies from their
application repositories to receive a newer verified RV1909 reading layer.

## Required publication gate

A revision is ready only when all of these pass:

1. The new change-set version is greater than the published channel version.
2. Every replacement identifies one exact source occurrence and records its
   reason; evidence links are required for deep contextual changes.
3. Reapplying the change set is idempotent.
4. The package contains all 66 books and reproduces the pinned corpus hashes.
5. The ephemeral signing smoke test validates source, package, reason, evidence
   and the signed envelope without using the production private key.
6. GitHub Actions signs and verifies the production bytes before changing the
   stable pointer.

Equal-version/different-hash releases are rejected as conflicts. Downgrades,
bad signatures, wrong corpus hashes, corrupt downloads and incomplete packages
must leave the last known valid revision active.

## KJV channel

`KJV-READING-2026` uses the separate signed pointer
`channel/kjv-channel-stable.json`. It is intentionally not added as a third
artifact to the RV1909 v1 channel because released v1 clients require exactly
the original two-artifact shape. Consumers must verify the same Ed25519 trust
key, the pinned KJV corpus hash, the monotonic KJV content version, and the
downloaded artifact before an atomic install. Until each consumer receiver has
passed its integration test, publication of the pointer is described as
available, while receipt remains independently verified per consumer.
