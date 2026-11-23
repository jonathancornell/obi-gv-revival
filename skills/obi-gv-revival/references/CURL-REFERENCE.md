# Driving the OBi web UI with curl

Useful when the browser shows plain-text pages (XSLT removal) or you want to script the process. All requests use **HTTP Digest** auth. Replace `<ip>`, and use your own admin password.

```sh
AUTH='--digest -u admin:admin'
```

## Read status
```sh
curl -s $AUTH http://<ip>/DI_S_.xml | grep -A12 'name="SoftwareVersion"'   # firmware version
```
Config pages are XML: `DI_S_.xml` (status), `DM_S_.xml` (auto provisioning), `VS_1_VP_1_L_1_.xml` (SP1 service), `VS_1_X_P2P_1_.xml` (OBiTALK service), `VS_1_X_FXS_1_.xml` (PHONE port). `menu.htm` lists them all. Each `<parameter>` has `<value hash="..." default="..." current="...">`. `scripts/obi_flatten.py page.xml` prints `parameter = current (default)`.

## Change settings
POST one form field, `ParameterList`, to `/result.html`: `hash1=Value&hash2=Value`, URI-encoded.
```sh
curl $AUTH --data-urlencode "ParameterList=46eb45e6=Disabled&585f758d=Disabled" http://<ip>/result.html
```
That disables Auto Firmware Update (`46eb45e6`) and OBiTALK Provisioning (`585f758d`). Success page says "Configuration Update Successful". Hashes were read from a device on this firmware; verify them on yours first. Use `default` as the value to reset a parameter.

## Back up
```sh
curl $AUTH -F "Backup=Backup" -o backup.xml http://<ip>/backup<MAC>.xml    # <MAC> as printed on webupdateconfig.htm, e.g. backupAABBCCDDEEFF.xml
```
The file holds credentials. Keep it private.

## Flash firmware
```sh
curl $AUTH -F "System=@file.fw" -F "WebUpdate=Update" http://<ip>/webupdategetconfig.htm
```
The response "Firmware Update Started" means the file was accepted. The unit reboots; poll `DI_S_.xml` until `SoftwareVersion` changes. Other endpoints on `webupdateconfig.htm`: `restore.xml` (restore config) and `reset.htm` (factory reset; avoid).

## Wait for the device
Poll until it answers, then read the version. A 401 just means you forgot digest auth.
```sh
until curl -s -m 8 $AUTH http://<ip>/DI_S_.xml | grep -q Build; do sleep 10; done
```
