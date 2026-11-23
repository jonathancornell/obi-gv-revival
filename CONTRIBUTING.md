# Contributing

## Most useful: device reports
Tried this on a model other than the OBi200? Open an issue using the **Device report** template: model, hardware version, starting firmware, route used, result, and anything that surprised you. Redact personal data (see SECURITY.md).

## Code and docs
- Run the offline tests before submitting: `python3 -m unittest discover -s tests -v`
- Keep `scripts/obi_gv.py` standard-library only (plus `curl`). Safety checks (model allowlist, checksum gate, bypass-firmware gate, secret masking) must keep their tests.
- Do not add third-party firmware binaries or device backups. Links and checksums only.
- Keep credits intact; if you reuse text from a forum or guide, credit the author in `skills/obi-gv-revival/references/CREDITS.md`.
- Anything you verify on real hardware should say which model and firmware it was verified on; label unverified claims as such.
