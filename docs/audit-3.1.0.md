# Audit note — 3.1.0

Companion to the 3.1.0 changelog entry. A settings backup that can be
restored, and the add-on rename that it enables.

Owner: CrystalHeeler. Date: 2026-10-06.

---

## 1. Why these two shipped together

They were planned as two releases. The settings export had to reach the owner's
running add-on first, so they could export before the slug changed and Home
Assistant started treating it as a different add-on.

The owner then said they already have the old settings in a text file and will
re-enter them by hand, so the sequencing was unnecessary. Both changes are in
this release. The export exists for the next migration, not this one.

---

## 2. Export and import

`GET /api/settings` already returned `{objects, hw_threshold, tag_duration}`,
and `POST /api/settings` already accepted that shape. No server change was
needed; both controls are in the settings page.

`_save_settings_file` stamps the current `_version` when it writes, so an
export taken from an older build imports cleanly instead of tripping the
version reset in `_load_settings_file`.

The import refuses a file that is not valid JavaScript Object Notation (JSON),
and one with no `objects` section. It then names the file and the object count
and asks for confirmation, because it replaces every current setting.

The human-readable `.txt` export stays. It is the one to read; the JSON one is
the one to restore.

---

## 3. The rename

| Field | Was | Now |
|---|---|---|
| `slug` | `oak_camera` | `luxonis_controller` |
| `name` | OAK-D LR Camera | Luxonis Controller |
| `panel_title` | OAK Camera | Luxonis Controller |
| Add-on folder | `addon/oak_camera/` | `addon/luxonis_controller/` |
| Changelog title | OAK-D LR Camera | Luxonis Controller |
| Tray tooltip | OAK-D LR Camera | Luxonis Controller |

### 3.1 What was deliberately not renamed

The Home Assistant event names and the sensor entity id keep the `oak_camera`
prefix:

    oak_camera_motion_started
    oak_camera_motion_stopped
    oak_camera_storage_alert
    sensor.oak_camera_storage

These are the public interface to the owner's automations. `ha_configuration.yaml`
triggers on two of them, and renaming them would break every automation
silently: the trigger would simply never fire again, with no error anywhere.

A rename is possible later. It needs the new names fired alongside the old ones
for one release, then the old ones removed once the automations are moved. That
is its own release with its own migration note, not a side effect of this one.

The Windows executable also keeps the name `OakCamera.exe`. Renaming it changes
the package filename, the Windows Firewall rules the user already approved, and
the startup entry. That is a separate decision.

---

## 4. Release checks

| Check | Result |
|---|---|
| `tests/test_modules.py` | 68 checks, 0 failures |
| 7 of them new, covering export, import, the file input, and both deployments | pass |
| `tests/privacy_scan.py` | no findings |
| `tests/jargon_scan.py` | every enforced acronym written out at first use |
| `tests/encode_check.py` | runs on the Windows runner |
| Image name matches the manifest | pass |
| Add-on version equals the tag | pass |
| Root and add-on changelogs identical | pass |
| Changelog structure | no duplicates, descending |

---

## 5. Not tested

| Not tested | Reason |
|---|---|
| Export and import in a browser | Both are client-side. The checks confirm the controls and the endpoint they call, not a round trip through a real browser. |
| The add-on install under the new slug | Needs a Home Assistant instance. |
| That automations still fire | Needs the camera and a motion event. The event names are unchanged strings in the source, which is the whole reason they were left alone. |
| The camera pipeline | Needs the camera. Unchanged in this release. |

The first one is worth a minute of the owner's time after installing: export,
change one confidence value, import, confirm the value returns.

---

## 6. Release state

Steps 1 to 3 done. The version was set to 3.1.0 and held for confirmation
before the tag and the build, because the owner had not named a number.
