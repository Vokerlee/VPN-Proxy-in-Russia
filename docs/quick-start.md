[← One-server walkthrough](single-server.md) · [Two-server scripts](two-hop-vpn.md#3-preview-and-apply-the-relay-helper)

# Let a script set up a fresh server

If you’d rather paste a few commands than fill in the server dashboard yourself, use this page. The script installs the VPN software and makes separate connection links for your phone and computer. You’ll still rent the server yourself and add the links to Hiddify afterward.

This is for **one fresh server**. Already have a working 3x-ui dashboard? [Create accounts there](server-inbound.md) instead; this installer stops when it finds an existing installation. For two servers, use [the two-server script instructions](two-hop-vpn.md#3-preview-and-apply-the-relay-helper).

**What you need:** a fresh Ubuntu or Debian server, its public IPv4 address, and working SSH access as **root**, its administrator. SSH is the terminal connection the script uses. The server needs systemd, the service manager normally supplied with those systems. [No server yet? Rent one first](choose-server.md).

**What you’ll get:** 3x-ui, the server’s browser dashboard; Xray, the program carrying the VPN traffic; and private links for Hiddify, the app on your devices. This guide’s preset uses Xray **26.7.28** with **classical** device links. [Version notes](handshakes-and-versions.md)

## Before the first command

1. On this repository’s GitHub page, choose **Code → Download ZIP** and extract it, or use your existing Git checkout.
2. Open the extracted folder containing **README.md** and **scripts**. On Windows, right-click inside it and open a terminal with PowerShell. On Linux or Mac, open a terminal there. All commands on this page start on **your computer**, not in the server’s SSH terminal.
3. Run `ssh -V`. If it’s missing, install the OpenSSH client for your operating system. On Windows it’s an Optional Feature called **OpenSSH Client**.
4. Linux/Mac users also need **Python 3.8+**. Check with `python3 --version`. The Windows launcher doesn’t need Python.

## See the plan, then let SSH ask for the password

Choose the commands for your computer. Replace **203.0.113.10** with your server’s real IPv4 address. It’s an example address, so copying it unchanged won’t connect to your server.

### Windows PowerShell

Preview first:

```powershell
.\scripts\Setup-Vpn.ps1 -ServerIp 203.0.113.10 -VpnPort 8443 -Target www.apple.com -Fingerprint safari
```

This only shows a plan. Check the address. To run the setup, repeat it with **-Apply**:

```powershell
.\scripts\Setup-Vpn.ps1 -ServerIp 203.0.113.10 -VpnPort 8443 -Target www.apple.com -Fingerprint safari -Apply
```

<details>
<summary>PowerShell won’t let the script run?</summary>

Read the script before allowing it. On a computer you manage, this runs it with a policy change limited to that new PowerShell process:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Setup-Vpn.ps1 -ServerIp 203.0.113.10 -VpnPort 8443 -Target www.apple.com -Fingerprint safari -Apply
```

Use your actual address here too. For a work or school computer, follow its administrator’s policy. The [manual setup](server-setup.md) is another route.

</details>

### Linux or Mac terminal

Preview:

```bash
python3 scripts/bootstrap_server.py --host 203.0.113.10 --vpn-port 8443 --target www.apple.com --fingerprint safari --plan
```

Check the address, then apply:

```bash
python3 scripts/bootstrap_server.py --host 203.0.113.10 --vpn-port 8443 --target www.apple.com --fingerprint safari --apply
```

### While it runs

SSH may ask you to confirm the server’s identity on the first connection. Compare the host fingerprint with the provider’s console when available. It then asks for the root password. Nothing appears while you type; that’s normal. Keep passwords out of commands. An already configured SSH key also works.

Leave the terminal open until setup finishes. The script checks for a fresh installation, installs the software, creates **desktop** and **phone** accounts, and saves the results. It doesn’t stop your existing VPN apps or change your computer’s network settings. If it stops with an error, use the table below rather than reinstalling the server.

These commands use **8443** for the VPN and **27297** for the dashboard. A port is a numbered connection entry point; those two numbers do different jobs. If the chosen VPN port is occupied, use 443 only if free. Don’t overwrite another service.

For a custom SSH port, add `-SshPort YOUR_PORT` on Windows or `--ssh-port YOUR_PORT` with Python. [Other options](automation.md#start-with-only-a-vps-ip-and-root-password)

## Open 3x-ui directly in your browser

When setup finishes, it prints the panel URL and the private output folder. Open that folder in your file manager; it sits under **.secrets** in this repository. On Linux, use **Ctrl+H** to show hidden folders if needed.

1. Open **server.json** locally in a text editor and find **panel_username** and **panel_password**.
2. Open the printed panel URL in your browser. With the default port, it looks like `http://YOUR_SERVER_IP:27297/`.
3. Sign in using those panel credentials. The SSH root password is a separate login.
4. Open **Inbounds**. You should see **Personal VPN**, enabled, with **desktop** and **phone** accounts. The script already created them; don’t add them again.

If the page doesn’t open, allow the actual panel TCP port in the hosting company’s firewall dashboard. The script can update an already active UFW firewall on the server, but it can’t change your provider account’s firewall. Keep SSH allowed too. [Manual panel access and HTTPS options](server-setup.md#required-open-the-dashboard-safely-in-your-browser)

## Bring the profile into Hiddify

Open **client-phone.txt** for your phone or **client-desktop.txt** for your computer. Copy the whole `vless://…` line. That’s the private connection link for that device.

**[Install Hiddify, add the link and test a website →](clients.md)**

The script also saves the original panel export in **panel-profile.txt** and a first-device Hiddify link in **hiddify-profile.txt**. Use the clearly named per-device files above for your two devices.

Save the output files privately before deleting the repository folder. Anyone with a connection link can use that account. The files are excluded from Git; don’t post them in an issue or screenshot.

## When the helper stops

A stopped helper tells you which stage needs attention. It does not roll back package installation, reset a database, or automatically wipe a partially installed server to try again.

| Message or symptom | What to do next |
|---|---|
| Existing 3x-ui detected | Open the existing panel or run `x-ui` over SSH to retrieve its settings; use the manual guide |
| Cannot authenticate over SSH | Recheck IP, root login permission, actual SSH port, and provider credentials; use a real interactive terminal |
| Selected VPN port is occupied | Use the other allowed port (443 or 8443) only if free; if both are occupied, stop and preserve both listeners |
| Public VPN TCP port is not reachable | In the provider website, find Firewall / Security group / Network rules and allow inbound **TCP** on the recorded VPN port; inspect custom host rules too |
| Installer or API stage failed | Read the private `/root/vpn-guide-bootstrap-*.log` over SSH; do not share it unredacted |
| Setup completed but local result files were not saved | Recover `/root/vpn-guide-bootstrap-result.json` privately over SSH |
| Browser cannot open the panel | Use the printed public IP, actual panel port and saved path; check the public listener and provider/custom firewall |
| Hiddify errors after import | Follow the [handshake and generated-config checks](troubleshooting.md), including the documented recovery helper |

**Optional, after the connection works:** read [server administration improvements](server-setup.md#5-optional-improve-server-administration-later) if you want a separate administrator account and tighter SSH access. The helper leaves these choices to you.

<details>
<summary>For reviewers: what has and has not been tested</summary>

The bootstrap's input handling, existing-install guard, API payload construction, preservation of unrelated template rules, private export behavior, and default dry-run behavior have offline regression tests. Its routes and installer flags were checked against the pinned official 3x-ui source.

On 2026-11-09, the Python launcher and shared payload completed a fresh Ubuntu 24.04 VPS integration over an existing alternate SSH path, with private display/account labels substituted. Installation, the root panel path, ForceIPv4, one account and the canonical public-endpoint export were checked live. A loopback API request must carry the public Host header so its exported profile does not point to localhost. Subsequent authenticated requests succeeded through an alternate path while direct TCP access failed; see [investigation C](network-path-debugging.md#recorded-investigation-c-2026-11-09). The Windows launcher remains covered by offline checks rather than a separate live provisioning run. These results do not establish that every provider, package mirror, firewall policy or future release behaves identically.

</details>
