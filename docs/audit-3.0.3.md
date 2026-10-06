# Audit note — 3.0.3

Companion to the 3.0.3 changelog entry. One change: the container image name.

Owner: CrystalHeeler. Date: 2026-10-06.

---

## 1. What changed and why

The container image is now `ghcr.io/crystalheeler/luxonis-controller`. It was
`ghcr.io/crystalheeler/luxonis-oak-d-lr`.

The owner renamed the repository to `luxonis-controller` on 2026-10-03 because
the project will add other Luxonis camera models. An image named after one
model contradicts that.

### 1.1 This reverses a 3.0.2 decision

3.0.2 kept the old image name deliberately. Section 6 of `docs/audit-3.0.2.md`
argued that a package is named independently of its repository, and that
renaming it would orphan the existing images for no gain.

That reasoning weighed only the migration cost. It missed the product
direction, which the owner supplied: the name has to describe what the project
is becoming, not the one model it started with. A name that is wrong now stays
wrong in every future release, and the migration cost only grows.

The 3.0.2 audit note keeps its original text with a pointer to this one.
Rewriting a shipped note would falsify the record.

---

## 2. Migration

Nothing breaks, because of the order the release runs in:

| Step | Effect |
|---|---|
| 1 The workflow builds and pushes `luxonis-controller:3.0.3` | The new image exists |
| 2 The Release is published | The Windows package is available |
| 3 The store repository is synced | Home Assistant first sees `image: .../luxonis-controller` at this point |

Home Assistant reads the manifest from the store repository. By the time it
points at the new name, the image behind that name is already published. An
add-on update pulls it and succeeds.

An install that stays on 3.0.2 keeps running from its local copy and is not
touched.

### 2.1 The old package stays

`ghcr.io/crystalheeler/luxonis-oak-d-lr` keeps tags 3.0.0, 3.0.1, 3.0.2 and
`latest`, on the owner's decision. A rollback to those versions still works.
It receives no new tags.

Deleting it would remove the last trace, and it would also remove the ability
to re-pull or roll back to any of those three versions. That is a one-way
action, so it waits until nobody is on them.

Note that its `latest` tag still points at 3.0.2 and will not move again.
Nothing in this project pulls `latest`; the add-on manifest always names an
exact version.

---

## 3. A guard against the next drift

The image name lives in two files that must agree:

    .github/workflows/release.yml   IMAGE_NAME, what the build pushes
    addon/oak_camera/config.yaml    image:, what Home Assistant pulls

A mismatch would publish an image nobody pulls and point Home Assistant at an
image nobody built. The symptom would appear only on a user's device, during
an update, as a failed pull.

The `check` job now compares the two and fails the build when they differ. This
runs before anything is packaged.

---

## 4. Release checks

| Check | Result |
|---|---|
| Image name matches in both files | pass |
| `tests/test_modules.py` | 61 checks, 0 failures |
| `tests/encode_check.py` | profile and chroma verified on the runner |
| `tests/privacy_scan.py` | no findings |
| Add-on version equals the tag | pass |
| Root and add-on changelogs identical | pass |
| Changelog structure | no duplicates, descending |
| Compile and YAML parse | pass |

---

## 5. Not tested

| Not tested | Reason |
|---|---|
| An add-on update across the rename | Needs a Home Assistant instance running 3.0.2. The migration argument in section 2 rests on the publish order, not on a test. |
| The camera pipeline | Needs the camera. Unchanged in this release. |
| Playback in Firefox or on the Pi decoder | Needs the hardware. Unchanged since 3.0.2, which the encoder check verifies on every build. |

This release changes names only. No runtime code changed, so the risk sits
entirely in the migration, and section 2 covers it.

---

## 6. Release state

All 6 steps done. The image was published before the store repository pointed
at it.
