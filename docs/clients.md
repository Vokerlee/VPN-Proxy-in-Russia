[← Guide index](../README.md)

# Connect your devices

# Part 2 — Connecting Your Phone or PC

Use a GUI app to connect directly to your VLESS + XTLS-Reality server. No separate proxy setup is needed — just import the connection URL and click connect.

You need the connection URL (or individual values: server IP, UUID, public key, short ID) from Part 1.

> Once connected, no further configuration is required — your VPN is fully set up and ready to use.

---

## Windows — Invisible Man XRay

**GitHub:** [https://github.com/InvisibleManVPN/InvisibleMan-XRayClient](https://github.com/InvisibleManVPN/InvisibleMan-XRayClient)

1. Download the latest release from [GitHub Releases](https://github.com/InvisibleManVPN/InvisibleMan-XRayClient/releases) and extract the archive
2. Launch the app and click **Manage server configuration**
3. Click **+** (plus button in the bottom-right corner)
4. Select **Import from link** and paste the `vless://...` URL from 3X-UI (see [Copy Your Connection URL](server-inbound.md#copy-your-connection-url))
5. Close the configuration manager and click **RUN**
6. The status should change from "Stopped" to "Connected"

## macOS — FoXray

**App Store:** [FoXray](https://apps.apple.com/app/foxray/id6448898396)

1. Download FoXray from the App Store
2. In 3X-UI, click the Info icon next to your client and copy the connection URL
3. In FoXray, click the **clipboard/paste** icon to import the URL
4. Press **Play** and allow the VPN configuration when prompted

## iOS — FoXray

**App Store:** [FoXray](https://apps.apple.com/app/foxray/id6448898396) (requires iOS 16+)

1. Download FoXray from the App Store
2. In 3X-UI, click the QR code icon next to your client
3. In FoXray, tap the **QR scan** icon (top-left corner) and scan the code
4. Tap **Play**, allow the VPN configuration, and enter your device passcode

## Android — Hiddify

**Google Play / GitHub:** [Hiddify](https://github.com/hiddify/hiddify-app)

1. Install Hiddify from [Google Play](https://play.google.com/store/apps/details?id=app.hiddify.com) or download the APK from [GitHub Releases](https://github.com/hiddify/hiddify-app/releases)
2. Launch the app and tap **+** (top-right corner)
3. Select **Add from QR code** and scan the QR code from 3X-UI (see [Copy Your Connection URL](server-inbound.md#copy-your-connection-url)), or choose **Add from clipboard** and paste the `vless://...` URL
4. The new profile should appear in the list
5. Tap the toggle on the profile to connect and confirm the VPN connection request

> **Troubleshooting — Google services unreachable:** If Google or other services remain inaccessible after connecting, try enabling **Fake DNS** in Hiddify settings. Fake DNS is a technique where the VPN intercepts all DNS queries and returns a synthetic (fake) IP address for every domain — the app then maps that fake IP back to the real hostname when establishing the connection through the tunnel. This prevents DNS leaks and ensures that apps which resolve domain names before the VPN is fully active still get routed correctly. To enable it: open Hiddify → **Settings** → **Advanced** → turn on **Fake DNS**.

> **Note:** NekoBox for Android ([MatsuriDayo/NekoBoxForAndroid](https://github.com/MatsuriDayo/NekoBoxForAndroid)) is no longer actively maintained and may be broken — Hiddify is the recommended alternative.
>
> The key difference is the underlying core engine: NekoBox runs on **Xray core** (the same engine that 3X-UI uses on the server), while Hiddify is powered by **sing-box** — a separate open-source project with a different codebase but overlapping protocol support. In practice, both handle VLESS+XTLS-Reality connections just fine. The distinction matters mainly when troubleshooting: if the server-side Xray config uses a feature or a parameter that sing-box interprets slightly differently, behavior may diverge. Since 3X-UI generates a standard `vless://` URI, this is rarely an issue for typical setups.

---

[← Guide index](../README.md)
