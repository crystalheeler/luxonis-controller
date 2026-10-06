"""
The RTSP encoder command, in one place.
=========================================
oak_bridge publishes with this. tests/encode_check.py probes the result with
ffprobe. Both call the same function, so the check cannot drift from the code
it guards.

This module imports nothing heavy, so a test can use it without depthai.
"""

# The camera thread produces BGR frames, which is what OpenCV hands back.
INPUT_PIXEL_FORMAT = "bgr24"

# x264 keeps full chroma when the input is BGR and nothing forces otherwise.
# It then emits High 4:4:4 Predictive, profile 244. A Raspberry Pi hardware
# decoder refuses that profile and falls back to software, and Firefox cannot
# play it at all, so a browser shows a black picture.
OUTPUT_PIXEL_FORMAT = "yuv420p"
OUTPUT_PROFILE      = "high"

BITRATE = "1000k"
PRESET  = "ultrafast"
TUNE    = "zerolatency"


def ffmpeg_args(exe: str, width: int, height: int, fps: int,
                output: str, rtsp: bool = True, loglevel: str = "warning") -> list:
    """Build the ffmpeg command.

    Pass rtsp=False and a file path to encode to a file instead, which is how
    the release check probes the stream without a server.

    The keyframe interval equals the frame rate, so a viewer that connects
    mid-stream waits at most one second for a picture. Without it x264 uses one
    keyframe every 250 frames, and AnyCam measured a 19 s to 28 s wait.
    """
    cmd = [
        exe, "-loglevel", loglevel,
        "-f", "rawvideo",
        "-pixel_format", INPUT_PIXEL_FORMAT,
        "-video_size", f"{width}x{height}",
        "-framerate", str(fps),
        "-i", "pipe:0",
        "-c:v", "libx264",
        "-preset", PRESET,
        "-tune", TUNE,
        "-b:v", BITRATE,
        "-pix_fmt", OUTPUT_PIXEL_FORMAT,
        "-profile:v", OUTPUT_PROFILE,
        "-g", str(fps),
        "-keyint_min", str(fps),
    ]
    if rtsp:
        cmd += ["-f", "rtsp", "-rtsp_transport", "tcp"]
    cmd.append(output)
    return cmd
