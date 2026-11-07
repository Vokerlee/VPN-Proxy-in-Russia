[← Setup overview](../README.md) · Step 4 of 4

# Connect your computer or phone

**Hiddify** is the app you install on your device to connect to your VPN server. A **connection profile** is the private `vless://...` link containing the server address and your account settings. Get that link from **3x-ui**, the server’s browser dashboard, or from the person who manages your VPN.

**Follow sections 1–4:** install, import, set the outbound domain strategy, and connect. Everything after **Your first connection is complete** is optional troubleshooting. Button labels below are from Hiddify **5.5.5**.

## 1. Install Hiddify

Download it using the links on the [official installation page](https://hiddify.com/app/How-to-install-Hiddify-app/) or the [official releases page](https://github.com/hiddify/hiddify-app/releases/latest). Choose the download for your device: Windows, Linux, macOS, Android, or iOS.

On Windows, install the Windows app. You do not need WSL (Windows Subsystem for Linux, an optional environment for running Linux programs inside Windows).

## 2. Import your connection link

1. Copy the whole `vless://...` link from [your account in 3x-ui](server-inbound.md#5-export-the-connection).
2. Open Hiddify and click **+ / New profile → Add from clipboard**.
3. Select the imported profile, for example **Personal VPN**.

On a phone, you can scan the account’s QR code instead of copying the link. Both contain the same connection settings. Keep the link and QR code private: anyone with them can use that account. The dashboard’s browser address is a different link and cannot be imported as a VPN profile.

**For a US REALITY server, use the Safari fingerprint in this walkthrough.** Before importing, check the link for **`fp=safari`**. If it has `fp=chrome` and you have the investigated timeout symptom, follow [the panel's Safari steps](server-inbound.md#3-set-transport-and-security) and import the new export. The Kansas comparison kept the Google SNI unchanged and succeeded with Safari in 12/12 requests while Chrome failed in 12/12. This was verified with the installed Hiddify 5.5.5 engine; other engines and networks need their own check.

![Hiddify: New profile, Add from clipboard, select Personal VPN](../images/hiddify-import.svg)

## 3. Important: set Outbound domain strategy to IPv4 only

**This was initially reported as an Android fix on 2026-11-07, but the failure later returned.** Keep this DNS check, but do not treat it as a proven cure for every timeout. For the investigated US REALITY connection, also check [Chrome versus Safari](troubleshooting.md#us-reality-server-chrome-times-out-but-safari-works).

1. In **Hiddify**, disconnect if connected.
2. Open **Settings → DNS**.
3. Tap **Outbound domain strategy**.
4. Select **IPv4 only**. Save or confirm if the app asks.
5. Return to the home screen and reconnect, then check a website as shown below.

**Choose this exact field.** It is on Hiddify’s **DNS** page. **Routing → IPv6 routing** is a different control, and the server’s **3x-ui → Outbounds → ForceIPv4** is a separate setting. Changing either of those does not replace this step.

![Hiddify buttons: Settings, DNS, Outbound domain strategy, IPv4 only, reconnect](../images/hiddify-outbound-ipv4.svg)

DNS turns names into IP addresses. This option makes Hiddify use IPv4 results for its outbound/direct name lookups. Choose **IPv4 only**, rather than **Prefer IPv4**, for the setup described here.

If you followed the earlier advice to change Fake DNS, Region, or the hidden Windows preferences and the phone still failed, check **Outbound domain strategy** before editing anything else. No Android system-file editing or Windows repair script is needed for this setting.

## 4. Connect and check a website

**Already using another VPN?** To check Hiddify while keeping that connection untouched, use the [optional manual proxy test](#press-connect-then-prove-the-route) below instead of activating another VPN/TUN connection.

1. **On a desktop**, open **Settings → Inbound → Service mode** and select **VPN / TUN**. This is the mode for using the VPN with your normal applications; TUN is its virtual network connection. On a phone, use the normal VPN mode.
2. Return to the home screen, select your profile, and press **Connect**.
3. Accept the operating system’s VPN or administrator permission request.
4. Open `https://www.cloudflare.com/cdn-cgi/trace` in your browser. Find the line starting with **`ip=`**. It should show your server’s outgoing address, rather than your ordinary internet address.
5. Open a website you wanted to use through the VPN.

If the address is unfamiliar, open the same test URL with Hiddify disconnected and compare. A server may have a different outgoing address from its login address, particularly when it also has IPv6. If the browser cannot load the page or still shows your ordinary address, first recheck [Outbound domain strategy → IPv4 only](#3-important-set-outbound-domain-strategy-to-ipv4-only), reconnect, and then use [the additional checks](#if-the-connection-fails-try-these-settings) if needed.

![Hiddify: Connect, grant VPN permission, open an IP-check page](../images/hiddify-connect.svg)

## Your first connection is complete

**You can stop here when the address check and your websites work.** You do not need to edit hidden preferences, compare network engines, or run a script.

The sections below are optional. Use them only for a failed connection or when switching from an older client.

## If the connection fails: try these settings

**Optional: skip if the connection works.** The options below are additional troubleshooting choices from the earlier Windows investigation. Try one at a time, reconnect, and repeat the browser check. For the investigated US REALITY timeout, check [the client fingerprint](troubleshooting.md#us-reality-server-chrome-times-out-but-safari-works) before changing more unrelated settings.

| Open | Set |
|---|---|
| **Settings → DNS** | **Fake DNS → Off** |
| **Settings → Routing**, region selector at the top | **Region → Other** |
| **Settings → Routing → ⋯** | **IPv6 routing → IPv4 only** |

DNS turns website names into IP addresses. **Fake DNS** is an extra feature that substitutes artificial addresses; leave it off for this setup. **Other** avoids adding country-based rules that can send some requests outside your VPN. **IPv4 only** simplifies the address types used on your device. The server can still choose an IPv6 exit; changing that is [an optional server setting](force-ipv4.md).

![Hiddify: Fake DNS off, Region Other, IPv4 only](../images/hiddify-settings.svg)

## Press Connect, then prove the route

**Optional diagnostic test for desktop users. Skip if the normal connection works.** This test asks Hiddify directly to load a webpage, which helps when a browser is using another app’s proxy. A **local proxy** is a program on your computer that forwards requests for other programs.

1. In Hiddify, select **Settings → Inbound → Service mode → Proxy** (manual).
2. Under **Settings → Inbound → Local proxy**, keep the mixed/local port enabled at **12334**, or choose a different unused port if necessary. A port is the number an application uses to reach that proxy.
3. Click **Connect**. This mode starts Hiddify’s proxy without changing the operating system’s proxy selection. It does not stop another VPN app.
4. Run the command for your computer, substituting your port if you changed it.

**Windows — PowerShell:**

```powershell
curl.exe --noproxy localhost,127.0.0.1 --proxy http://127.0.0.1:12334 --connect-timeout 5 --max-time 15 https://www.cloudflare.com/cdn-cgi/trace
```

**Linux/macOS — terminal:**

```bash
curl --noproxy '' --proxy http://127.0.0.1:12334 --connect-timeout 5 --max-time 15 https://www.cloudflare.com/cdn-cgi/trace
```

**curl** is a command-line webpage downloader. These commands explicitly use Hiddify at `127.0.0.1` (your own computer), so they test its proxy rather than the browser’s proxy choice. Find `ip=` in the response.

If the command works but the browser fails, check [which proxy the browser uses](ports-and-modes.md#windows-selects-a-proxy-it-does-not-merge-them). If the command fails too, save its error and follow [troubleshooting](troubleshooting.md). The [ports and modes guide](ports-and-modes.md) explains the other modes when you need them.

## Advanced recovery when the normal settings are not enough

**Windows-only fallback. Skip if the connection works.** First check [Hiddify’s outbound domain strategy](#3-important-set-outbound-domain-strategy-to-ipv4-only). The preference changes below were made together during an earlier Windows investigation; they were not isolated as the cause and are not needed to apply the Android fix.

Hiddify uses a network engine, also called a **core**, to make connections. Some of that engine’s settings are saved in a file rather than shown as switches in Hiddify 5.5.5. The **Clash API** lets other software control or monitor the engine; an **independent DNS cache** stores name-lookup results separately for different resolvers. Both were disabled during the earlier Windows recovery. In particular, its General page has a **Clash API port** field but no corresponding enable/disable toggle, and independent DNS cache is not a visible switch on its DNS page. Do not waste time looking for those controls.

The earlier Windows recovery used these saved preferences:

```json
{
  "flutter.enable-clash-api": false,
  "flutter.independent-dns-cache": false,
  "flutter.region": "other",
  "flutter.enable-fake-dns": false,
  "flutter.service-mode": "proxy"
}
```

Use [the repair helper](automation.md#repair-hiddify-preferences-on-windows) to preview and, if needed, apply those settings. It requires Hiddify to be closed, backs up its preferences, never stops another VPN app, and leaves Windows’ selected proxy unchanged. A backup is useful because disabling the API can affect API-based monitoring or integrations. Revert if you need those features, then test changes individually.

You can make this advanced recovery change without a script too. On Windows, close Hiddify yourself, press **Win+R**, open `%APPDATA%\Hiddify\hiddify`, and make a private backup copy of `shared_preferences.json`. Open the original with a text editor. Merge the five entries shown above into the existing file; keep all unrelated entries. The three `false` values have no quotes; `"other"` and `"proxy"` are strings and need quotes. Keep valid JSON commas between entries. Do not replace the entire preferences file with this small example. Save it, reopen Hiddify, reconnect, and test. If the file no longer parses or the change does not help, close Hiddify and restore your backup.

The initial Android improvement after **Outbound domain strategy → IPv4 only** did not last. Keep visible DNS and fingerprint checks separate from these Windows-only file edits; the later controlled fingerprint comparison isolated Chrome versus Safari on the tested connection. The helper is an optional way to avoid manual JSON mistakes.

The effective file under `%APPDATA%\Hiddify\hiddify\data\current-config.json` is diagnostic output, not the persistent place to make this repair. Hiddify regenerates it.

## Switching from Invisible Man - XRay Client

**Optional: read this only if you already use Invisible Man - XRay Client.** New Hiddify users can skip this section.

[**Invisible Man - XRay Client**](https://github.com/InvisibleManVPN/InvisibleMan-XRayClient) is a Windows VPN/proxy app used in the original guide. It provides a graphical interface around **Xray-core**, the software that makes the network connections. Hiddify is the alternative app used in this updated walkthrough; you do not need to install both.

As checked on **2026-11-06**, the project’s latest published release was **3.2.5**, dated **2025-02-02**, and bundled Xray **25.1.30**. That bundled engine failed against the newer server in the comparison below, so this guide uses Hiddify for new connections. If your existing installation works, you can keep it; test Hiddify separately before switching.

The connection tests recorded for this guide used the same account link, server, and internet provider:

| Test | Result |
|---|---|
| Xray client **25.1.30** → Xray server **26.9.9** | `REALITY: processed invalid connection` |
| Xray client **26.10.31** → the same server | Authenticated HTTPS requests succeeded |
| Hiddify **5.5.5**, Windows native core, simple profile | Authenticated HTTPS requests succeeded |
| Hiddify **5.5.5**, repaired app settings above | App's real local proxy succeeded |

Copying the link again cannot update the bundled network engine. After upgrading a client, run the webpage test above to check that the new version connects to your server.

**Optional engine detail:** Hiddify’s own network engine is based on **sing-box**, another proxy engine. The checked 5.5.5 core reported `hiddify-sing-box 1.15.0-alpha.13`; its build also linked Xray 26.10.31. Those build facts do not mean it forwards traffic through Xray. Hiddify's build may include Xray libraries for parsing or conversion. In the checked 5.5.5 build, the Xray traffic backend was unimplemented and the global “use Xray” option was disabled in app code. We therefore repaired its native engine's configuration. Do not follow advice to flip a nonexistent engine selector or replace a DLL with `xray.exe`.

The [technical compatibility discussion](xray-internals.md#why-a-valid-profile-can-stop-working-after-an-update) explains why newer REALITY servers can reject older client handshakes. If you specifically need a graphical app that runs standalone Xray, [v2rayN](https://github.com/2dust/v2rayN/releases/latest) is another option; verify its actual core version and test the tunnel.

## Keep a record that helps the next investigation

Write down panel version, server Xray version, client app version, client core version, and the last successful test date. A short note such as “Hiddify 5.5.5; manual proxy 12334; HTTPS exit check matched the server” is more useful than a screenshot of a green button alone. Keep the private connection link and passwords out of that note.

## References

- [Invisible Man - XRay Client 3.2.5 release](https://github.com/InvisibleManVPN/InvisibleMan-XRayClient/releases/tag/v3.2.5)
- [Hiddify 5.5.5 settings screens](https://github.com/hiddify/hiddify-app/tree/v5.5.5/lib/features/settings/overview/sections)
- [Hiddify 5.5.5 configuration preferences](https://github.com/hiddify/hiddify-app/blob/v5.5.5/lib/features/settings/data/config_option_repository.dart)
- [Checked Hiddify core's Xray backend](https://github.com/hiddify/hiddify-sing-box/blob/1614c5edb52dd44a4cc079201ba1e790fdfad8a0/protocol/hiddify/xray/outbound.go)
- [Upstream REALITY compatibility report](https://github.com/SagerNet/sing-box/issues/4520)
