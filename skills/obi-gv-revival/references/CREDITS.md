# Credits

This repo documents and archives other people's work. Everything technically hard here was done by them.

- **naf**: author of the community firmware for OBi2xx/3xx (`arrynrob` series, including `arrynrob13`), the `6259-signed-fw-bypass-uboot-mod` bridge firmware, the Google Voice (GV-SIP) work, and the in-firmware Google Voice instructions reproduced in the guide. Also author of the `naf` firmware for OBi100/110 and the original certificate work on OBi110 (December 2017). Years of patient support in the forum threads.
- **taoman, olisom, ssyspro, aa2k**: authors of the sibling firmwares for OBi2000, OBi1000-series, OBi5xx and VVX D230 listed on obifirmware.com (not covered here).
- **Klaberte**: wrote the "why use third-party firmware" explainer on obifirmware.com. **OBi1FW** updated it after the OBiTALK shutdown and appears to maintain the download site.
- **obifirmware.com** ("naf firmware"): hosts the firmware and the Google Voice provisioning XML files.
- **DSLReports** (taken offline 2025-01-15) and its **VoIP Tech Chat** forum community, now continued on **Broadband Bulletin**. The "Obihai OBi20x/30x + OBi1000 + OBi50x + OBi2000 firmware mods" thread is the source of nearly everything in this guide. A user contributed an archive of that thread, linked on obifirmware.com.
- **primerisk** (also `/u/PrimeRisk` on Reddit): wrote the step-by-step upgrade guides (Google Docs) for OBi2xx/3xx, OBi10xx and OBi21xx devices, posted in the Broadband Bulletin thread "Firmware Upgrade Guides: Obihai 2xx/3xx/10xx/21xx" (April 2025), after gathering advice from Reddit users. Their guide's cautions (Chrome, incognito, power-cycling, MD5 checks) are summarised in `GUIDE.md`. primerisk is explicit that they developed none of the firmware. The Reddit contributors they drew on are credited with them.
- **Thread contributors whose answers appear in the troubleshooting table**: `naf` (403 and 400 diagnoses, `CustomizationStatus`, the PHONE2 page), `andre2` (masked AuthPassword, ITSP provisioning resetting itself, the 2026 text-page change), `sutomo` and `mdSeuss` (DNS fixes), `tjn` (router/power-cycle fix), `OzarkEdge` (reset and power-supply advice).
- **Forum members whose reports shaped the troubleshooting section**: `berkeleyuser` (reported the full three-firmware route working on an OBi202 on 2026-09-07), `phane` (explained that the token is in the URL of the dead obitalk.com page), `ezc2578` (factory reset fixed 400 errors), `tpedwards` (WAN/LAN access tips and GV on a 202), `mdSeuss` (local DNS entries for obihai.sip.google.com), `jsolo1` (OBi212 route, certificate analysis), `andre2`, and others in the threads.
- **Kavex** keeps a GitHub mirror of earlier firmware (`github.com/Kavex/OBi200`).

If you are named here and want something changed or removed, open an issue.

Obihai, OBi, OBiTALK, Polycom, Poly, HP and Google Voice are trademarks of their owners. This project is not affiliated with or endorsed by any of them, or by Anthropic.
