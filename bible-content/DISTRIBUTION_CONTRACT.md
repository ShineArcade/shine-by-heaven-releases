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

## KJV limitation

`KJV-READING-2026` is currently bundled independently in Mobile, Desktop and
Website. It is **not yet distributed by this signed runtime channel**. Therefore
KJV is `NOT_READY_SINGLE_SOURCE_DISTRIBUTION`, even though its current package
can be parity-checked across the three source repositories.

Do not add KJV as a third artifact to the existing v1 channel: released v1
clients require exactly the RV1909 corpus plus its reading filter and would
reject that incompatible shape. KJV needs a separate signed channel (or a
backward-compatible v2 receiver) and consumer tests before it can be called an
automatic one-source update.
