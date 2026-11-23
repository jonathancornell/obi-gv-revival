# Security policy

## Reporting a problem
Please open a **private security advisory** on GitHub (Security tab > Report a vulnerability) for anything involving credential leakage, unsafe defaults, or a way the helper could damage a device or expose secrets. For non-sensitive bugs, open a normal issue.

## Never post these publicly (issues, PRs, logs)
- A Google **refresh token**, an OAuth redirect URL (it contains a one-time code), or any `AuthPassword` value
- Device configuration backups (they contain credentials)
- Your device's MAC address, OBi number, serial, public IP, or phone number
Redact them before pasting output. If you leaked one, revoke the Google Voice grant at myaccount.google.com/connections and change the device password.

## Known security considerations
- The arrynrob firmware enables an SSH server with the default login `root` / `obi`. Change it, keep the device LAN-only, and never port-forward it. A factory reset does not clear it.
- The helper passes credentials to `curl` on stdin (not on the command line), never prints the refresh token, writes backups with mode 600, and refuses to write them inside a git repository.
- Firmware is third-party and unaudited. Verify checksums; never execute firmware files on your computer.

## Supported versions
Only the latest commit on `main` is maintained.
