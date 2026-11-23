#!/usr/bin/env python3
"""obi-gv: guided Google Voice revival for OBi200/202/212/300/302/312 (MIT licence).

Python 3.8+, standard library only. Needs `curl` on PATH (used for HTTP digest auth;
credentials are passed to curl on stdin, never on the command line).

Safe by default: `status`, `plan` and `--dry-run` change nothing. Every flash asks for
confirmation. Read references/GUIDE.md first. No warranty: flashing can
brick a device.
"""
import argparse, getpass, hashlib, os, re, subprocess, sys, time, urllib.parse
from pathlib import Path

ALLOWED_MODELS = {"OBi200", "OBi202", "OBi212", "OBi300", "OBi302", "OBi312"}
HERE = Path(__file__).resolve().parent
DEFAULT_FW_DIR = Path.cwd() / "firmware-files"

# name -> (filename, sha256, expected substring of SoftwareVersion afterwards, download URL)
# Firmware is NOT shipped with this project: download it yourself into --fw-dir (default ./firmware-files).
FIRMWARE = {
    "stock5921": ("OBi202-3-2-2-5921EX-332148940.fw",
                  "ee1886a0c7d442b492f76f40b92fbad3357c3aada43df1361a33fe967b85c4ac", "Build: 5921EX",
                  "https://www.obifirmware.com/fw/OBi202-3-2-2-5921EX-332148940.fw"),
    "bypass": ("OBi302-3-2-2-6259-signed-fw-bypass-uboot-mod.fw",
               "5139075fbf468e88c5c4c944fd743d568e26a8b045e8493e306a69ca8384eebb", "Build: 6259",
               "https://www.obifirmware.com/fw/OBi302-3-2-2-6259-signed-fw-bypass-uboot-mod.fw"),
    "arrynrob13": ("OBi2xx-3-2-2-8680EX-arrynrob13.fw",
                   "ea68fc963c76fc0219698bc1d44b124602bce2f1a27122722fa8429b2df49877", "arrynrob13",
                   "https://www.obifirmware.com/fw/OBi2xx-3-2-2-8680EX-arrynrob13.fw"),
}
GV_CONFIG_URL = "https://www.obifirmware.com/fw/EnableGVSIPWithoutOBiTALK{}.xml"  # '' for SP1, _SP2.. for others
SUCCESS_MARK = "Configuration Update Successful"
KEYPAD_FIX = ("If the web UI is unreachable: from a phone on the OBi dial ***0, press 30#, press 1 "
              "(new value), press 1# (enable), press 1 (save), then hang up.")


class ObiError(Exception):
    pass


def cfg_quote(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


class Obi:
    def __init__(self, host, user, password, dry_run=False):
        self.base = "http://" + host
        self.user, self.password, self.dry = user, password, dry_run

    def _curl(self, url, extra_cfg=(), timeout=20):
        cfg = ["digest", "silent", "show-error", "max-time = %d" % timeout,
               "user = " + cfg_quote("%s:%s" % (self.user, self.password)), "url = " + cfg_quote(url)]
        cfg += list(extra_cfg)
        r = subprocess.run(["curl", "-K", "-"], input="\n".join(cfg) + "\n", capture_output=True,
                           text=True, errors="replace")
        if r.returncode != 0:
            raise ObiError("curl failed (%d): %s" % (r.returncode, r.stderr.strip()[:200]))
        return r.stdout

    def get(self, path, timeout=20):
        return self._curl(self.base + "/" + path, timeout=timeout)

    def set_params(self, params, mask=()):
        """params: list of (hash, value). Values in `mask` positions are hidden in dry-run output."""
        inner = "&".join("%s=%s" % (h, urllib.parse.quote(v, safe="")) for h, v in params)
        if self.dry:
            shown = "&".join("%s=%s" % (h, "****" if h in mask else v) for h, v in params)
            print("  [dry-run] POST /result.html ParameterList=" + shown)
            return
        out = self._curl(self.base + "/result.html",
                         ["data-urlencode = " + cfg_quote("ParameterList=" + inner)])
        if SUCCESS_MARK not in out:
            raise ObiError("device did not confirm the settings change")

    def upload_firmware(self, path):
        if self.dry:
            print("  [dry-run] POST /webupdategetconfig.htm System=@%s" % path)
            return
        out = self._curl(self.base + "/webupdategetconfig.htm",
                         ["form = " + cfg_quote("System=@" + str(path)), "form = WebUpdate=Update"], timeout=600)
        if "Firmware Update Started" not in out:
            raise ObiError("device did not accept the firmware (no 'Firmware Update Started')")

    def reboot(self):
        if self.dry:
            print("  [dry-run] GET /rebootgetconfig.htm")
            return
        self.get("rebootgetconfig.htm")


# ---------- XML helpers ----------
def parse_params(xml):
    """Return {(object, parameter): (hash, current, default)}. current falls back to default."""
    res, obj = {}, None
    for m in re.finditer(r'<object name="([^"]*)"|<parameter name="([^"]*)"[^>]*>.*?<value ([^>]*)>', xml, re.S):
        if m.group(1) is not None:
            obj = m.group(1)
            continue
        a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(3)))
        res[(obj, m.group(2))] = (a.get("hash"), a.get("current", a.get("default", "")), a.get("default", ""))
    return res


