# Audit note — 3.1.1

Companion to the 3.1.1 changelog entry. Names only.

Owner: CrystalHeeler. Date: 2026-10-06.

---

## 1. What 3.1.0 missed

The owner saw "Luxonis OAK-D LR" as the section heading in the Home Assistant
App store after installing 3.1.0.

That heading is `name:` in `repository.yaml`, the file that marks a repository
as an add-on repository. The 3.1.0 rename replaced "OAK-D LR Camera" and
"OAK Camera", but the heading read "Luxonis OAK-D LR", which matched neither
pattern, so it was left untouched.

A string-level rename only finds the spellings it is given. The sweep that
followed searched for `OAK-D`, `OAK `, `oak_camera` and `OakCamera` instead,
which is what should have run the first time.

## 2. Changed

| Where | Was | Now |
|---|---|---|
| `repository.yaml` | Luxonis OAK-D LR | Luxonis Controller |
| Camera connect and discovery logs | "Connecting to OAK-D LR at ..." | "Connecting to the camera at ..." |
| Startup log | "OAK-D LR bridge starting" | "Luxonis Controller starting" |
| Motion event `camera` field | OAK-D LR | Luxonis Controller |
| Storage notification | "OAK recordings are using ..." | "Recordings are using ..." |
| `ha_configuration.yaml` | 5 references | Luxonis Controller |
| Both READMEs, `luxonis_config.yaml`, 3 module docstrings | OAK-D LR | the camera, or Luxonis Controller |

Messages about the hardware now say "the camera" or "a Luxonis camera" rather
than naming a model, because the project is adding other Luxonis models.

## 3. Release checks

68 module checks, privacy scan, jargon scan, changelog structure, image name,
version match, changelog sync, compile and YAML parse. All pass.

A sweep for `OAK-D`, `OAK `, `oak_camera` and `OakCamera` across every tracked
file returns nothing outside `CHANGELOG.md` and the audit notes, which keep
their original text because they record what shipped.

## 4. Not tested

The App store heading itself. It needs a Home Assistant instance to re-read the
repository. The value is a single YAML field, verified by parse.
