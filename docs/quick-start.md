[← Guide index](../README.md) · [Manual server walkthrough](server-setup.md) · [What the helpers do](automation.md)

# Optional: let a helper prepare a new server

This is an optional alternative to the [manual setup walkthrough](server-setup.md). You can complete the whole main guide without running these helpers.

A **VPS** is a rented remote server; **root** is its administrator account. **SSH** is the secure terminal connection used to log in. The helper uses **OpenSSH**, the program providing that connection on your computer. If you do not have one yet, follow [choosing and creating a server](choose-server.md) first. Once the provider has supplied its IP and root login, a helper can automate the installation and account creation.

The helper prepares a new Ubuntu or Debian server that uses systemd, the normal service manager on those distributions. It does not require Ubuntu 24.04 specifically. You can launch it from Windows, Linux, or macOS.

It installs **3x-ui**, the server's browser dashboard, and generates a connection profile—a private link that tells a client app how to connect. The connection uses the VLESS + REALITY + Vision settings explained in the manual guide, with an IPv4 exit address—the address websites see. The desktop/phone app used below is **Hiddify**. It does not need a domain name or access to your provider account.

An existing 3x-ui installation is a different situation. The helper recognizes it and stops before resetting it. If you already have a panel, use [the existing-server walkthrough](server-inbound.md) and [Hiddify setup](clients.md); do not erase a working VPS to make an installer happy.

The current fresh-server default pins **Xray 26.7.28** independently of **3x-ui 3.8.5** and writes a **classical Hiddify profile**. Keep the panel export in `panel-profile.txt`; import `hiddify-profile.txt`, whose query includes `keyshare=classical`. [Why the versions matter](handshakes-and-versions.md)

## Before the first command

Download this repository using Git or GitHub's **Code → Download ZIP**, extract it, and open a terminal in the folder containing `README.md` and `scripts/`.

On Windows, use **PowerShell** in that folder. Check that the built-in OpenSSH client is available:

```powershell
ssh -V
```

If Windows says the command is missing, install **OpenSSH Client** through Windows' Optional features, then reopen the terminal. The Windows launcher does not require local Python.

On Linux/macOS, have OpenSSH and Python 3.8+ available. The automatic server setup expects root SSH access on port 22; a custom SSH port is supported by a flag. The server needs internet/package access. Provider security-group changes may still require its website because a root password does not grant that separate account access.

## See the plan, then let SSH ask for the password

**Choose your computer’s operating system below.** Run the Windows commands or the Linux/macOS commands, not both.

On Windows, preview the plan:

```powershell
.\scripts\Setup-Vpn.ps1 -VpnPort 8443 -Target www.apple.com -Fingerprint safari
```

Enter the VPS IPv4 address when asked. This first command does not connect or change anything.

Then run the real setup:

```powershell
.\scripts\Setup-Vpn.ps1 -VpnPort 8443 -Target www.apple.com -Fingerprint safari -Apply
```

