[← Setup overview](../README.md) · Step 2 of 4

# Install and prepare the VPN server

You have rented a Linux server and saved its login details. If you have not, start with [getting a server](choose-server.md). You can perform the steps below from Windows or Linux; the commands run on the remote server after you log in.

We will install **3x-ui**, a browser-based dashboard for managing connection accounts. Later, **Xray**, the network engine it manages, will carry the traffic. You do not need to learn either program's internals to install the panel.

UI instructions in this guide are based on **3x-ui 3.8.5**, checked on **2026-11-06**. Record your panel and Xray versions before making changes; they have independent release numbers. Existing working installations do not need a reinstall.

**Do this page if your server does not yet have a working 3x-ui dashboard.** If you can already log in to 3x-ui, skip installation and [open Step 3: create your connection account](server-inbound.md).

Follow sections 1–4 and 6 for setup. Section 5 is optional administration advice; it is labeled before its commands. Public HTTPS panel access is an advanced alternative, kept closed below.

## 1. Choose the deployment

A **VPS** is your rented remote server. **Hiddify** is the app you will install on your devices to use it. A **proxy** forwards network requests for another program.

| You need | Deploy |
|---|---|
| A normal VPN on Windows, Linux, macOS, or a phone | One VPS, then [Hiddify](clients.md) on each device |
| An optional proxy for Linux terminal programs or a server without a desktop | One VPS, then the [standalone Xray client](linux-xray.md) |
| One proxy endpoint for several devices | The VPS plus a separate [restricted proxy host](share-proxy.md) |

Choose one row for your needs. For an ordinary Linux desktop, follow the same Hiddify path as on Windows; you do not need the standalone Xray chapter. The shared server installation below is the same for all three choices. If you already have a server, keep it and check its resources rather than ordering another one.

Use a supported Ubuntu release available from your provider, one CPU core, about 1 GiB RAM, a public IPv4 address, and enough transfer allowance. Ubuntu 22.04 and 24.04 are examples, not a requirement to reinstall a different working version. These resource values are practical starting points, not a capacity guarantee. IPv6 on the VPS is optional. HostVDS and FirstVDS are examples used by this project; check current locations, traffic limits, payment methods, and network reachability before purchasing. No particular provider guarantees an unblocked route.

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

## 4. Check port availability and firewalls

A **listener** is a running program waiting for connections on a port. A **firewall** decides which incoming connections are allowed. The next chapter creates a REALITY inbound—the VPN listener for your devices. It uses **TCP**, the connection transport selected in that form.

On the server, list ports already in use:

```bash
ss -lntp
```

Look for `:443` in the **Local Address:Port** column. If there is no listener on that port, use TCP `443` for your new VPN inbound. Existing web servers may already own it; choose another free TCP port, such as `8443`, or plan the coexistence explicitly. A nonstandard port is valid, but networks may filter it differently. Opening TCP 443 does not make a listener on 8443 reachable.

Allow the selected VPN TCP port in **both** the provider's firewall/security group and the host firewall, if enabled. UDP 443 is not required for the RAW/TCP inbound in this guide.

**UFW** is Ubuntu’s common firewall-management tool. If your server uses it, check its state and allow the chosen VPN port:

```bash
ufw status verbose
ufw allow 443/tcp
```

Replace `443` if you selected another VPN port. Before enabling a new firewall, allow your actual SSH port. The private dashboard in this guide uses that same SSH access; it needs no public panel-port rule. Do not enable a default-deny firewall from a remote session before protecting SSH access. If UFW is absent, inspect the existing nftables/iptables rules rather than installing a second firewall blindly.

## 5. Keep administration recoverable

**Optional for the first connection.** These steps improve ongoing administration. You may go straight to section 6 and return here after the VPN works. If you already have a tested administrator and SSH keys, keep them; you do not need another account.

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

## 6. Verify services before creating a client

```bash
systemctl is-active x-ui
systemctl --failed --no-pager
/usr/local/x-ui/x-ui -v
/usr/local/x-ui/bin/xray-linux-amd64 version
```

Paths and executable names can differ by architecture or installation method. Xray may run as a child of `x-ui`, without a separate `xray.service`. The VPN listener is created in Step 3, so you will check its port there.

**Step 2 is complete when:** the panel opens, you know the selected public VPN port, and SSH still works.

**[Next step: create your connection account →](server-inbound.md)**
