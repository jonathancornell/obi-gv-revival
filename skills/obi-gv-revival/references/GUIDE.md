# Reviving Google Voice on an OBi200/202/212/300/302/312

Step-by-step, verified on **2026-11-22** on an OBi200 (hardware 1.4) running stock 3.2.2 (Build 8680EX). It ends with Google Voice connected and working in both directions.

> **Tested** end to end on an OBi200 (hardware 1.4); the other listed models follow the same community route.
>
> **Responsibility.** Using unofficial firmware and Google's unofficial sign-in route may breach vendor or Google terms. You are responsible for your own use. This guide is not affiliated with or endorsed by HP, Poly, Obihai, Google or Anthropic.
>
> **Risk.** You are flashing firmware. Doing it wrong can leave the unit in recovery mode, and in rare cases bricked. No warranty.

## Why this is needed
HP shut down the OBiTALK portal on **2024-11-01**. Stock OBi firmware needed that portal to obtain the Google Voice (GV) OAuth token, so stock devices show `Connecting to ...;Token Error`. The community firmware (**arrynrob**, by naf) removes the dependency on OBiTALK: it adds a built-in page that gets the token directly from Google.

## What you need
- An OBi200/202/212/300/302/312 on your LAN (wired to the **WAN/Ethernet** port, never Wi-Fi for flashing) and a phone plugged into the PHONE port.
- A **consumer** Google Voice account (Workspace accounts are not supported by this method).
- The three firmware files, downloaded from the links in [`FIRMWARE.md`](FIRMWARE.md) and checked against their checksums (this project does not host firmware).
- The device IP (read it with the phone: dial `***`, then `1`).
- Default web login is `admin` / `admin` unless you changed it.

## Which route do you take?
Check `SoftwareVersion` on the status page (`http://<ip>/DI_S_.xml`, or System Status in the UI).

| Current firmware | Route |
|---|---|
| lower than 5853 | flash arrynrob directly |
| 5853 up to (but not including) 6259 | bypass-uboot-mod, then arrynrob |
| **6259 or higher (includes stock 8680EX)** | **stock 5921EX, then bypass-uboot-mod, then arrynrob** |

**Never flash bypass-uboot-mod while on 6259 or higher.** It drops the unit into recovery mode (which can still flash any firmware, but avoid it).

## Step 0: stop the unit changing itself
In the web UI, System Management > Auto Provisioning, set **Auto Firmware Update > Method = Disabled** and **OBiTALK Provisioning > Method = Disabled**. The firmware author notes a unit with OBiTALK Service enabled could still be pushed a firmware update, so you will also disable that later.

## Step 1: back up the config
Web UI: System Management > Device Update > Backup Configuration. The file contains credentials and tokens: **keep it private and never commit it.**

## Step 2: flash, in order, checking after each
Web UI: System Management > Device Update > Firmware Update, choose the file, Update. Wait about 5 minutes. After each flash confirm the version on the status page before continuing, and stop if anything looks wrong.

1. `OBi202-3-2-2-5921EX-332148940.fw` -> expect `3.2.2 (Build: 5921EX)`
2. `OBi302-3-2-2-6259-signed-fw-bypass-uboot-mod.fw` -> expect `3.2.2 (Build: 6259)`
3. `OBi2xx-3-2-2-8680EX-arrynrob13.fw` -> expect `3.2.2 (Build: 8680EX-arrynrob13)`

