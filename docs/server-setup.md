[← Setup overview](../README.md) · Step 2 of 4

# Install and prepare the VPN server

You have rented a Linux server and saved its login details. If you have not, start with [getting a server](choose-server.md). You can perform the steps below from Windows or Linux; the commands run on the remote server after you log in.

We will install **3x-ui**, a browser-based dashboard for managing connection accounts. Later, **Xray**, the network engine it manages, will carry the traffic. You do not need to learn either program's internals to install the panel.

UI instructions in this guide are based on **3x-ui 3.8.5**, checked on **2026-11-06**. Record your panel and Xray versions before making changes; they have independent release numbers. Existing working installations do not need a reinstall.

**Do this page if your server does not yet have a working 3x-ui dashboard.** If you can already log in to 3x-ui, skip installation and [open Step 3: create your connection account](server-inbound.md).

**Required here:** connect over SSH, install and open the dashboard, and choose the VPN port (sections 2–4). The other sections are optional background, security improvements, or extra checks. They are closed below so you can follow the main path without reading them.

## 1. The ordinary setup: one server, one app

Use your existing rented server (**VPS**) and install **Hiddify**, the VPN app, on each device you want to connect. Windows and Linux desktops follow the same path. You do not need another server.

<details>
<summary>Optional: other deployment choices and resource notes. Skip for an ordinary personal VPN.</summary>

A **VPS** is your rented remote server. **Hiddify** is the app you will install on your devices to use it. A **proxy** forwards network requests for another program.

| You need | Deploy |
|---|---|
| A normal VPN on Windows, Linux, macOS, or a phone | One VPS, then [Hiddify](clients.md) on each device |
| An optional proxy for Linux terminal programs or a server without a desktop | One VPS, then the [standalone Xray client](linux-xray.md) |
| One proxy endpoint for several devices | The VPS plus a separate [restricted proxy host](share-proxy.md) |

Choose one row for your needs. For an ordinary Linux desktop, follow the same Hiddify path as on Windows; you do not need the standalone Xray chapter. The shared server installation below is the same for all three choices. If you already have a server, keep it and check its resources rather than ordering another one.

Use a supported Ubuntu release available from your provider, one CPU core, about 1 GiB RAM, a public IPv4 address, and enough transfer allowance. Ubuntu 22.04 and 24.04 are examples, not a requirement to reinstall a different working version. These resource values are practical starting points, not a capacity guarantee. IPv6 on the VPS is optional. HostVDS and FirstVDS are examples used by this project; check current locations, traffic limits, payment methods, and network reachability before purchasing. No particular provider guarantees an unblocked route.

</details>

## 2. Connect over SSH

**SSH** is the secure connection you use to administer the server from a command window. Open **PowerShell** on Windows or a **terminal** on Linux/macOS. The SSH command is the same on both.

Your provider supplies an IP address and a login method. If the login user is `root` (the administrator account), run:

```bash
ssh root@YOUR_SERVER_IP
```

Replace `YOUR_SERVER_IP` with the address from your provider. If the provider gave you a user such as `ubuntu`, use that name instead of `root`; after login, run `sudo -i` for the administrative installation commands below. If the provider supplied an SSH key or custom SSH port, follow its access instructions rather than assuming a root password exists.

On the first connection, SSH shows a **host fingerprint**, an identifier for the server’s SSH key. Compare it with the provider’s console when available, then accept the matching key. Enter the password at the prompt; nothing appears while you type. Keep the password out of commands and screenshots.

The following installation commands run **on the VPS**, initially as root:

```bash
apt update
apt upgrade -y
apt install -y curl ca-certificates
```

If a reboot is required, reconnect afterward before continuing.

![Installer walkthrough: run the installer and save its complete output](../images/3x-ui-installation.svg)

## 3. Install 3x-ui

