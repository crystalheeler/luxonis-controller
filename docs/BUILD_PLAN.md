# Luxonis Controller Build Plan

**Compiled:** Updated 6 October 2026, late. Current release: 3.1.0, published 2026-10-06. Built, not pushed: 3.1.1.
**Purpose:** the open task list. Read it before every build, and confirm the version and the scope with CrystalHeeler.

`docs/BUILD_PLAN.html` is generated from this file by `docs/render_build_plan.py`; regenerate it after every change here.

---

## Next up: push and field-test 3.1.1

1. **Built, not pushed:** 3.1.1 (F1, F2, F3, and the last of the renaming). Four commits wait on CrystalHeeler's push order.
2. **Field test 3.1.1:** the App store section reads "Luxonis Controller"; the add-on zip unzips into `/addons` and appears under Local apps; the Export JSON and Import JSON buttons round-trip a settings file.
3. **Waiting on CrystalHeeler:** the order to push and publish 3.1.1; C1 (bootloader, scope agreement); F4 (which signing route, if any).

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
| F4 | Discuss | **Stop the SmartScreen warning on the Windows build** | CrystalHeeler, 2026-10-06, asked for a cheaper option or a workaround. Research 2026-10-06 found the usual advice is out of date. [Microsoft's own comparison](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options) (updated 2026-08-29): an Extended Validation certificate **no longer bypasses SmartScreen**, removed in 2024, so the 400 US dollars a year buys nothing here. An Organization Validated certificate is 150 to 300 a year, needs a hardware token since June 2023, and still builds reputation from zero. [Azure Artifact Signing](https://learn.microsoft.com/en-us/azure/trusted-signing/), formerly Trusted Signing, is about 10 US dollars a month with no token, but individuals are limited to the USA and Canada and it also builds reputation rather than granting it. Two claims that circulate are wrong: submitting the file to Microsoft Security Intelligence clears a malware detection, not a reputation warning, and [Microsoft states](https://learn.microsoft.com/en-us/answers/questions/5857071/how-can-a-small-software-publisher-build-smartscre) there is no manual allow-listing and no fast track for a small publisher | Three routes, for a decision. **Free, and the only one with no warning at all:** publish as an MSIX package through the Microsoft Store, which re-signs it; it costs a repackage and a certification pass. **Free, and the best fit:** [SignPath Foundation](https://signpath.org) signs qualifying open-source projects at Organization Validated level; this repository is public and MIT licensed, so check eligibility first. **Paid:** Azure Artifact Signing at about 10 a month, if the region allows it. Meanwhile the free user-side fix is already real: right-click the downloaded zip, Properties, tick Unblock, **then** extract. Windows copies the Mark of the Web from the zip onto every file inside it, so unblocking afterwards means unblocking each file separately |

---

## Done: take these off the older lists

| Item | Where it was listed | Evidence |
|---|---|---|
| The H.264 4:4:4 stream | AnyCam B38 | Fixed in 3.0.2. `tests/encode_check.py` asserts 4:2:0 and one keyframe a second on every build |
| The add-on zip for drag and drop | CrystalHeeler, 2026-10-06 | Built in 3.1.1 and backfilled onto all five published releases |
| The Install section wording | CrystalHeeler, 2026-10-06 | The release notes generator now produces the three sections, with the badge pointing at the add-on store repository |
| B1, the H.264 4:4:4 stream | This plan, B1 | CrystalHeeler field-tested 3.0.3 on 2026-10-06: the feed shows in the AnyCam card. Closes AnyCam's B38 from this side |
| F5, delete the old container package | This plan, F5 | CrystalHeeler, 2026-10-06: `luxonis-oak-d-lr` stays forever. It keeps 3.0.0 to 3.0.2 installable and receives no new tags |

---

## Not this project

| Item | Where it belongs |
|---|---|
| A card counting the stream description as its first frame | AnyCam B41 |
| Cards asking for a new picture 8 times a second | AnyCam B42 |
