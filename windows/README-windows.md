Luxonis Controller — portable build for Windows
=============================================

WHAT THIS IS
  A standalone version of Luxonis Controller. It runs the same
  AI detection, Real Time Streaming Protocol (RTSP) stream, motion recording
  and web settings page as the
  Home Assistant add-on. It needs no installer and no administrator rights.

FIRST RUN
  1 Unzip this folder anywhere you can write to. A USB stick works.
    Do not use C:\Program Files: Windows blocks writes there, and the program
    then falls back to %LOCALAPPDATA%\LuxonisController for its data.
  2 Open luxonis_config.yaml in a text editor. Set camera_ip to the address of
    your camera. Save the file.
  3 Run LuxonisController.exe.
  4 Windows Firewall asks to allow the program. Click Allow for private
    networks. You are asked once for LuxonisController.exe and once for mediamtx.exe.
    Decline, and the stream works on this computer only.
  5 A camera icon appears in the notification area, next to the clock.
    Right-click it and choose Open settings.

THE TRAY ICON
  Open settings            the web panel, at http://localhost:8767/
  View log                 opens luxonis_controller.log
  Open data folder         settings, the log and the generated mediamtx config
  Open recordings folder   the motion clips
  Start with Windows       adds or removes a startup entry for your account
  Restart                  reloads the camera pipeline
  Quit                     stops the program and every child process

WHERE THINGS GO
  data\luxonis_settings.json   per-object detection settings from the web panel
  data\luxonis_controller.log      rotating log, 2 MB per file, 5 files
  recordings\              motion clips, named motion_<time>_<objects>.mp4
  models\                  put yolo11n.tar.xz here to use the yolo11n model
  bin\                     mediamtx.exe and ffmpeg.exe, copied on first run

  All of these sit beside LuxonisController.exe, so the whole folder is portable.
  Point them somewhere else with recordings_dir, data_dir and models_dir in
  luxonis_config.yaml.

PORTS
  8765   RTSP stream, at rtsp://<this-pc>:8765/stream
  8766   JPEG snapshot, at http://<this-pc>:8766/snapshot
  8767   settings page and the live Motion JPEG (MJPEG) feed
  8764   held open internally to stop a second copy from starting

UPGRADING
  Unzip the new version over this folder and keep your data, recordings and
  models folders. Your luxonis_config.yaml is not overwritten.

HOME ASSISTANT
  Leave ha_token empty and the program runs fully standalone.
  Fill in ha_url and a long-lived access token to send motion events, storage
  alerts and a storage sensor to Home Assistant.

TROUBLESHOOTING
  Nothing happens          read data\luxonis_controller.log. The program is windowed,
                           so it reports every error there and never opens a
                           console.
  No camera found          check camera_ip, and ping the camera.
  No RTSP stream           ffmpeg.exe or mediamtx.exe is missing, or you denied
                           the firewall prompt. The log names the cause. The
                           MJPEG feed and recording still work without them.
  Already running          another copy holds port 8764. Quit it from the tray
                           icon, or end LuxonisController.exe in Task Manager.
  SmartScreen warning      this build is not code-signed. Avoid it entirely:
                           right-click the downloaded zip, choose Properties,
                           tick Unblock, then extract. Windows copies the
                           Mark of the Web from the zip onto every file inside
                           it, so unblocking afterwards means unblocking each
                           file one at a time.
                           If you already extracted it, choose More info, then
                           Run anyway.

SOURCE AND ISSUES
  https://github.com/crystalheeler/luxonis-controller
