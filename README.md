# SHINE Releases

Public release bucket for SHINE installers and auto-update metadata.

This repository is intentionally small and public. It does **not** contain SHINE source code or user content. It only hosts release assets that Electron/electron-updater can download.

## Current Stable Release

- Version: `1.1.86`
- Release: https://github.com/ShineArcade/shine-by-heaven-releases/releases/tag/v1.1.86
- Installer: https://github.com/ShineArcade/shine-by-heaven-releases/releases/download/v1.1.86/SHINE.Setup.1.1.86.exe
- Public download route: https://shinebyheaven.app/api/download/latest

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

## Notes

GitHub normalizes release asset filenames with spaces into dots. `latest.yml` must point to dotted asset names, for example:

```yaml
path: SHINE.Setup.1.1.86.exe
```
