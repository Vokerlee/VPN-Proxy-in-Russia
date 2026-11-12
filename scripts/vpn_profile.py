#!/usr/bin/env python3
"""Inspect, generate, or test this guide's VLESS + REALITY + Vision profiles.

Guide: docs/automation.md; profile fields: docs/server-inbound.md#5-export-the-connection
No dependency installation, system proxy changes, service changes, or process discovery.
Only the temporary Xray child started by 'test' is terminated by this script.
"""
import argparse
import base64
import binascii
from dataclasses import dataclass
import getpass
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from urllib.parse import parse_qsl, unquote, urlsplit, urlunsplit
import uuid

GUIDE = "https://github.com/Vokerlee/VPN-Proxy-in-Russia/blob/master/docs/automation.md"


@dataclass(frozen=True)
class Profile:
    host: str
    port: int
    account: str
    sni: str
    public_key: str
    short_id: str
    fingerprint: str
    spider_x: str
    transport: str = "raw"
    flow: str = "xtls-rprx-vision"
    key_share: str = "hybrid"
    path: str = "/"
    mode: str = "stream-one"
    http_host: str = ""

    def summary(self):
        return {"server": self.host, "vpn_port": self.port,
                "protocol": "VLESS", "transport": self.transport, "security": "REALITY",
                "flow": self.flow, "sni": self.sni, "key_share": self.key_share,
                "fingerprint": self.fingerprint,
                "credentials": "UUID, public key and short ID validated; values hidden"}


def clean_text(value, label):
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError(f"{label} contains control characters")
    return value


