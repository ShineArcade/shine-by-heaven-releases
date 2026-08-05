# SHINE Bible Content

This directory is the single public editorial source for:

- Reina-Valera 1909 (`RV1909`), preserved exactly;
- the optional and reversible `RV1909-LECTURA-2026` reading layer.

The 66 files under `apps/mobile/assets/bible_direction/` are edited only
through reviewed change sets under `editorial-changes/`. The deterministic
builder validates every source hash, verse offset, expected string and overlap
before creating a package.

A reviewed rule may target one `chapter` and `verse`, or a `references` list
when the same exact replacement was checked in several verses. Single-word
rules match whole words only; a word embedded inside a longer form is rejected.
The generated book files still record every resulting offset separately.

## Update flow

1. Add a monotonic `editorial-changes/vN.json` change set.
2. Apply it locally with:

   `node apps/mobile/tool/apply_editorial_change_set.mjs`

3. Build the filter with:

   `node apps/mobile/tool/build_reading_2026_package.mjs --package-only`

4. Push the reviewed source to `main`.
5. GitHub Actions verifies and publishes `channel/channel-stable.json`, the
   versioned artifacts and immutable release `bible-content-vN`.
6. Website, Mobile and Desktop compare `contentVersion`, validate the package
   and retain their last known valid copy if anything fails.

The Ed25519 signature is an integrity mechanism. It prevents a modified or
forged package from silently replacing the official channel; it is not an
external theological or legal approval requirement.

## Stable endpoint

`https://raw.githubusercontent.com/ShineArcade/shine-by-heaven-releases/main/bible-content/channel/channel-stable.json`

The filter preference remains local to each device. Updating content never
turns the user's switch on or off.
