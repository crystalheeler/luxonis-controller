# Luxonis Controller Build Plan

**Compiled:** Updated 6 October 2026. Current release: 3.1.0, published 2026-10-06. Built, not pushed: 3.1.1.
**Purpose:** the open task list. Read it before every build, and confirm the version and the scope with CrystalHeeler.

`docs/BUILD_PLAN.html` is generated from this file by `docs/render_build_plan.py`; regenerate it after every change here.

---

## Next up: push and field-test 3.1.1

1. **Built, not pushed:** 3.1.1 (F1, F2, F3, and the last of the renaming). Four commits wait on CrystalHeeler's push order.
2. **Field test 3.1.1:** the App store section reads "Luxonis Controller"; the add-on zip unzips into `/addons` and appears under Local apps; the Export JSON and Import JSON buttons round-trip a settings file.
3. **Waiting on CrystalHeeler:** the order to push and publish 3.1.1; C1 (bootloader, scope agreement); B1 (field result from AnyCam against the fixed stream).

---

## Status key

| Status | Meaning |
|---|---|
| You | Waiting on CrystalHeeler: a field test, a report, a decision, or an order |
| Logs | Needs logs before any investigation |
| Discuss | Needs a discussion before any code |
| Ready | Can be built when scheduled |
| Blocked | Waits on another item, named in "Next step" |
| Later | Parked by CrystalHeeler for later |

---

## Versions 3.0.0 to 3.1.1: done

| Version | Theme | Items |
|---|---|---|
| 3.0.0 | Standalone Windows build, one source tree for three deployments | Portable executable, tray icon, file logging, one launcher |
| 3.0.1 | Windows desktop faults found on first run | Child console windows, no visible startup, the add-on's Shut down button |
| 3.0.2 | Stream compatibility | 4:2:0 High instead of High 4:4:4 Predictive |
| 3.0.3 | Container image renamed to `luxonis-controller` | Image rename, image-name consistency check |
| 3.1.0 | Renamed to Luxonis Controller | Slug, display name, events, entity, Windows artefacts, JSON export and import |
| 3.1.1 | The last of the renaming, and release packaging | The App store heading, the add-on zip, the Install wording |

---

## A. Field tests

| # | Status | Item | Why / source | Next step |
|---|---|---|---|---|
| A1 | You | **Field-test 3.1.1 once it is pushed** | Four commits are built and not pushed. Nothing in 3.1.1 has run on real hardware | The three checks listed under "Next up" |

## B. Bugs

| # | Status | Item | Why / source | Next step |
|---|---|---|---|---|
| B1 | You | **Confirm the fixed stream plays in Firefox and on the Raspberry Pi decoder** | AnyCam 3.7.1, 2026-10-06, test system B, reported the stream as H.264 `High 4:4:4 Predictive`, profile 244: the Pi's hardware decoder refused it and Firefox and LibreWolf could not play it. Fixed in 3.0.2 with `-pix_fmt yuv420p`; the release check now verifies 4:2:0 and one keyframe a second on every build. The encoder emits Constrained Baseline, which every decoder and browser accepts. Recorded on the AnyCam side as its B38 | An AnyCam run against the 3.0.2 or later stream, to close the report. Not yet confirmed on real hardware from this side |

## C. Camera and device support

| # | Status | Item | Why / source | Next step |
|---|---|---|---|---|
| C1 | Discuss | **Handle the network bootloader update from inside the app** | DepthAI warns on every connection: "An optional NETWORK bootloader update is available (installed: 0.0.28, available: 0.0.29). Updating is recommended to improve device discoverability." Discovery is the one thing that has failed repeatedly here, so the warning is worth acting on. Today it means stopping the add-on and running `depthai --flash` by hand from a machine with the DepthAI tools. Luxonis states the operation "can potentially soft-brick your device" and that the connection must not be disturbed; a corrupted **user** bootloader falls back to the **factory** one, so only the user path is recoverable | Agree the scope first. Proposed: show the installed and available versions in the settings panel; a flash button behind a confirmation that names the risk; stop the camera thread, flash through `dai.DeviceBootloader.flashBootloader` with its progress callback, then restart through the existing restart path; never flash automatically, and never expose the factory path. Three API details need confirming against the installed DepthAI first: how to read both versions, how the network type is selected, and whether the device must be in `X_LINK_BOOTLOADER` state |

## D. Streaming and recording

| # | Status | Item | Why / source | Next step |
|---|---|---|---|---|

## E. Code health

| # | Status | Item | Why / source | Next step |
|---|---|---|---|---|
| E1 | Later | **The Python modules are still named `oak_*`** | 3.1.1 removed every user-visible `oak` name. The source files are still `oak_bridge.py`, `oak_paths.py`, `oak_launcher.py`, `oak_tray.py`, `oak_runtime.py`, `oak_logging.py` and `oak_encoder.py`. Nobody but a reader of the source sees them | Rename them together with the imports and the PyInstaller spec, when something else is already touching those files |

## F. Release engineering

| # | Status | Item | Why / source | Next step |
|---|---|---|---|---|
| F4 | Later | **The Windows build is not code-signed** | SmartScreen warns on first run of every release, and the user has to choose "More info" then "Run anyway". An unsigned installer would warn the same way, so the portable form costs nothing here | An organisation-validated code-signing certificate, roughly 200 to 400 US dollars a year. Not worth it before there are users |
| F5 | Later | **Delete the old container package** | `ghcr.io/crystalheeler/luxonis-oak-d-lr` still holds 3.0.0, 3.0.1, 3.0.2 and `latest`. It receives no new tags. Keeping it lets 3.0.0 to 3.0.2 still install; deleting it is one-way and would break those three | CrystalHeeler's call, once nobody needs those versions |

---

## Done: take these off the older lists

| Item | Where it was listed | Evidence |
|---|---|---|
| The H.264 4:4:4 stream | AnyCam B38 | Fixed in 3.0.2. `tests/encode_check.py` asserts 4:2:0 and one keyframe a second on every build |
| The add-on zip for drag and drop | CrystalHeeler, 2026-10-06 | Built in 3.1.1 and backfilled onto all five published releases |
| The Install section wording | CrystalHeeler, 2026-10-06 | The release notes generator now produces the three sections, with the badge pointing at the add-on store repository |

---

## Not this project

| Item | Where it belongs |
|---|---|
| A card counting the stream description as its first frame | AnyCam B41 |
| Cards asking for a new picture 8 times a second | AnyCam B42 |
