#!/usr/bin/env python3
"""Fresh Ubuntu/Debian VPS provisioning payload used by bootstrap_server.py.

Not a local workstation setup script. Direct execution only prints a refusal.
Guide: docs/quick-start.md and docs/automation.md#start-with-only-a-vps-ip-and-root-password
Only executes when the launcher supplies BOOTSTRAP_OPTIONS over authenticated SSH.
"""
import base64
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import secrets
import shutil
import socket
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

VERSION = "v3.8.5"
INSTALLER = f"https://raw.githubusercontent.com/MHSanaei/3x-ui/{VERSION}/install.sh"
EXISTING_PATHS = ("/usr/local/x-ui/x-ui", "/etc/x-ui/x-ui.db")
FINGERPRINTS = ("chrome", "safari", "firefox", "edge", "ios", "android", "random", "randomized", "360", "qq")


def core_number(version):
    match = re.search(r"(?:^|Xray\s+|v)(\d{1,2})\.(\d{1,2})\.(\d{1,2})(?:\s|$)", version)
    if not match:
        raise ValueError("Xray version must be a release number such as 26.7.28")
    return tuple(map(int, match.groups()))


def validate_core_options(version, key_share, transport="raw"):
    number = core_number(version)
    if key_share not in ("classical", "hybrid"):
        raise ValueError("key share must be classical or hybrid")
    if transport not in ("raw", "xhttp"):
        raise ValueError("transport must be raw or xhttp")
    if key_share == "classical" and number >= (26, 9, 8):
        raise ValueError("classical requires a compatible older server; use 26.7.28 or select hybrid")
    return ".".join(map(str, number))


def check_target(target):
    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.set_alpn_protocols(["h2"])
    addresses = socket.getaddrinfo(target, 443, family=socket.AF_INET, type=socket.SOCK_STREAM)
    for family, kind, protocol, _, address in addresses[:3]:
        try:
            with socket.socket(family, kind, protocol) as connection:
                connection.settimeout(5)
                connection.connect(address)
                with context.wrap_socket(connection, server_hostname=target) as secure:
                    if secure.selected_alpn_protocol() == "h2":
                        return
        except OSError:
            continue
    raise RuntimeError("REALITY target needs reachable IPv4, a valid certificate, TLS 1.3 and HTTP/2")


def install_pinned_core(version, command):
    """Pin the core on a newly installed panel, verifying the official asset digest."""
    version = ".".join(map(str, core_number(version)))
    current = next(p for p in Path("/usr/local/x-ui/bin").glob("xray-*")
                   if p.is_file() and os.access(p, os.X_OK))
    machine = platform.machine().lower()
    architectures = {"x86_64": "64", "amd64": "64", "aarch64": "arm64-v8a", "arm64": "arm64-v8a"}
    if machine not in architectures:
        raise RuntimeError("Pinned core installation supports x86-64 and ARM64 VPSs")
    asset_name = "Xray-linux-" + architectures[machine] + ".zip"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    release_url = "https://api.github.com/repos/XTLS/Xray-core/releases/tags/v" + version
    with opener.open(release_url, timeout=30) as response:
        release = json.load(response)
    assets = [a for a in release.get("assets", []) if a.get("name") == asset_name]
    if len(assets) != 1 or not re.fullmatch(r"sha256:[0-9a-f]{64}", assets[0].get("digest", "")):
        raise RuntimeError("The official release has no unique SHA-256-verified core asset")
    asset = assets[0]
    expected_url = "https://github.com/XTLS/Xray-core/releases/download/v" + version + "/" + asset_name
    if asset.get("browser_download_url") != expected_url:
        raise RuntimeError("Unexpected official core download URL")
    env = dict(os.environ, XRAY_LOCATION_ASSET=str(current.parent), GODEBUG="multipathtcp=0")
    with tempfile.TemporaryDirectory(prefix=".vpn-core-", dir=current.parent) as directory:
        directory = Path(directory)
        archive = directory / asset_name
        with opener.open(expected_url, timeout=60) as response, archive.open("wb") as output:
            shutil.copyfileobj(response, output)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != asset["digest"].split(":", 1)[1]:
            raise RuntimeError("Core archive SHA-256 verification failed")
        staged = directory / "xray"
        with zipfile.ZipFile(archive) as bundle:
            staged.write_bytes(bundle.read("xray"))
        staged.chmod(0o755)
        if not command([str(staged), "version"], env=env, capture=True).startswith("Xray " + version + " "):
            raise RuntimeError("Downloaded core reports a different version")
        command([str(staged), "run", "-test", "-config", str(current.parent / "config.json")], env=env)
        saved = Path("/root/vpn-core-backups") / (time.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(4))
        saved.mkdir(mode=0o700, parents=True)
        shutil.copy2(current, saved / "xray")
        dropin = Path("/etc/systemd/system/x-ui.service.d/90-vpn-guide-core.conf")
        previous = dropin.read_bytes() if dropin.exists() else None
        try:
            dropin.parent.mkdir(parents=True, exist_ok=True)
            dropin.write_text('[Service]\nEnvironment="GODEBUG=multipathtcp=0"\n')
            os.replace(staged, current)
            command(["systemctl", "daemon-reload"])
            command(["systemctl", "restart", "x-ui"])
            command(["systemctl", "is-active", "--quiet", "x-ui"])
        except Exception:
            restored = directory / "restored-xray"
            shutil.copy2(saved / "xray", restored)
            os.replace(restored, current)
            if previous is None:
                dropin.unlink(missing_ok=True)
            else:
                dropin.write_bytes(previous)
            command(["systemctl", "daemon-reload"])
            command(["systemctl", "restart", "x-ui"])
            raise
    return str(saved)


