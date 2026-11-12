#!/usr/bin/env python3
"""Remote 3x-ui relay payload. Invoked by bootstrap_relay.py, not locally."""
import base64
import copy
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import sqlite3
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
import uuid

from provision_remote import inbound_payload, set_ipv4, validate_core_options, check_target
from vpn_profile import parse_profile, client_config, write_config, curl_command, redact, hiddify_link

STATE = Path("/etc/vpn-guide-relay/routes.json")


def obj(value):
    return json.loads(value) if isinstance(value, str) else value


def private_write(path, value):
    path = Path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp-" + secrets.token_hex(4))
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(value, f, indent=2)
    os.replace(temporary, path)


def global_ipv6():
    interfaces = json.loads(subprocess.check_output(
        ["ip", "-j", "-6", "address", "show", "scope", "global"], text=True))
    return [a["local"] for i in interfaces for a in i.get("addr_info", [])
            if a.get("family") == "inet6" and a.get("scope") == "global"
            and not a.get("tentative") and not a.get("deprecated")]


def inspect():
    present = Path("/usr/local/x-ui/x-ui").exists()
    return {"panel_present": present, "ipv6": global_ipv6(),
            "core_version": subprocess.check_output([core_binary(), "version"], text=True).splitlines()[0] if present else None,
            "ipv6_default": bool(subprocess.check_output(
                ["ip", "-6", "route", "show", "default"], text=True).strip()),
            "routes": json.loads(STATE.read_text()) if STATE.exists() else {}}


class Panel:
    def __init__(self, options):
        self.options = options
        output = subprocess.check_output(
            ["/usr/local/x-ui/x-ui", "setting", "-getApiToken"], text=True)
        self.token = next(x.split("apiToken: ", 1)[1].strip()
                          for x in output.splitlines() if "apiToken: " in x)
        self.base = "http://127.0.0.1:" + str(options["panel_port"]) + "/panel/api/"
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def api(self, endpoint, payload=None, form=False, export_host=None):
        headers = {"Authorization": "Bearer " + self.token,
                   "Host": (export_host or self.options["public_host"]) + ":" +
                           str(self.options["panel_port"])}
        data = None
        if payload is not None:
            headers["Content-Type"] = ("application/x-www-form-urlencoded" if form
                                       else "application/json")
            data = (urllib.parse.urlencode(payload) if form
                    else json.dumps(payload)).encode()
        with self.opener.open(urllib.request.Request(self.base + endpoint,
                             data=data, headers=headers), timeout=30) as response:
            result = json.load(response)
        if not result.get("success"):
            raise RuntimeError("Panel rejected " + endpoint + "; inspect the private backup and panel.")
        return result.get("obj")

    def template(self):
        return obj(obj(self.api("xray/", {}))["xraySetting"])

    def set_template(self, template):
        self.api("xray/update", {"xraySetting": json.dumps(template)}, form=True)

    def inbound(self, inbound_id):
        return next(i for i in self.api("inbounds/list") if i["id"] == inbound_id)

    def activate(self, inbound_id, enabled=True):
        value = self.inbound(inbound_id)
        value["enable"] = enabled
        self.api("inbounds/update/" + str(inbound_id), value)
        self.api("server/restartXrayService", {})

    def attach(self, inbound_id, labels):
        existing = {c["email"]: c for c in self.api("clients/list")}
        flow = "" if getattr(self, "options", {}).get("transport", "raw") == "xhttp" else "xtls-rprx-vision"
        for label in labels:
            email = urllib.parse.quote(label, safe="")
            if label in existing:
                if existing[label].get("flow", "xtls-rprx-vision") != flow:
                    raise ValueError("Existing account flow differs; choose a separate label for the new transport")
                self.api("clients/" + email + "/attach", {"inboundIds": [inbound_id]})
            else:
                self.api("clients/add", {"inboundIds": [inbound_id], "client": {
                    "id": str(uuid.uuid4()), "email": label, "enable": True,
                    "flow": flow, "subId": secrets.token_hex(12),
                    "expiryTime": 0, "totalGB": 0, "limitIp": 0}})

    def export(self, inbound_id, label, expected_host, fingerprint):
        inbound = self.inbound(inbound_id)
        host_header = "[" + expected_host + "]" if ":" in expected_host else expected_host
        links = self.api("clients/links/" + urllib.parse.quote(label, safe=""),
                         export_host=host_header)
        account = next(c for c in obj(inbound["settings"])["clients"] if c["email"] == label)
        matches = []
        for link in links:
            try:
                p = parse_profile(link)
            except ValueError:
                continue
            if (p.host == expected_host and p.port == inbound["port"]
                    and p.account == account["id"] and p.fingerprint == fingerprint
                    and p.sni == self.options["target"]
                    and p.transport == self.options.get("transport", "raw")
                    and (p.transport != "xhttp" or p.path == self.options.get("xhttp_path", "/vpn"))):
                matches.append(link)
        if len(matches) != 1:
            raise RuntimeError("No unique canonical panel export matched the requested endpoint.")
        return matches[0]


