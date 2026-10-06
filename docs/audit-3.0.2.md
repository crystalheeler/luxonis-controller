# Audit note — 3.0.2

Companion to the 3.0.2 changelog entry. One encoder defect, reported from the
field, plus the repository rename.

Owner: CrystalHeeler. Date: 2026-10-06.

---

## 1. The report

AnyCam 3.7.1 on test system B, 2026-10-06, found the add-on's H.264 stream
encoded as profile **High 4:4:4 Predictive**, profile 244, at 1280x720 and
15 fps.

| Consumer | Result |
|---|---|
| Raspberry Pi H.264 hardware decoder | Refused it: "Profile 244 not supported". AnyCam decoded in software. |
| Firefox, LibreWolf | Cannot play it. The card stayed black and live view failed. |
| Chrome | Played it, in software. |

A black live view in two browsers is the user-visible failure. The software
decode is a cost, not a break.

---

## 2. Cause

The camera thread hands ffmpeg `bgr24` frames, which is what OpenCV produces.

x264 preserves full chroma when the input is BGR and nothing forces an output
format. It then selects a 4:4:4 profile, which is correct behaviour for the
input it was given and wrong for every consumer of this stream.

The fix is two flags: `-pix_fmt yuv420p` converts to 4:2:0, and
`-profile:v high` pins the declared profile.

### 2.1 The profile the stream actually declares

The report asked for profile `High`. The encoder emits **Constrained Baseline**,
and that is the better outcome.

`-profile:v high` is a ceiling, not a floor. It caps what x264 may use. x264
then declares the lowest profile the stream actually needs, and `-preset
ultrafast` disables CABAC, 8x8 DCT and B-frames, so the stream needs only
Constrained Baseline.

Constrained Baseline is the most widely supported H.264 profile. Every hardware
decoder and every browser accepts it, including the two that refused the old
stream. Forcing a real High stream would mean dropping `-preset ultrafast`,
which raises the CPU cost on the Raspberry Pi the add-on runs on, for no
compatibility gain.

The defect was never the profile name. It was the 4:4:4 chroma, and
`-pix_fmt yuv420p` fixes that. `-profile:v high` stays as a documented ceiling,
so a later preset change cannot reach High 4:4:4 Predictive again.

The first 3.0.2 build failed on this, because the check asserted the report's
wording rather than the requirement behind it. The check now accepts
Constrained Baseline, Baseline, Main or High, and rejects anything else.

### 2.2 The keyframe interval was already correct

The report asked for a keyframe interval as item 2. `-g` has equalled the frame
rate since 2.4.2. 3.0.2 adds `-keyint_min` so the lower bound is pinned too,
which stops x264 placing a keyframe earlier than the interval.

Nothing else changed about the stream. The bitrate, preset and tune are as they
were.

---

## 3. Design change

The encoder flags move into `src/oak_encoder.py`, a module that imports nothing
heavy.

`oak_bridge` publishes with `ffmpeg_args()`. `tests/encode_check.py` calls the
same function with `rtsp=False` and a file path. The check therefore probes
exactly what the bridge publishes, and the two cannot drift. Before this, a
test would have had to copy the flag list, and a copy goes stale.

---

## 4. Release checks

Two checks, at two depths.

**`tests/test_modules.py` — 61 checks, 0 failures.** 8 are new in 3.0.2 and
read the built argument list:

| Check | Guards |
|---|---|
| Output pixel format is `yuv420p` | Firefox |
| Profile ceiling is `high` | stops a later preset change reaching 4:4:4 |
| Input pixel format is `bgr24` | the frames the camera thread produces |
| Keyframe interval equals the frame rate | time to first picture |
| Minimum keyframe interval matches | the same |
| `-pix_fmt` precedes the output | flag order, which ffmpeg cares about |
| RTSP output uses TCP | unchanged behaviour |
| File mode drops the RTSP options | the check can encode to a file |

**`tests/encode_check.py` — the real thing.** It encodes 60 frames of moving
content through the actual command, then reads the result back with ffprobe and
asserts a 4:2:0 profile, `pix_fmt yuv420p`, and a keyframe every 15 frames.
See 2.1 for why the profile name is not pinned to `High`.

This runs on the Windows runner, which already downloads ffmpeg for the
package. It now takes ffprobe as well. Neither tool ships in the package:
ffprobe is a build tool, and the spec lists only `mediamtx.exe` and
`ffmpeg.exe`.

It skips with exit 0 when no ffmpeg is present, so a developer machine without
one does not fail the suite.

---

## 5. Not tested

| Not tested | Reason |
|---|---|
| The encoder, on this machine | No ffmpeg is installed here, so `encode_check` skipped locally. Continuous integration runs it against the same ffmpeg build the package carries. |
| Playback in Firefox or LibreWolf | Needs a browser and a live stream. The ffprobe assertions stand in for it: 4:2:0 High is what those browsers accept. |
| Decode on the Raspberry Pi hardware decoder | Needs the Pi. Same reasoning. |
| AnyCam against the fixed stream | Needs both products running. This is the check that closes the report. |
| The camera pipeline end to end | Needs the camera. |

The first item is the one that matters, and the release workflow closes it
before the package is built. The rest need the owner's hardware.

---

## 6. The repository rename

The repository was renamed to `luxonis-controller` on 2026-10-03. GitHub
redirects the old name, so nothing broke, and an existing add-on install keeps
working.

8 references across 4 files now name the real repository: the My Home Assistant
install badge, the clone command and its folder, the releases link, and the
`url` field in both `repository.yaml` and the add-on manifest. The git remote
was updated too.

**The container image keeps its original name**, `ghcr.io/crystalheeler/luxonis-oak-d-lr`.
A package is named independently of its repository. Renaming it would orphan
the 3.0.0 and 3.0.1 images and break any add-on already pulling them, for no
gain.

---

## 7. Release state

All 6 steps done. 3.0.1 was published first, as its own release, and the add-on
store repository was synced to it before this work began. 3.0.2 follows.
