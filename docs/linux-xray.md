[← Guide index](../README.md) · [Server inbound](server-inbound.md) · [Share the proxy](share-proxy.md)

# Use your VPN connection from a Linux terminal

**Hiddify**, the VPN app in the main guide, also works on Linux desktops. This optional chapter shows another approach for command-line programs and servers.

**Xray** is the network engine that carries the connection. Here you will run it directly, without a desktop app. It provides a **local proxy**, a program on this Linux machine that forwards another program's requests through the remote server. Programs such as curl or the APT package manager can explicitly use it.

Run this walkthrough on the **Linux client machine**, not on a rented server (VPS) where the 3x-ui browser dashboard already manages Xray. It creates a separate client service with an HTTP proxy on `127.0.0.1:10801`. Programs that ignore proxy settings will still use their normal route; this chapter configures selected programs rather than routing the whole device.

**Optional chapter: skip it for a normal Linux desktop VPN.** [Hiddify works on Linux](clients.md) and is the main guide’s client. Continue here only if you want a standalone proxy for terminal programs or a machine without a desktop.

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

This client must support your server’s **REALITY** connection type. The [temporary client test](automation.md#test-a-real-authenticated-tunnel) lets you test a profile before installing it as the persistent service configuration.

## Put your account settings in a client file

Have your private [VLESS link from 3x-ui](server-inbound.md#5-export-the-connection) ready. **Choose one method:** edit the example below manually, or use the optional helper in the closed box. Both create the same client file; do not do both.

### Manual method

**nano** is a terminal text editor. If it is unavailable, use another editor you know or install it with your Linux distribution’s package manager.

On the **Linux client**, create a private folder and open the file:

```bash
mkdir -p -m 700 "$HOME/.config/vpn-guide"
nano "$HOME/.config/vpn-guide/client.json"
```

Paste the configuration below. Replace the placeholders with the values from your account. Also replace the example server port and `serverName` if your profile uses different ones.

| In the client file | From your VLESS link |
|---|---|
| `address` | Server address after `@` |
| Remote `port` | Port after the server address, for example `443` or `8443` |
| `id` | Account UUID between `vless://` and `@` |
| `serverName` | `sni=` value |
| `publicKey` | `pbk=` value; never the server’s private key |
| `shortId` | `sid=` value |

This example is for RAW/TCP + REALITY + Vision, the connection type created in the main guide. Keep the local inbound port **10801** unless it is already occupied. It is separate from the remote server port.

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
        "port": 8443,
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
        "serverName": "www.apple.com",
        "fingerprint": "safari",
        "publicKey": "YOUR_PUBLIC_KEY",
        "shortId": "YOUR_SHORT_ID",
        "spiderX": "/"
      }
    }
  }]
}
```

In nano, press **Ctrl+O**, **Enter**, then **Ctrl+X** to save and exit. Keep this file private; it contains your account credentials.

<details>
<summary>Optional alternative: generate that file from the link with a repository helper. Skip if you edited it above.</summary>

With Python 3.8+ available, run from this repository’s root:

```bash
mkdir -p -m 700 "$HOME/.config/vpn-guide"
python3 scripts/vpn_profile.py config --output "$HOME/.config/vpn-guide/client.json" --port 10801
```

Paste the link at the hidden prompt. The helper fills the account fields and rejects unsupported connection types. It refuses to overwrite an existing file unless you explicitly request it. See [the helper guide](automation.md#generate-a-client-configuration) for options.

</details>

### Install the file — required after either method

Before replacing a pre-existing service config, make a backup with a fresh name. For a new installation with the default file, for example:

```bash
sudo cp -a /usr/local/etc/xray/config.json /usr/local/etc/xray/config.json.before-guide
xray_service_user=$(systemctl show xray -p User --value)
xray_service_group=$(systemctl show xray -p Group --value)
[ -n "$xray_service_user" ] || xray_service_user=root
if [ -z "$xray_service_group" ]; then
    xray_service_group=$(id -gn "$xray_service_user")
fi
sudo install -o root -g "$xray_service_group" -m 640 "$HOME/.config/vpn-guide/client.json" /usr/local/etc/xray/config.json
sudo /usr/local/bin/xray run -test -config /usr/local/etc/xray/config.json
```

If the original file does not exist, skip the backup command. If `config.json.before-guide` already exists, choose another backup name; do not overwrite your recovery copy. The commands read the service account/group so an unprivileged Xray service can read the config without exposing it to every user. If `id` fails because your custom unit uses a dynamic account, stop here and inspect that unit rather than substituting an unrelated group. If the syntax test fails, restore the backup before restarting the service.

The local HTTP inbound carries HTTP and HTTPS CONNECT requests; it is not a general UDP tunnel.

## Start it, then make a real request

```bash
sudo systemctl enable --now xray
sudo systemctl restart xray
systemctl status xray --no-pager
ss -lnt 'sport = :10801'
```

If the service reports a permissions error, inspect `systemctl cat xray` and confirm the configured user/group can traverse the configuration directory and read the file. The install command above grants the service group read access; do not change the file to world-readable.

Now ask curl to use the proxy, overriding any existing `NO_PROXY` exemption:

```bash
curl --noproxy '' --proxy http://127.0.0.1:10801 --connect-timeout 5 --max-time 15 https://www.cloudflare.com/cdn-cgi/trace
```

Find `ip=`. It should be the VPS's exit address. A successful listener test alone does not establish that the account authenticated. If this request fails, inspect `journalctl -u xray --since '10 minutes ago' --no-pager` and follow [troubleshooting](troubleshooting.md).

## Let selected programs use it automatically

**Optional: skip this section if your explicit proxy command is all you need.** Choose only the applications you want to configure below; shell variables, APT, and a systemd service are separate choices.

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
