# Cross-platform catalog

What lives where regardless of OS. Read this always; add `macos.md` or `linux.md` for the platform you're on.

## Developer dependency caches (Tier 3 while in use, Tier 1 when tool abandoned)

| Location | Tool | Native cleaner |
|---|---|---|
| `~/.npm`, `~/.yarn`, `~/.pnpm-store`, `~/.bun` | Node | `npm cache clean --force`, `yarn cache clean`, `pnpm store prune` |
| `~/.nvm/versions` | Node versions | remove old versions via `nvm uninstall` |
| `~/.gradle/caches`, `~/.m2/repository`, `~/.ivy2`, `~/.sbt` | JVM builds | delete folder (re-downloads on next build) |
| Coursier cache (`~/Library/Caches/Coursier` / `~/.cache/coursier`) | Scala | delete folder (re-downloads) |
| pip cache (`~/Library/Caches/pip` / `~/.cache/pip`) | Python | `pip cache purge` |
| `~/.conda/pkgs`, `~/.pyenv/versions` | Python envs | `conda clean --all`; old pyenv versions |
| `~/.cargo/registry`, `~/.rustup/toolchains` | Rust | old toolchains via `rustup toolchain list` then `rustup toolchain uninstall` |
| `~/.docker`, Docker images/volumes | Docker | `docker system df` to audit, `docker system prune -a` (ask first — removes unused images) |
| Playwright / Cypress browser caches | Test browsers | old versions Tier 2; current one breaks tests until reinstall |
| `~/.cache/huggingface`, `~/.ollama/models`, other ML model stores | ML models | often the biggest single item on a dev machine; re-downloadable but slow — ask |

## Version-stacking apps (one folder per version, old ones never removed)

- **JetBrains IDEs**: `<config-root>/JetBrains/<Product><Version>` — stacks identically in the config, cache, *and* log roots. Current version: `build.txt` inside the installed app. Old Toolbox 1.x also left whole IDE binaries under `JetBrains/Toolbox/apps/`.
- **Android Studio**: same pattern under `Google/AndroidStudio<Version>`. The SDK lives separately (`~/Library/Android` or `~/Android/Sdk`), emulators in `~/.android`.
- Many Electron apps keep old updater payloads (ShipIt/squirrel folders).

Rule: find the installed version first, then everything older is Tier 1/2 — optionally keep the single previous version's *config* as a settings-rollback fallback.

## Browser data — handle with care

Browser data roots (Chrome/Chromium/Firefox/Edge/Arc) contain **profiles: bookmarks, cookies, passwords, extensions → Keep, always**. Deletable parts: the separate cache folders, and large re-downloadable components (e.g. Chrome's `OptGuideOnDeviceModel`, an on-device AI model of several GB). Browser must be closed.

## User files — report size only, never tier

Downloads, Trash, Documents, Desktop, project trees, mail stores, photo libraries, cloud-synced folders. Only the user can decide these, item by item.
