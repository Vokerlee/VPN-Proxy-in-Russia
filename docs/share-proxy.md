[← Guide index](../README.md)

# Share a proxy with other devices

## Section B — Use This Machine as a Proxy for Other Devices

By default, Xray listens on `127.0.0.1:10801` (local only). This section shows how to expose that proxy to the network so other devices — phones, PCs, or other servers — can route their traffic through this machine and out through the VPN. This corresponds to Setup 3 from Part 1.

### Allow Connections from Outside

Edit `/usr/local/etc/xray/config.json` and change:

```json
"listen": "0.0.0.0"
```

Restart Xray:

```bash
sudo systemctl restart xray
```

### Open the Firewall Port

**Option A — Open to everyone (no IP restriction)**

Use this if you want any machine to be able to connect to your proxy:

```bash
sudo ufw allow 10801/tcp
```

> **Warning:** An open proxy with no authentication is a security risk. Anyone on the internet who discovers port 10801 can route their traffic through your server and VPN. Only use this on isolated or trusted networks.

**Option B — Restrict to a specific IP (recommended)**

Use this to allow only your home/office IP and block everyone else:

```bash
# Allow only your IP to access the proxy
sudo ufw allow from YOUR_HOME_IP to any port 10801 proto tcp

# Deny everyone else
sudo ufw deny 10801/tcp
```

> Replace `YOUR_HOME_IP` with your actual public IP address (find it with `curl ifconfig.me` from your home machine).

In both cases, make sure ufw is enabled:

```bash
sudo ufw enable
sudo ufw status
```

### Test from Another Device

Set your system proxy to:

```
http://YOUR_CLIENT_SERVER_IP:10801
```

Test with curl:

```bash
curl -x http://YOUR_CLIENT_SERVER_IP:10801 https://ifconfig.me
```

This should return the VPN server's IP.

[← Guide index](../README.md)
