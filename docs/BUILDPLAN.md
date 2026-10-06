# Build plan

Work that is agreed but not yet built. One section per task. Move a task into a
release by giving it a version, then delete it from here once it ships.

---

## 1. Handle the network bootloader update

**Status:** not started
**Added:** 2026-10-06
**Size:** medium

### The problem

DepthAI logs this on every camera connection:

```
[depthai] [warning] An optional NETWORK bootloader update is available
(installed: 0.0.28, available: 0.0.29). Updating is recommended to improve
device discoverability.
```

The warning is correct and the fix is real: a newer network bootloader improves
how reliably the camera is found on the network. Discovery failures are the one
problem this project has hit repeatedly.

Today the user has to stop the add-on and run `depthai --flash` or
`flash_network_bootloader.py` by hand, from a machine with the DepthAI tools
installed.

### What to build

**1. Detect and report, in the settings panel.**
Read the installed and available bootloader versions when the camera connects.
Show them in the panel with a plain sentence when an update exists. Do not warn
on every log line; once per connection is enough.

**2. Flash on request, never automatically.**
A button in the settings panel, behind a confirmation that states the risk and
the time it takes. Flashing must never happen on startup, on a schedule, or as
a side effect of anything else.

**3. Stop the pipeline first.**
The camera cannot be flashed while the pipeline holds it. The flow is: stop the
camera thread, open `DeviceBootloader`, flash with a progress callback, close,
then restart the pipeline through the existing restart path.

**4. Report progress and the outcome.**
`flashBootloader` takes a progress callback. Feed it to the panel so the user
sees movement, and write each step to the log. A silent flash is indistinguishable
from a hang.

### API notes

`dai.DeviceBootloader`, with `flashBootloader(progressCb, path)`. Confirm
against the installed DepthAI version before building:

- the method for reading the installed and available versions,
- whether the network bootloader type is selected by an argument or by which
  bootloader the device already runs,
- whether the device must be in `X_LINK_BOOTLOADER` state first, as the
  explicit-address connect path already sets.

### Risk, and how to contain it

Luxonis states that this "can potentially soft-brick your device" and that the
host and the connection must not be disturbed during the flash.

There is one real mitigation: a corrupted **user** bootloader falls back to the
**factory** bootloader. Flashing the user bootloader is therefore recoverable;
flashing the factory bootloader is not. Build the user path only, and say so in
the confirmation.

Refuse to start the flash when the camera is not reachable, and make the
confirmation name the risk rather than hiding it behind "Are you sure?".

### Done when

- The panel shows the installed and available versions.
- A flash can be started, shows progress, and reports success or failure.
- The pipeline stops before and restarts after.
- The log records the start, the progress and the result.
- Flashing the factory bootloader is not reachable from the user interface.
