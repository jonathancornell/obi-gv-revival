# Firmware: where to get it, and how to check it

**This project does not host firmware.** Download the three files yourself, put them in one folder, and verify the checksums. They are the exact files used in the reference run (2026-11-22).

Flash in this order on an OBi200/202/212/300/302/312 running stock 6259 or newer (including 8680EX). See `GUIDE.md` for other starting versions.

| # | File | Size (bytes) | MD5 | SHA-256 | Download |
|---|---|---|---|---|---|
| 1 | `OBi202-3-2-2-5921EX-332148940.fw` (official stock) | 14,025,548 | `05d40bb42fd2661ed0d17a55da453404` (ours; none published) | `ee1886a0c7d442b492f76f40b92fbad3357c3aada43df1361a33fe967b85c4ac` | https://www.obifirmware.com/fw/OBi202-3-2-2-5921EX-332148940.fw (the original `fw.obihai.com` link no longer resolves) |
| 2 | `OBi302-3-2-2-6259-signed-fw-bypass-uboot-mod.fw` (naf) | 13,301,428 | `59229dd211edb52d9f2e49729cee9794` (matches the published value) | `5139075fbf468e88c5c4c944fd743d568e26a8b045e8493e306a69ca8384eebb` | https://www.obifirmware.com/fw/OBi302-3-2-2-6259-signed-fw-bypass-uboot-mod.fw |
| 3 | `OBi2xx-3-2-2-8680EX-arrynrob13.fw` (naf, 2024-12-11) | 14,401,208 | `b438e5161220e1e7c161e005de1d6bb6` (matches the published value) | `ea68fc963c76fc0219698bc1d44b124602bce2f1a27122722fa8429b2df49877` | https://www.obifirmware.com/fw/OBi2xx-3-2-2-8680EX-arrynrob13.fw |

Project page and the author's own instructions: https://www.obifirmware.com/

The stock 5921EX file has **no published checksum**; the values above are from a download on 2026-11-22 that flashed successfully on a real OBi200. The Internet Archive may also hold copies of the original vendor URL (not checked).

Verify (run in the folder holding the three files):

```sh
shasum -a 256 -c <<'EOF'
ee1886a0c7d442b492f76f40b92fbad3357c3aada43df1361a33fe967b85c4ac  OBi202-3-2-2-5921EX-332148940.fw
5139075fbf468e88c5c4c944fd743d568e26a8b045e8493e306a69ca8384eebb  OBi302-3-2-2-6259-signed-fw-bypass-uboot-mod.fw
ea68fc963c76fc0219698bc1d44b124602bce2f1a27122722fa8429b2df49877  OBi2xx-3-2-2-8680EX-arrynrob13.fw
EOF
```

The helper tool (`scripts/obi_gv.py`) checks these SHA-256 values itself before touching your device and tells you where to download any missing file (`--fw-dir`, default `./firmware-files`).

Treat all firmware as untrusted binaries: never run them on your computer, only upload them to the device. All firmware is third-party property; see `docs/CREDITS.md`.
