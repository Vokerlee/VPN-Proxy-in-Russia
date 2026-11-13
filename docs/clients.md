[← Choose a setup](../README.md) · [Create device accounts](server-inbound.md)

# Connect your phone or computer

This is the last part: add your connection to **Hiddify**, the VPN app, and check that it works. If someone has already sent you a VPN link, you can start here. You don’t need access to their server dashboard.

Have your device’s private connection link ready. It starts with `vless://` and contains the server address and account settings. The dashboard’s `http://…` browser address is a different link; Hiddify can’t use that as a VPN connection.

Use the link for your chosen setup:

| Setup | Link to add to Hiddify |
|---|---|
| One server | Your device account on the foreign server (HostVDS in our example) |
| Two servers | Your device account on Moscow (FirstVDS in our example) |

For two servers, the foreign relay link goes into Moscow’s outbound, not Hiddify. If you don’t have a device link yet, [create it on the single foreign server](server-inbound.md) or [finish the two-server setup on Moscow](two-hop-vpn.md#on-moscow-connect-the-device-inbound-to-nl).

The buttons below were checked in **Hiddify 5.5.5**. If you install another version, some labels may differ.

## 1. Install Hiddify

Your server is ready to receive a VPN connection. Now your device needs an app that can make it. We’ll install **Hiddify** on the phone or computer you want to connect; this doesn’t install anything else on the server.

Use [Hiddify’s official downloads](https://github.com/hiddify/hiddify-app/releases). The tests in this guide used **5.5.5**; find that release if you want to reproduce the same setup. A later release needs its own connection check.

- **Android:** open the release on your phone and download its Android APK. Choose Universal if you’re unsure which build to use. Open the download and allow installation from that browser if Android asks. You can switch that permission off afterward.
- **Windows, Linux or Mac:** download the package for your computer and install it. On Windows, you don’t need WSL or any Linux tools.
- **iPhone or iPad:** follow [Hiddify’s iOS installation instructions](https://hiddify.com/app/How-to-install-Hiddify-app/).

Open Hiddify. You should see its home screen, ready for a connection to be added.

## 2. Import your connection link

The link contains your server address and account settings. Importing it saves those settings in Hiddify, so you don’t have to enter its keys and other fields by hand. It adds a connection to the app; it doesn’t turn the VPN on yet.

1. Copy your device’s whole `vless://…` link. The guide’s example account names are **phone** and **desktop**; if you chose other names, use the link for the account you created for this device.
2. In Hiddify, press **+ → Clipboard**. Some versions call it **Add from clipboard**.
3. Select the new connection. Its name can include both the server and device, such as **Personal VPN-phone**.

If you used our one-server scripts, copy the link from **client-phone.txt** or **client-desktop.txt** in the output folder. The two-server scripts call those files **phone.txt** and **desktop.txt**. If someone manages the server for you, ask them for your device’s link.

You can scan a QR code instead if it was made from that same link. Keep links and QR codes private: they let someone use the account.

## 3. Choose how your apps use the VPN

Hiddify knows how to reach the server now. We also need your browser and other apps to use that connection. We’ll use VPN mode so you don’t have to configure each app separately.

On a **phone**, use the normal VPN connection. Hiddify will ask for the phone’s VPN permission when you connect.

On a **computer**, open **Settings → Inbound → Service mode** and choose **VPN / TUN**. That lets ordinary apps use the connection without each needing its own proxy settings. TUN is the virtual network connection the app creates.

If another VPN is already running and you need to keep it connected, use [the separate proxy test](hiddify-troubleshooting.md#press-connect-then-prove-the-route) instead of switching on a second VPN mode. Otherwise, return to Hiddify’s home screen.

## 4. Connect and check a website

Now we’ll start the connection and check that a website actually goes through your server. The app’s connected indicator alone can’t confirm which route your browser used; the address check and a working website give us that result.

1. Select your connection and press **Connect**.
2. Accept the VPN or administrator permission prompt if shown.
3. Open [the address check](https://www.cloudflare.com/cdn-cgi/trace) in your browser. Look for **`ip=`**. It should show the address your server uses to reach websites. For two servers, that’s the foreign server’s address.
4. Open a website you wanted to use through the VPN.
5. On your phone, repeat with Wi-Fi switched off so you test mobile data too.

If you don’t know which address to expect, ask the person managing the server or compare with a check made on the server. The outgoing address can differ from the login address, especially with IPv6. Seeing any different address isn’t enough if another VPN is still connected.

## Your first connection is complete

If your websites open and the address check matches, you’re done. Use **Disconnect** when you want to stop using this connection. You can close the server’s dashboard; it doesn’t need to stay open.

If a check fails, start with [the troubleshooting table](troubleshooting.md#first-choose-the-symptom-that-matches-yours). The separate [Hiddify recovery page](hiddify-troubleshooting.md) has app-specific checks when you need them.
