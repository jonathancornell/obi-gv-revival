# obi-gv-revival

Guide, safety-checked helper script and [Claude Code](https://claude.com/claude-code) skill for reviving **Google Voice** on **OBi200 / 202 / 212 / 300 / 302 / 312** adapters after HP shut down OBiTALK on 2024-11-01, using the community firmware by **naf**.

> **Tested** end to end on an OBi200 (hardware 1.4): stock 8680EX to `8680EX-arrynrob13`, Google Voice connected, inbound and outbound calls working (2026-11-22). The other listed models follow the same community route. **Flashing can brick hardware. Use at your own risk.**

## Why this exists
Stock OBi firmware needed the OBiTALK portal to obtain a Google Voice OAuth token. With the portal gone, stock units show `Connecting to ...;Token Error`. The community **arrynrob** firmware adds a built-in page that gets the token directly from Google. Getting onto it from current stock firmware needs three flashes in a specific order, because the vendor locked down signed firmware. The original guidance lived on DSLReports (taken offline in January 2025) and in scattered forum posts. This project consolidates it, verifies it, and adds tooling.

## What is in this repository
| Path | What |
|---|---|
| [`skills/obi-gv-revival/`](skills/obi-gv-revival/SKILL.md) | The Claude Code skill (self-contained: `SKILL.md`, `scripts/`, `references/`) |
| [`references/GUIDE.md`](skills/obi-gv-revival/references/GUIDE.md) | **Start here.** Full process, flash routes by starting version, Google token steps, lock-down, troubleshooting table |
| [`references/FIRMWARE.md`](skills/obi-gv-revival/references/FIRMWARE.md) | Firmware download links, sizes and checksums (**link-only: no firmware is hosted here**) |
| [`references/CURL-REFERENCE.md`](skills/obi-gv-revival/references/CURL-REFERENCE.md) | Driving the device web UI with `curl` (useful now that browsers are dropping XSLT) |
| [`references/SOURCES.md`](skills/obi-gv-revival/references/SOURCES.md) | **Further reading:** the firmware site, other people's guides, and the forums where you can get help |
| [`references/CREDITS.md`](skills/obi-gv-revival/references/CREDITS.md) | Who did the real work |
| [`scripts/obi_gv.py`](skills/obi-gv-revival/scripts/README.md) | The guided helper: `status`, `plan`, `backup`, `harden`, `flash`, `gv-setup` |
| [`docs/FEASIBILITY.md`](docs/FEASIBILITY.md) | Design assessment: what can and cannot be automated, risks, limits |
| [`tests/`](tests/) | Offline unit tests for the routing and safety logic |

## Quick start
**Manual:** read the [guide](skills/obi-gv-revival/references/GUIDE.md).

**With the helper script** (Python 3.8+ and `curl`; no other dependencies):
```sh
git clone https://github.com/jonathancornell/obi-gv-revival
cd obi-gv-revival/skills/obi-gv-revival
export OBI_PASSWORD='admin'                            # device web password
python3 scripts/obi_gv.py --host 192.168.1.50 status   # read-only
python3 scripts/obi_gv.py --host 192.168.1.50 plan     # which firmware steps you need
```
See [`scripts/README.md`](skills/obi-gv-revival/scripts/README.md) for the rest.

**With Claude Code:** copy the skill folder, then ask Claude to help revive Google Voice on your OBi:
```sh
cp -R skills/obi-gv-revival ~/.claude/skills/
```

## The process in 30 seconds
1. Disable auto firmware update and OBiTALK provisioning; back up the config.
2. On stock 6259 or newer: flash **stock 5921EX**, then the **6259 bypass-uboot-mod**, then **arrynrob13**, confirming the version after each.
3. Revoke old Google Voice grants, then use the Google Voice page that arrynrob adds to the web UI to get a refresh token and enable Google Voice.
4. Lock down: disable the remaining update paths, and **change the default SSH password** (`root`/`obi`).

## Design principles
- **Human in the loop.** Every flash is confirmed; the Google sign-in is always done by the user in their own browser; the tooling asks for nothing beyond a hidden prompt for the refresh token.
- **Verify, then act.** Firmware SHA-256 is checked before the device is touched; the version is checked after every flash; unexpected states stop the run.
- **Link, don't host.** Third-party firmware stays with its authors.
- **No secrets in the repo.** `.gitignore` blocks backups, tokens and firmware binaries; the helper refuses to write backups inside a git repo; CI rejects committed binaries and backups.

## Limitations
- Model coverage beyond the OBi200 comes from community reports.
- Depends on Google continuing to accept this unofficial route and on third-party sites (obifirmware.com) staying online. It can stop working at any time.
- Cannot do Google sign-in and consent, hardware recovery (factory reset, recovery-mode rescue), or change the SSH password for you.

## Contributing
Reports from other models are the most valuable contribution: see [CONTRIBUTING.md](CONTRIBUTING.md). Security issues: [SECURITY.md](SECURITY.md).

## Licence
Code and skill: MIT. Documentation: CC BY 4.0. Third-party firmware and quoted firmware text are not covered. See [LICENSE.md](LICENSE.md).

Created by [jonathancornell](https://github.com/jonathancornell), built with Claude Code.

Not affiliated with or endorsed by HP, Poly, Obihai, Google or Anthropic. All trademarks belong to their owners.

Using unofficial firmware and Google's unofficial sign-in route may breach vendor or Google terms. You are responsible for your own use.
