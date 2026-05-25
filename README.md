# SHINE Releases

Public release bucket for SHINE installers and auto-update metadata.

This repository is intentionally small and public. It does **not** contain SHINE source code or user content. It only hosts release assets that Electron/electron-updater can download.

## Current Stable Release

- Version: `1.0.5`
- Release: https://github.com/ShineArcade/shine-by-heaven-releases/releases/tag/v1.0.5
- Installer: https://github.com/ShineArcade/shine-by-heaven-releases/releases/latest/download/SHINE.Setup.1.0.5.exe
- Update feed file: https://github.com/ShineArcade/shine-by-heaven-releases/releases/latest/download/latest.yml

## Electron Updater Feed

Generic feed base URL:

```text
https://github.com/ShineArcade/shine-by-heaven-releases/releases/latest/download/
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

## Notes

GitHub normalizes release asset filenames with spaces into dots. `latest.yml` must point to dotted asset names, for example:

```yaml
path: SHINE.Setup.1.0.5.exe
```