def key_pair():
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption
    key = X25519PrivateKey.generate()
    encode = lambda v: base64.urlsafe_b64encode(v).decode().rstrip("=")
    return (encode(key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())),
            encode(key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)))


def new_inbound(options):
    private, public = key_pair()
    payload = inbound_payload({"target": options["target"], "fingerprint": options["fingerprint"],
        "server_country": "unknown", "vpn_port": options["port"],
        "transport": options.get("transport", "raw"), "xhttp_path": options.get("xhttp_path", "/vpn")},
        private, public, str(uuid.uuid4()), secrets.token_hex(4))
    settings = obj(payload["settings"])
    settings["clients"] = []
    payload.update(remark=options["remark"], listen=options["listen"],
                   enable=False, settings=json.dumps(settings))
    return payload


def insert_rules(template, rules):
    existing = template.setdefault("routing", {}).setdefault("rules", [])
    # Preserve API reachability and every unrelated rule, including other countries.
    index = 0
    while index < len(existing) and existing[index].get("outboundTag") == "api":
        index += 1
    existing[index:index] = rules
    return template


def hub_template(template, inbound_tag, route, link, hub_ipv6, users=None):
    template = copy.deepcopy(template)
    profile = parse_profile(link)
    address = ipaddress.ip_address(profile.host)
    if address.version != 6 or address.ipv4_mapped:
        raise ValueError("The inter-server endpoint must be a literal IPv6 address.")
    tag = "relay-" + route
    if any(o.get("tag") == tag for o in template.get("outbounds", [])):
        raise ValueError("A relay outbound with this route name already exists.")
    outbound = client_config(profile, 10809)["outbounds"][0]
    if profile.transport == "xhttp":
        outbound["streamSettings"]["xhttpSettings"]["mode"] = "stream-one"
    outbound.update(tag=tag, sendThrough=hub_ipv6)
    outbound["streamSettings"]["sockopt"] = {"domainStrategy": "ForceIPv6"}
    template.setdefault("outbounds", []).append(outbound)
    rule = {"type": "field", "inboundTag": [inbound_tag], "outboundTag": tag}
    if users:
        rule["user"] = users
    return insert_rules(template, [rule])


def exit_template(template, inbound_tag, hub_ipv6):
    template = set_ipv4(copy.deepcopy(template))
    return insert_rules(template, [
        {"type": "field", "inboundTag": [inbound_tag], "ip": ["::/0"], "outboundTag": "blocked"},
        {"type": "field", "inboundTag": [inbound_tag], "source": [hub_ipv6 + "/128"],
         "outboundTag": "direct"},
        {"type": "field", "inboundTag": [inbound_tag], "outboundTag": "blocked"}])


def backup(route, panel):
    directory = Path("/root/vpn-relay-backups") / (time.strftime("%Y%m%d-%H%M%S") +
                                                   "-" + route + "-" + secrets.token_hex(3))
    directory.mkdir(mode=0o700, parents=True)
    source = sqlite3.connect("/etc/x-ui/x-ui.db")
    destination = sqlite3.connect(directory / "x-ui.db")
    source.backup(destination)
    destination.close()
    source.close()
    (directory / "x-ui.db").chmod(0o600)
    private_write(directory / "template.json", panel.template())
    if STATE.exists():
        shutil.copy2(STATE, directory / "routes.json")
    return str(directory)


def validate_runtime(options):
    if options["port"] not in (443, 8443):
        raise ValueError("Only 443 or 8443 may be used for public VPN inbounds.")
    if options["hub_ipv6"] not in global_ipv6() and options["role"] == "hub":
        raise ValueError("Requested Moscow IPv6 source is not configured.")
    if options["role"] == "exit" and options["listen"] not in global_ipv6():
        raise ValueError("The foreign IPv6 address must already be configured.")
    if not inspect()["ipv6_default"]:
        raise ValueError("This server has no IPv6 default route.")
    if "key_share" in options:
        version = subprocess.check_output([core_binary(), "version"], text=True).splitlines()[0]
        validate_core_options(version, options["key_share"], options.get("transport", "raw"))
    if "target" in options:
        check_target(options["target"])