def find(params, obj, name):
    try:
        return params[(obj, name)]
    except KeyError:
        raise ObiError("parameter not found on this firmware: %s / %s" % (obj, name))


def device_info(obi):
    p = parse_params(obi.get("DI_S_.xml"))
    g = lambda o, n: p.get((o, n), (None, "", ""))[1]
    ver = next((v[1] for k, v in p.items() if k[1] == "SoftwareVersion"), "")
    up = next((v[1] for k, v in p.items() if k[1] == "UpTime"), "")
    m = re.search(r"(\d+) Days\s+(\d+):(\d+):(\d+)", up)
    up_s = (int(m.group(1)) * 86400 + int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4))) if m else None
    sp = {n: g("SP%d Service Status" % n, "Status") for n in range(1, 5)}
    return {"model": g("Product Information", "ModelName"), "hw": next((v[1] for k, v in p.items() if k[1] == "HardwareVersion"), ""),
            "version": ver, "uptime_s": up_s, "sp": sp,
            "customization": next((v[1] for k, v in p.items() if k[1] == "CustomizationStatus"), "")}


def build_number(ver):
    m = re.search(r"Build: (\d+)", ver)
    return int(m.group(1)) if m else None


def require_supported(info):
    if info["model"] not in ALLOWED_MODELS:
        raise ObiError("model %r is not supported (allowed: %s). Other OBi families need different routes."
                       % (info["model"], ", ".join(sorted(ALLOWED_MODELS))))
    if build_number(info["version"]) is None:
        raise ObiError("cannot read the firmware build from %r" % info["version"])


def plan_route(ver, bypass_installed=False, stock_6259=False):
    b = build_number(ver)
    if "arrynrob13" in ver:
        return []
    if "arrynrob" in ver:
        return ["arrynrob13"]  # earlier community build: signature check already bypassed
    if b == 6259:
        if bypass_installed:
            return ["arrynrob13"]
        if stock_6259:
            return ["stock5921", "bypass", "arrynrob13"]
        raise ObiError("Build 6259 is ambiguous: it is both a stock release and the bypass firmware. "
                       "Re-run with --bypass-installed (you flashed the bypass) or --stock-6259 (untouched stock).")
    if b < 5853:
        return ["arrynrob13"]
    if b < 6259:
        return ["bypass", "arrynrob13"]
    return ["stock5921", "bypass", "arrynrob13"]


def step_allowed(name, ver, bypass_done):
    b = build_number(ver)
    if name == "bypass":
        return b is not None and 5853 <= b < 6259 and "arrynrob" not in ver
    if name == "arrynrob13":
        return "arrynrob" in ver or (b is not None and (b < 6259 or (b == 6259 and bypass_done)))
    return True


# ---------- waiting ----------
def wait_back(obi, prev_version, expect=None, timeout=720):
    """Wait for the device after a flash (expect set) or a plain reboot (expect None)."""
    t0 = time.time()
    time.sleep(25)
    while time.time() - t0 < timeout:
        try:
            info = device_info(obi)
        except ObiError:
            time.sleep(10)
            continue
        fresh = info["uptime_s"] is not None and info["uptime_s"] < 240
        if expect is None:
            if fresh:
                return info
        elif expect in info["version"]:
            return info
        elif fresh:
            raise ObiError("device rebooted but reports %r, not the expected %r: the flash was not applied"
                           % (info["version"], expect))
        time.sleep(10)
    raise ObiError("timed out waiting for the device. " + KEYPAD_FIX)


def confirm(msg, yes):
    if yes:
        return
    if not sys.stdin.isatty():
        raise ObiError("refusing to continue without a terminal; pass --yes to confirm non-interactively")
    if input(msg + " Type 'yes' to continue: ").strip().lower() != "yes":
        raise ObiError("aborted by user")


