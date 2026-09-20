import os, sys, time, ctypes
from ctypes import wintypes

# Ensure vendored vgamepad is importable
_here = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(os.path.join(_here, "vgamepad")) and _here not in sys.path:
    sys.path.insert(0, _here)

# ---- Single instance ----
# Mashing the trigger must not stack virtual pads: while one press is in
# flight, any extra copy just exits.
ERROR_ALREADY_EXISTS = 183

_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
_kernel32.CreateMutexW.restype  = wintypes.HANDLE

def _already_running():
    # the mutex handle is deliberately never closed; it lives as long as the process
    handle = _kernel32.CreateMutexW(None, False, "Local\\xinhome")
    return bool(handle) and ctypes.get_last_error() == ERROR_ALREADY_EXISTS

# ---- One guide press on a throwaway virtual X360 ----
def press_guide(settle_ms=1500, hold_ms=200, linger_ms=500, ready_timeout_ms=3000):
    t0 = time.monotonic()

    # imported here, not at the top: importing vgamepad already connects to ViGEmBus
    import vgamepad as vg  # vendored
    import vgamepad.win.vigem_client as vcli
    import vgamepad.win.vigem_commons as vcom

    # constructs and plugs in a virtual X360; blocks until the device is operational
    pad = vg.VX360Gamepad()
    try:
        # The pad only exists for XInput once the XUSB driver has handed it a
        # player slot, so wait for that instead of sleeping blindly.
        slot = wintypes.ULONG()
        deadline = time.monotonic() + ready_timeout_ms / 1000.0
        while vcli.vigem_target_x360_get_user_index(pad._busp, pad._devicep, ctypes.byref(slot)) \
                != vcom.VIGEM_ERRORS.VIGEM_ERROR_NONE:
            if time.monotonic() > deadline:
                raise TimeoutError("virtual pad never got an XInput slot")
            time.sleep(0.01)
        print("[xinhome] virtual pad ready after %d ms" % ((time.monotonic() - t0) * 1000))

        # whoever listens for the guide button (Game Bar, Steam, ...) needs a
        # moment to notice the new controller before it sees the press
        time.sleep(settle_ms / 1000.0)

        guide = vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE
        pad.press_button(button=guide)
        pad.update()
        time.sleep(hold_ms / 1000.0)
        pad.release_button(button=guide)
        pad.update()
        print("[xinhome] guide pressed for %d ms" % hold_ms)

        # let the release get delivered before the pad is unplugged
        time.sleep(linger_ms / 1000.0)
    finally:
        # deleting object disconnects the virtual pad
        pad = None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Press the Xbox (guide) button once on a throwaway virtual X360, then exit")
    parser.add_argument("--settle-ms", type=int, default=1500, help="Wait between the pad showing up and the press (ms)")
    parser.add_argument("--hold-ms", type=int, default=200, help="How long the guide button is held (ms)")
    parser.add_argument("--linger-ms", type=int, default=500, help="Wait between the release and unplugging the pad (ms)")
    args = parser.parse_args()

    if _already_running():
        print("[xinhome] a press is already in flight, exiting")
        sys.exit(0)

    press_guide(
        settle_ms=args.settle_ms,
        hold_ms=args.hold_ms,
        linger_ms=args.linger_ms,
    )
