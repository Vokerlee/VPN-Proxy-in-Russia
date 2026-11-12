[← Single-server overview](single-server.md) · Step 2 of 4

# Install and prepare the VPN server

Here we’ll put a browser dashboard on your rented server, so you can manage the VPN without editing configuration files for every device.

Have the server’s **IP address**, **login name** and **password or SSH key** from your hosting company ready. The IP address tells your computer which server to contact. If you don’t have a server yet, [rent one first](choose-server.md).

Start on your own Windows, Linux or Mac computer. After you log in, the commands run on the rented server. A **terminal** is the command window you type them into; on Windows, use PowerShell.

We’ll install **3x-ui**, the dashboard you’ll open in your browser to manage the VPN. First get that dashboard working; we’ll set up the program behind it afterward.

These button instructions use **3x-ui 3.8.5**. The installer command below selects that dashboard version.

Already able to sign in to 3x-ui on this server? Keep that installation and skip the installer. Follow [the VPN program installation step](#install-the-vpn-program-version-used-in-this-guide) and [VPN port](#4-choose-the-vpn-port), then use the next step for your server’s role below.

**Follow steps 1–5 in order.** They prepare this server for the VPN. We’ll explain each tool or setting when you reach it. Sections marked **Optional** are alternatives or background; you can leave them closed.

## 1. Choose which server you are preparing

Follow this page once for a one-server VPN. For a two-server VPN, follow it **twice**, once in Moscow’s SSH terminal and once in the foreign server’s SSH terminal. Install a separate dashboard on each server and save each panel’s URL and login separately.

| Your route and server | Example provider | After this page |
|---|---|---|
| One-server route: foreign server | HostVDS | [Make device accounts](server-inbound.md) |
| Two-server route: Moscow | FirstVDS | Prepare the foreign dashboard too, then return to the two-server guide |
| Two-server route: foreign server, NL example | HostVDS | [Link the two panels](two-hop-vpn.md#how-the-two-3x-ui-panels-connect) once both are ready |

Before the two-server installation, you should already have rented **both** servers and passed [their IPv6 checks](two-hop-vpn.md#1-configure-ipv6-yourself-using-your-vps-providers-instructions). Renting only Moscow doesn’t complete the setup.

<details>
<summary>Optional: other deployment choices and resource notes. Skip for an ordinary personal VPN.</summary>

Use Hiddify on each phone or computer once the server setup is finished. A normal Linux desktop follows the same app steps as Windows. The [standalone Linux proxy](linux-xray.md) and [proxy-sharing chapter](share-proxy.md) are optional alternatives for specific tasks; neither replaces a missing Moscow or foreign server in the two-server route.

Use a supported Ubuntu release available from your provider, one CPU core, about 1 GiB RAM, a public IPv4 address, and enough transfer allowance. Ubuntu 22.04 and 24.04 are examples, not a requirement to reinstall a different working version. These resource values are practical starting points, not a capacity guarantee. IPv6 on the VPS is optional for one server. The two-server route requires it on both servers. HostVDS and FirstVDS are examples used by this project; check current locations, traffic limits, payment methods, and network reachability before purchasing. No particular provider guarantees an unblocked route.

</details>

## 2. Connect over SSH

**SSH** is the secure connection you use to administer the server from a command window. Open **PowerShell** on Windows or a **terminal** on Linux/macOS. The SSH command is the same on both.

Your provider supplies an IP address and a login method. If the login user is `root` (the administrator account), run:

```bash
ssh root@YOUR_SERVER_IP
```

Replace `YOUR_SERVER_IP` with the address from your provider. If the provider gave you a user such as `ubuntu`, use that name instead of `root`; after login, run `sudo -i` for the administrative installation commands below. If the provider supplied an SSH key or custom SSH port, follow its access instructions rather than assuming a root password exists.

If your SSH port is different from 22, the command is `ssh -p YOUR_SSH_PORT YOUR_LOGIN_USER@YOUR_SERVER_IP`. Replace all three placeholders with your provider’s values. With a key file, follow the provider’s instructions for selecting it.

On the first connection, SSH shows a **host fingerprint**, an identifier for the server’s SSH key. Compare it with the provider’s console when available, then accept the matching key. Enter the password at the prompt; nothing appears while you type. Keep the password out of commands and screenshots.

Once you see the server’s command prompt, you’re logged in. **root** means the server’s administrator; it is a username, not a password. Run `whoami` if you want to confirm which account you’re using.

If login fails or stalls, check the hosting company’s web console and login details before continuing. None of the installation commands below can run until you are connected.

The following installation commands run **on the VPS**, initially as root:

```bash
apt update
apt install -y curl ca-certificates
```

These commands refresh the package list and install curl, the download tool used below, with trusted certificate data.

<details>
<summary>Optional: update the server’s other installed packages</summary>

Run `apt upgrade -y` if you want to update existing packages now. If an update requires a reboot, reboot and reconnect before continuing. This package upgrade is separate from installing the VPN panel.

</details>

## 3. Install 3x-ui

Use the [official 3x-ui repository](https://github.com/MHSanaei/3x-ui) and its [release instructions](https://github.com/MHSanaei/3x-ui/releases). Download and run the installer:

```bash
curl -fL https://raw.githubusercontent.com/MHSanaei/3x-ui/v3.8.5/install.sh -o /tmp/3x-ui-install.sh
bash /tmp/3x-ui-install.sh v3.8.5
```

The installer runs with administrator access, so use the official source linked above. **Optional review:** after downloading and before running it, `less /tmp/3x-ui-install.sh` lets you read the script; press `q` to exit. Record the installed version if you later need troubleshooting help.

### Save the installer’s login details

At the installer prompts:

1. If asked for a database, keep **SQLite**, the built-in choice for a personal server.
2. Choose an unused panel port, for example **27297**, when offered. A port is a numbered network entry point. This one is for managing the server, not for VPN traffic.
3. For panel certificates, choose **Skip SSL / HTTP only** for direct HTTP browser access. The optional HTTPS instructions below explain certificates.
4. Save the printed **panel port, URL path, username, and password** in a password manager. The panel credentials are different from your root/SSH login.

### Open the dashboard in your browser

The ordinary setup opens the panel directly by the server's public IP. You do not need a second terminal or an SSH forwarding connection to keep using it.

**1. On the server**, enable the public panel listener:

```bash
/usr/local/x-ui/x-ui setting -listenIP 0.0.0.0
systemctl restart x-ui
```

**2. In your hosting company’s dashboard**, allow incoming **TCP on your panel port**, for example **27297**, if it has a firewall/security-group setting. Keep SSH access allowed. If there is no such restriction, continue to the browser step.

**3. In your computer or phone's browser**, open the complete saved URL:

```text
http://YOUR_SERVER_IP:YOUR_PANEL_PORT/YOUR_PANEL_PATH/
```

Replace the IP, port and path with the installer result. Keep the saved path and its slashes. A panel with the root path `/` uses `http://YOUR_SERVER_IP:27297/`. The address is on your VPS; `127.0.0.1` would mean the device running your browser.

Enter the **panel username and password**, then click **Login**. These are separate from the root/SSH password.

**Check:** the login page opens directly and the panel accepts your credentials. Closing SSH afterward does not close browser access. If the page is unreachable, check the actual panel listener and both firewalls. A listener bound to `127.0.0.1` accepts only local connections; repeat step 1 to make an existing private panel public.

<details>
<summary>Optional: use HTTPS for browser-to-panel encryption</summary>

The checked installer offers **Let's Encrypt IP certificate** without a domain. Select that option during installation and enter the public IP. For an existing installation, run `x-ui`, open **SSL Certificate Management**, and choose **Let's Encrypt SSL Certificate for IP Address** (menu 20, then 6 in 3.8.5).

Issuance and automatic renewal need incoming **TCP 80** reachable from the certificate authority. Preserve any existing service on port 80; plan coexistence rather than stopping it. Keep the panel port allowed as well. Confirm certificate installation and renewal setup succeeded, then open the printed `https://...` URL including its panel port and saved path. Check that the browser trusts the certificate.

If converting a private panel, also run `/usr/local/x-ui/x-ui setting -listenIP 0.0.0.0` and restart `x-ui`; installing a certificate alone does not change its listen address.

</details>

<details>
<summary>Optional: keep the panel private and access it through SSH</summary>

Choose this only when you want SSH to be required for browser access. For an HTTP panel, run on the VPS:

```bash
/usr/local/x-ui/x-ui setting -listenIP 127.0.0.1
systemctl restart x-ui
```

On your computer, open a second terminal and keep this command running:

```bash
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:18080:127.0.0.1:YOUR_PANEL_PORT YOUR_LOGIN_USER@YOUR_SERVER_IP
```

Replace the port, login user and server IP with your values. Add `-p YOUR_SSH_PORT` for a custom SSH port. Open `http://127.0.0.1:18080/YOUR_PANEL_PATH/` and sign in with the panel credentials. Closing this forwarding terminal ends browser access; the VPN keeps running. No public panel-port rule is needed for this option.

</details>

The panel port is an administration port. Do not put it in the VPN client's server-port field. See [the port map](ports-and-modes.md#the-ports-you-will-see).

If you lose the panel URL or credentials, run `x-ui` over SSH and use the menu's settings/reset options. Do not assume the installer always chooses the same defaults.

### Install the VPN program version used in this guide

You should now be signed in to the dashboard. There are two programs on the server: **3x-ui** gives you this control panel, and **Xray** carries the actual VPN connection. The installer has already put both on the server. Here we’ll use the dashboard to install the Xray version that matches the rest of this walkthrough.

Before a website can load, the app and server exchange opening messages to start their encrypted connection. In our tests, Hiddify worked on Wi-Fi but failed on mobile data with a newer server version. Version **26.7.28** accepts the shorter opening message that worked on the tested mobile connection. We’ll select that option when making your device links on the next page. For the foreign server behind Moscow, use **26.9.9**: that is the version we tested for the separate connection between the servers.

You don’t have to choose between unfamiliar settings. Find your server in this table:

| Server you’re working on | Version to install |
|---|---|
| The only server in a one-server VPN | **26.7.28** |
| Moscow in a two-server VPN | **26.7.28** |
| The foreign server behind Moscow | **26.9.9** |

**Already serving other users?** Save a panel backup and the original version number before switching; the change can briefly interrupt their connections. Check their connections again afterward.

**In your browser, on that server’s 3x-ui dashboard:**

1. Open the dashboard’s main status page. Find **Xray**, its running/stopped status, and the version number beside it. If it already matches the table and says **Running**, this step is complete; go to [choosing the VPN port](#4-choose-the-vpn-port).
2. Click that **version number**. It is a button; hovering over it shows **Version**. This opens **Xray Updates**.
3. Keep the **Xray** section open. Find **v26.7.28** or **v26.9.9**, using the table above. The `v` is just part of the release label.
4. Click the **circle beside that version**. A confirmation asks whether you want to change the Xray version. Check the number and click **Confirm**.
5. Wait while the panel downloads, installs and activates it. Keep the browser tab open and don’t refresh during installation.
6. Back on the status page, check the version now matches the table and the status says **Running**. Then continue to [choosing the VPN port](#4-choose-the-vpn-port).

That’s the installation—there’s no separate program to download onto your phone or PC for this step. The dashboard’s own version remains **3x-ui 3.8.5**.

If the version list is empty, the requested release is missing, or installation reports an error, keep the exact message and [check the server](troubleshooting.md#server-checks) before continuing. Don’t choose a different number just because it’s nearby in the list.

The older version is a compatibility choice, not a guarantee that every mobile network will work. [The phone test, opening-message sizes and security tradeoffs](handshakes-and-versions.md#match-the-client-option-to-the-server) are explained separately.

[Checked 3x-ui 3.8.5 version button](https://github.com/MHSanaei/3x-ui/blob/v3.8.5/frontend/src/pages/index/OverviewActionBar.tsx) · [Version list and installation confirmation](https://github.com/MHSanaei/3x-ui/blob/v3.8.5/frontend/src/pages/index/VersionModal.tsx)

## 4. Choose the VPN port

Your server has one internet address but runs several programs. A **port** is the number that tells it which program a connection is for. You already used the dashboard’s port, such as **27297**, in your browser address. Now choose a separate port for the VPN connection.

Use the number for your setup, if it’s free:

| This server | VPN port in this guide |
|---|---|
| Only server in a one-server VPN | **8443** |
| Moscow in the first two-server route | **443** |
| Foreign server behind Moscow | **443** |

The two servers can both use 443 because they have different addresses. The next page uses this number when creating the VPN entry.

**In that server’s SSH terminal**, check the port you intend to use. For the one-server example:

```bash
ss -lntp 'sport = :8443'
```

For the two-server example, run `ss -lntp 'sport = :443'` on **each** server instead.

- **Only column headings appear:** that port is free. Record it for this server and use it in the next guide.
- **A listener appears:** preserve it and check the other allowed port, 443 or 8443. If both are occupied, stop and resolve the conflict. If you use a different port from the example, use that actual port in its inbound, firewall rule and connection checks too.

Changing a port can help when one particular port is filtered. It cannot bypass filtering of the server's whole IP address.

Save the selected number. In 3x-ui you will enter it as the inbound’s **Port**. The exported connection link will then include it automatically.

**In your provider’s dashboard**, check whether this server has incoming network restrictions, usually called **Firewall**, **Security group**, or **Network rules**. If it does, allow incoming **TCP** on your selected VPN port. TCP is the connection type used by this setup. If your provider already allows incoming connections, there is no rule to add there.

Keep the SSH access and panel-port rule you already use. If a port is still unreachable, use [the server checks](troubleshooting.md#server-checks) rather than adding more setup steps here.

## 5. Protect SSH logins with fail2ban

**fail2ban** watches for repeated failed logins and temporarily bans the source addresses. Run these commands in **this server’s SSH terminal**, as root:

```bash
apt install fail2ban -y
systemctl start fail2ban
systemctl enable fail2ban
```

Check that SSH protection is active:

```bash
fail2ban-client status sshd
```

It should show the **sshd** jail, meaning the SSH login protection is loaded. If it reports an error, [use the fail2ban check](troubleshooting.md#fail2ban-is-installed-but-ssh-protection-isnt-active). For two servers, repeat this on both Moscow and the foreign server.

**This server is ready when:** its panel opens, the VPN program shows the version selected above and **Running**, you have recorded its free VPN port, and SSH still works. For the two-server route, check that list for **both servers** before linking them.

**For one server:** [make your device connection links →](server-inbound.md)

**For two servers:** prepare the other dashboard too, then [return to linking the panels →](two-hop-vpn.md#how-the-two-3x-ui-panels-connect).
