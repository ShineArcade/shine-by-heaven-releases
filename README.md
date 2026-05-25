# SHINE By Heaven Releases

Public release bucket for SHINE By Heaven installers and auto-update metadata.

This repository is intentionally small and public. It does **not** contain SHINE source code or user content. It only hosts release assets that Electron/electron-updater can download.

## Current Stable Release

- Version: `1.0.2`
- Release: https://github.com/ShineArcade/shine-by-heaven-releases/releases/tag/v1.0.2
- Installer: https://github.com/ShineArcade/shine-by-heaven-releases/releases/latest/download/SHINE.By.Heaven.Setup.1.0.2.exe
- Update feed file: https://github.com/ShineArcade/shine-by-heaven-releases/releases/latest/download/latest.yml

## Electron Updater Feed

For the current SHINE app implementation, the generic feed base URL is:

```text
https://github.com/ShineArcade/shine-by-heaven-releases/releases/latest/download/
```

The installed app should fetch:

```text
latest.yml
SHINE.By.Heaven.Setup.<version>.exe
SHINE.By.Heaven.Setup.<version>.exe.blockmap
```

## Required Assets Per Release

Each release must include:

- `SHINE.By.Heaven.Setup.<version>.exe`
- `SHINE.By.Heaven.Setup.<version>.exe.blockmap`
- `latest.yml`

Optional but useful:

- `release-report.md`
- `release-report.json`

## Notes

GitHub normalizes release asset filenames with spaces into dots. For this reason `latest.yml` must point to dotted asset names, for example:

```yaml
path: SHINE.By.Heaven.Setup.1.0.2.exe
```

not:

```yaml
path: SHINE By Heaven Setup 1.0.2.exe
```