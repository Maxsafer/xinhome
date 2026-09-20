# xinhome

## What is this?
A one-shot script that presses the **x**box (**xin**put) **home** / guide button.

It plugs in a throwaway virtual Xbox 360 controller, presses the guide button once, unplugs the controller and exits. Whatever listens for the guide button (Steam Big Picture, Game Bar, an emulator frontend, ...) reacts exactly as if a real controller had pressed it.

Built on the same base as [xinagg360](https://github.com/Maxsafer/xinagg360).

## But why?
I own an [AYANEO Slide](https://www.ayaneo.com/product/AYANEO-SLIDE.html). It has what is basically a full Xbox controller built in, but **no Xbox / guide button**. That button is what Steam, Game Bar and most frontends use to open their overlay, so on the Slide there is simply no way to press it.

The Slide does have programmable custom buttons though (the AYA button and the LC / RC buttons). AYASpace lets you bind one of them to launch any program, so I built this script into a windowless `xinhome.exe` and bound my custom button to run it. Press the button, the guide press lands, Steam opens. Problem solved.

It should work the same on any handheld or PC where you can bind a key or button to launch an executable.

## Dependencies
- [ViGEmBus](https://github.com/nefarius/ViGEmBus) 1.22.0 by [nefarius](https://github.com/nefarius) - the driver that creates virtual controllers. **Must be installed.** The installer ships inside the vendored `vgamepad` folder (`vgamepad\win\vigem\install\x64\ViGEmBusSetup_x64.msi`) and also in the [xinagg360 repo](https://github.com/Maxsafer/xinagg360).
- [vgamepad](https://github.com/yannbouteiller/vgamepad) by [yannbouteiller](https://github.com/yannbouteiller) - **included in this repo**, no pip install needed.
- Python 3.12 (tested on 3.12.10) - only needed to run the script or to build the exe.
- [PyInstaller](https://pyinstaller.org/) - only needed to build the exe.

## Quick start
1. Install ViGEmBus (see above). Reboot if the installer asks.
2. Clone this repo.
3. Build the exe (see [Building](#building)), or just run the script directly.
4. Bind a button, key or shortcut to `dist\xinhome\xinhome.exe`.

## Building
The `dist` folder is **not** committed. Build it yourself:
```
pip install pyinstaller
build.bat
```
This produces `dist\xinhome\xinhome.exe`. The `xinhome` folder can be moved anywhere, but `xinhome.exe` needs the `_internal` folder next to it.

`build.bat` uses `--onedir` on purpose: a `--onefile` exe has to unpack itself on every launch, which adds roughly 1.7 s to every press.

## How to run
### Method 1: xinhome.exe (recommended)
Point your button / shortcut / launcher at:
```
dist\xinhome\xinhome.exe
```
It has no window, so it won't steal focus from a game.

On the AYANEO Slide: open AYASpace, go to the custom button settings, pick the button you want and set its action to launch `xinhome.exe`. Other handhelds usually have an equivalent in their own control center; on a desktop a shortcut with a hotkey works too.

### Method 2: CLI
```
python xinhome.py
```
Prints what it is doing, handy for testing. Use `pythonw xinhome.py` to run it without a console.

### Parameters
Work for both the exe and the script:
```
xinhome.exe --settle-ms 1500 --hold-ms 200 --linger-ms 500
```
| Parameter     | Default | What it does |
|---------------|---------|--------------|
| `--settle-ms` | 1500    | Wait between the virtual controller showing up and the press |
| `--hold-ms`   | 200     | How long the guide button is held (raise it for a "long press") |
| `--linger-ms` | 500     | Wait between the release and unplugging the controller |

## How it works
1. Takes a named mutex so only one press can be in flight at a time.
2. Plugs in a virtual X360 pad through ViGEmBus and waits until XInput has given it a player slot.
3. Waits `--settle-ms` so listeners notice the new controller.
4. Presses and releases the guide button, holding it for `--hold-ms`.
5. Waits `--linger-ms` so the release gets delivered, then unplugs the pad and exits.

## Things to keep in mind
- The press lands ~2 seconds after the trigger. Most of that is `--settle-ms`: listeners need a moment to notice a freshly plugged controller, and presses sent too early are silently ignored. On my Slide ~1000 ms was hit or miss and 1500 ms was reliable. If the press gets ignored, raise it; if you want it snappier, lower it and test.
- Windows opens Game Bar on the guide button by default. If you only want Steam to react, turn off *Settings > Gaming > Game Bar > Allow your controller to open Game Bar*.
- For Steam, it has to be running, with the guide button enabled under *Steam > Settings > Controller*.
- A second controller shows up for a couple of seconds on every press. Games generally don't care, but it is there.
- Mashing the trigger is safe: while a press is in flight, extra launches exit immediately.
- If the virtual controller shows up under a third-party driver (XBCD, Inno, ...) instead of the stock Xbox one, change its driver in Device Manager, same as noted in [xinagg360](https://github.com/Maxsafer/xinagg360#things-to-keep-in-mind).

## Related projects
All of these share the same ViGEmBus + vgamepad base and were built around my AYANEO Slide.

| Project | What it does |
|---|---|
| [xinagg360](https://github.com/Maxsafer/xinagg360) | Aggregates every connected XInput controller into one virtual Xbox 360 pad. Fixes old games that choke on modern controllers, and lets any pad drive one stable controller. |
| [emuCenter](https://github.com/Maxsafer/emuCenter) | Emulator hub / game launcher built for handheld PCs like the AYANEO Slide. Has the xinagg360 virtual controller built in. |

## License
[GPL-3.0](LICENSE), same as xinagg360. The vendored `vgamepad` keeps its own [MIT license](https://github.com/yannbouteiller/vgamepad/blob/master/LICENSE).