Use the [official 3x-ui repository](https://github.com/MHSanaei/3x-ui) and its [release instructions](https://github.com/MHSanaei/3x-ui/releases). Download the installer before running it so it can be inspected:

```bash
curl -fL https://raw.githubusercontent.com/MHSanaei/3x-ui/main/install.sh -o /tmp/3x-ui-install.sh
less /tmp/3x-ui-install.sh
bash /tmp/3x-ui-install.sh
```

Press `q` to leave `less`. Running the installer grants it root access. Use an official stable release, and record the installed version rather than assuming the latest panel and every client engine are compatible.

### Required: install the panel and save its login details

At the installer prompts:

1. If asked for a database, keep **SQLite**, the built-in choice for a personal server.
2. Choose an unused panel port, for example **27297**, when offered. A port is a numbered network entry point. This one is for managing the server, not for VPN traffic.
3. For panel certificates, choose **Skip SSL / HTTP only**. The next steps carry the browser connection through encrypted SSH, so you do not need a domain or public certificate.
4. Save the printed **panel port, URL path, username, and password** in a password manager. The panel credentials are different from your root/SSH login.

### Required: open the dashboard safely in your browser

This connection is only for managing the dashboard. It does not carry your VPN traffic and does not need to stay open while using the VPN. Follow these steps after the installer finishes.

**1. On the server**, in the SSH window you already opened, run:

```bash
/usr/local/x-ui/x-ui setting -listenIP 127.0.0.1
systemctl restart x-ui
```

This makes the dashboard private: only the server itself can reach it directly. Next, give your browser a secure way in.

**2. On your computer**, open a **second PowerShell window or terminal**. Do not type this command inside the server's SSH session:

```bash
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:18080:127.0.0.1:YOUR_PANEL_PORT YOUR_LOGIN_USER@YOUR_SERVER_IP
```

Replace these three placeholders before pressing Enter:

| Replace | With |
|---|---|
| `YOUR_PANEL_PORT` | The panel port saved from the installer, for example `27297` |
| `YOUR_LOGIN_USER` | Your server login user, such as `root` |
| `YOUR_SERVER_IP` | Your server's public IP address |

If your provider uses a custom SSH port, add `-p YOUR_SSH_PORT` after `ssh`. Enter the SSH password when asked. **Leave this window open**; no further output is normal. It is carrying your browser connection securely to the server. If it reports that local port 18080 is already in use, choose another unused local port in both this command and the browser address below.

**3. In your computer's browser**, open:

```text
http://127.0.0.1:18080/YOUR_PANEL_PATH/
```

Replace `YOUR_PANEL_PATH` with the path printed by the installer. For example, a saved path `/abc123/` gives `http://127.0.0.1:18080/abc123/`. Keep the slashes and the path. Use your **panel username and password**, then click **Login**.

**Check:** the dashboard opens. Keep the second terminal open while using it. You can close it when finished; the VPN service keeps running. To open the dashboard tomorrow, repeat steps 2 and 3. Step 1 only needs to be done once.

<details>
<summary>Optional advanced alternative: public HTTPS dashboard. Skip for the ordinary setup above.</summary>

Use this instead of the private dashboard access above only if you intentionally want a public administration endpoint. You do not need it for the VPN to work. An already-private installation also needs its listen address changed deliberately before it can accept public connections.

The checked installer offers **Let's Encrypt IP certificate** without a domain name. During installation, select that option and enter the public IP. Certificate issuance and renewal need incoming **TCP 80** reachable from the certificate authority, and browser access needs the chosen panel TCP port allowed from your administration IP in both applicable firewalls. Preserve any existing web service using port 80; plan coexistence rather than stopping it.

Use the printed `https://...` URL including its path, and log in with the generated panel credentials. Confirm the certificate is trusted. A completed installation alone does not establish that certificate issuance or future renewal succeeded.

</details>

The panel port is an administration port. Do not put it in the VPN client's server-port field. See [the port map](ports-and-modes.md#the-ports-you-will-see).

If you lose the panel URL or credentials, run `x-ui` over SSH and use the menu's settings/reset options. Do not assume the installer always chooses the same defaults.

![Panel login walkthrough: full URL, credentials, and Login](../images/3x-ui-panel-login.svg)

## 4. Choose the VPN port

Use **443** for the VPN connection if that port is free. A **port** is a numbered network entry point; it lets the server distinguish VPN connections from SSH and dashboard access.

**On the server**, check whether another program already uses 443:

```bash
ss -lntp 'sport = :443'
```

- **Only the column headings appear:** port 443 is free. Use **443** in the next chapter.
- **A row appears:** another program is using 443. Keep it running and check **8443** with `ss -lntp 'sport = :8443'`. If that is free, use **8443** in the next chapter.

Save the selected number. In 3x-ui you will enter it as the inbound’s **Port**. The exported connection link will then include it automatically.

**In your provider’s dashboard**, check whether this server has incoming network restrictions, usually called **Firewall**, **Security group**, or **Network rules**. If it does, allow incoming **TCP** on your selected VPN port. TCP is the connection type used by this setup. If your provider already allows incoming connections, there is no rule to add there.

You do not need to install or enable UFW for this walkthrough. Keep your existing SSH access; the private dashboard uses that same SSH connection.

<details>
<summary>Optional: this server already has its own firewall. Skip if you have not configured one and your server image does not include one.</summary>

A provider firewall and a firewall running on the server are separate. If the server already filters incoming traffic, allow the VPN port there too. Use its existing management tool; do not install a second firewall just for this guide.

For an existing **UFW** installation (Ubuntu’s firewall-management tool), inspect its state:

```bash
ufw status verbose
```

If it says **inactive**, do not enable it as part of this step. If it says **active**, allow your selected port, for example:

```bash
ufw allow 443/tcp
```

Substitute 8443 if you selected that port. Keep the current SSH rules. If the server uses nftables or iptables instead, update its existing policy with that tool. Do not reset the rules on a remotely managed server.

</details>

## 5. Optional: improve server administration later

**Skip for now if you want to finish the VPN setup first.** These changes help long-term administration; they are not required to establish the VPN connection.

<details>
<summary>Optional security improvements: administrator account, fail2ban, and SSH login restrictions</summary>

Create a separate administrator:

```bash
adduser YOUR_ADMIN_NAME
usermod -aG sudo YOUR_ADMIN_NAME
```

In a **second terminal**, verify `ssh YOUR_ADMIN_NAME@YOUR_SERVER_IP` works and that `sudo -v` succeeds. Keep the first session open while changing SSH access. Set up and test an SSH key before disabling password authentication.

**Optional: block repeated failed SSH logins with fail2ban.** On Ubuntu, install and start it:

```bash
apt install fail2ban -y
systemctl start fail2ban
systemctl enable fail2ban
```

Check SSH protection with `fail2ban-client status sshd`. If it lists the `sshd` jail, protection is active. If it reports an error, inspect `systemctl status fail2ban --no-pager` and `journalctl -u fail2ban --no-pager`; do not assume installation alone enabled protection on every Ubuntu image.

If you choose to disable root SSH login, set `PermitRootLogin no` in the effective SSH server configuration, check `sshd -t`, then reload `ssh`. Ubuntu include files can override settings; verify the effective result with `sshd -T`. Test a new administrator login before closing the original session.

</details>

## 6. Optional: check the service from the terminal

**Skip if the dashboard opens normally.** If it does not, run on the server:

```bash
systemctl is-active x-ui
```

The expected result is `active`. For any other result, use [the server checks](troubleshooting.md#server-checks). You do not need to collect version numbers or read logs before moving to the next page.

**Step 2 is complete when:** the panel opens, you know the selected public VPN port, and SSH still works.

**[Next step: create your connection account →](server-inbound.md)**