# ---------- commands ----------
def cmd_status(obi, a):
    i = device_info(obi)
    print("Model: %s (hw %s)\nFirmware: %s\nUptime: %s s\nCustomization: %s"
          % (i["model"], i["hw"], i["version"], i["uptime_s"], i["customization"]))
    for n, s in i["sp"].items():
        print("SP%d: %s" % (n, s))
    dm = parse_params(obi.get("DM_S_.xml"))
    for o in ("Auto Firmware Update", "LUA Script Update", "ITSP Provisioning", "OBiTalk Provisioning"):
        print("%s: %s" % (o, find(dm, o, "Method")[1]))
    p2p = parse_params(obi.get("VS_1_X_P2P_1_.xml"))
    print("OBiTALK Service enabled: %s" % find(p2p, "OBiTALK Service Settings", "Enable")[1])
    print("(SSH: if you run arrynrob, change the default root/obi password; this tool cannot verify it.)")


def cmd_plan(obi, a):
    i = device_info(obi)
    require_supported(i)
    route = plan_route(i["version"], a.bypass_installed, a.stock_6259)
    print("Current: %s" % i["version"])
    print("Route: " + (" -> ".join(route) if route else "none, already on arrynrob13"))


def firmware_path(fwdir, name):
    fname, sha, _, url = FIRMWARE[name]
    path = Path(fwdir) / fname
    if not path.is_file():
        raise ObiError("missing firmware file: %s\nDownload it from %s and keep it in %s" % (path, url, fwdir))
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    if h != sha:
        raise ObiError("checksum mismatch for %s (got %s)" % (path.name, h))
    return path


def inside_git_repo(p):
    """True if p is in a git work tree OR inside this project's own folder (which may be about to become one)."""
    p = p.resolve()
    project = HERE.parent  # the skill folder itself
    return any((q / ".git").exists() for q in [p, *p.parents]) or p == project or project in p.parents


def cmd_backup(obi, a):
    out_dir = Path(a.out)
    if inside_git_repo(out_dir if out_dir.exists() else out_dir.parent) and not a.force:
        raise ObiError("%s is inside a git repository; backups contain credentials. Use another folder or --force." % out_dir)
    m = re.search(r"backup([0-9A-Fa-f]+)\.xml", obi.get("webupdateconfig.htm"))
    if not m:
        raise ObiError("could not find the backup endpoint")
    data = obi._curl(obi.base + "/" + m.group(0), ["form = Backup=Backup"], timeout=60)
    if "<ParameterList>" not in data:
        raise ObiError("backup did not return a configuration file")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / ("obi-backup-%s.xml" % time.strftime("%Y%m%d-%H%M%S"))
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(data)
    print("Saved %s (%d bytes, mode 600). It contains credentials: keep it private." % (path, len(data)))


def disable_updates(obi, full=False):
    dm = parse_params(obi.get("DM_S_.xml"))
    wanted = [("Auto Firmware Update", "Method"), ("OBiTalk Provisioning", "Method")]
    if full:
        wanted += [("LUA Script Update", "Method"), ("ITSP Provisioning", "Method")]
    todo = []
    for o, n in wanted:
        h, cur, _ = find(dm, o, n)
        if cur != "Disabled":
            todo.append((h, "Disabled"))
    params = list(todo)
    if full:
        p2p = parse_params(obi.get("VS_1_X_P2P_1_.xml"))
        h, cur, _ = find(p2p, "OBiTALK Service Settings", "Enable")
        if cur != "false":
            params.append((h, "false"))
    if params:
        obi.set_params(params)
    else:
        print("  already disabled")
    return bool(params)


def cmd_harden(obi, a):
    i = device_info(obi)
    require_supported(i)
    confirm("Disable auto firmware update and OBiTALK provisioning%s." % (" plus LUA/ITSP/OBiTALK service" if a.full else ""), a.yes or obi.dry)
    disable_updates(obi, a.full)
    print("Done." if not obi.dry else "Dry run only.")


def cmd_flash(obi, a):
    info = device_info(obi)
    require_supported(info)
    route = plan_route(info["version"], a.bypass_installed, a.stock_6259)
    if not route:
        print("Already on %s: nothing to flash." % info["version"])
        return
    print("Current: %s\nRoute: %s" % (info["version"], " -> ".join(route)))
    paths = {n: firmware_path(a.fw_dir, n) for n in route}  # verify every checksum before touching the device
    print("All firmware checksums verified.")
    print("Preconditions: wired Ethernet, original power supply, no one needs the phone for ~20 minutes, config backed up.")
    confirm("Begin flashing %d file(s)." % len(route), a.yes or obi.dry)
    bypass_done = a.bypass_installed
    sim = {"stock5921": "5921EX", "bypass": "6259", "arrynrob13": "8680EX-arrynrob13"}
    sim_ver = info["version"]
    for n in route:
        info = {"version": sim_ver} if obi.dry else device_info(obi)
        if not step_allowed(n, info["version"], bypass_done):
            raise ObiError("refusing to flash %s while on %r (would be unsafe, e.g. bypass from 6259+)" % (n, info["version"]))
        if n != route[0]:
            confirm("Next: flash %s." % paths[n].name, a.yes or obi.dry)
        print("Flashing %s ..." % paths[n].name)
        obi.upload_firmware(paths[n])
        if obi.dry:
            sim_ver = "3.2.2 (Build: %s)" % sim[n]
            bypass_done = bypass_done or n == "bypass"
            continue
        new = wait_back(obi, info["version"], FIRMWARE[n][2])
        print("  now running: %s" % new["version"])
        bypass_done = bypass_done or n == "bypass"
    print("Flashing complete." if not obi.dry else "Dry run only: nothing was sent.")
    print("Next: revoke old Google Voice grants, get a refresh token, then run `gv-setup`.")