If PowerShell blocks a script you have inspected and trust, you can allow just this process without changing the machine-wide execution policy:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Setup-Vpn.ps1 -VpnPort 8443 -Target www.apple.com -Fingerprint safari -Apply
```

Respect managed-device policy; the manual walkthrough remains available if script execution is prohibited.

On Linux/macOS, the equivalent commands are:

```bash
python3 scripts/bootstrap_server.py --vpn-port 8443 --target www.apple.com --fingerprint safari --plan
python3 scripts/bootstrap_server.py --vpn-port 8443 --target www.apple.com --fingerprint safari --apply
```

These commands explicitly choose the tested **8443 + Safari + www.apple.com** preset. If 8443 is occupied, use 443 only if it is free; otherwise stop and preserve both existing listeners. The helper's bare defaults remain 443/Google and a regional fingerprint policy; the commands above override them.

The first SSH connection may ask you to confirm the server's host-key fingerprint. Compare it with the provider's console when available. After that, **SSH itself** asks for the root password. The password is hidden while you type; it never becomes a script argument, a configuration file, or a Git commit. SSH keys work too if you have already configured them.

Keep the terminal open. A fresh installation can take several minutes. The helper prints stages such as package preparation, panel installation, and client creation; it keeps installer output with generated credentials in a private log on the VPS.

## What the helper prepares for you

The default setup uses the version this guide describes, **3x-ui 3.8.5**, rather than silently following whatever a future latest release changes. It installs the panel through its official installer, selects the pinned core with SHA-256 verification, then configures the new installation through its supported CLI and API.

You get:

- One VLESS + RAW/TCP + REALITY inbound and separate `desktop` and `phone` accounts with Vision flow.
- Xray **26.7.28**, a **classical** Hiddify link, and a separately saved original panel export.
- Public VPN TCP port **8443** with the commands above. An occupied explicitly selected port stops setup; a busy default 443 can select a free 8443.
- Generated UUID, REALITY keys, short ID, and panel credentials. The panel URL path is `/`.
- The **Safari** fingerprint and **www.apple.com** target/SNI selected explicitly above. The optional auto fingerprint policy is described in the [automation guide](automation.md#choose-the-client-fingerprint-by-server-country); country is not a substitute for a real client test.
- **ForceIPv4** on the server’s outgoing path, so hostname-based website requests use IPv4.
- A public HTTP panel on **YOUR_SERVER_IP:27297**, opened directly in a browser.
- The VPN and panel TCP ports allowed in an existing UFW firewall, if active. UFW is Ubuntu’s firewall-management tool; the helper does not install or enable it. Existing SSH rules and custom/provider firewalls are not reset.
- A private `server.json` and `hiddify-profile.txt` saved under the repository's ignored `.secrets/` folder.

The helper checks that the server listener starts and probes its public TCP port from your computer. A reachable socket is still not an authenticated VPN test; importing the profile and running the final request below completes that check.

For a custom SSH port, use `-SshPort` / `--ssh-port`. Public VPN inbounds are restricted to **443 or 8443**; select one with `-VpnPort` / `--vpn-port`. Use `-PanelPort` / `--panel-port` if the administration port is occupied. Read the [automation details](automation.md#start-with-only-a-vps-ip-and-root-password) before changing defaults.

During **Apply**, the helper looks up the VPS's public IP country using [Country](https://country.is/); it sends the public IP, never your credentials. **Plan mode makes no lookup or SSH connection.** To skip that lookup or correct its result, add `-ServerCountry US` on Windows or `--server-country US` with Python; use another two-letter code for another country. To choose a tested preset yourself, add `-Fingerprint safari` / `--fingerprint safari` (or `chrome`, `firefox`, etc.). An explicit fingerprint overrides the country policy. If automatic lookup fails, the helper stops before installation and tells you which option to supply.

## Open 3x-ui directly in your browser

At completion, the helper prints the full panel URL. For the default port and root path it is:

```text
http://YOUR_SERVER_IP:27297/
```

Replace `YOUR_SERVER_IP` with your VPS IPv4 address. Open this address on your computer or phone. No SSH forwarding window is required, and closing the setup terminal does not close panel access.

If your provider filters incoming traffic, allow **TCP 27297**, or the actual panel port you selected. The VPN port is a different rule. The helper adds the panel allow rule only when UFW is already active; it does not control the provider firewall.

![Open the panel: full server URL, credentials, then Login](../images/3x-ui-panel-login.svg)

Open the generated `server.json` locally and find `panel_username` and `panel_password`. Enter them in the panel's **Username** and **Password** boxes and click **Login**. The root password is for SSH, not for the panel.

In the sidebar, click **Inbounds**. You should see **Personal VPN**, enabled, on the VPN port recorded in `server.json`. The account already exists; do not add a duplicate inbound.

![First visit to 3x-ui: Login, Inbounds, Personal VPN, then the desktop account share action](../images/3x-ui-first-visit.svg)

**Optional check:** **Outbounds → direct → Edit → Strategy** shows the IPv4 exit setting. It was applied by the helper; the [ForceIPv4 guide](force-ipv4.md) explains the setting and effective socket option.

For optional HTTPS or an intentionally private SSH-only panel, follow the [panel access alternatives](server-setup.md#required-open-the-dashboard-safely-in-your-browser). Older helper exports used a loopback-only listener: to make such a panel public, run `/usr/local/x-ui/x-ui setting -listenIP 0.0.0.0` on the VPS, restart `x-ui`, and allow the actual panel port.

![Separate browser-panel and VPN traffic paths](../images/ports-paths.svg)

## Bring the profile into Hiddify

The server and account are ready. Open the generated `hiddify-profile.txt` in a text editor and copy the whole `vless://...` line. This is your private connection profile.

**[Now follow Step 4: install Hiddify, import this link, and connect →](clients.md)**

**In Hiddify, set Settings → DNS → Outbound domain strategy → IPv4 only before reconnecting.** This helped during the first Android test. The timeout later returned, so use it as a troubleshooting check. The helper’s server-side ForceIPv4 setting does not set this option in your phone’s app.

The linked page gives the exact buttons, browser check, and optional additional recovery steps. You do not need to create another account in 3x-ui or run a preference-repair script first.

![Hiddify: add the generated profile from the clipboard](../images/hiddify-import.svg)

Copy the generated credentials/profile to your private password manager before deleting the working folder. `.secrets/` is deliberately not committed to Git. Do not paste those files into a public issue or screenshot.

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
