[← Setup overview](../README.md) · Step 3 of 4

# Create your first connection account

Open **3x-ui**, the browser dashboard installed on your server. Here you will create an account for one device and copy the private connection link into your VPN app.

An **inbound** is the server entry point that accepts a device's connection. **VLESS + REALITY** is the connection type used in this walkthrough; the table below supplies its required settings. An **outbound** is the path the server uses afterward to reach a website.

The dashboard runs **Xray**, the network engine that handles the connections. These labels refer to **3x-ui 3.8.5**. The panel's HTTP/HTTPS port is separate from the inbound's VPN port.

**Do this page if you need a connection account.** Already have an enabled account and its exported VLESS link? Skip this page and [open Step 4: connect your device](clients.md). Otherwise, follow sections 1–6 in order. The reference links at the end are optional.

## 1. Open the correct form

1. Open the dashboard using the browser address from [Step 2](server-setup.md#required-open-the-dashboard-safely-in-your-browser). For the default private setup, keep its SSH forwarding window open. Sign in with the panel credentials.
2. In the main left sidebar, click **Inbounds**.
3. Click **Add Inbound**. On a narrow screen, open the sidebar with the menu button first.

![3x-ui buttons: Inbounds, then Add Inbound](../images/3x-ui-add-inbound.svg)

## 2. Set the listener

The **listener** waits for devices to connect on the selected port. Use the free port you chose in the previous page; allow that same TCP port in the server firewall and any provider firewall.

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
| Server Names / SNI | `www.google.com` for that example | SNI is the website name sent during connection setup; use one covered by the target’s certificate |
| Fingerprint / uTLS, when offered | `chrome` | Selects the browser-style connection handshake exported to the client |
| Short IDs | Generate a short ID | A short random label used to recognize this connection; keep the exported value |
| Private / Public Key | Click **Get New Key** for a new inbound | Keep the private key on the server |
| SpiderX, when offered | `/` | Keep the exported value |
| Sniffing | Off for the initial setup | Inspects initial traffic to identify its destination; unnecessary for this simple setup |

**TLS** is the encryption used by HTTPS websites. The REALITY target must provide suitable TLS and be reachable from your rented server (VPS). On that server, test the example target:

```bash
curl -I --connect-timeout 5 --max-time 15 https://www.google.com/
```

You should receive HTTP response headers rather than a timeout or connection error. This checks website reachability; the device test in Step 4 will check the actual VPN connection.

For an existing inbound, do **not** regenerate keys or short IDs: that invalidates existing profiles. A client's REALITY public key is not the website's certificate key.

![REALITY form: RAW/TCP, REALITY, Get New Key, Vision and Create](../images/3x-ui-reality-settings.svg)

## 4. Set the client account

Some forms reveal Flow only after selecting REALITY.

| Client field | Set it to |
|---|---|
| Enable | On |
| Email / Name | A label for this device, for example `laptop` |
| ID / UUID | Generate the unique account identifier, or keep the existing account’s value |
| Flow | `xtls-rprx-vision` |
| Encryption | `none`, where shown |
| Expiry / Traffic limit / IP limit | No limit for initial testing, unless you intentionally require one |

`encryption=none` is the VLESS payload setting; the connection is still protected by REALITY. It does not mean the VPN is sent as plaintext.

Click **Create** / **Save**, then apply or restart Xray if the panel prompts for it. This can interrupt existing VPN sessions briefly.

![3x-ui client row: expand the inbound and open Info or Share](../images/3x-ui-client-info.svg)

## 5. Export the connection

The **connection profile** is a private link containing the account’s connection settings. You will import it into **Hiddify**, the VPN app on your device.

1. In **Inbounds**, expand the inbound’s client list if needed.
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

**Check:** Xray owns the intended public listener, the client is enabled, and the exported link matches it.

For an IPv4 exit address, use the separate [ForceIPv4 guide](force-ipv4.md). For failed handshakes, follow [troubleshooting](troubleshooting.md).

## Versioned references

- [3x-ui 3.8.5 inbound form source](https://github.com/MHSanaei/3x-ui/tree/v3.8.5/frontend/src/pages/inbounds)
- [Xray REALITY configuration](https://xtls.github.io/en/config/transport.html#realityobject)
- [RAW/TCP transport](https://xtls.github.io/en/config/transports/raw.html)

**Step 3 is complete when:** you have an enabled account, its private connection link, and a listening server port.

**[Next step: import the account into Hiddify and connect →](clients.md)**
