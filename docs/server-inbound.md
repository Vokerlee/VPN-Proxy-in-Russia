[← One-server walkthrough](single-server.md) · Step 3 of 4

# Make a connection link for your phone and computer

By the end of this page, you’ll have two private links: one for your phone and one for your computer. Later you’ll add each link to **Hiddify**, the app that connects your devices.

You’ll work in **3x-ui**, the browser dashboard on your server. If you haven’t installed it yet, [do that first](server-setup.md). Have its browser address, panel login and chosen VPN port ready. The example here uses **8443**; use **443** if that’s the free port you chose.

The panel calls a connection entry point an **inbound**. We’ll make one inbound and put two device accounts on it. Both devices use the same server port, but each gets its own credentials.

The instructions match **3x-ui 3.8.5**. On the previous page, you installed the program that carries the VPN connection, called **Xray**. For this one-server phone setup, its status should show **26.7.28** and **Running**. If you haven’t done that step yet, [install the matching version first](server-setup.md#install-the-vpn-program-version-used-in-this-guide)

**Using two servers? Create phone and desktop accounts on Moscow only. The foreign server gets a separate relay account for Moscow. Follow [the two-server panel steps](two-hop-vpn.md#how-the-two-3x-ui-panels-connect). That page gives different settings for the device connection and the connection between servers. This page explains the single-server form.

**Follow steps 1–5 to create the connection.** The sections labelled **Optional** are for another transport or for diagnosing a failed startup; skip them for your first setup.

## 1. Open the correct form

1. Open the dashboard using the browser address from [Step 2](server-setup.md#open-the-dashboard-in-your-browser). Use `http://YOUR_SERVER_IP:YOUR_PANEL_PORT/YOUR_PANEL_PATH/` with your saved values. Sign in with the panel credentials.
2. In the main left sidebar, click **Inbounds**.
3. Click **Add Inbound**. On a narrow screen, open the sidebar with the menu button first.

## 2. Set the listener

The **listener** waits for devices to connect on the selected port. Use **443 or 8443 only**, as chosen in the previous page; allow that same TCP port in the server firewall and any provider firewall.

| Field | Set it to | Check |
|---|---|---|
| Enable | On | The inbound must remain enabled |
| Remark | A recognizable name, such as `Personal VPN` | This is a display name |
| Protocol | `vless` | The imported client must also use VLESS |
| Listen IP | Empty/default, or the intended public listener address | Do not set it to `127.0.0.1` for a public listener |
| Port | `8443`, if free | Use the selected port in the client and both firewalls |

Do not replace a working listener just to match the examples. Preserve its actual port and connection parameters.

## 3. Set transport and security

| Field | Set it to | Why |
|---|---|---|
| Transmission / Network | `TCP` or `RAW` | Newer Xray names TCP transport RAW; `tcp` remains an alias in relevant releases |
| Security | **REALITY** | Protects the connection between your device and this server |
| Proxy Protocol | Off | Enable only when an upstream proxy actually sends PROXY headers |
| Target / Dest | `www.apple.com:443` | A website used during REALITY connection setup; it must be reachable from this server |
| Server Names / SNI | `www.apple.com` for that example | SNI is the website name sent during connection setup; use one covered by the target’s certificate |
| Fingerprint / uTLS, when offered | `safari` | Shapes the app’s opening connection message; this value worked in our tests |
| Short IDs | Generate a short ID | A short random label used to recognize this connection; keep the exported value |
| Private / Public Key | Click **Get New Key** for a new inbound | Keep the private key on the server |
| SpiderX, when offered | `/` | Keep the exported value |
| Sniffing | Off for the initial setup | Inspects initial traffic to identify its destination; unnecessary for this simple setup |

These names are settings to copy, not topics you need to learn before continuing. Keep **Target** and **SNI** paired as shown. **Safari** here describes the app’s first connection message; it doesn’t install or open the Safari browser.

For an existing inbound, keep its keys and short IDs. Generating new ones would stop its existing device links from working. For a new inbound, generate them once and let the exported links carry the right values.

<details>
<summary>Optional: check whether the example target website is reachable. Use this if connections fail.</summary>

**TLS** is the encryption used by HTTPS websites. The REALITY target must provide suitable TLS and be reachable from your rented server (VPS). On that server, test the example target:

```bash
curl -4 -I --connect-timeout 5 --max-time 15 https://www.apple.com/
```

You should receive HTTP response headers rather than a timeout or connection error. The target must support TLS 1.3 and HTTP/2; see the [official REALITY requirements](https://github.com/XTLS/REALITY/blob/main/README.en.md). This checks website reachability; the device test in Step 4 will check the actual VPN connection.

</details>

## 4. Set the client account

Some forms reveal Flow only after selecting REALITY.

| Client field | Set it to |
|---|---|
| Enable | On |
| Email / Name | `desktop` for the first account, or a name you choose; this is a label, not an email address |
| ID / UUID | Keep the generated value for a new account; keep the original value when editing an existing account |
| Flow | `xtls-rprx-vision` |
| Encryption | `none`, where shown |
| Expiry / Traffic limit / IP limit | No limit for initial testing, unless you intentionally require one |

`encryption=none` is the VLESS payload setting; the connection is still protected by REALITY. It does not mean the VPN is sent as plaintext.

**desktop** and **phone** are example names, not required keywords. You can choose your own labels to recognize the accounts. Each account gets its own connection link.

Create a second client named **phone** (or your chosen second name), with a different generated UUID and the same **Vision** flow. Use the form’s add-client action if it allows several rows. Otherwise save the inbound, reopen its client list and add the second account there. A UUID is the generated account identifier; don’t reuse the desktop value for the phone.

Click **Create** / **Save**, then apply or restart Xray if prompted. This can briefly interrupt existing VPN connections. You should now see one enabled inbound with **desktop** and **phone** accounts, and Xray should show as running.

## 5. Export the connection

The **connection profile** is a private link containing the account’s connection settings. You will import it into **Hiddify**, the VPN app on your device.

1. In **Inbounds**, expand the inbound’s client list if needed.
2. Find the intended client row.
3. Open its **Info / connection details** action, or the QR/share action. Depending on the layout, actions may be in **⋯**.
4. Copy the **VLESS URL** for that account.
5. Paste the copied link into a text editor and save a private copy of the original. For the **26.7.28** preset, find the `#` before its display name and insert **`&keyshare=classical`** immediately before it. This asks Hiddify to use the tested connection setup. If `keyshare=` already exists, change its value instead of adding it again.
6. Copy the adjusted whole line for Hiddify. Repeat with the other device’s account and keep the two links separately named.

For example, the end of the link changes from `…&spx=%2F#Personal-VPN-phone` to `…&spx=%2F&keyshare=classical#Personal-VPN-phone`. Keep everything else unchanged. Don’t add this option to a **26.9.9** entry server; [that version needs hybrid mode](handshakes-and-versions.md#match-the-client-option-to-the-server).

The panel’s QR code may contain the original link without this adjustment. Use the adjusted text link for this first connection.

A placeholder link looks like this; import the panel's real export rather than copying this example:

```text
vless://YOUR_UUID@YOUR_SERVER_IP:8443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=www.apple.com&fp=safari&pbk=YOUR_PUBLIC_KEY&sid=YOUR_SHORT_ID&type=tcp&spx=%2F&keyshare=classical#Personal-VPN-phone
```

Copy the whole link. Its account ID and key values are easy to damage by retyping; you only need to add the classical option shown above.

For a desktop and phone, use two separately named client accounts, `desktop` and `phone`, on this same inbound. Export each account's own link; each device keeps its own credentials and can be revoked separately. Both accounts can use the same listener. When replacing a test account, verify the new accounts before removing the test account from the inbound and central client list.

## Optional XHTTP instead of RAW

Choose **XHTTP** in the transport field, set **Path** to `/vpn`, choose server mode **auto**, and keep **REALITY** as security. The XHTTP account's **Flow** is empty. Export and import the new XHTTP link; it contains a different transport and path. For this guide's RAW accounts, keep Vision flow. This entry variant is available in the helper and needs an end-to-end test on the intended network.

## 6. Optional: check the server listener from the terminal

**Skip if the saved inbound is enabled and Xray shows as running in the panel.** If it fails to start, the commands below help explain why.

<details>
<summary>Open the terminal listener and log checks</summary>

On the VPS, replacing `8443` with the actual inbound port:

```bash
ss -lntp 'sport = :8443'
journalctl -u x-ui --since '10 minutes ago' --no-pager
```

**Check:** Xray owns the intended public listener, the client is enabled, and the exported link matches it.

</details>

For an IPv4 exit address, use the separate [ForceIPv4 guide](force-ipv4.md). For failed handshakes, follow [troubleshooting](troubleshooting.md).

## Versioned references

- [3x-ui 3.8.5 inbound form source](https://github.com/MHSanaei/3x-ui/tree/v3.8.5/frontend/src/pages/inbounds)
- [Xray REALITY configuration](https://xtls.github.io/en/config/transport.html#realityobject)
- [RAW/TCP transport](https://xtls.github.io/en/config/transports/raw.html)

**Step 3 is complete when:** your inbound and account are enabled, Xray is running, and you have copied the private connection link.

**[Next step: import the account into Hiddify and connect →](clients.md)**
