# obi_gv.py: guided helper

MIT licensed (see `../LICENSE`).

Standard-library Python 3.8+ plus `curl` on your PATH. It talks only to the IP you give it (no scanning) and never puts credentials on a command line. **Read `../references/GUIDE.md` first.** Flashing can brick a device.

## Test coverage
- 12 offline unit tests (`tests/`): route planning, safety gates, checksum gate, secret masking.
- Live against an OBi200 (hw 1.4): `status`, `plan`, `backup`.
- `--dry-run` for `harden`, `flash` and `gv-setup`, showing the exact requests sent.
- The requests it sends are the ones used in the full reference run (flash, settings, Google Voice provisioning).

```sh
export OBI_PASSWORD='admin'                     # device web password (default admin)
python3 scripts/obi_gv.py --host 192.168.1.50 status      # read-only
python3 scripts/obi_gv.py --host 192.168.1.50 plan        # which firmware steps you need
python3 scripts/obi_gv.py --host 192.168.1.50 backup --out ~/obi-backups   # mode 600; refuses folders inside this skill or any git repo
python3 scripts/obi_gv.py --host 192.168.1.50 harden      # disable auto firmware update + OBiTALK provisioning
python3 scripts/obi_gv.py --host 192.168.1.50 --dry-run flash   # show exactly what would be sent
python3 scripts/obi_gv.py --host 192.168.1.50 flash       # asks before each flash; verifies version after each
# get a refresh token in your own browser (see GUIDE.md Step 3), then:
python3 scripts/obi_gv.py --host 192.168.1.50 gv-setup --sp 1   # token is prompted, hidden
python3 scripts/obi_gv.py --host 192.168.1.50 harden --full     # final lock-down
```

## Built-in safety rules
- Only OBi200/202/212/300/302/312; anything else is refused.
- Every firmware file's SHA-256 is checked **before** the device is touched.
- It will not flash the bypass firmware unless the device is on build 5853-6258, and checks again at execution time.
- Build 6259 is ambiguous (stock vs. the bypass firmware itself), so you must say which with `--stock-6259` or `--bypass-installed`.
- Stops on any unexpected version, a flash that was not applied, or a device that does not return.
- Never prints the refresh token; dry-run output masks it.

## What it does not do
- Google sign-in/consent and revoking old grants (you do those in your browser).
- Exchange the redirect URL for a refresh token: use the button on the firmware's own Google Voice > Provisioning page, then paste only the token here.
- Change the SSH password (default `root`/`obi`): you must do that yourself.
- Recover a unit stuck in recovery mode, or fix a dead web server (phone-keypad steps are in the guide).

Known unknowns: behaviour of the `flash` and `gv-setup` live paths on other models and firmware states; the `SIP Credentials > AuthPassword` page layout on non-OBi200 units.
