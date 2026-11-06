# Set up your own VPN

Have a **new VPS**, its **IP address**, and its **root password**? Start below. The setup script prepares the server and gives you a connection profile for Hiddify.

These steps are for **Windows + a fresh Ubuntu 24.04 VPS**. If your server already has 3x-ui, keep it and start with [connecting Hiddify](docs/clients.md). For Linux/macOS, use the [same setup walkthrough with the Python command](docs/quick-start.md#see-the-plan-then-let-ssh-ask-for-the-password).

## 1. Download this guide

On this GitHub page, click **Code → Download ZIP**, then extract the downloaded folder.

Open the extracted folder—the one containing `README.md` and `scripts`. Right-click inside it and choose **Open in Terminal**. Use a **PowerShell** tab.

## 2. Let the script prepare your server

Copy this command into that PowerShell window and press Enter:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Setup-Vpn.ps1 -Apply
```

The execution-policy option applies only to this run of the script. You can [read what the setup changes](docs/quick-start.md#what-the-helper-prepares-for-you) before running it.

When asked:

1. Enter the VPS **IPv4 address** from your provider.
2. On the first SSH connection, check the host fingerprint against your provider's console and confirm it if it matches.
3. Enter the VPS **root password**. Nothing appears while you type; that is normal.

Wait for setup to finish. It creates the VPN account, selects IPv4 for outgoing traffic, and prints where it saved two private files:

| File | What you use it for |
|---|---|
| `hiddify-profile.txt` | Your VPN connection link |
| `server.json` | Your new 3x-ui panel login details |

The files are inside the generated `.secrets/server-...` folder. Keep them private. The script refuses to overwrite an existing 3x-ui installation.

If a step fails or Windows says SSH is missing, follow the [setup walkthrough](docs/quick-start.md). It explains the same steps with checks and recovery instructions.

## 3. Connect your Windows PC

1. [Download Hiddify for Windows](https://github.com/hiddify/hiddify-app/releases/latest/download/Hiddify-Windows-Setup-x64.exe) and install it.
2. Open Hiddify once, then close it. In the same PowerShell window, apply the guide's tested starting settings:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Repair-Hiddify.ps1 -Apply -ServiceMode Manual
   ```

   This backs up Hiddify's settings. It does not stop Invisible Man or another client.

3. Open `hiddify-profile.txt` and copy its whole `vless://...` line.
4. Open Hiddify, click **+ → Add from clipboard**, and select **Personal VPN**.
5. Open **Settings → Inbound → Service mode**, choose **System Proxy**, and click **Connect**. Reconnect if you changed the mode while connected.

![Hiddify: click New profile, import from clipboard, and select your profile](images/hiddify-import.svg)

Open a website. Then [check the VPN's exit address](docs/clients.md#press-connect-then-prove-the-route) to confirm it uses your VPS. System Proxy covers applications that follow Windows' proxy settings; the [client guide](docs/clients.md) explains VPN/TUN mode for other applications.

**If it does not work:** start with [the symptom table](docs/troubleshooting.md#first-choose-the-symptom-that-matches-yours). Do not reinstall the server or regenerate its keys as the first fix.

## Open the 3x-ui panel when you need it

You do not need the panel for everyday connecting. The setup already created your first account.

To open it, run the **SSH-forwarding command printed by setup** in a second terminal and leave that terminal open. Then open the **local browser URL printed by setup**. Log in using the panel username/password in `server.json`, not the root password.

[Show me the exact panel-opening steps →](docs/quick-start.md#open-3x-ui-without-opening-another-public-port)

![3x-ui: Login, open the prepared Personal VPN inbound, and find the client share action](images/3x-ui-first-visit.svg)

<details>
<summary><strong>Other setups, manual instructions, and the expert guide</strong></summary>

You can follow every step by hand, connect other devices, or learn how the tunnel works:

- [Full automatic setup walkthrough](docs/quick-start.md)
- [Manual VPS installation and administration](docs/server-setup.md)
- [Create a VLESS + REALITY account in 3x-ui](docs/server-inbound.md)
- [Hiddify settings and the old Invisible Man compatibility problem](docs/clients.md)
- [Choose ForceIPv4 through the 3x-ui buttons](docs/force-ipv4.md)
- [Ports, Windows proxy settings, and what Connect changes](docs/ports-and-modes.md)
- [Linux Xray client](docs/linux-xray.md)
- [Share a proxy through SSH or a restricted network](docs/share-proxy.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Automation helpers: commands, checks, and undo](docs/automation.md)
- [Inside Xray: a technical guide for programmers and network engineers](docs/xray-internals.md)

The illustrated UI baseline is **3x-ui 3.8.5 / Hiddify 5.5.5**, checked on **2026-11-06**. Pictures are labeled navigation diagrams, not captured screenshots. A fresh-VPS bootstrap still needs a disposable live integration test; its offline checks do not establish every provider's network behavior. Reachability depends on the network and compatible client/server engines.

</details>
