#!/usr/bin/env python3
"""Add an IPv4-entry -> IPv6-relay -> IPv4-exit route without replacing other routes.

Defaults to a local plan. Root passwords are entered only at native OpenSSH prompts.
The original bootstrap_server.py single-server mode remains independent.
"""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

from provision_remote import core_number, validate_core_options

ROOT = Path(__file__).resolve().parents[1]


def ipv6_host(value):
    address = ipaddress.ip_address(value)
    if (address.version != 6 or address.is_link_local or address.is_unspecified
            or address.is_multicast or address.ipv4_mapped):
        raise ValueError("Use an assigned global IPv6 host address, not a subnet or link-local address.")
    return str(address)


def hostname(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", value):
        raise ValueError("Targets must be hostnames without ports or URL schemes.")
    return value


def validate(args):
    for name in ("hub_host", "exit_host"):
        if ipaddress.ip_address(getattr(args, name)).version != 4:
            raise ValueError(name + " must be the server's public IPv4 address.")
    if args.hub_host == args.exit_host:
        raise ValueError("Hub and exit must be different servers.")
    for name in ("entry_port", "exit_port"):
        if getattr(args, name) not in (443, 8443):
            raise ValueError("Public VPN inbound ports must be 443 or 8443.")
    for port in (args.hub_ssh_port, args.exit_ssh_port, args.hub_panel_port, args.exit_panel_port):
        if not 1 <= port <= 65535:
            raise ValueError("Invalid SSH or panel port.")
    if len({args.hub_ssh_port, args.hub_panel_port, args.entry_port}) != 3:
        raise ValueError("Hub SSH, panel and inbound ports must differ.")
    if len({args.exit_ssh_port, args.exit_panel_port, args.exit_port}) != 3:
        raise ValueError("Exit SSH, panel and inbound ports must differ.")
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,23}", args.route):
        raise ValueError("Route name must use lowercase letters, digits and hyphens.")
    args.exit_ipv6 = ipv6_host(args.exit_ipv6)
    if args.hub_ipv6:
        args.hub_ipv6 = ipv6_host(args.hub_ipv6)
    for name in ("entry_target", "exit_target"):
        hostname(getattr(args, name))
    args.hub_core_version = validate_core_options(args.hub_core_version, args.entry_key_share, args.entry_transport)
    args.exit_core_version = validate_core_options(args.exit_core_version, "hybrid", args.relay_transport)
    if args.shared_entry and args.entry_transport != "raw":
        raise ValueError("Shared entries currently require RAW and distinct country account labels")
    args.clients = args.clients.split(",")
    if (not args.clients or len(set(args.clients)) != len(args.clients)
            or any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", c) for c in args.clients)):
        raise ValueError("Provide unique comma-separated account labels without spaces.")
    from ssh_http_connect import proxy_address
    for value in (args.hub_ssh_proxy, args.exit_ssh_proxy):
        if value:
            proxy_address(value)
    return args


def remote_payload(options):
    lines = ["import json,sys,types"]
    for name in ("vpn_profile", "provision_remote"):
        source = (ROOT / "scripts" / (name + ".py")).read_text()
        lines += ["m=types.ModuleType(" + repr(name) + ")",
                  "sys.modules[m.__name__]=m",
                  "exec(" + repr(source) + ",m.__dict__)"]
    lines += ["RELAY_OPTIONS=json.loads(" + repr(json.dumps(options)) + ")",
              (ROOT / "scripts/relay_remote.py").read_text()]
    return "\n".join(lines)


class SSH:
    def __init__(self, host, port, proxy, directory, label):
        self.host = host
        self.control = str(Path(directory) / (label + ".sock"))
        self.base = [shutil.which("ssh") or "ssh", "-F", "NUL" if os.name == "nt" else "/dev/null",
            "-T", "-o", "StrictHostKeyChecking=ask", "-o", "ConnectTimeout=15",
            "-o", "ConnectionAttempts=1", "-o", "ServerAliveInterval=15",
            "-o", "ServerAliveCountMax=3", "-o", "ProxyJump=none"]
        if proxy:
            command = [sys.executable, str(ROOT / "scripts/ssh_http_connect.py"),
                       "--proxy", proxy, "%h", "%p"]
            proxy_command = subprocess.list2cmdline(command) if os.name == "nt" else shlex.join(command)
            self.base += ["-o", "ProxyCommand=" + proxy_command]
        else:
            self.base += ["-o", "ProxyCommand=none"]
        if os.name != "nt":
            self.base += ["-o", "ControlMaster=auto", "-o", "ControlPersist=120",
                          "-o", "ControlPath=" + self.control]
        else:
            self.base += ["-o", "ControlMaster=no"]
        self.base += ["-p", str(port), "root@" + host]
        self.description = label + (" via explicitly selected local proxy" if proxy else " directly")

    def gate(self):
        print("Authenticate " + self.description + "; verify any new host key.", flush=True)
        subprocess.run(self.base + ["true"], check=True, timeout=150)

    def payload(self, text):
        result = None
        process = subprocess.Popen(self.base + ["python3 -"], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        try:
            process.stdin.write(text)
            process.stdin.close()
            for line in process.stdout:
                if line.startswith(("VPN_RELAY_RESULT ", "VPN_BOOTSTRAP_RESULT ")):
                    result = json.loads(line.split(" ", 1)[1])
                else:
                    print(line.rstrip(), flush=True)
            code = process.wait()
            if code or result is None:
                raise RuntimeError("Remote operation did not complete on " + self.description)
            return result
        except BaseException:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            raise

    def run(self, options):
        return self.payload(remote_payload(options))

    def close(self):
        if os.name != "nt" and Path(self.control).exists():
            subprocess.run(self.base[:-1] + ["-O", "exit", self.base[-1]],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)


def private_json(path, value):
    path = Path(path)
    if path.exists() and path.is_symlink():
        raise ValueError("Refusing to write a symlink.")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(value, f, indent=2)
        f.write("\n")


def ensure_panel(ssh, state, host, ssh_port, panel_port, vpn_port, target, fingerprint,
                 core_version="26.7.28", key_share="classical", transport="raw"):
    if state["panel_present"]:
        actual = state.get("core_version")
        if actual is None or core_number(actual) != core_number(core_version):
            raise ValueError("Existing " + ssh.description + " core differs from requested " + core_version +
                             "; verify its version and select matching options or change the core manually")
        validate_core_options(actual, key_share, transport)
        return None
    # A panel-only install creates no public VPN inbound or temporary device account.
    options = {"host": host, "ssh_port": ssh_port, "panel_port": panel_port,
               "vpn_port": vpn_port, "target": target, "fingerprint": fingerprint,
               "server_country": "auto", "panel_only": True, "core_version": core_version,
               "key_share": key_share, "transport": transport}
    from bootstrap_server import remote_payload as fresh_payload
    return ssh.payload(fresh_payload(options))


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hub-host", required=True)
    p.add_argument("--exit-host", required=True)
    p.add_argument("--exit-ipv6", required=True)
    p.add_argument("--hub-ipv6")
    p.add_argument("--route", required=True, help="stable country/route key, e.g. nl or de")
    p.add_argument("--entry-port", type=int, choices=(443, 8443), default=8443)
    p.add_argument("--exit-port", type=int, choices=(443, 8443), default=443)
    p.add_argument("--entry-target", default="yandex.ru")
    p.add_argument("--entry-fingerprint", choices=("safari", "chrome", "firefox", "ios"), default="safari")
    p.add_argument("--exit-target", default="www.google.com")
    p.add_argument("--exit-fingerprint", choices=("chrome", "safari", "firefox", "ios"), default="chrome")
    p.add_argument("--hub-core-version", default="26.7.28")
    p.add_argument("--exit-core-version", default="26.7.28")
    p.add_argument("--entry-key-share", choices=("classical", "hybrid"), default="classical")
    p.add_argument("--entry-transport", choices=("raw", "xhttp"), default="raw")
    p.add_argument("--relay-transport", choices=("xhttp", "raw"), default="xhttp")
    p.add_argument("--shared-entry", action="store_true", help="attach distinct country accounts to an existing RAW entry port")
    p.add_argument("--clients", default="desktop,phone")
    p.add_argument("--hub-ssh-port", type=int, default=22)
    p.add_argument("--exit-ssh-port", type=int, default=22)
    p.add_argument("--hub-panel-port", type=int, default=27297)
    p.add_argument("--exit-panel-port", type=int, default=27297)
    p.add_argument("--hub-ssh-proxy", help="explicitly authorized loopback HTTP proxy IP:port")
    p.add_argument("--exit-ssh-proxy", help="explicitly authorized loopback HTTP proxy IP:port")
    p.add_argument("--output-dir", type=Path)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--apply", action="store_true")
    return p


def main(argv=None):
    args = validate(parser().parse_args(argv))
    print("Relay route " + args.route + ": IPv4 client -> hub:" + str(args.entry_port) +
          " -> [" + args.exit_ipv6 + "]:" + str(args.exit_port) + " -> IPv4 destinations.")
    print("Entry preset: " + args.entry_target + " / " + args.entry_fingerprint +
          "; inter-server preset: " + args.exit_target + " / " + args.exit_fingerprint)
    print("Entry " + args.entry_transport + ", core " + args.hub_core_version + ", " + args.entry_key_share +
          "; relay " + args.relay_transport + ", exit core " + args.exit_core_version + ".")
    print("Other hub routes and existing single-server inbounds/accounts are preserved.")
    print("SSH proxies, if specified, are management-only; the deployed relay uses native IPv6.")
    if not args.apply:
        print("Plan only. No connections, files or server changes made.")
        return 0
    if not shutil.which("ssh"):
        raise ValueError("Native OpenSSH is required.")
    output = args.output_dir or ROOT / ".secrets" / (
        "relay-" + args.route + "-" + time.strftime("%Y%m%d-%H%M%S"))
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    if os.name != "nt":
        output.chmod(0o700)
    results = {"route": args.route, "entry_host": args.hub_host, "entry_port": args.entry_port,
               "exit_host": args.exit_host, "exit_ipv6": args.exit_ipv6,
               "status": "preflight", "clients": args.clients}
    with tempfile.TemporaryDirectory(prefix="vpn-relay-ssh-") as directory:
        hub = SSH(args.hub_host, args.hub_ssh_port, args.hub_ssh_proxy, directory, "hub")
        exit_server = SSH(args.exit_host, args.exit_ssh_port, args.exit_ssh_proxy, directory, "exit")
        try:
            hub.gate()
            exit_server.gate()
            hub_state = hub.run({"action": "inspect"})
            exit_state = exit_server.run({"action": "inspect"})
            candidates = hub_state["ipv6"]
            if not args.hub_ipv6:
                if len(candidates) != 1:
                    raise ValueError("Specify --hub-ipv6; hub has zero or multiple global IPv6 addresses.")
                args.hub_ipv6 = candidates[0]
            if args.hub_ipv6 not in candidates or not hub_state["ipv6_default"]:
                raise ValueError("Hub IPv6 is not configured with a default route.")
            if args.exit_ipv6 not in exit_state["ipv6"] or not exit_state["ipv6_default"]:
                raise ValueError("Configure the foreign IPv6 address and provider-specific gateway first.")
            results["hub_ipv6"] = args.hub_ipv6
            for ssh, state, host, port, panel_port, vpn_port, target, fingerprint, role in [
                (hub, hub_state, args.hub_host, args.hub_ssh_port, args.hub_panel_port,
                 args.entry_port, args.entry_target, args.entry_fingerprint, "hub"),
                (exit_server, exit_state, args.exit_host, args.exit_ssh_port, args.exit_panel_port,
                 args.exit_port, args.exit_target, args.exit_fingerprint, "exit")]:
                core = args.hub_core_version if role == "hub" else args.exit_core_version
                key_share = args.entry_key_share if role == "hub" else "hybrid"
                transport = args.entry_transport if role == "hub" else args.relay_transport
                installed = ensure_panel(ssh, state, host, port, panel_port, vpn_port, target,
                                         fingerprint, core, key_share, transport)
                if installed:
                    results[role + "_panel"] = installed
                    private_json(output / "relay.json", results)
            common = {"action": "apply", "route": args.route, "hub_ipv6": args.hub_ipv6}
            exit_options = dict(common, role="exit", public_host=args.exit_host,
                panel_port=args.exit_panel_port, listen=args.exit_ipv6,
                export_host=args.exit_ipv6, port=args.exit_port, target=args.exit_target,
                fingerprint=args.exit_fingerprint, remark="Relay " + args.route,
                clients=["relay-" + args.route], transport=args.relay_transport,
                key_share="hybrid", xhttp_path="/relay-" + args.route)
            results["exit"] = exit_server.run(exit_options)
            private_json(output / "relay.json", results)
            link = results["exit"]["links"]["relay-" + args.route]
            results["inter_server_test"] = hub.run({"action": "test",
                "exit_link": link, "expect_ip": args.exit_host})
            results["hub"] = hub.run(dict(common, role="hub", public_host=args.hub_host,
                panel_port=args.hub_panel_port, listen="0.0.0.0", export_host=args.hub_host,
                port=args.entry_port, target=args.entry_target, fingerprint=args.entry_fingerprint,
                remark="VLESS RU", clients=args.clients, exit_link=link,
                transport=args.entry_transport, key_share=args.entry_key_share,
                xhttp_path="/entry-" + args.route, shared_entry=args.shared_entry))
            results["status"] = "configured"
            private_json(output / "relay.json", results)
            private_json(output / "panel-profiles.json", results["hub"]["canonical_links"])
            for label, link in results["hub"]["links"].items():
                path = output / (label + ".txt")
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "w") as f:
                    f.write(link + "\n")
            print("IPv6 inter-server authentication succeeded; foreign IPv4 exit: " + args.exit_host)
            print("Private canonical client profiles and panel recovery details: " + str(output))
            print("Hub panel: http://" + args.hub_host + ":" + str(args.hub_panel_port) + "/")
            print("Still verify the complete client -> hub -> exit path before migrating devices.")
            return 0
        except BaseException:
            results["status"] = "incomplete"
            private_json(output / "relay.json", results)
            print("Setup stopped. Preserve servers and inspect private relay.json and remote backups.",
                  file=sys.stderr)
            raise
        finally:
            hub.close()
            exit_server.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as error:
        print("Error: " + str(error), file=sys.stderr)
        raise SystemExit(1)