def select_fingerprint(country, requested="auto"):
    if requested != "auto":
        if requested not in FINGERPRINTS:
            raise ValueError("unsupported client fingerprint")
        return requested
    if not re.fullmatch(r"[A-Z]{2}", country) or country in ("XX", "ZZ"):
        raise ValueError("VPS country is unresolved; set --server-country or --fingerprint explicitly")
    return "safari" if country == "US" else "chrome"


def detect_server_country(host):
    # Public-IP geolocation only; never sends credentials. See docs/automation.md.
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open("https://api.country.is/" + urllib.parse.quote(host, safe=""), timeout=5) as response:
            value = json.load(response)
        country = value.get("country", "")
        if value.get("ip") != host:
            raise ValueError("country response does not match the VPS IP")
        select_fingerprint(country)
        return country
    except (OSError, ValueError, TypeError, AttributeError) as error:
        raise RuntimeError("VPS country lookup failed. No installation was started. Supply --server-country US/DE/etc. (PowerShell: -ServerCountry), or an explicit --fingerprint / -Fingerprint.") from error


def resolve_fingerprint_options(options):
    country = options.get("server_country", "auto")
    requested = options.get("fingerprint", "auto")
    if country == "auto":
        country = detect_server_country(options["host"]) if requested == "auto" else "unknown"
    options["fingerprint"] = select_fingerprint(country, requested)
    options["server_country"] = country
    return options


def assert_fresh(root=Path("/")):
    if any((root / name.lstrip("/")).exists() for name in EXISTING_PATHS):
        raise RuntimeError("Existing 3x-ui installation detected. Nothing was reset. Use the existing-server guide.")


def available_port(preferred, host="0.0.0.0"):
    try:
        with socket.socket() as s:
            s.bind((host, preferred))
        return preferred
    except OSError:
        return None


def inbound_payload(options, private, public, account, sid):
    fingerprint = select_fingerprint(options.get("server_country", "auto"), options.get("fingerprint", "auto"))
    transport = options.get("transport", "raw")
    client = {"id": account, "flow": "" if transport == "xhttp" else "xtls-rprx-vision", "email": options.get("client_label", "first-device"),
              "enable": True, "expiryTime": 0, "totalGB": 0, "limitIp": 0,
              "subId": secrets.token_hex(12), "reset": 0}
    stream = {"network": "tcp", "security": "reality", "realitySettings": {
        "show": False, "xver": 0, "target": options["target"] + ":443",
        "serverNames": [options["target"]], "privateKey": private, "shortIds": [sid],
        "settings": {"publicKey": public, "fingerprint": fingerprint,
                     "serverName": options["target"], "spiderX": "/"}}}
    if transport == "xhttp":
        stream["network"] = "xhttp"
        stream["xhttpSettings"] = {"path": options.get("xhttp_path", "/vpn"), "mode": "auto"}
    return {"remark": "Personal VPN", "enable": True, "listen": "0.0.0.0",
            "port": options["vpn_port"], "protocol": "vless", "expiryTime": 0,
            "total": 0, "up": 0, "down": 0,
            "settings": json.dumps({"clients": [client], "decryption": "none", "fallbacks": []}),
            "streamSettings": json.dumps(stream), "sniffing": json.dumps({"enabled": False})}