def assert_free(listen, port):
    family = socket.AF_INET6 if ":" in listen else socket.AF_INET
    with socket.socket(family, socket.SOCK_STREAM) as s:
        s.bind((listen, port))


def core_binary():
    return next(str(p) for p in Path("/usr/local/x-ui/bin").glob("xray-*")
                if p.is_file() and os.access(p, os.X_OK))


def check_core():
    result = subprocess.run([core_binary(), "run", "-test", "-config",
        "/usr/local/x-ui/bin/config.json"], capture_output=True, text=True, timeout=15)
    if result.returncode:
        raise RuntimeError("Effective Xray configuration failed syntax validation.")


def test_exit(link, expected_ip):
    profile = parse_profile(link)
    if ipaddress.ip_address(profile.host).version != 6:
        raise ValueError("This test requires an IPv6 exit endpoint.")
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    with tempfile.TemporaryDirectory(prefix="vpn-relay-test-") as d:
        config = Path(d) / "client.json"
        write_config(config, client_config(profile, port))
        with (Path(d) / "core.log").open("w") as log:
            child = subprocess.Popen([core_binary(), "run", "-config", str(config)],
                                     stdout=log, stderr=log)
            try:
                time.sleep(.4)
                attempts = []
                consecutive = 0
                for attempt in range(1, 4):
                    result = subprocess.run(curl_command("curl", port,
                        "https://www.cloudflare.com/cdn-cgi/trace", 8),
                        capture_output=True, text=True, timeout=11)
                    actual = dict(l.split("=", 1) for l in result.stdout.splitlines() if "=" in l).get("ip")
                    attempts.append({"attempt": attempt, "curl": result.returncode, "exit": actual})
                    if not result.returncode and actual and actual != expected_ip:
                        raise RuntimeError("IPv6 relay returned an unexpected exit IP: " + actual)
                    consecutive = consecutive + 1 if not result.returncode and actual == expected_ip else 0
                    if consecutive == 2:
                        return {"authenticated": True, "transport": "IPv6", "exit_ipv4": actual,
                                "attempts": attempts}
                    if attempt < 3:
                        time.sleep(1)
                raise RuntimeError("IPv6 relay did not pass two consecutive authenticated HTTPS tests: " +
                                   redact(result.stderr.strip()[:200], profile))
            finally:
                if child.poll() is None:
                    child.terminate()
                try:
                    child.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()


def route_identity(options):
    result = {k: options[k] for k in ("role", "port", "listen", "target",
                                      "fingerprint", "hub_ipv6", "remark", "clients")}
    if options["role"] == "hub":
        result["exit_link_digest"] = hashlib.sha256(options["exit_link"].encode()).hexdigest()
    return result


def route_exports(panel, inbound_id, options):
    canonical = {label: panel.export(inbound_id, label, options["export_host"], options["fingerprint"])
                 for label in options["clients"]}
    return {"canonical_links": canonical,
            "links": {label: hiddify_link(link, options.get("key_share", "hybrid"))
                      for label, link in canonical.items()}}


