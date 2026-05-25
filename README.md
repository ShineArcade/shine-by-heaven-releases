# SHINE Releases

Public release bucket for SHINE installers and auto-update metadata.

This repository is intentionally small and public. It does **not** contain SHINE source code or user content. It only hosts release assets that Electron/electron-updater can download.

## Current Stable Release

- Version: `1.0.3`
- Release: https://github.com/ShineArcade/shine-by-heaven-releases/releases/tag/v1.0.3
- Installer: https://github.com/ShineArcade/shine-by-heaven-releases/releases/latest/download/SHINE.Setup.1.0.3.exe
- Update feed file: https://github.com/ShineArcade/shine-by-heaven-releases/releases/latest/download/latest.yml

## Electron Updater Feed

For the current SHINE app implementation, the generic feed base URL is:

```text
https://github.com/ShineArcade/shine-by-heaven-releases/releases/latest/download/
```

The installed app fetches:

```text
latest.yml
SHINE.Setup.<version>.exe
SHINE.Setup.<version>.exe.blockmap
```

## Required Assets Per Release

Each release must include:

- `SHINE.Setup.<version>.exe`
- `SHINE.Setup.<version>.exe.blockmap`
- `latest.yml`

Optional but useful:

- `release-report.md`
- `release-report.json`

## Notes

GitHub normalizes release asset filenames with spaces into dots. `latest.yml` must point to dotted asset names, for example:

```yaml
path: SHINE.Setup.1.0.3.exe
```