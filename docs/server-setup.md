[← Guide index](../README.md) · Next: [Create the inbound](server-inbound.md)

# Install and prepare the VPN server

**Where:** an Ubuntu VPS outside your filtered network. **Result:** a working 3x-ui panel and a server ready to accept VPN connections.

UI instructions in this guide are based on **3x-ui 3.8.5**, checked on **2026-11-06**. Record your panel and Xray versions before making changes; they have independent release numbers. Existing working installations do not need a reinstall.

## 1. Choose the deployment

| You need | Deploy |
|---|---|
| A VPN for a phone or Windows PC | One VPS, then [Hiddify](clients.md) on each device |
| Proxy access for Linux programs | One VPS, then the [Linux client](linux-xray.md) |
| One proxy endpoint for several devices | The VPS plus a separate [restricted proxy host](share-proxy.md) |

Start with Ubuntu 24.04 LTS, one CPU core, about 1 GiB RAM, a dedicated IPv4 address, and enough transfer allowance. These are practical starting values, not a capacity guarantee. IPv6 on the VPS is optional. HostVDS and FirstVDS are examples used by this project; check current locations, traffic limits, payment methods, and network reachability before purchasing. No particular provider guarantees an unblocked route.

## 2. Connect over SSH

Your VPS provider supplies an IP and a root password or SSH key:

```bash
ssh root@YOUR_SERVER_IP
```

Compare the first-connection host fingerprint with the provider's console when available. Enter the password at the prompt; do not put it in the command or publish it in a screenshot.

The following installation commands run **on the VPS**, initially as root:

```bash
apt update
apt upgrade -y
apt install -y curl ca-certificates
```

If a reboot is required, reconnect afterward before continuing.

## 3. Install 3x-ui

Use the [official 3x-ui repository](https://github.com/MHSanaei/3x-ui) and its [release instructions](https://github.com/MHSanaei/3x-ui/releases). Download the installer before running it so it can be inspected:

```bash
curl -fL https://raw.githubusercontent.com/MHSanaei/3x-ui/main/install.sh -o /tmp/3x-ui-install.sh
less /tmp/3x-ui-install.sh
bash /tmp/3x-ui-install.sh
```

Press `q` to leave `less`. Running the installer grants it root access. Use an official stable release, and record the installed version rather than assuming the latest panel and every client engine are compatible.

At the installer prompts:

1. Choose a panel port when offered. Use an unused port, for example `27297`.
2. Follow the certificate/HTTPS setup offered by your installer version. A trusted certificate for a hostname avoids browser certificate warnings. A panel certificate and REALITY transport security are separate things.
3. Copy the printed **panel URL, username, password, and URL path** to a password manager.
4. Open that exact URL in a browser. Keep the URL path; opening only the IP and port may return 404.
5. Sign in and check the dashboard's panel and Xray versions.

The panel port is an administration port. Do not put it in the VPN client's server-port field. See [the port map](ports-and-modes.md#the-ports-you-will-see).

If you lose the panel URL or credentials, run `x-ui` over SSH and use the menu's settings/reset options. Do not assume the installer always chooses the same defaults.

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