def apply_route(options):
    validate_runtime(options)
    panel = Panel(options)
    registry = json.loads(STATE.read_text()) if STATE.exists() else {}
    key = options["route"]
    identity = route_identity(options)
    identity.update(transport=options.get("transport", "raw"), key_share=options.get("key_share", "hybrid"),
                    xhttp_path=options.get("xhttp_path", "/vpn"), shared_entry=options.get("shared_entry", False))
    if key in registry:
        old = registry[key]
        old_identity = dict(old.get("identity", {}))
        for field, default in (("transport", "raw"), ("key_share", "hybrid"),
                               ("xhttp_path", "/vpn"), ("shared_entry", False)):
            old_identity.setdefault(field, default)
        if old_identity != identity or old.get("status") != "ready":
            raise RuntimeError("This route already exists with different or incomplete settings; inspect its backup.")
        inbound = panel.inbound(old["inbound_id"])
        if not inbound["enable"]:
            raise RuntimeError("The existing route is disabled; refusing to claim readiness.")
        return {"inbound_id": inbound["id"], "tag": inbound["tag"], "reused": True,
                **route_exports(panel, inbound["id"], options),
                "backup": old["backup"]}
    shared = options.get("shared_entry", False)
    original_inbound = None
    if shared:
        if options["role"] != "hub":
            raise ValueError("Only a hub entry can be shared")
        matches = [i for i in panel.api("inbounds/list") if i["enable"] and
                   i["port"] == options["port"] and i["listen"] == options["listen"] and i["protocol"] == "vless"]
        if len(matches) != 1:
            raise ValueError("Expected one enabled VLESS inbound on the shared entry address and port")
        original_inbound = matches[0]
        stream = obj(original_inbound["streamSettings"])
        network = "raw" if stream.get("network") == "tcp" else stream.get("network")
        if network != options.get("transport", "raw") or options["target"] not in stream.get("realitySettings", {}).get("serverNames", []):
            raise ValueError("Shared entry transport and SNI must match the existing inbound")
        existing_labels = {c["email"] for c in obj(original_inbound["settings"])["clients"]}
        if existing_labels.intersection(options["clients"]):
            raise ValueError("Use distinct country-specific account labels for a shared entry")
    else:
        assert_free(options["listen"], options["port"])
    previous = panel.template()
    saved = backup(key, panel)
    created_id = None
    try:
        if shared:
            inbound = original_inbound
        else:
            panel.api("inbounds/add", new_inbound(options))
            matches = [i for i in panel.api("inbounds/list") if
                       i["port"] == options["port"] and i["listen"] == options["listen"]
                       and i["remark"] == options["remark"]]
            if len(matches) != 1:
                raise RuntimeError("Cannot identify the newly created inbound.")
            inbound = matches[0]
            created_id = inbound["id"]
        inbound_id = inbound["id"]
        registry[key] = {"identity": identity, "inbound_id": inbound_id,
                         "backup": saved, "status": "staged"}
        private_write(STATE, registry)
        panel.attach(inbound_id, options["clients"])
        if options["role"] == "exit":
            updated = exit_template(previous, inbound["tag"], options["hub_ipv6"])
        else:
            updated = hub_template(previous, inbound["tag"], key, options["exit_link"],
                                   options["hub_ipv6"], options["clients"] if shared else None)
        panel.set_template(updated)
        if shared:
            panel.api("server/restartXrayService", {})
        else:
            panel.activate(inbound_id)
        time.sleep(2)
        check_core()
        if shutil.which("ufw"):
            status = subprocess.check_output(["ufw", "status"], text=True)
            if status.startswith("Status: active"):
                subprocess.run(["ufw", "allow", str(options["port"]) + "/tcp"], check=True,
                               stdout=subprocess.DEVNULL)
        links = route_exports(panel, inbound_id, options)
        registry[key]["status"] = "ready"
        private_write(STATE, registry)
        return {"inbound_id": inbound_id, "tag": inbound["tag"], **links,
                "backup": saved, "reused": False}
    except Exception:
        # Restore the existing listener or disable the newly owned one.
        try:
            if shared:
                panel.api("inbounds/update/" + str(original_inbound["id"]), original_inbound)
                panel.set_template(previous)
                panel.api("server/restartXrayService", {})
                registry[key]["status"] = "failed-restored"
                private_write(STATE, registry)
            elif created_id is not None:
                panel.activate(created_id, False)
                panel.set_template(previous)
                panel.api("server/restartXrayService", {})
                registry[key]["status"] = "failed-disabled"
                private_write(STATE, registry)
        except Exception:
            raise RuntimeError("Relay setup and restoration failed. Inspect private backup " + saved) from None
        result = "Shared inbound was restored. " if shared else "New inbound was left disabled when possible. "
        raise RuntimeError("Relay setup stopped. " + result +
                           "Inspect private backup " + saved + "; do not reset the panel.") from None


def run(options):
    if os.geteuid() != 0:
        raise RuntimeError("Run this payload as root on the intended VPS.")
    if options["action"] == "inspect":
        return inspect()
    if options["action"] == "test":
        return test_exit(options["exit_link"], options["expect_ip"])
    if options["action"] == "apply":
        import fcntl
        with open("/var/lock/vpn-guide-relay.lock", "a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            return apply_route(options)
    raise ValueError("Unknown relay action.")


if __name__ == "__main__":
    if "RELAY_OPTIONS" not in globals():
        raise SystemExit("Use bootstrap_relay.py --plan; do not run this payload locally.")
    try:
        print("VPN_RELAY_RESULT " + json.dumps(run(RELAY_OPTIONS)), flush=True)
    except Exception as error:
        print("Relay stopped: " + str(error), flush=True)
        raise SystemExit(1)
