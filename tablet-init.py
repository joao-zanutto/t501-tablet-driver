#!/usr/bin/env python3
"""Initialize T501 tablet to use full drawing area via hidraw.

The T501 tablet exposes two HID interfaces. Interface 2 handles pen input but
defaults to a small inner active area. The Windows driver sends a sequence of
HID SET_FEATURE reports during initialization that activates the full drawing
surface. This script replays that same sequence on Linux via the hidraw ioctl
interface, without detaching the kernel HID driver.
"""
import os, fcntl, glob, sys

VENDOR_PRODUCT = "0003:000008F2:00006811"

# HIDIOCSFEATURE ioctl = _IOWR('H', 0x06, size)
def hidiocsfeature(size):
    return 0xC0004806 | (size << 16)

def find_hidraw():
    """Find hidraw device for interface 2 of the tablet."""
    for path in sorted(glob.glob("/sys/class/hidraw/hidraw*")):
        uevent = os.path.join(path, "device", "uevent")
        try:
            with open(uevent) as f:
                content = f.read()
            if VENDOR_PRODUCT in content and "input2" in content:
                return "/dev/" + os.path.basename(path)
        except OSError:
            continue
    return None

def main():
    dev = find_hidraw()
    if not dev:
        print("Tablet hidraw device not found", file=sys.stderr)
        return 1

    fd = os.open(dev, os.O_RDWR)

    # Feature reports (report ID 0x08) — captured from Windows driver USB traffic
    # Subcommand 0x06 with byte 0x01 enables config mode
    # Subcommand 0x01 sets the active area range to full surface
    # Subcommand 0x06 with byte 0x00 exits config mode and restores buttons
    for cmd in [
        "0806010000000000",  # enter config mode
        "080100fff000fff0",  # set full area
        "0806000000000000",  # exit config mode (restores buttons)
    ]:
        buf = bytearray(bytes.fromhex(cmd))
        fcntl.ioctl(fd, hidiocsfeature(len(buf)), buf)

    os.close(fd)
    print(f"Tablet initialized via {dev}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
