[← Guide index](../README.md)

# Server setup

## How It Works

VLESS with XTLS-Reality uses a unique identification method during the TLS handshake to distinguish authorized clients from outsiders. When the server recognizes the client as "its own," it functions as a proxy. When unrecognized traffic arrives, the connection is redirected to a real website (e.g., google.com) and mimics its behavior.

Your proxy traffic is disguised as regular browser HTTPS traffic using a real TLS certificate. This makes proxy detection virtually impossible for deep packet inspection (DPI) systems.

**Why VLESS + XTLS-Reality over WireGuard or Shadowsocks?**

- WireGuard is already being blocked in some regions
- Shadowsocks is an older protocol with known detection signatures
- VLESS + XTLS-Reality is the most modern obfuscation and encryption protocol available

---

## Choosing a VPS

> Skip this section if you already have a VPS server.

You need a VPS server in a country of your choice (Europe, US, etc.). Requirements:

- **OS:** Ubuntu 20.04 / 22.04 / 24.04
- **Minimum specs:** 1 CPU core, 512 MB RAM, 10 GB disk
- **Unlimited traffic** (important for VPN usage)
- **Dedicated IPv4 address**

**Recommended providers:**

| Use case | Provider | Notes |
|----------|----------|-------|
| VPN server (Europe / USA) | [HostVDS](https://hostvds.com) | Good selection of European and US locations, affordable plans, KVM virtualization, Ubuntu supported; accepts **Mir**, **Mastercard**, and **crypto** |
| Proxy server (Moscow / Russia) | [FirstVDS](https://firstvds.ru) | Russian data centers, low latency from Moscow, budget-friendly, Ubuntu supported |

> Any other VPS provider will also work (Hetzner, DigitalOcean, Vultr, OVH, etc.).

**Possible setups — choose what fits your situation:**

---

**Setup 1 — VPN server only, direct connection from a personal device**

Use this when you just want to bypass restrictions on your phone, laptop, or PC.

```
Your device (phone / PC)
       │
       │  VLESS + XTLS-Reality tunnel, encrypted
       ▼
HostVDS server (Europe / USA)
  └─ runs 3X-UI + VLESS inbound on port 443
       │
       ▼
   Internet
```

→ Follow Part 1 to set up the VPN server, then Part 2 to connect from your device using a GUI client app.

---

**Setup 2 — VPN server only, system-wide proxy on a Linux server**

Use this when you want an entire Linux server (e.g., a cloud VM) to route all its traffic through the VPN — no separate proxy VDS needed.

```
Linux server (any location)
  └─ runs Xray HTTP proxy on 127.0.0.1:10801
       │
       │  VLESS + XTLS-Reality tunnel, encrypted
       ▼
HostVDS server (Europe / USA)
  └─ runs 3X-UI + VLESS inbound on port 443
       │
       ▼
   Internet
```

→ Follow Part 1 to set up the VPN server, then Part 3 to configure system-wide proxy on the Linux server.

---

**Setup 3 — Two-server setup with a Russian proxy**

Use this when you are based in Russia and want all your devices to go through the VPN via a single local entry point.

```
Your devices (Russia)
       │
       │  direct connection, low latency
       ▼
FirstVDS server (Moscow, Russia)
  └─ runs Xray HTTP proxy on port 10801
       │
       │  VLESS + XTLS-Reality tunnel, encrypted
       ▼
HostVDS server (Europe / USA)
  └─ runs 3X-UI + VLESS inbound on port 443
       │
       ▼
   Internet
```

- Your devices connect to the **FirstVDS proxy** using a short local hop (low latency, no censorship friction)
- The FirstVDS proxy forwards all traffic through an encrypted **VLESS + XTLS-Reality tunnel** to the HostVDS VPN server abroad
- From the outside, the tunnel looks like normal HTTPS traffic to google.com — DPI cannot distinguish it

→ Follow Part 1 to set up the HostVDS server, then Part 3 to configure the FirstVDS server as the proxy, and [Share the Proxy with Other Devices](share-proxy.md) to allow your devices to connect to it.

---

After purchasing a VPS, you'll receive:
- Server IP address
- Root password (or SSH key)

---

## Install the 3X-UI Management Panel

### Connect to Your Server via SSH

```bash
ssh root@YOUR_SERVER_IP
```

When asked about the fingerprint, type `yes` and press Enter. Then enter your password.

### Update the System

```bash
apt update && apt upgrade -y
```

### Install Curl

```bash
apt install curl -y
```

### Run the Installation Script

Run the official installation script from GitHub:

```bash
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
```

> This same script can be used to update the panel to the latest version at any time.

### Set Credentials and Panel URL

After installation completes, it will ask if you want to customize the port — answer **Y** (yes).

![3X-UI installation — port customization prompt](../images/3x-ui-installation.png)

- **Port:** Choose a port for the web panel (e.g., `14288`; use a high port up to 65535)

The username and password are generated automatically. When installation finishes, it prints the panel URL and the generated credentials — copy them immediately.

![3X-UI installation complete — credentials and panel URL](../images/3x-ui-credentials.png)

To change the username and password, log in to the panel at `https://YOUR_SERVER_IP:YOUR_PORT/YOUR_PATH/` and update them in the settings.

> **Note:** If you skip the modification step (answer **N**), both the port and URL path will also be randomized. The installer still prints all values to the terminal — copy them before closing the session. You can also retrieve or reset them at any time by running `x-ui` in the terminal.

The panel is now installed. You can manage it with these commands:

| Command | Action |
|---------|--------|
| `x-ui` | Enter admin menu |
| `x-ui start` | Start the panel |
| `x-ui stop` | Stop the panel |
| `x-ui restart` | Restart the panel |
| `x-ui status` | Show panel status |
| `x-ui enable` | Enable auto-start on boot |
| `x-ui disable` | Disable auto-start on boot |
| `x-ui log` | View logs |
| `x-ui update` | Update the panel |

---

## Harden Server Security

### Block Brute-Force Attempts with fail2ban

This automatically bans IP addresses after too many failed login attempts:

```bash
apt install fail2ban -y
systemctl start fail2ban
systemctl enable fail2ban
```

### Create a Non-Root Admin User

```bash
adduser YOUR_USERNAME
```

Enter a strong password and optionally fill in user details (or leave them blank).

Add the new account to the sudo group:

```bash
usermod -aG sudo YOUR_USERNAME
```

Switch to the new account:

```bash
su - YOUR_USERNAME
```

### Disable Root SSH Login

Edit the SSH config:

```bash
sudo nano /etc/ssh/sshd_config
```

Find the line `PermitRootLogin` and set it to:

```
PermitRootLogin no
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

Restart SSH:

```bash
sudo service sshd restart
```

From now on, connect using: `ssh YOUR_USERNAME@YOUR_SERVER_IP`

---

[← Guide index](../README.md)
