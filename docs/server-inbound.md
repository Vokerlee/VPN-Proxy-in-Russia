[← One-server walkthrough](single-server.md) · Step 3 of 4

# Make a connection link for your phone and computer

By the end of this page, you’ll have two private links: one for your phone and one for your computer. Later you’ll add each link to **Hiddify**, the app that connects your devices.

You’ll work in **3x-ui**, the browser dashboard on your server. If you haven’t installed it yet, [do that first](server-setup.md). Have its browser address and panel login ready. We’ll choose the VPN port while filling in the connection form below.

The panel calls a connection entry point an **inbound**. We’ll make one inbound and put two device accounts on it. Both devices use the same server port, but each gets its own credentials.

The instructions match **3x-ui 3.8.5**. On the previous page, you installed the program that carries the VPN connection, called **Xray**. For this one-server phone setup, its status should show **26.7.28** and **Running**. If you haven’t done that step yet, [install the matching version first](server-setup.md#install-the-vpn-program-version-used-in-this-guide)

**Using two servers?** Create phone and desktop accounts on Moscow only. The foreign server gets a separate relay account for Moscow. Follow [the two-server panel steps](two-hop-vpn.md#how-the-two-3x-ui-panels-connect). That page gives different settings for the device connection and the connection between servers. This page explains the single-server form.

**Follow steps 1–5 to create the connection.** The XHTTP section after the next-step link is an optional experiment; skip it for your first setup.

## 1. Open the correct form

The dashboard is ready, but it doesn’t yet have an entry for your devices to connect to. We’ll open the form that creates that entry, called an **inbound**.

1. Open the dashboard using the browser address from [Step 2](server-setup.md#open-the-dashboard-in-your-browser). Use `http://YOUR_SERVER_IP:YOUR_PANEL_PORT/YOUR_PANEL_PATH/` with your saved values. Sign in with the panel credentials.
2. In the main left sidebar, click **Inbounds**.
3. Click **Add Inbound**. On a narrow screen, open the sidebar with the menu button first.

## 2. Set the listener

The **Port** is the number where your device’s VPN connection arrives. It is separate from the browser dashboard’s port. Use **8443** here; **443** works too. HTTPS websites normally use 443, and 8443 is a common HTTPS alternative. Both suit this connection’s browser-like opening, but the port number alone doesn’t disguise a VPN.

In the **Basics** tab, fill in:

| Field | Enter |
|---|---|
| **Enable** | Off for now; we’ll turn it on after adding the accounts |
| **Remark** | `Personal VPN` |
| **Protocol** | `vless` |
| **Address** | Your server’s public IPv4 address |
| **Port** | `8443` |
| **Share address strategy** | `Custom` |
| **Custom share address** | The same public IPv4 address, without `http://` or a port |
| **Disable XTLS flow** | Off |

**Address** controls where the server accepts connections. **Custom share address** puts the right server address into your device links. The flow switch stays off because we’ll use Vision, a connection setting selected on each account below.

Leave the form open. We still need its transport and security settings.

## 3. Set transport and security

A **transport** is how the VPN carries your traffic. **RAW**, previously called TCP, carries it directly over a TCP connection. **XHTTP** packages it into HTTP requests and streams instead. Both can use the same encrypted protection. XHTTP isn’t automatically harder to block; it changes the traffic pattern and needs a matching client profile.

For this first device connection, use **RAW**: it is the phone setup tested in this guide. We’ll protect it using **REALITY**, which makes the initial connection resemble a secure website connection and lets your app recognize your server.

1. In the form, click **Stream** and set **Network** to **RAW** (TCP in some versions).
2. Click **Security** and select **REALITY**.
3. Enter these settings:

| Field | Enter | What it does |
|---|---|---|
| **Target** | `www.apple.com:443` | Website used during connection setup |
| **SNI** | `www.apple.com` | Website name sent in the opening message; keep it paired with Target |
| **uTLS** | `safari` | Makes the app’s opening message resemble Safari’s; Safari needn’t be installed |

The target doesn’t decide which websites you can visit. It is used to set up the protected connection.

4. Click **Get New Cert** below the key fields. In 3x-ui 3.8.5 this generates the REALITY keys; you don’t need to buy a certificate or domain. **Public Key** and **Private Key** should fill in.
5. Keep the generated **Short IDs**. If empty, use the circular regenerate button beside that field.
6. Leave the other settings unchanged and click **Create**.

You should see **Personal VPN** in **Inbounds**, still disabled. Its keys will be included correctly in the exported links. When editing an existing working inbound, keep its keys and short IDs: replacing them would invalidate its existing device links.

## 4. Set the client account

An inbound is the shared entry point; a **client account** gives a device permission to use it. We’ll make two accounts so either device’s access can be removed later without affecting the other.

In this panel version, accounts are created through the separate **Clients** page:

1. In the left sidebar, click **Clients → Add Client**.
2. In **Basics**, enter `desktop` in **Email**. Despite the field’s name, this is just an account label; no email address is needed.
3. In **Attached inbounds**, select **Personal VPN**. This connects the account to the entry you just made.
4. Keep **Enable** on. Leave traffic and IP limits at `0` (unlimited), and expiry unset for this first setup.
5. Open **Credentials**. Keep the generated **UUID**, the account’s unique identifier.
6. Set **Flow** to **xtls-rprx-vision**. Vision is the flow used with this guide’s RAW connection. Select the attached inbound first if Flow isn’t visible.
7. Click **Create**.
8. Repeat **Clients → Add Client** for `phone`, attached to **Personal VPN**, with its own generated UUID and the same Vision flow.

`desktop` and `phone` are names you choose, not device types or required keywords. You could use `alex-laptop` and `alex-mobile`. Each account gets its own private link. You should now see both accounts in **Clients**, attached to **Personal VPN**.

## 5. Export the connection

We’ll turn on the entry and copy each account’s settings as a private **connection link**. This saves typing addresses and keys into Hiddify.

1. Open **Inbounds**, edit **Personal VPN**, and in **Basics** turn **Enable** on.
2. Click **Save Changes**. Accept a restart if prompted. If the panel reports a busy port, use [the port-conflict fix](troubleshooting.md#the-vpn-port-is-already-in-use).
3. Open **Clients** and find `phone`.
4. Click its **ⓘ Client Information** action. Under **Copy URL**, find the VLESS link for **Personal VPN** and click its copy icon. Copy the account link, rather than a subscription or dashboard address.
5. Paste it into a text editor and keep a private copy.

For the **26.7.28** server version installed earlier, we’ll ask Hiddify to use the shorter opening message that worked in our mobile test. Find the `#` before the link’s display name and insert **`&keyshare=classical`** immediately before it. If `keyshare=` already exists, change its value instead of adding it twice.

For example, the end changes from `…&spx=%2F#Personal-VPN-phone` to `…&spx=%2F&keyshare=classical#Personal-VPN-phone`. Keep everything else unchanged. [Why this version and option go together](handshakes-and-versions.md) is explained separately for curious readers.

Copy the adjusted whole line for Hiddify. Repeat with `desktop` and keep the two links separately named. The panel’s QR code can contain the original link without the adjustment, so use the adjusted text link for this first connection.

**This step is complete when:** the inbound and both accounts are enabled, Xray is running, and you have two private adjusted links.

**[Next: import your account into Hiddify and connect →](clients.md)**

## Optional XHTTP instead of RAW

<details>
<summary>Try another transport after the RAW connection works</summary>

Use a separate test inbound and account so your working RAW profiles stay usable. Only one inbound can use a given address and port: if RAW uses 8443, use 443 for this test when it is available.

Follow the form steps above, with these changes:

1. In **Basics**, give the inbound a different remark, use the other available port, and turn **Disable XTLS flow** on.
2. In **Stream**, choose **Network → XHTTP**, **Path → /vpn**, and **Mode → auto**. The path is a shared connection setting, not a folder you need to create.
3. Keep **Security → REALITY** and generate this new inbound’s own keys.
4. Save the inbound, then create a separate account in **Clients**, attached to the test inbound. Leave **Flow** empty/None if shown; XHTTP doesn’t use Vision.
5. Enable the test inbound and export its account link through **Client Information → Copy URL**. Add the same classical option for the selected server version, import it as a new Hiddify profile, and test on Wi-Fi and mobile data.

The new link contains the different transport and path. Your old RAW link cannot connect to an XHTTP-only inbound. Keep whichever complete setup works on your network; a transport change is a test, not a guaranteed fix for blocking.

</details>

## Versioned references

- [3x-ui 3.8.5 inbound form source](https://github.com/MHSanaei/3x-ui/tree/v3.8.5/frontend/src/pages/inbounds)
- [Xray REALITY configuration](https://xtls.github.io/en/config/transport.html#realityobject)
- [RAW/TCP transport](https://xtls.github.io/en/config/transports/raw.html)
