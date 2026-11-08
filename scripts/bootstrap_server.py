#!/usr/bin/env python3
"""Prepare a fresh VPS from its IPv4 address using the native SSH password prompt.

Default is --plan (no connection). --apply installs/configures a fresh VPS only.
Guide: docs/quick-start.md; details: docs/automation.md#start-with-only-a-vps-ip-and-root-password
The root password is handled by OpenSSH, never stored or accepted as a CLI flag.
"""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
# The shell guard runs before package installation, even when python3 is missing.
REMOTE_COMMAND = "bash -c " + shlex.quote(
    "if [ -e /usr/local/x-ui/x-ui ] || [ -e /etc/x-ui/x-ui.db ]; then "
    "echo 'Existing 3x-ui found; refusing to overwrite it.'; exit 3; fi; "
    "command -v python3 >/dev/null || { apt-get update >&2 && DEBIAN_FRONTEND=noninteractive apt-get install -y python3 >&2; }; "
    "exec python3 -")


FINGERPRINTS = ("auto", "chrome", "safari", "firefox", "edge", "ios", "android", "random", "randomized", "360", "qq")


def validate_options(host, ssh_port=22, vpn_port=443, panel_port=27297, target="www.google.com",
                     server_country="auto", fingerprint="auto"):
    address = ipaddress.ip_address(host)
    if address.version != 4:
        raise ValueError("use the VPS IPv4 address for this walkthrough")
    if any(not 1 <= p <= 65535 for p in (ssh_port, vpn_port, panel_port)):
        raise ValueError("ports must be between 1 and 65535")
    if len({ssh_port, vpn_port, panel_port}) != 3:
        raise ValueError("SSH, public VPN and administration panel ports must be different")
    if not re.fullmatch(r"[A-Za-z0-9.-]+", target) or target.startswith("-"):
        raise ValueError("target must be a hostname without a URL scheme, port or credentials")
    country = "auto" if server_country.lower() == "auto" else server_country.upper()
    if country != "auto" and not re.fullmatch(r"[A-Z]{2}", country):
        raise ValueError("server country must be auto or a two-letter code such as US or DE")
    if fingerprint not in FINGERPRINTS:
        raise ValueError("unsupported fingerprint; see --help")
    return {"host": str(address), "ssh_port": ssh_port, "vpn_port": vpn_port,
            "panel_port": panel_port, "target": target,
            "server_country": country, "fingerprint": fingerprint}


def ssh_command(ssh, options):
    return [ssh, "-T", "-o", "StrictHostKeyChecking=ask", "-o", "ConnectTimeout=15",
            "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=3",
            "-p", str(options["ssh_port"]), "root@" + options["host"], REMOTE_COMMAND]


def panel_command(result, local_port=18080):
    return ["ssh", "-N", "-o", "ExitOnForwardFailure=yes", "-p", str(result["ssh_port"]),
            "-L", f"127.0.0.1:{local_port}:127.0.0.1:{result['panel_port']}", "root@" + result["host"]]


def panel_url(result, local_port=18080):
    path = result["web_path"].strip("/")
    return f"http://127.0.0.1:{local_port}/" + (path + "/" if path else "")


def save_result(result, output):
    output = Path(output)
    output.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name != "nt":
        output.chmod(0o700)
    for name, text in [("server.json", json.dumps(result, indent=2) + "\n"),
                       ("hiddify-profile.txt", result["client_link"] + "\n")]:
        fd = os.open(output / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", help="VPS IPv4 address; prompted when omitted")
    modes = p.add_mutually_exclusive_group()
    modes.add_argument("--plan", action="store_true", help="show the plan without connecting (default)")
    modes.add_argument("--apply", action="store_true", help="provision a fresh Ubuntu/Debian systemd VPS over SSH")
    p.add_argument("--ssh-port", type=int, default=22)
    p.add_argument("--vpn-port", type=int, default=443)
    p.add_argument("--panel-port", type=int, default=27297)
    p.add_argument("--target", default="www.google.com")
    p.add_argument("--server-country", default="auto", help="VPS country code, e.g. US/DE; auto looks up its public IP during apply")
    p.add_argument("--fingerprint", choices=FINGERPRINTS, default="auto", help="auto selects Safari for US, Chrome elsewhere; an explicit preset overrides that policy")
    p.add_argument("--output-dir", type=Path)
    args = p.parse_args()
    try:
        options = validate_options(args.host or input("VPS IPv4 address: ").strip(), args.ssh_port,
                                   args.vpn_port, args.panel_port, args.target,
                                   args.server_country, args.fingerprint)
        print("Fresh-server plan: official 3x-ui v3.8.5, one REALITY/Vision account, ForceIPv4,")
        print("a loopback-only administration panel, and private local profile/credential files.")
        print("Fingerprint policy: US → Safari; other countries → Chrome; explicit --fingerprint overrides.")
        print("Country lookup runs only during apply; --server-country skips it.")
        print("Existing installs/listeners are preserved. No SSH hardening, OS upgrade, client stop,")
        print("provider-firewall change, or workstation system-proxy change will be attempted.")
        if not args.apply:
            print("Plan only: no connection or change made. Use --apply when this is a fresh VPS.")
            return 0
        ssh = shutil.which("ssh")
        if not ssh:
            raise ValueError("OpenSSH client is required; see docs/quick-start.md")
        payload = "import json\nBOOTSTRAP_OPTIONS = json.loads(" + repr(json.dumps(options)) + ")\n"
        payload += (ROOT / "scripts/provision_remote.py").read_text(encoding="utf-8")
        print("SSH will ask you to verify a new host key, then enter root's password securely.")
        print("The setup can take several minutes; keep this terminal open.", flush=True)
        # OpenSSH reads its password/host-key response from the controlling terminal.
        # The Python process never reads the root password. No shell interpolation.
        proc = subprocess.Popen(ssh_command(ssh, options), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                text=True, encoding="utf-8", errors="replace")
        result = None
        try:
            proc.stdin.write(payload)
            proc.stdin.close()
            for line in proc.stdout:
                if line.startswith("VPN_BOOTSTRAP_RESULT "):
                    result = json.loads(line.split(" ", 1)[1])
                else:
                    print(line.rstrip(), flush=True)
            code = proc.wait()
        except BaseException:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)
            raise
        if code or result is None:
            print("Setup did not report completion. Read docs/quick-start.md#when-the-helper-stops.", file=sys.stderr)
            return 1
        folder = args.output_dir or ROOT / ".secrets" / ("server-" + options["host"] + "-" + time.strftime("%Y%m%d-%H%M%S"))
        save_result(result, folder)
        print("Private panel credentials:", folder / "server.json")
        print("Private Hiddify import link:", folder / "hiddify-profile.txt")
        print("VPS country:", result["server_country"], "| exported client fingerprint:", result["fingerprint"])
        print(result["firewall"])
        try:
            with socket.create_connection((result["host"], result["vpn_port"]), timeout=5):
                print("The public VPN TCP port is reachable from this computer; authentication still needs a client test.")
        except OSError:
            print(f"ACTION: allow inbound TCP {result['vpn_port']} in the provider's firewall/security group and inspect any custom host firewall.")
        print("Open the panel: leave this command running in a second terminal:")
        print(subprocess.list2cmdline(panel_command(result)) if os.name == "nt" else shlex.join(panel_command(result)))
        print("Then open: " + panel_url(result))
        print("Log in with the generated panel credentials in server.json, not the root password.")
        print("Next: docs/quick-start.md#bring-the-profile-into-hiddify")
        return 0
    except (ValueError, OSError, EOFError, subprocess.SubprocessError) as error:
        print("Error:", error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
