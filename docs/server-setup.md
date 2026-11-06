[← Guide index](../README.md) · Previous: [Get a server](choose-server.md) · Next: [Create the inbound](server-inbound.md)

# Install and prepare the VPN server

You have rented a Linux server and saved its login details. If you have not, start with [getting a server](choose-server.md). You can perform the steps below from Windows or Linux; the commands run on the remote server after you log in.

We will install **3x-ui**, a browser-based dashboard for managing connection accounts. Later, **Xray**, the network engine it manages, will carry the traffic. You do not need to learn either program's internals to install the panel.

UI instructions in this guide are based on **3x-ui 3.8.5**, checked on **2026-11-06**. Record your panel and Xray versions before making changes; they have independent release numbers. Existing working installations do not need a reinstall.

## 1. Choose the deployment

| You need | Deploy |
|---|---|
| A normal VPN on Windows, Linux, macOS, or a phone | One VPS, then [Hiddify](clients.md) on each device |
| An optional proxy for Linux terminal programs or a server without a desktop | One VPS, then the [standalone Xray client](linux-xray.md) |
| One proxy endpoint for several devices | The VPS plus a separate [restricted proxy host](share-proxy.md) |

Choose one row for your needs. For an ordinary Linux desktop, follow the same Hiddify path as on Windows; you do not need the standalone Xray chapter. The shared server installation below is the same for all three choices. If you already have a server, keep it and check its resources rather than ordering another one.

Use a supported Ubuntu release available from your provider, one CPU core, about 1 GiB RAM, a public IPv4 address, and enough transfer allowance. Ubuntu 22.04 and 24.04 are examples, not a requirement to reinstall a different working version. These resource values are practical starting points, not a capacity guarantee. IPv6 on the VPS is optional. HostVDS and FirstVDS are examples used by this project; check current locations, traffic limits, payment methods, and network reachability before purchasing. No particular provider guarantees an unblocked route.

## 2. Connect over SSH

**SSH** is the secure connection you use to administer the server from a command window. Open **PowerShell** on Windows or a **terminal** on Linux/macOS. The SSH command is the same on both.

Your provider supplies an IP address and a login method. If the login user is `root`, run:

```bash
ssh root@YOUR_SERVER_IP
```

Replace `YOUR_SERVER_IP` with the address from your provider. If the provider gave you a user such as `ubuntu`, use that name instead of `root`; after login, run `sudo -i` for the administrative installation commands below. If the provider supplied an SSH key or custom SSH port, follow its access instructions rather than assuming a root password exists.

Compare the first-connection host fingerprint with the provider's console when available. Enter the password at the prompt; do not put it in the command or publish it in a screenshot.

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

At the installer prompts:

1. If asked for a database, keep **SQLite**, the simple built-in choice for a personal server.
2. Choose an unused administration-panel port, for example **27297**, when offered. A port is a numbered network entry point; the panel port will be separate from the VPN connection port.
3. Choose how to protect the panel's browser login, as explained below.
4. Copy the printed **panel URL, username, password, and URL path** into a password manager. These are newly generated panel credentials, separate from the server's SSH/root password.
5. Open the exact panel URL in your browser. Keep its path; opening only the IP and port may return 404.
6. Enter the generated panel username/password and click **Login**. You should reach the dashboard.

### Open the panel with HTTPS

HTTPS encrypts the browser connection to the panel. Its certificate proves which server the browser reached. This is separate from the REALITY setting you will later use for VPN connections.

The checked 3x-ui installer offers **Let's Encrypt IP certificate** for a server without a domain name. Choose that label, enter the server's public IP when requested, and follow the prompts. A domain name is a website-style name such as `panel.example.com`; it is not required for this IP-certificate option.

Certificate issuance needs incoming **TCP port 80** reachable from the certificate authority. Allow it in the provider's firewall and in an existing host firewall if necessary. If another program already uses port 80, do not stop it blindly; use an appropriate existing web-server setup or the private-access option below. The installer configures renewal for its short-lived IP certificate, so keep that renewal path working.

When the installer prints an `https://...` URL, use that URL. Also allow the chosen panel TCP port from your administration IP if your firewall blocks it. If certificate setup failed, do not assume the panel now has trusted HTTPS merely because the installer finished.

