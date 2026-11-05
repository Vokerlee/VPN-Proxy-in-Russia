[← Guide index](../README.md) · Previous: [Server setup](server-setup.md) · Next: [Client setup](clients.md)

# Create a VLESS + REALITY inbound in 3x-ui

**Where:** the server's web panel. **Result:** a private `vless://` connection link for one client.

These labels refer to **3x-ui 3.8.5**. Inbounds accept clients; outbounds carry their traffic to websites. The panel's HTTP/HTTPS port is separate from the inbound's VPN port.

## 1. Open the correct form

1. Sign in using the full panel URL printed during installation.
2. In the main left sidebar, click **Inbounds**.
3. Click **Add Inbound**. On a narrow screen, open the sidebar with the menu button first.

![3x-ui buttons: Inbounds, then Add Inbound](../images/3x-ui-add-inbound.svg)

## 2. Set the listener

| Field | Set it to | Check |
|---|---|---|
| Enable | On | The inbound must remain enabled |
| Remark | A recognizable name, such as `Personal VPN` | This is a display name |
| Protocol | `vless` | The imported client must also use VLESS |
| Listen IP | Empty/default, or the intended public listener address | Do not set it to `127.0.0.1` for a public listener |
| Port | `443`, if free | If using `8443`, use 8443 in the client and both firewalls |

Do not replace a working listener just to match the examples. Preserve its actual port and connection parameters.

## 3. Set transport and security

| Field | Set it to | Why |
|---|---|---|
| Transmission / Network | `TCP` or `RAW` | Newer Xray names TCP transport RAW; `tcp` remains an alias in relevant releases |
| Security | **REALITY** | Different from ordinary certificate-based TLS |
| Proxy Protocol | Off | Enable only when an upstream proxy actually sends PROXY headers |
| Target / Dest | A reachable TLS endpoint, for example `www.google.com:443` | This endpoint must work from the VPS |
| Server Names / SNI | `www.google.com` for that example | Use a name covered by the target's certificate |
| Fingerprint / uTLS, when offered | `chrome` | This is exported for the client |
| Short IDs | Generate a short ID | Keep the value from the exported link |
| Private / Public Key | Click **Get New Key** for a new inbound | Keep the private key on the server |
| SpiderX, when offered | `/` | Keep the exported value |
| Sniffing | Off for the initial setup | Add it later only when a routing requirement needs it |

The example target is not a promise of availability on your network. From the VPS, test your selected name:

```bash
curl -I --connect-timeout 5 --max-time 15 https://www.google.com/
```

For an existing inbound, do **not** regenerate keys or short IDs: that invalidates existing profiles. A client's REALITY public key is not the website's certificate key.

![REALITY form: RAW/TCP, REALITY, Get New Key, Vision and Create](../images/3x-ui-reality-settings.svg)

## 4. Set the client account

Some forms reveal Flow only after selecting REALITY.

| Client field | Set it to |
|---|---|
| Enable | On |
| Email / Name | A label for this device, for example `laptop` |
| ID / UUID | Generate a UUID, or retain the existing client's UUID |
| Flow | `xtls-rprx-vision` |
| Encryption | `none`, where shown |
| Expiry / Traffic limit / IP limit | No limit for initial testing, unless you intentionally require one |

`encryption=none` is the VLESS payload setting; the connection is still protected by REALITY. It does not mean the VPN is sent as plaintext.

Click **Create** / **Save**, then apply or restart Xray if the panel prompts for it. This can interrupt existing VPN sessions briefly.

![3x-ui client row: expand the inbound and open Info or Share](../images/3x-ui-client-info.svg)

## 5. Export the connection

1. In **Inbounds**, expand the inbound's client list if needed.
2. Find the intended client row.
3. Open its **Info / connection details** action, or the QR/share action. Depending on the layout, actions may be in **⋯**.
4. Copy the **VLESS URL**, or scan the client's QR code in Hiddify.

A placeholder link looks like this; import the panel's real export rather than copying this example:

```text
vless://YOUR_UUID@YOUR_SERVER_IP:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=www.google.com&fp=chrome&pbk=YOUR_PUBLIC_KEY&sid=YOUR_SHORT_ID&type=tcp&spx=%2F#Personal-VPN
```

Check server IP, VPN port, UUID, Flow, REALITY public key, short ID, SNI, fingerprint, and transport. A correct IP with the wrong key or short ID can establish TCP and still fail REALITY authentication.

Create another client account for another person/device when you need separate revocation or usage accounting. You can reuse the same inbound; a second listener port is not required.

![Client details actions: Copy VLESS URL or Show QR code](../images/3x-ui-client-share.svg)

## 6. Verify the listener

On the VPS, replacing `443` with the actual inbound port:

```bash
ss -lntp 'sport = :443'
journalctl -u x-ui --since '10 minutes ago' --no-pager
```

**Success:** Xray owns the intended public listener, the client is enabled, and the exported link matches it. Then [configure Hiddify](clients.md).

For an IPv4 exit address, use the separate [ForceIPv4 guide](force-ipv4.md). For failed handshakes, follow [troubleshooting](troubleshooting.md).

## Versioned references

- [3x-ui 3.8.5 inbound form source](https://github.com/MHSanaei/3x-ui/tree/v3.8.5/frontend/src/pages/inbounds)
- [Xray REALITY configuration](https://xtls.github.io/en/config/transport.html#realityobject)
- [RAW/TCP transport](https://xtls.github.io/en/config/transports/raw.html)
