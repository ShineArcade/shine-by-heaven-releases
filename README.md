# SHINE Releases

Public release bucket for SHINE installers and auto-update metadata.

This repository is intentionally small and public. It does **not** contain SHINE source code or user content. It only hosts release assets that Electron/electron-updater can download.

## Current Stable Release

- Version: `1.1.86`
- Release: https://github.com/ShineArcade/shine-by-heaven-releases/releases/tag/v1.1.86
- Installer: https://github.com/ShineArcade/shine-by-heaven-releases/releases/download/v1.1.86/SHINE.Setup.1.1.86.exe
- Public download route: https://shinebyheaven.app/api/download/latest

Supported Windows target:

- Minimum practical configuration: Windows 10 22H2 x64, 2 CPU cores, 4 GB RAM, 3 GB free disk, 1280 x 720 display.
- Recommended: Windows 11 x64, 4 CPU cores, 8 GB RAM, SSD, 1920 x 1080 display.
- Windows 7, 8, 8.1, 32-bit Windows, and Windows ARM are not release targets.

## Electron Updater Feed

Generic feed base URL:

```text
https://github.com/ShineArcade/shine-by-heaven-releases/releases/download/app-latest/
```

Required app resource inside each installed build:

```text
resources/app-update.yml
```

Required assets per release:

- `SHINE.Setup.<version>.exe`
- `SHINE.Setup.<version>.exe.blockmap`
- `latest.yml`

Optional but useful:

- `release-report.md`
- `release-report.json`

## macOS channel

macOS is not publicly available yet. Its updater is isolated from Windows and will use this channel only after signed, notarized, and physically tested artifacts exist:

```text
https://github.com/ShineArcade/shine-by-heaven-releases/releases/download/app-mac-latest/
```

Expected Mac assets:

- `SHINE-<version>-universal.dmg`
- `SHINE-<version>-universal-mac.zip`
- `latest-mac.yml`
- ZIP blockmap and SHA-256 release evidence

Do not create or move the `app-mac-latest` channel to an unsigned candidate.

Planned Mac target: macOS 12 or later on Intel x64 and Apple Silicon arm64. It remains unavailable until native runtimes, signing, notarization, auto-update, and physical tests pass.

## One source version, platform-specific artifacts

Windows and Mac installers must be built from the same private source commit and the same `package.json` version. A product fix is made once. Native runtimes, package signing, artifact inspection, and updater metadata remain platform-specific. This repository stores only the resulting public artifacts; it must not contain Desktop source or user data.

## Notes

GitHub normalizes release asset filenames with spaces into dots. `latest.yml` must point to dotted asset names, for example:

```yaml
path: SHINE.Setup.1.1.86.exe
```
