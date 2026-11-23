# Design notes: what can be automated, and the risks

Short answer: **yes for about 80%, with a human kept in the loop for the rest.** The reference run was done almost entirely with `curl` against the device's web interface, which is exactly what a tool would do.

## Status
The reference run (OBi200 hw 1.4, stock 8680EX to `8680EX-arrynrob13`, Google Voice connected, calls verified) was done with `curl` against the device web interface. `skills/obi-gv-revival/scripts/obi_gv.py` automates those same requests; its test coverage is listed in its `README.md`.

## What can be automated safely
| Step | Automatable? | Notes |
|---|---|---|
| Find the device, read model / hardware / firmware | Yes | `DI_S_.xml` over digest auth |
| Choose the flash route from the current version | Yes | table in `references/GUIDE.md`; refuse unsupported models (OBi1xx, OBi5xx, OBi2000, VVX and others have different routes) |
| Verify firmware checksums before upload | Yes | hard gate |
| Disable auto-update / OBiTALK provisioning | Yes | hashes were identified (`references/CURL-REFERENCE.md`); verify by re-reading |
| Back up the config | Yes | file is secret: write with `0600`, refuse to put it in a git repo |
| Flash, wait, confirm `SoftwareVersion`, stop on anomaly | Yes | the core value; ~20 min |
| Enable GV via ConfigURL, reboot, check SP1 = Connected | Yes | after the token is in place |
| Final lockdown + status report | Yes | |
| Change the dropbear SSH password | Mostly | needs SSH with legacy algorithms; tool can generate a strong password and show it once |
| Exchange the Google redirect URL for a refresh token | Probably | the firmware's own page does it; the tool could call that page. Needs investigation of its endpoint |

## What must stay manual (by design or physics)
- **Google sign-in and consent.** OAuth consent must be completed by the account owner in their own browser. A tool should open the link and ask the user to paste back the redirect URL, never ask for a Google password.
- **Revoking old Google Voice grants** in the Google account.
- **Physical recovery**: factory reset (paperclip), phone-keypad fix to re-enable the web server (`***0`, `30#`, `1`, `1#`, `1`), recovery-mode handling, and the rare SPI/serial rescue of a bricked unit.
- **Power and cabling**: wired connection, original power supply, no power-cycling mid-flash.

## Recommended shape
1. **A small Python CLI (`obi-gv`), standard library only**, with a state machine: `detect -> plan -> backup -> disable-updates -> flash (3 steps) -> gv-setup -> lockdown -> verify`. Dry-run by default, explicit confirmation before each flash, resumable, refuses on any version mismatch, logs without secrets.
2. **A thin Claude Code skill** (`SKILL.md`) that drives the CLI and handles the conversational parts (explaining the Google step, interpreting errors). This is essentially what produced the reference run.
3. **No web-page version**: browsers can't do digest auth to a LAN device cleanly and mixed-content rules get in the way.

## Safety rails the tool must have
- Model/hardware allowlist; refuse anything else.
- Never flash the bypass firmware when the current build is 6259 or higher.
- Checksum gate; firmware treated as opaque data, never executed.
- Stop and report on any unexpected version, unreachable device after the wait, or "identical version" message.
- Secrets (refresh token, backups, SSH password) never printed to logs or committed; `.gitignore` already enforces this for backups.
- Force or strongly prompt the SSH password change at the end.

## Risks and open questions
- **Bricking liability.** One user in the thread reported an OBi202 bricked by a *different* firmware (arrynrob6, a bootloader change); our route has multiple successful reports. Keep the tool interactive, with confirmations and a clear disclaimer.
- **Firmware is link-only.** Nothing third-party is hosted here; `references/FIRMWARE.md` gives links and checksums. The tool and skill fetch nothing themselves: you download the files, they verify them.
- **Google Voice terms.** This uses an unofficial client path. Google could change or block it at any time; no tool or archive can prevent that.
- **Dependency on obifirmware.com.** The firmware, the GV config XML files and the token page live there, so this project depends on that site staying online. Mirroring them would remove that single point of failure but should only be done with the maintainers' permission; this repo links only.
- **Model coverage.** Verified on an OBi200 hw 1.4 (stock 8680EX). OBi202/212/300/302/312 follow the same route per the community; device reports are welcome (see `CONTRIBUTING.md`).

## Outcome
- **Guide, firmware links and checksums, credits:** published in this repository (MIT for code and skill, CC BY 4.0 for docs).
- **CLI helper:** implemented as `skills/obi-gv-revival/scripts/obi_gv.py`.
- **Skill:** implemented as `skills/obi-gv-revival/`.
- **Next:** device reports from other models (see `CONTRIBUTING.md`) and an optional step to exchange the Google redirect URL for a refresh token inside the helper.