def parse_profile(link):
    link = link.strip()
    if len(link) > 65536:
        raise ValueError("profile is too long")
    clean_text(link, "profile")
    try:
        u = urlsplit(link)
        host, port = u.hostname, u.port or 443
    except ValueError:
        raise ValueError("invalid server address or port") from None
    if u.scheme.lower() != "vless" or not host or not u.username or u.password is not None:
        raise ValueError("expected a VLESS share link with one client UUID and server address")
    if not 1 <= port <= 65535:
        raise ValueError("VPN port must be between 1 and 65535")
    if u.path not in ("", "/"):
        raise ValueError("unexpected URL path; export the VLESS link from the panel again")
    try:
        account = str(uuid.UUID(unquote(u.username)))
    except ValueError:
        raise ValueError("client ID is not a UUID supported by this guide") from None
    pairs = parse_qsl(u.query, keep_blank_values=True)
    params = {}
    for k, v in pairs:
        if k in params:
            raise ValueError(f"duplicate query parameter: {k}")
        params[k] = clean_text(v, "query value")
    if params.get("security") != "reality":
        raise ValueError("this helper supports security=reality only")
    transport = params.get("type", "tcp")
    if transport not in ("tcp", "raw", "xhttp"):
        raise ValueError("this helper supports RAW/TCP and XHTTP")
    if params.get("encryption", "none") != "none":
        raise ValueError("this helper supports VLESS encryption=none only")
    flow = params.get("flow", "")
    if flow not in ("", "xtls-rprx-vision") or (transport == "xhttp" and flow):
        raise ValueError("use Vision or an empty flow for RAW; XHTTP requires an empty flow")
    key_share = params.get("keyshare", "hybrid")
    if "key_share" in params or "keyShare" in params:
        raise ValueError("VLESS links use keyshare=classical; key_share is the JSON field")
    if key_share not in ("hybrid", "classical"):
        raise ValueError("keyshare must be hybrid or classical")
    mode = params.get("mode", "stream-one") or "stream-one"
    if mode not in ("auto", "stream-one", "stream-up", "packet-up"):
        raise ValueError("unsupported XHTTP mode")
    path = params.get("path", "/")
    if not path.startswith("/"):
        raise ValueError("XHTTP path must start with /")
    if params.get("extra", "") not in ("", "{}"):
        raise ValueError("Advanced XHTTP extra settings require the client UI; this helper handles basic XHTTP")
    sni = params.get("sni", "")
    if not sni or len(sni) > 253 or not re.fullmatch(r"[A-Za-z0-9._-]+", sni):
        raise ValueError("missing or invalid SNI/server name")
    key = params.get("pbk", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", key):
        raise ValueError("REALITY public key must be a 43-character base64url X25519 key")
    try:
        if len(base64.b64decode(key + "=", altchars=b"-_", validate=True)) != 32:
            raise ValueError("invalid public key length")
    except (ValueError, binascii.Error):
        raise ValueError("invalid REALITY public key encoding") from None
    if "sid" not in params:
        raise ValueError("missing sid; export the server's intended short ID")
    sid = params["sid"]
    if len(sid) > 16 or len(sid) % 2 or not re.fullmatch(r"[0-9a-fA-F]*", sid):
        raise ValueError("short ID must have an even number of hex digits, at most 16")
    fp = params.get("fp", "chrome")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", fp):
        raise ValueError("invalid fingerprint name")
    return Profile(clean_text(host, "host"), port, account, sni, key, sid.lower(), fp,
                   params.get("spx", "/"), "raw" if transport == "tcp" else transport,
                   flow, key_share, path, mode, params.get("host", ""))


def hiddify_link(link, key_share):
    """Add Hiddify's client option while preserving the panel's query and fragment."""
    if key_share not in ("hybrid", "classical"):
        raise ValueError("key share must be hybrid or classical")
    value = urlsplit(link)
    existing = [v for k, v in parse_qsl(value.query, keep_blank_values=True) if k == "keyshare"]
    if existing:
        if existing != [key_share]:
            raise ValueError("the exported profile already requests a different key share")
        return link
    if key_share == "hybrid":
        return link
    query = value.query + ("&" if value.query else "") + "keyshare=classical"
    return urlunsplit(value._replace(query=query))


def read_profile(args):
    if args.link_file:
        link = sys.stdin.read(65537) if args.link_file == "-" else Path(args.link_file).read_text(encoding="utf-8-sig")
    elif args.link_env:
        link = os.environ.get(args.link_env, "")
        if not link:
            raise ValueError("the requested profile environment variable is empty")
    elif sys.stdin.isatty():
        link = getpass.getpass("Paste the VLESS link (hidden): ")
    else:
        raise ValueError("use --link-file FILE, --link-file -, or --link-env NAME when not interactive")
    return parse_profile(link)


def client_config(p, port, engine="xray"):
    if not 1 <= port <= 65535:
        raise ValueError("local proxy port must be between 1 and 65535")
    if engine == "hiddify":
        outbound = {"type": "vless", "tag": "vpn", "server": p.host,
                    "server_port": p.port, "uuid": p.account,
                    "tls": {"enabled": True, "server_name": p.sni,
                            "utls": {"enabled": True, "fingerprint": p.fingerprint},
                            "reality": {"enabled": True, "public_key": p.public_key,
                                        "short_id": p.short_id, "key_share": p.key_share}}}
        if p.flow:
            outbound["flow"] = p.flow
        if p.transport == "xhttp":
            outbound["transport"] = {"type": "xhttp", "path": p.path, "mode": p.mode}
            if p.http_host:
                outbound["transport"]["host"] = p.http_host
        return {"inbounds": [{"type": "mixed", "listen": "127.0.0.1", "listen_port": port}],
                "outbounds": [outbound], "route": {"final": "vpn"}}
    if engine != "xray":
        raise ValueError("engine must be xray or hiddify")
    if p.key_share == "classical":
        raise ValueError("Xray config generation cannot request Hiddify's classical mode; use --engine hiddify")
    config = {"log": {"loglevel": "warning"},
            "inbounds": [{"listen": "127.0.0.1", "port": port, "protocol": "http", "settings": {}}],
            "outbounds": [{"protocol": "vless", "settings": {"vnext": [{"address": p.host, "port": p.port,
                "users": [{"id": p.account, "encryption": "none", "flow": p.flow}]}]},
                "streamSettings": {"network": "tcp", "security": "reality", "realitySettings": {
                    "serverName": p.sni, "fingerprint": p.fingerprint, "publicKey": p.public_key,
                    "shortId": p.short_id, "spiderX": p.spider_x}}}]}
    if p.transport == "xhttp":
        stream = config["outbounds"][0]["streamSettings"]
        stream["network"] = "xhttp"
        stream["xhttpSettings"] = {"path": p.path, "mode": p.mode}
        if p.http_host:
            stream["xhttpSettings"]["host"] = p.http_host
    return config


def write_config(path, config, overwrite=False):
    path = Path(path).expanduser()
    if path.is_symlink():
        raise ValueError("refusing to replace a symlink")
    if path.exists():
        if not overwrite:
            raise ValueError("output exists; use another path or --overwrite to back it up first")
        backup = path.with_name(path.name + ".backup-" + uuid.uuid4().hex[:12])
        shutil.copy2(path, backup)
        if os.name != "nt":
            backup.chmod(0o600)
        print(f"Backup: {backup}")
    flags = os.O_WRONLY | os.O_CREAT | (os.O_TRUNC if overwrite else os.O_EXCL)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    if os.name != "nt":
        path.chmod(0o600)


def redact(text, profile):
    for secret in (profile.account, profile.public_key, profile.short_id):
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return text


def curl_command(curl, port, url, timeout):
    # NO_PROXY=* would silently bypass the very proxy being tested. Override it.
    return [curl, "--noproxy", "", "--proxy", f"http://127.0.0.1:{port}",
            "--silent", "--show-error", "--fail", "--connect-timeout", "5",
            "--max-time", str(timeout), url]


def test_tunnel(profile, args):
    u = urlsplit(args.url)
    if u.scheme != "https" or not u.hostname or u.username or u.password or u.fragment:
        raise ValueError("test URL must be HTTPS without embedded credentials or a fragment")
    clean_text(args.url, "test URL")
    engine = getattr(args, "engine", "xray")
    executable = args.hiddify if engine == "hiddify" else args.xray
    binary = shutil.which(executable)
    if not binary:
        raise ValueError("Requested engine executable not found; install its official binary first")
    curl = shutil.which("curl.exe" if os.name == "nt" else "curl")
    if not curl:
        raise ValueError("curl is required for the authenticated HTTPS test")
    v = subprocess.run([binary, "version"], capture_output=True, text=True, timeout=5)
    print((v.stdout or v.stderr).splitlines()[0] if (v.stdout or v.stderr).strip() else "Xray version unavailable")
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    with tempfile.TemporaryDirectory(prefix="vpn-guide-test-") as folder:
        folder = Path(folder)
        config_path = folder / "client.json"
        write_config(config_path, client_config(profile, port, engine))
        with (folder / "core.log").open("w+", encoding="utf-8") as log:
            command = ([binary, "srun", "-c", str(config_path)] if engine == "hiddify"
                       else [binary, "run", "-config", str(config_path)])
            p = subprocess.Popen(command, stdout=log, stderr=log)
            try:
                deadline = time.monotonic() + 5
                ready = False
                while time.monotonic() < deadline and p.poll() is None:
                    try:
                        with socket.create_connection(("127.0.0.1", port), timeout=0.15):
                            ready = True
                        break
                    except OSError:
                        time.sleep(0.1)
                if not ready or p.poll() is not None:
                    raise RuntimeError("temporary Xray client did not start")
                result = subprocess.run(curl_command(curl, port, args.url, args.timeout),
                                        capture_output=True, text=True, timeout=args.timeout + 3)
                if result.returncode:
                    print("Authenticated HTTPS test failed:", redact(result.stderr.strip(), profile), file=sys.stderr)
                    return 1
                body = redact(result.stdout[:8192], profile)
                print("Authenticated HTTPS request succeeded through the temporary local proxy.")
                print(body.strip())
                if args.expect_ip:
                    actual = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line).get("ip")
                    if actual is None or ipaddress.ip_address(actual) != ipaddress.ip_address(args.expect_ip):
                        print("Exit IP did not match --expect-ip", file=sys.stderr)
                        return 1
                return 0
            finally:
                if p.poll() is None:
                    p.terminate()
                    try:
                        p.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        p.kill()
                        p.wait(timeout=3)
                log.seek(0)
                if p.returncode not in (0, None) and args.show_core_log:
                    print(redact(log.read(4096), profile), file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, epilog="Walkthrough and examples: " + GUIDE)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, helptext in [("inspect", "Validate a link; hide account/key values"),
                           ("config", "Write a standalone localhost Xray configuration"),
                           ("test", "Run an isolated Xray child and authenticate an HTTPS request")]:
        p = sub.add_parser(name, help=helptext, epilog="See docs/automation.md and docs/troubleshooting.md")
        source = p.add_mutually_exclusive_group()
        source.add_argument("--link-file", help="private text file containing a VLESS link; '-' reads stdin")
        source.add_argument("--link-env", help="name of an environment variable containing the VLESS link")
        if name == "inspect":
            p.add_argument("--connect", action="store_true", help="also test TCP reachability; not authentication")
        elif name == "config":
            p.add_argument("--engine", choices=("xray", "hiddify"), default="xray")
            p.add_argument("--output", required=True)
            p.add_argument("--port", type=int, default=10809, help="local HTTP proxy port (default: 10809)")
            p.add_argument("--overwrite", action="store_true", help="back up an existing file before replacing it")
        else:
            p.add_argument("--engine", choices=("xray", "hiddify"), default="xray")
            p.add_argument("--hiddify", default="HiddifyCli", help="installed Hiddify CLI path")
            p.add_argument("--xray", default="xray", help="installed official Xray executable (path or command)")
            p.add_argument("--url", default="https://www.cloudflare.com/cdn-cgi/trace")
            p.add_argument("--timeout", type=int, default=15)
            p.add_argument("--expect-ip", help="optional expected exit IP, for the default trace endpoint")
            p.add_argument("--show-core-log", action="store_true", help="print a redacted excerpt from the temporary core")
    args = parser.parse_args(argv)
    try:
        profile = read_profile(args)
        if args.command == "inspect":
            print(json.dumps(profile.summary(), indent=2))
            if args.connect:
                with socket.create_connection((profile.host, profile.port), timeout=5):
                    print("TCP is reachable. This does not verify REALITY or VLESS authentication.")
            return 0
        if args.command == "config":
            write_config(args.output, client_config(profile, args.port, args.engine), args.overwrite)
            print("Wrote private client config. No process, route or system proxy was changed.")
            return 0
        if not 1 <= args.timeout <= 120:
            raise ValueError("timeout must be between 1 and 120 seconds")
        if args.expect_ip:
            ipaddress.ip_address(args.expect_ip)
        return test_tunnel(profile, args)
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print("Error: " + str(error), file=sys.stderr)
        print("Read docs/troubleshooting.md; no system settings were changed.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