Notes:
- Do not power-cycle during a flash. Use the original 12 V supply.
- "Previous version identical to the update" means the flash was not applied.
- After a stock or bypass flash the web server can get disabled (the OBi200's only Ethernet port is the "WAN" side). If `http://<ip>` stops answering, from a phone on the OBi dial `***0`, press `30#`, press `1` (enter new value), press `1#` (enable), press `1` (save), then hang up.
- On the verified run all three flashes succeeded on the first try and the web UI stayed reachable.

### Browser shows a blank/plain-text page?
The OBi UI is XML + XSLT, and current browsers are dropping XSLT, so pages can render as plain text. Everything above can be done with `curl` instead; see [`CURL-REFERENCE.md`](CURL-REFERENCE.md).

## Step 3: Google Voice setup
First, in your Google account go to **myaccount.google.com/connections** (or `/linkedapps`), find **Google Voice**, and delete all existing connections. Skipping this caused 403 errors for other users.

Then open **Google Voice > Provisioning** in the OBi's left sidebar. It opens the instructions built into the arrynrob firmware. They are reproduced below (credit: naf; the firmware's own text):

```
Instructions:
1) open this link in new tab to request a single-use authorization token for "obitalk.com": request GV oauth token

2) after logging into your google voice account and agreeing to grant obitalk.com permission to make/receive calls (click 'select all' permissions if prompted), your browser will receive a 404 error from www.obitalk.com because it is no longer functional as of 10/31/2024. however, an authorization code is present in that url

3) copy/paste the full non-functional url from the other tab into the textbox below (it will look like 'https://www.obitalk.com/obinet/pg/obhdev/gvtoken?code=xxxxxxxxxxxxxxxxxx&scope=blah&lotsofotherstuff=junk') and then click 'Get Refresh Token From Code In URL' button below

4) copy/paste the Refresh Token contents (that will appear after button is pressed) into obi local web gui's AuthPassword field at Voice Services > SPx Service > SIP Credentials > AuthPassword (SPx # must match config chosen in next step), then click Submit at the bottom

5) based on the desired SPx # used in step5, choose the corresponding config URL for provisioning:
  SP1: https://www.obifirmware.com/fw/EnableGVSIPWithoutOBiTALK.xml
  SP2: https://www.obifirmware.com/fw/EnableGVSIPWithoutOBiTALK_SP2.xml
  SP3: https://www.obifirmware.com/fw/EnableGVSIPWithoutOBiTALK_SP3.xml
  SP4: https://www.obifirmware.com/fw/EnableGVSIPWithoutOBiTALK_SP4.xml

6) copy/paste chosen url into local webgui at System Management > Auto Provisioning > ITSP Provisioning > ConfigURL, set provisioning "Method" to "System Start", click Submit at the bottom, then click Reboot to force the config to download
```

Plain-language tips that matter:
- **The "broken" page in step 2 is expected.** The token is in the address bar of that error page. Copy the entire URL, not anything on the page.
- Paste **only the refresh token** into AuthPassword (arrynrob13 format). The older `client_id=...&refresh_token=...` form still works for backward compatibility.
- Treat the refresh token as a password. Do not paste it into chats, issues, or logs.
- The device needs outbound HTTPS (TCP 443) to `obifirmware.com` to fetch the config.
- Submit each settings page separately, then reboot.
- Success is **SP1 status = `Connected`** (it may show `Registration Not Required` for a moment first). Then place a test call in and out.

## Step 4: lock it down
- **Change the SSH password** (strongly recommended). arrynrob enables a dropbear SSH server with default login **`root` / `obi`**. Run `ssh root@<ip>` (modern macOS may need `-o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa`), then `passwd`. A factory reset does not clear this password. Keep the unit LAN-only and never port-forward it.
- Disable **Voice Services > OBiTALK Service**, **LUA Script Update**, **ITSP Provisioning** (after GV works) and keep **Auto Firmware Update** and **OBiTALK Provisioning** disabled.
- Take a fresh config backup and store it somewhere private.