def cmd_gv_setup(obi, a):
    info = device_info(obi)
    require_supported(info)
    if "arrynrob" not in info["version"]:
        raise ObiError("community firmware (arrynrob) is required first; run `flash`.")
    token = os.environ.get("OBI_GV_REFRESH_TOKEN") or (getpass.getpass("Paste Google refresh token (hidden): ") if sys.stdin.isatty() else "")
    token = token.strip()
    if len(token) < 20 or re.search(r"\s", token):
        raise ObiError("that does not look like a refresh token (paste only the token, nothing else)")
    sp = a.sp
    page = "VS_1_VP_1_L_%d_.xml" % sp  # SPn service pages live under ITSP profile A
    h_tok = find(parse_params(obi.get(page)), "SIP Credentials", "AuthPassword")[0] if not obi.dry else "<AuthPassword>"
    dm = parse_params(obi.get("DM_S_.xml"))
    h_url, h_meth = find(dm, "ITSP Provisioning", "ConfigURL")[0], find(dm, "ITSP Provisioning", "Method")[0]
    url = GV_CONFIG_URL.format("" if sp == 1 else "_SP%d" % sp)
    print("SP%d: set AuthPassword (hidden), ITSP ConfigURL=%s, Method=System Start, then reboot." % (sp, url))
    confirm("Apply Google Voice settings to SP%d." % sp, a.yes or obi.dry)
    obi.set_params([(h_tok, token)], mask=(h_tok,))
    obi.set_params([(h_url, url), (h_meth, "System Start")])
    obi.reboot()
    if obi.dry:
        print("Dry run only.")
        return
    wait_back(obi, info["version"], None)
    deadline = time.time() + 240
    status = ""
    while time.time() < deadline:
        status = device_info(obi)["sp"][sp]
        if status.startswith("Connected"):
            break
        time.sleep(10)
    print("SP%d status: %s" % (sp, status))
    if status.startswith("Connected"):
        disable_updates(obi, full=True)  # provisioning normally resets itself; make sure
        print("Connected. Provisioning paths disabled. Place a test call in and out, then change the SSH password.")
    else:
        print("Not connected yet. See the troubleshooting table in references/GUIDE.md (revoke old grants, reset, retry).")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--host", required=True, help="device IP address (no scanning is done)")
    ap.add_argument("--user", default="admin")
    ap.add_argument("--dry-run", action="store_true", help="show what would be sent; change nothing")
    ap.add_argument("--yes", action="store_true", help="skip confirmations (non-interactive)")
    ap.add_argument("--fw-dir", default=str(DEFAULT_FW_DIR))
    ap.add_argument("--bypass-installed", action="store_true", help="you already flashed the 6259 bypass firmware")
    ap.add_argument("--stock-6259", action="store_true", help="the device is on untouched stock 6259")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("plan")
    b = sub.add_parser("backup"); b.add_argument("--out", default="backup"); b.add_argument("--force", action="store_true")
    h = sub.add_parser("harden"); h.add_argument("--full", action="store_true", help="also disable LUA, ITSP and the OBiTALK service")
    sub.add_parser("flash")
    g = sub.add_parser("gv-setup"); g.add_argument("--sp", type=int, choices=[1, 2, 3, 4], default=1)
    a = ap.parse_args()
    pw = os.environ.get("OBI_PASSWORD", "admin")
    obi = Obi(a.host, a.user, pw, a.dry_run)
    cmds = {"status": cmd_status, "plan": cmd_plan, "backup": cmd_backup, "harden": cmd_harden,
            "flash": cmd_flash, "gv-setup": cmd_gv_setup}
    try:
        cmds[a.cmd](obi, a)
    except ObiError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\nInterrupted. If a flash was in progress, do NOT power-cycle the device; wait 10 minutes.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
