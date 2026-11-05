[← Guide index](../README.md)

# Create a VLESS + REALITY inbound

## Create a VPN Client in 3X-UI

### Open the Web Panel

Open in your browser:

```
https://YOUR_SERVER_IP:YOUR_PORT/YOUR_PATH/
```

> The port and URL path were set during installation — see [Set Credentials and Panel URL](server-setup.md#set-credentials-and-panel-url) if you need to look them up again.

Log in with the username and password you created (or the random ones generated during installation).

### Add a New Inbound

1. Go to **Inbounds**
2. Click **Add Inbound**

![3X-UI — Add Inbound button](../images/3x-ui-add-inbound.png)

### Fill In the Settings

**General settings:**

| Setting | Value |
|---------|-------|
| Remark | Any name (e.g., `VLESS XTLS-Reality`) |
| Protocol | `vless` |
| Listen IP | Leave empty |
| Port | `443` |

**Client settings:**

| Setting | Value |
|---------|-------|
| Email | Any client name (e.g., `SOME_USER_NAME`) |
| ID | Auto-generated UUID |
| Flow | `xtls-rprx-vision` (appears after selecting Reality in transport) |
| Encryption | `none` |

**Transport settings:**

| Setting | Value |
|---------|-------|
| Transmission Protocol | `TCP` |
| Proxy Protocol | OFF |
| Security | Select the **Reality** tab |
| uTLS | `chrome` |
| Dest | `google.com:443` |
| Server Names | `google.com, www.google.com` |
| Short IDs | Auto-generated |
| Spider X | `/` |
| Private Key / Public Key | Click **Get New Key** |
| Sniffing | OFF |

![3X-UI — inbound settings with Reality enabled](../images/3x-ui-settings.png)

### Save and Create

Click **Create**. Your VLESS + XTLS-Reality inbound is ready!

> To connect multiple devices, you don't need separate inbounds — just add more clients to the same one. Click the **Edit** icon on the inbound, then add another client entry (e.g., `YET_ANOTHER_USER_NAME`) with its own UUID. Each client gets its own connection URL.

### Copy Your Connection URL

Click the **Info** icon (circle with **i**) in the Menu column next to your client:

![3X-UI — inbound list with client menu icons](../images/3x-ui-get-client-info-1.png)

A details panel will open showing all connection parameters and the connection URL at the bottom:

![3X-UI — client details with connection URL](../images/3x-ui-get-client-info-2.png)

```
vless://UUID@SERVER_IP:443/?type=tcp&security=reality&fp=chrome&pbk=PUBLIC_KEY&sni=google.com&flow=xtls-rprx-vision&sid=SHORT_ID&spx=%2F#NAME
```

Save this URL — you'll need it for client configuration. You can also click the QR code icon to get a scannable code for mobile apps.

---

[← Guide index](../README.md)