## Careful habits from the community guide
primerisk's Google-Doc guide (linked in [`SOURCES.md`](SOURCES.md)) adds precautions we did not all need but which cost nothing:
- Before flashing, enable the web server from the phone if it is off (the keypad steps in Step 2) and note the unit's IP (`***1`).
- Use a desktop **Chrome** in a fresh Incognito window; the guide reports failed flashes from Firefox. We used `curl`, which worked, but do not flash from a flaky browser or over Wi-Fi.
- Disable **Auto Firmware Update** and **ITSP Provisioning** (the guide) and, as we did, **OBiTALK Provisioning**, submit, reboot, and check the settings stuck.
- Verify the MD5/SHA-256 of every file before uploading.
- After each flash: confirm the build number, **unplug power for 30 seconds**, then log in again from a new browser window. (Our `curl` run did not power-cycle between steps and had no problems; this is extra caution.)
- Settings usually survive the flashes. Non-GV SIP accounts restore fine (you may need to re-enter passwords); **Google Voice config generally does not carry over**, so expect to redo Step 3.

## Troubleshooting (community reports, not guarantees)
| Symptom | Things people reported working |
|---|---|
| `Token Error` after setup | Redo the token steps; delete the old Google Voice grant first; a **factory reset** (paperclip in the reset hole) then redo, which fixed several users; occasionally it started working on its own days later |
| `Connecting to ...; Token Error` with address `0.0.0.0`, or stuck on `Connecting to 216.239.36.145` | Usually DNS: check the OBi can resolve names. Some users added local DNS records for `obihai.sip.google.com` and `obihai.telephony.goog`. Try a reset first |
| `Connect Failed: 400 Bad Request` | Factory reset and redo the steps. Do **not** put your Google username or GV number in AuthUserName (the provisioning file fills `${DSN}_1` for you). naf suspects a config that is not GV-style SIP, or leftover zero-touch settings: check `CustomizationStatus` on the status page and, if it is locked to non-GV, run `clear_zt_params` over SSH, factory-reset and start over (our unit showed `Generic`) |
| `Connect Failed: 403 Forbidden` | Remove old Google Voice grants and redo. If the Google side seems fine, naf's advice: confirm you can sign in at voice.google.com *with that exact account* and that it shows a phone number. Also try power-cycling the OBi **and** your router, then reconnecting the OBi once the router is fully up (this fixed one user on a new ISP gateway) |
| Web UI unreachable after a flash | Re-enable the web server with the phone keypad steps in Step 2. On units with a LAN port, connect to that port instead of the WAN port |
| Can't dial out, dial tone stays | Check the phone first (we had dead batteries in a cordless handset). Then dial `***` to confirm digits are detected |
| AuthPassword shows `••••••••` after Submit | Normal: the field is masked |
| ITSP Provisioning goes back to `Disabled` by itself | Normal after a successful GV provisioning |
| The "broken" page is plain text (`PDMS-SP is no longer available`) instead of a 404 | Reported in 2026. The token is still in the address-bar URL; copy the full URL as before |
| Only one phone port shows in the menu (OBi202) | Cosmetic. Open `http://<ip>/VS_1_X_FXS_2_.xml` directly |
| Token worked once, then `Token Error` weeks later | Tokens for an unused line can lapse; reprovision (redo Step 3) |
| Red/green flashing LED after flashing | The unit may have fallen into **recovery mode** (it has its own web page and accepts any firmware). If it still ends up in recovery after a recovery flash, the flash is not being written |

## Certificates (Nov 2026 note)
Some GV-SIP client certificates expired on **2026-11-07**. Those were a rogue-client certificate extracted from an old OBi100 and shared for software-only clients. Genuine OBi200-family hardware carries its own factory certificate with years left. naf says the arrynrob14 build adds a `cert_expiration_check` command (run over SSH) that reports your certificate's expiry. See the community thread for details.

## What we did (reference run)
Stock `3.2.2 (Build: 8680EX)`, SP1 showing `Token Error`. Provisioning disabled, config backed up, then flashed 5921EX, 6259 bypass, `8680EX-arrynrob13` (each verified by `SoftwareVersion`), then the Google token steps above. SP1 became `Connected`, inbound call worked immediately, outbound worked after replacing the batteries in the cordless phone. Total flashing time about 20 minutes.

More guides, forums and background are listed in [`SOURCES.md`](SOURCES.md). See [`CREDITS.md`](CREDITS.md) for who made all of this possible.