def set_ipv4(template):
    matches = [o for o in template.get("outbounds", []) if o.get("protocol") == "freedom"]
    direct = next((o for o in matches if o.get("tag") == "direct"), None)
    if direct is None:
        raise RuntimeError("The fresh template has no direct/freedom outbound; stopped rather than guessing routing.")
    direct.setdefault("settings", {}).pop("domainStrategy", None)
    direct.setdefault("streamSettings", {}).setdefault("sockopt", {})["domainStrategy"] = "ForceIPv4"
    return template


def panel_share_link(options, account, public, sid, links):
    """Select the exact panel export; never reconstruct its title or SpiderX."""
    fingerprint = select_fingerprint(options.get("server_country", "auto"), options.get("fingerprint", "auto"))
    transport = options.get("transport", "raw")
    expected = {"encryption": "none", "flow": "" if transport == "xhttp" else "xtls-rprx-vision",
        "security": "reality", "sni": options["target"], "fp": fingerprint, "pbk": public,
        "sid": sid, "type": "xhttp" if transport == "xhttp" else "tcp"}
    if transport == "xhttp":
        expected["path"] = options.get("xhttp_path", "/vpn")
    for link in links if isinstance(links, list) else []:
        if not isinstance(link, str):
            continue
        try:
            value = urllib.parse.urlsplit(link)
            matches = (value.scheme == "vless" and value.username == account
                       and value.hostname == options["host"] and value.port == options["vpn_port"]
                       and bool(value.fragment))
            query = urllib.parse.parse_qs(value.query, keep_blank_values=True)
            # VLESS defaults to none; 3x-ui can omit this default in its export.
            # Validate the meaning while returning the original URI unchanged.
            query.setdefault("encryption", ["none"])
            query.setdefault("flow", [""])
            if matches and all(query.get(key) == [expected_value] for key, expected_value in expected.items()):
                return link
        except ValueError:
            continue
    raise RuntimeError("The panel did not export a matching named client link. Open the existing panel to inspect it; do not rerun provisioning or invent a replacement URI.")