### Or keep the panel private through SSH

This is useful if you do not want a public panel port or cannot use certificate issuance. In the installer, choose **Skip SSL / HTTP only** only when you will immediately use this private-access setup. Run on the server:

```bash
/usr/local/x-ui/x-ui setting -listenIP 127.0.0.1
systemctl restart x-ui
```

This binds the panel to the server's own loopback address, which is not reachable directly from the internet. On **your computer**, open a second terminal and run:

```bash
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:18080:127.0.0.1:YOUR_PANEL_PORT YOUR_LOGIN_USER@YOUR_SERVER_IP
```

Replace the panel port, login user, and server IP with the values you saved. Leave this terminal open. It forwards your computer's local port 18080 securely over SSH to the panel.

Open `http://127.0.0.1:18080/YOUR_PANEL_PATH/` in your computer's browser, using the saved panel path. Log in with the generated **panel credentials**, not the SSH password. The browser-to-localhost address is HTTP, while the hop to the VPS is carried inside encrypted SSH. You do not need to open a public firewall port for the panel in this arrangement.

These are manual steps; no repository script is required. The [optional setup helper](quick-start.md) chooses private SSH-forwarded access for you when you explicitly use it.

The panel port is an administration port. Do not put it in the VPN client's server-port field. See [the port map](ports-and-modes.md#the-ports-you-will-see).

If you lose the panel URL or credentials, run `x-ui` over SSH and use the menu's settings/reset options. Do not assume the installer always chooses the same defaults.

![Panel login walkthrough: full URL, credentials, and Login](../images/3x-ui-panel-login.svg)

## 4. Check port availability and firewalls

Before assigning the public VPN port, inspect listeners:

```bash
ss -lntp
```

Use TCP `443` for a new REALITY inbound if it is free. Existing web servers may already own it; choose another free TCP port, such as `8443`, or plan the coexistence explicitly. A nonstandard port is valid, but networks may filter it differently. Opening TCP 443 does not make a listener on 8443 reachable.

Allow the selected VPN TCP port in **both** the provider's firewall/security group and the host firewall, if enabled. UDP 443 is not required for the RAW/TCP inbound in this guide.

For an existing UFW installation, inspect the current rules before adding one:

```bash
ufw status verbose
ufw allow 443/tcp
```

Replace `443` if you selected another VPN port. Before enabling a new firewall, allow your actual SSH port and arrange access to the panel from your administration IP. Do not enable a default-deny firewall from a remote session before protecting SSH access. If UFW is absent, inspect the existing nftables/iptables rules rather than installing a second firewall blindly.

## 5. Keep administration recoverable

Create a separate administrator:

```bash
adduser YOUR_ADMIN_NAME
usermod -aG sudo YOUR_ADMIN_NAME
```

In a **second terminal**, verify `ssh YOUR_ADMIN_NAME@YOUR_SERVER_IP` works and that `sudo -v` succeeds. Keep the first session open while changing SSH access. Set up and test an SSH key before disabling password authentication.

For SSH brute-force protection on Ubuntu:

```bash
apt install -y fail2ban
cat > /etc/fail2ban/jail.d/sshd.local <<'EOF'
[sshd]
enabled = true
backend = systemd
EOF
systemctl enable --now fail2ban
fail2ban-client status sshd
```

If you choose to disable root SSH login, set `PermitRootLogin no` in the effective SSH server configuration, check `sshd -t`, then reload `ssh`. Ubuntu include files can override settings; verify the effective result with `sshd -T`. Test a new administrator login before closing the original session.

## 6. Verify services before creating a client

```bash
systemctl is-active x-ui
systemctl --failed --no-pager
/usr/local/x-ui/x-ui -v
/usr/local/x-ui/bin/xray-linux-amd64 version
```

Paths and executable names can differ by architecture or installation method. Xray may run as a child of `x-ui`, without a separate `xray.service`. An active panel alone does not prove the VPN listener is running.

**Success:** the panel opens, you know the selected public VPN port, and SSH still works. Continue with [inbound creation](server-inbound.md).
