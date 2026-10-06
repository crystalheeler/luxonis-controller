"""
Check the RTSP encoder output with ffprobe.
=============================================
Feeds raw frames through the exact command oak_bridge publishes with, then
asserts three properties of the result:

  profile   High          a Raspberry Pi hardware decoder and Firefox both
                          refuse High 4:4:4 Predictive, profile 244
  pix_fmt   yuv420p       the input is bgr24, and x264 keeps full chroma
                          unless the output format is forced
  keyframes once a second a viewer that connects mid-stream waits for the
                          next keyframe before it can draw anything

No camera and no RTSP server are needed. The encoder settings decide the
profile, not the output container, so this writes a file and probes it.

    python tests/encode_check.py [path-to-ffmpeg]

Looks for ffmpeg and ffprobe in windows/bin, then on PATH. Exits 0 with a SKIP
when neither is present, so a machine without ffmpeg does not fail the suite.
The release workflow supplies both.
"""

import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "src"))

import oak_encoder

WIDTH, HEIGHT = 1280, 720
FPS           = 15
SECONDS       = 4
FRAMES        = FPS * SECONDS


def find_tool(name: str) -> str | None:
    exe = f"{name}.exe" if sys.platform == "win32" else name
    local = os.path.join(REPO, "windows", "bin", exe)
    if os.path.isfile(local):
        return local
    return shutil.which(name)


def make_frame(i: int) -> bytes:
    """Moving content, so the encoder cannot collapse every frame to nothing."""
    row = bytearray()
    for x in range(WIDTH):
        v = (x + i * 7) % 256
        row += bytes((v, (v * 3) % 256, (v * 5) % 256))
    return bytes(row) * HEIGHT


def encode(cmd: list) -> tuple[bool, str]:
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for i in range(FRAMES):
            p.stdin.write(make_frame(i))
        p.stdin.close()
    except (BrokenPipeError, OSError):
        pass
    err = p.stderr.read().decode("utf-8", "replace")
    p.wait()
    return p.returncode == 0, err


def probe(ffprobe: str, path: str) -> dict:
    out = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=profile,pix_fmt,codec_name,width,height",
         "-of", "json", path],
        capture_output=True, text=True, check=True)
    info = json.loads(out.stdout)["streams"][0]

    frames = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "frame=key_frame", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True).stdout.split("\n")
    keys = [i for i, f in enumerate(frames) if f.strip() == "1"]
    info["keyframes"] = keys
    info["gaps"] = [b - a for a, b in zip(keys, keys[1:])]
    return info


def main() -> int:
    ffmpeg  = sys.argv[1] if len(sys.argv) > 1 else find_tool("ffmpeg")
    ffprobe = find_tool("ffprobe")

    print("Encoder check")
    print("=" * 60)
    if not ffmpeg or not ffprobe:
        print("SKIP: ffmpeg or ffprobe not found. This check needs both.")
        print("      The release workflow downloads them before it runs this.")
        return 0

    out_dir = os.path.join(REPO, "build")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "encode_check.mp4")

    # The same builder oak_bridge uses, with the RTSP output swapped for a file.
    cmd = oak_encoder.ffmpeg_args(ffmpeg, WIDTH, HEIGHT, FPS,
                                  out_path, rtsp=False, loglevel="error")
    cmd.insert(1, "-y")
    print("command:", " ".join(cmd[1:]))
    print()

    ok, err = encode(cmd)
    if not ok:
        print("FAIL: ffmpeg did not encode")
        print(err)
        return 1

    info = probe(ffprobe, out_path)
    print(f"  codec:     {info['codec_name']}")
    print(f"  profile:   {info['profile']}")
    print(f"  pix_fmt:   {info['pix_fmt']}")
    print(f"  size:      {info['width']}x{info['height']}")
    print(f"  keyframes: {info['keyframes']}")
    print(f"  gaps:      {info['gaps']}")
    print()

    findings = []
    if info["profile"] != "High":
        findings.append(
            f"profile is {info['profile']!r}, expected 'High'. "
            "A Raspberry Pi hardware decoder refuses High 4:4:4 Predictive.")
    if info["pix_fmt"] != "yuv420p":
        findings.append(
            f"pix_fmt is {info['pix_fmt']!r}, expected 'yuv420p'. "
            "Firefox cannot play 4:4:4 H.264.")
    if not info["gaps"]:
        findings.append(f"only one keyframe in {SECONDS} s, expected one a second.")
    elif not all(g == FPS for g in info["gaps"]):
        findings.append(
            f"keyframe gaps are {info['gaps']}, expected every {FPS} frames.")

    try:
        os.remove(out_path)
    except OSError:
        pass

    if findings:
        for f in findings:
            print("FAIL:", f)
        return 1

    print("RESULT: profile High, pix_fmt yuv420p, one keyframe a second.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
