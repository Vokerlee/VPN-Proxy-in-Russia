[← Guide index](../README.md)

# Linux Xray client

## Section A — Connect This Machine to the VPN

Install Xray core, configure it as a local HTTP proxy that tunnels all traffic through your VLESS server, then point the OS at that proxy.

---

## Install Xray Core

```bash
sudo bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
```

## Write the Configuration File

Replace the placeholder values below with your actual server details from the 3X-UI connection URL.

```bash
sudo tee /usr/local/etc/xray/config.json > /dev/null << 'EOF'
{
  "log": {
    "access": "",
    "error": "",
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "port": 10801,
      "listen": "127.0.0.1",
      "protocol": "http",
      "settings": {
        "udp": true,
        "allowTransparent": false
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "vless",
      "settings": {
        "vnext": [
          {
            "address": "YOUR_VPN_SERVER_IP",
            "port": 443,
            "users": [
              {
                "id": "YOUR_UUID",
                "alterId": 0,
                "email": "t@t.tt",
                "encryption": "none",
                "flow": "xtls-rprx-vision"
              }
            ]
          }
        ],
        "userLevel": 0
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "fingerprint": "chrome",
          "serverName": "www.google.com",
          "publicKey": "YOUR_PUBLIC_KEY",
          "shortId": "YOUR_SHORT_ID",
          "spiderX": "/"
        }
      }
    }
  ]
}
EOF
```

**Values to replace:**

| Placeholder | Where to find it |
|-------------|-----------------|
| `YOUR_VPN_SERVER_IP` | Your VPN server's IP address |
| `YOUR_UUID` | The client ID from 3X-UI (e.g., `876e7cdd-44e3-4e71-86e1-66b8959ca6ea`) |
| `YOUR_PUBLIC_KEY` | The Public Key generated in 3X-UI |
| `YOUR_SHORT_ID` | The ShortId from 3X-UI |

## Start Xray and Verify

```bash
sudo systemctl daemon-reload
sudo systemctl enable xray
sudo systemctl start xray
```

Check that it's running:

```bash
sudo systemctl status xray --no-pager
```

Test the proxy is working:

```bash
curl -x http://127.0.0.1:10801 -s -o /dev/null -w "HTTP status: %{http_code}\n" https://www.google.com
```

You should see `HTTP status: 200`.

Check that traffic exits through the VPN:

```bash
curl -x http://127.0.0.1:10801 https://ifconfig.me
```

This should return your VPN server's IP, not the local server's IP.

## Route All Traffic Through the Proxy

### Shell Sessions

Create `/etc/profile.d/proxy.sh` so every new terminal session uses the proxy automatically:

```bash
sudo tee /etc/profile.d/proxy.sh > /dev/null << 'EOF'
export http_proxy="http://127.0.0.1:10801"
export https_proxy="http://127.0.0.1:10801"
export HTTP_PROXY="http://127.0.0.1:10801"
export HTTPS_PROXY="http://127.0.0.1:10801"
export no_proxy="localhost,127.0.0.1,::1"
export NO_PROXY="localhost,127.0.0.1,::1"
EOF
```

Load it into the current session:

```bash
source /etc/profile.d/proxy.sh
```

> Both lowercase and uppercase variants are needed because different tools read different ones — curl and wget use lowercase, some Java/Python libraries use uppercase.

### APT Package Manager (Optional)

```bash
sudo tee /etc/apt/apt.conf.d/95proxy > /dev/null << 'EOF'
Acquire::http::Proxy "http://127.0.0.1:10801";
Acquire::https::Proxy "http://127.0.0.1:10801";
EOF
```

### Background System Services (Optional)

This ensures services started by systemd (Docker, cron jobs, nginx, etc.) also use the proxy:

```bash
sudo mkdir -p /etc/systemd/system.conf.d

sudo tee /etc/systemd/system.conf.d/proxy.conf > /dev/null << 'EOF'
[Manager]
DefaultEnvironment="http_proxy=http://127.0.0.1:10801" "https_proxy=http://127.0.0.1:10801" "HTTP_PROXY=http://127.0.0.1:10801" "HTTPS_PROXY=http://127.0.0.1:10801" "no_proxy=localhost,127.0.0.1,::1"
EOF

sudo systemctl daemon-reexec
```

## What Persists After Reboot

Everything above survives reboots automatically:

| Component | File | Persists? |
|-----------|------|-----------|
| Xray service | `systemctl enable xray` | Yes |
| Shell proxy | `/etc/profile.d/proxy.sh` | Yes (every login shell) |
| APT proxy | `/etc/apt/apt.conf.d/95proxy` | Yes |
| Systemd proxy | `/etc/systemd/system.conf.d/proxy.conf` | Yes |

---

[← Guide index](../README.md)