def run(options):
    if os.geteuid() != 0:
        raise RuntimeError("The setup needs root on the VPS.")
    if options.get("vpn_port") not in (443, 8443):
        raise ValueError("public VPN inbound port must be 443 or 8443")
    assert_fresh()
    version = validate_core_options(options.get("core_version", "26.7.28"),
                                    options.get("key_share", "classical"), options.get("transport", "raw"))
    os_release = Path("/etc/os-release").read_text()
    if not any(f'ID={value}' in os_release or f'ID="{value}"' in os_release for value in ("ubuntu", "debian")):
        raise RuntimeError("This bootstrap supports fresh Ubuntu/Debian systemd VPS installations only.")
    if not Path("/run/systemd/system").exists():
        raise RuntimeError("A systemd VPS is required; this is not a container/WSL installer.")
    options = resolve_fingerprint_options(dict(options))
    labels = options.get("clients", ["first-device"])
    if (not isinstance(labels, list) or not labels or len(set(labels)) != len(labels)
            or any(not isinstance(label, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", label) for label in labels)):
        raise ValueError("Provide unique client labels containing letters, digits, dots, underscores or hyphens")
    print("VPS country: " + options["server_country"] + "; client fingerprint: " + options["fingerprint"], flush=True)
    vpn_port = available_port(options["vpn_port"])
    if vpn_port is None:
        if options["vpn_port"] == 443 and available_port(8443):
            options["vpn_port"] = 8443
            print("VPN TCP 443 is occupied; selecting free TCP 8443.", flush=True)
        else:
            raise RuntimeError("Selected VPN port is occupied. No existing listener was stopped.")
    if available_port(options["panel_port"], "127.0.0.1") is None:
        raise RuntimeError("The selected panel port is occupied; choose --panel-port and retry.")
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    log_path = Path("/root") / ("vpn-guide-bootstrap-" + stamp + ".log")
    fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as log:
        def command(argv, timeout=600, env=None, capture=False):
            result = subprocess.run(argv, stdout=subprocess.PIPE if capture else log,
                stderr=log, text=True, timeout=timeout, env=env)
            if result.returncode:
                raise RuntimeError(f"A setup command failed; inspect the private VPS log {log_path}. No automatic reset was attempted.")
            return result.stdout if capture else ""

        env = dict(os.environ, DEBIAN_FRONTEND="noninteractive", LC_ALL="C")
        print("Preparing packages on the fresh VPS...", flush=True)
        command(["apt-get", "update"], env=env)
        command(["apt-get", "install", "-y", "curl", "ca-certificates", "python3-cryptography"], env=env)
        print("Checking the REALITY target over IPv4...", flush=True)
        check_target(options["target"])
        username = "vpnadmin_" + secrets.token_hex(4)
        password = secrets.token_urlsafe(24)
        web_path = "/"
        install_env = dict(env, XUI_NONINTERACTIVE="1", XUI_DB_TYPE="sqlite", XUI_SSL_MODE="none",
            XUI_ENABLE_FAIL2BAN="false",
            XUI_USERNAME=username, XUI_PASSWORD=password, XUI_WEB_BASE_PATH=web_path,
            XUI_PANEL_PORT=str(options["panel_port"]), XUI_SERVER_IP=options["host"])
        print("Installing pinned official 3x-ui " + VERSION + "...", flush=True)
        with tempfile.TemporaryDirectory(prefix="vpn-guide-install-") as folder:
            installer = Path(folder) / "install.sh"
            with urllib.request.urlopen(INSTALLER, timeout=30) as response:
                installer.write_bytes(response.read())
            command(["bash", str(installer), VERSION], timeout=1800, env=install_env)
        binary = "/usr/local/x-ui/x-ui"
        print("Enabling direct browser access to the panel...", flush=True)
        command([binary, "setting", "-listenIP", "0.0.0.0", "-webBasePath", web_path])
        command(["systemctl", "restart", "x-ui"])
        core_backup = install_pinned_core(version, command)
        token_output = command([binary, "setting", "-getApiToken"], capture=True)
        token_line = next((line for line in token_output.splitlines() if "apiToken: " in line), None)
        if token_line is None:
            raise RuntimeError("Could not obtain the new installation's API token. Use the local panel to finish; credentials remain in /etc/x-ui/install-result.env.")
        token = token_line.split("apiToken: ", 1)[1].strip()
        base = f"http://127.0.0.1:{options['panel_port']}{web_path}panel/api/"
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

        def api(endpoint, payload=None, form=False):
            data = None
            headers = {"Authorization": "Bearer " + token, "X-Requested-With": "XMLHttpRequest",
                       "Host": f"{options['host']}:{options['panel_port']}"}
            if payload is not None:
                if form:
                    data = urllib.parse.urlencode(payload).encode()
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                else:
                    data = json.dumps(payload).encode()
                    headers["Content-Type"] = "application/json"
            try:
                with opener.open(urllib.request.Request(base + endpoint, data=data, headers=headers), timeout=30) as r:
                    result = json.load(r)
            except (OSError, ValueError, urllib.error.URLError):
                raise RuntimeError(f"Panel API request failed at {endpoint}; finish through the local panel rather than rerunning the installer.") from None
            if not result.get("success"):
                raise RuntimeError(f"Panel rejected {endpoint}; inspect the private server log/panel. No credentials are printed here.")
            return result.get("obj")

        for attempt in range(20):
            try:
                with socket.create_connection(("127.0.0.1", options["panel_port"]), timeout=1):
                    break
            except OSError:
                time.sleep(1)
        print("Selecting ForceIPv4 in the new panel template...", flush=True)
        wrapper = api("xray/", {})
        if isinstance(wrapper, str):
            wrapper = json.loads(wrapper)
        template = wrapper["xraySetting"]
        if isinstance(template, str):
            template = json.loads(template)
        api("xray/update", {"xraySetting": json.dumps(set_ipv4(template))}, form=True)
        if options.get("panel_only"):
            if shutil.which("ufw"):
                status = command(["ufw", "status"], capture=True, env=env)
                if status.startswith("Status: active"):
                    command(["ufw", "allow", str(options["panel_port"]) + "/tcp"], env=env)
            xray = next(p for p in Path("/usr/local/x-ui/bin").glob("xray-*")
                        if p.is_file() and os.access(p, os.X_OK))
            result = {"host": options["host"], "ssh_port": options["ssh_port"],
                      "panel_port": options["panel_port"], "web_path": web_path,
                      "panel_username": username, "panel_password": password,
                      "panel_version": VERSION, "panel_only": True,
                      "core_backup": core_backup,
                      "core_version": command([str(xray), "version"], capture=True).splitlines()[0],
                      "server_log": str(log_path)}
            fd = os.open("/root/vpn-guide-panel-result.json",
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as f:
                json.dump(result, f, indent=2)
            print("Panel installed; no VPN inbound or client account created.", flush=True)
            print("VPN_BOOTSTRAP_RESULT " + json.dumps(result), flush=True)
            return
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption
        key = X25519PrivateKey.generate()
        encode = lambda value: base64.urlsafe_b64encode(value).decode().rstrip("=")
        private = encode(key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption()))
        public = encode(key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw))
        account, sid = str(uuid.uuid4()), secrets.token_hex(4)
        print("Creating one VLESS/REALITY client account...", flush=True)
        options["client_label"] = labels[0]
        api("inbounds/add", inbound_payload(options, private, public, account, sid))
        accounts = {labels[0]: account}
        if len(labels) > 1:
            inbounds = api("inbounds/list")
            selected = [item for item in inbounds if item["port"] == options["vpn_port"] and item["remark"] == "Personal VPN"]
            if len(selected) != 1:
                raise RuntimeError("Cannot identify the new inbound for additional device accounts")
            for label in labels[1:]:
                client = json.loads(inbound_payload(dict(options, client_label=label), private, public,
                                    str(uuid.uuid4()), sid)["settings"])["clients"][0]
                api("clients/add", {"inboundIds": [selected[0]["id"]], "client": client})
                accounts[label] = client["id"]
        api("server/restartXrayService", {})
        command(["systemctl", "enable", "x-ui"])
        ufw = subprocess.run(["bash", "-c", "command -v ufw"], capture_output=True, text=True)
        firewall = "No active UFW policy was changed; check any custom/provider firewall."
        if ufw.returncode == 0:
            status = command(["ufw", "status"], capture=True, env=env)
            if status.startswith("Status: active"):
                for port in (options["vpn_port"], options["panel_port"]):
                    command(["ufw", "allow", str(port) + "/tcp"], env=env)
                firewall = "Added VPN and panel TCP allow rules to the already-active UFW policy; SSH rules were preserved."
        xray = next((p for p in Path("/usr/local/x-ui/bin").glob("xray-*") if p.is_file() and os.access(p, os.X_OK)), None)
        if xray is None:
            raise RuntimeError("Installed Xray binary not found; open the panel to inspect the installation.")
        core_version = command([str(xray), "version"], capture=True).splitlines()[0]
        for attempt in range(20):
            try:
                with socket.create_connection(("127.0.0.1", options["vpn_port"]), timeout=1):
                    break
            except OSError:
                if attempt == 19:
                    raise RuntimeError("The new VPN listener did not start; inspect the panel and server log.")
                time.sleep(1)
        from vpn_profile import hiddify_link
        canonical_links = {label: panel_share_link(options, client_id, public, sid,
            api("clients/links/" + urllib.parse.quote(label, safe=""))) for label, client_id in accounts.items()}
        key_share = options.get("key_share", "classical")
        client_links = {label: hiddify_link(link, key_share) for label, link in canonical_links.items()}
        canonical = canonical_links[labels[0]]
        result = {"host": options["host"], "ssh_port": options["ssh_port"], "panel_port": options["panel_port"],
            "web_path": web_path, "panel_listen": "0.0.0.0", "panel_username": username, "panel_password": password,
            "vpn_port": options["vpn_port"], "target": options["target"], "panel_version": VERSION,
            "core_version": core_version, "canonical_link": canonical,
            "client_link": hiddify_link(canonical, key_share), "key_share": key_share,
            "canonical_links": canonical_links, "client_links": client_links,
            "transport": options.get("transport", "raw"), "core_backup": core_backup,
            "server_country": options["server_country"], "fingerprint": options["fingerprint"],
            "firewall": firewall, "server_log": str(log_path)}
        result_file = Path("/root/vpn-guide-bootstrap-result.json")
        result_fd = os.open(result_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(result_fd, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print("Server prepared. Provider firewall and end-to-end client verification remain separate checks.", flush=True)
        print("VPN_BOOTSTRAP_RESULT " + json.dumps(result), flush=True)


if __name__ == "__main__":
    if "BOOTSTRAP_OPTIONS" not in globals():
        raise SystemExit("Do not run this payload locally. Read docs/quick-start.md and use scripts/bootstrap_server.py --plan.")
    try:
        run(BOOTSTRAP_OPTIONS)
    except Exception as error:
        print("Setup stopped: " + str(error), flush=True)
        print("Keep the VPS and inspect it; do not erase an existing installation to retry.", flush=True)
        raise SystemExit(1)
