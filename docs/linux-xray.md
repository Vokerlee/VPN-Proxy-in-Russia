[← Guide index](../README.md) · [Server inbound](server-inbound.md) · [Share the proxy](share-proxy.md)

# Give Linux a local Xray proxy

You do not need a desktop VPN window to send a Linux program through the VPS. A small Xray process can listen on localhost, and a program such as curl or APT can explicitly use it.

Run this walkthrough on the **Linux client machine**, not on a VPS where 3x-ui already manages Xray. It creates a separate client service with an HTTP proxy on `127.0.0.1:10801`. Programs that ignore proxy settings will still use their normal route; this is not a TUN/transparent-routing guide.

## Install the official core

Use the [official Xray installer](https://github.com/XTLS/Xray-install), inspect it, and install the core:

```bash
curl -fL https://raw.githubusercontent.com/XTLS/Xray-install/main/install-release.sh -o /tmp/xray-install.sh
less /tmp/xray-install.sh
sudo bash /tmp/xray-install.sh install
```

Press `q` to leave `less`. Check the actual version and service:

```bash
/usr/local/bin/xray version
systemctl status xray --no-pager
```

Keep client/server REALITY compatibility in mind. The [temporary client test](automation.md#test-a-real-authenticated-tunnel) lets you test a profile before installing it as the persistent service configuration.

## Give Xray the connection link

Have the real [VLESS URL from 3x-ui](server-inbound.md#5-export-the-connection) ready. From this repository's root, make a private output folder and run:

```bash
mkdir -m 700 .secrets
python3 scripts/vpn_profile.py config --output .secrets/client.json --port 10801
```

If the folder already exists, check its permissions. Paste the URI at the hidden prompt. The helper maps its parameters into the client configuration, so you do not have to retype the UUID, SNI, key, short ID, or nonstandard server port. It supports the guide's RAW/TCP + REALITY + Vision setup; it will reject another transport rather than silently misconfigure it.

Before replacing a pre-existing service config, make a backup with a fresh name. For a new installation with the default file, for example:

```bash
sudo cp -a /usr/local/etc/xray/config.json /usr/local/etc/xray/config.json.before-guide
sudo install -m 600 .secrets/client.json /usr/local/etc/xray/config.json
sudo /usr/local/bin/xray run -test -config /usr/local/etc/xray/config.json
```

If the original file does not exist, skip the backup command. If `config.json.before-guide` already exists, choose another backup name; do not overwrite your recovery copy. If the syntax test fails, restore the backup before restarting the service.

<details>
<summary>See the shape of the generated configuration</summary>

The helper writes a local HTTP inbound and one VLESS outbound. This placeholder example explains the important fields; use your exported profile to generate the real values:

```json
{
  "log": {"loglevel": "warning"},
  "inbounds": [{
    "listen": "127.0.0.1",
    "port": 10801,
    "protocol": "http",
    "settings": {}
  }],
  "outbounds": [{
    "protocol": "vless",
    "settings": {
      "vnext": [{
        "address": "YOUR_VPN_SERVER_IP",
        "port": 443,
        "users": [{
          "id": "YOUR_UUID",
          "encryption": "none",
          "flow": "xtls-rprx-vision"
        }]
      }]
    },
    "streamSettings": {
      "network": "tcp",
      "security": "reality",
      "realitySettings": {
        "serverName": "www.google.com",
        "fingerprint": "chrome",
        "publicKey": "YOUR_PUBLIC_KEY",
        "shortId": "YOUR_SHORT_ID",
        "spiderX": "/"
      }
    }
  }]
}
```

The local port and the VPS port can have different values. The example HTTP inbound does not provide a general UDP tunnel. Adding an arbitrary `udp: true` field would not change that.

</details>

## Start it, then make a real request

```bash
sudo systemctl enable --now xray
sudo systemctl restart xray
systemctl status xray --no-pager
ss -lnt 'sport = :10801'
```

The service must be able to read its configuration. Check `systemctl cat xray` for the configured service user. If your installer runs Xray as an unprivileged account, grant that account read access to the private configuration using its group/ACL; do not make credentials world-readable to hide a permissions error.

Now ask curl to use the proxy, overriding any existing `NO_PROXY` exemption:

```bash
curl --noproxy '' --proxy http://127.0.0.1:10801 --connect-timeout 5 --max-time 15 https://www.cloudflare.com/cdn-cgi/trace
```

Find `ip=`. It should be the VPS's exit address. A successful listener test alone does not establish that the account authenticated. If this request fails, inspect `journalctl -u xray --since '10 minutes ago' --no-pager` and follow [troubleshooting](troubleshooting.md).

## Let selected programs use it automatically

The safest first step is one shell session:

```bash
export http_proxy=http://127.0.0.1:10801
export https_proxy=http://127.0.0.1:10801
export HTTP_PROXY=http://127.0.0.1:10801
export HTTPS_PROXY=http://127.0.0.1:10801
export no_proxy=localhost,127.0.0.1,::1
export NO_PROXY=localhost,127.0.0.1,::1
```

A program must honor these variables. Tools differ in case handling, and sudo/services do not necessarily inherit your shell environment. To make the setting persist for your own login shells, place it in the appropriate shell startup file. A file under `/etc/profile.d/` affects supported login shells for more users, so choose that only when you actually want that scope.

For APT, a dedicated configuration is more predictable than hoping it inherits your terminal variables:

```bash
sudo tee /etc/apt/apt.conf.d/95proxy >/dev/null <<'EOF'
Acquire::http::Proxy "http://127.0.0.1:10801";
Acquire::https::Proxy "http://127.0.0.1:10801";
EOF
```

For one systemd service, run `sudo systemctl edit YOUR_SERVICE` and add an override such as:

```ini
[Service]
Environment="http_proxy=http://127.0.0.1:10801"
Environment="https_proxy=http://127.0.0.1:10801"
Environment="no_proxy=localhost,127.0.0.1,::1"
```

Reload/restart that service as appropriate. This only helps software that uses those variables; it does not route every container, background program, or kernel packet. Configure containers and applications according to their own proxy support. Avoid a global systemd environment change when one service is all you need.

## Make recovery easy

The enabled Xray service persists after reboot. Shell exports persist only if you saved them in a startup file; APT and systemd overrides persist as their own files. They do not make the client reachable when its VPS or network path is down.

To return a shell to direct access, unset the proxy variables. To restore APT or a service, remove only the specific proxy configuration/override you added and reload that service. Restore the saved Xray configuration if you need to undo a client-file change. Keep backups private.

If another device needs this proxy, continue with [sharing through SSH or a restricted network](share-proxy.md).
