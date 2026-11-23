---
name: obi-gv-revival
description: Guides a user through reviving Google Voice on an OBi200, OBi202, OBi212, OBi300, OBi302 or OBi312 adapter after the OBiTALK shutdown, by flashing community arrynrob firmware and re-linking Google Voice with a safety-checked helper script. Use when the user mentions an OBi or Obihai adapter with "Token Error", Google Voice no longer working on an OBi, OBiTALK being shut down, or flashing arrynrob firmware.
---

# OBi Google Voice revival

Verified end to end on an OBi200 (hardware 1.4).

Flashing can brick hardware, so work slowly, verify each step, and let the user decide at every flash.

## Files in this skill
- `scripts/obi_gv.py`: the helper (run it; do not read it into context). Usage: `scripts/README.md`.
- `references/GUIDE.md`: the full process, flash routes, Google token steps, lock-down, troubleshooting table. Read it before starting.
- `references/FIRMWARE.md`: firmware download links, sizes and checksums. Firmware is **not** bundled.
- `references/CURL-REFERENCE.md`: manual `curl` equivalents, for when the helper cannot be used.
- `references/SOURCES.md`: other guides, the firmware site and forums to point users to for more help.
- `references/CREDITS.md`: the people whose work this builds on.

## Ground rules
- Supported models only: OBi200, OBi202, OBi212, OBi300, OBi302, OBi312. For anything else (OBi1xx, 5xx, 10xx, 21xx, 2000, VVX) stop: this route does not apply.
- Use only the device IP the user provides. Never scan the network.
- The Google sign-in and consent are done by the user in their own browser. Never ask for a Google password. Never print, log, store or echo the refresh token; it goes only into the helper's hidden prompt or the device's AuthPassword field.
- Backups contain credentials: store them outside any git repository and outside this skill folder (the helper enforces this).
- Never flash a file whose SHA-256 does not match (the helper checks before touching the device).
- Never flash the bypass firmware from build 6259 or higher. Build 6259 is ambiguous (stock release or the bypass firmware itself): ask which.
- Stop and report on anything unexpected: wrong version after a flash, "identical version", no response after about 12 minutes, red/green LED. Do not power-cycle during a flash.
- Get explicit confirmation before each flash and each settings change. Before the first flash confirm: wired Ethernet, original power supply, nobody needs the phone for about 20 minutes, config backed up.

## Workflow
Copy this checklist and keep it updated:

```
- [ ] 1 Preflight: model, IP, admin password (OBI_PASSWORD), `status`, `plan`
- [ ] 2 Download firmware per references/FIRMWARE.md; checksums verified
- [ ] 3 `backup --out <folder outside any repo>`
- [ ] 4 `harden` (disable auto firmware update and OBiTALK provisioning)
- [ ] 5 `--dry-run flash`, then `flash` with confirmations
- [ ] 6 Google token steps (user, in browser), then `gv-setup --sp 1`
- [ ] 7 Verify SP1 = Connected; inbound and outbound test calls
- [ ] 8 `harden --full`; advise changing the default SSH login
```

1. **Preflight.** Run `python3 scripts/obi_gv.py --host <ip> status` then `plan`. If the web UI is unreachable, give the phone-keypad fix in the guide.
2. **Firmware and backup.** Have the user download and verify the files; run `backup`.
3. **Flash.** Show `--dry-run flash` output first. Then `flash`; relay each confirmation prompt and the version check after each step.
4. **Google Voice.** The user (a) deletes old "Google Voice" connections at myaccount.google.com/connections, (b) opens Google Voice > Provisioning in the device web UI, follows the link, signs in with a consumer Google Voice account, accepts all permissions, copies the full URL of the resulting error page, and uses the page's button to get the refresh token. Then run `gv-setup --sp 1`; the token is typed into the hidden prompt.
5. **Verify.** Expect `SP1: Connected`; the user places inbound and outbound calls. If outbound gives only dial tone, check the phone first (dead batteries caused this once) and test by dialing `***`.
6. **Lock down.** `harden --full`. Recommend changing the default SSH login (`root` / `obi`) with `passwd`, keeping the device LAN-only and never port-forwarding it. If the user keeps the default, treat it as their informed choice and do not nag.

## If something fails
Use the troubleshooting table in `references/GUIDE.md` (Token Error, 400, 403, 0.0.0.0, red LED, no dial tone). Prefer redoing the token steps, and a factory reset, over experimenting with individual settings.

## Limits to state honestly
Using unofficial firmware and Google's unofficial sign-in route may breach vendor or Google terms; the user is responsible for their own use. Depends on Google continuing to accept this unofficial route and on third-party sites staying online. Other listed models follow the community-reported route.
