[← Connect your device](clients.md) · [Choose a symptom](troubleshooting.md)

# Hiddify checks and recovery

Use this page only if a connection fails, if you need to test Hiddify while another VPN stays connected, or if you are migrating an older client. A working connection doesn’t need these changes. Pick the relevant section; don’t apply every option.

## Check the profile's handshake mode

The adjusted links from the setup steps and script output already include this choice. Use the check below only when you need to confirm a different imported link or investigate a failed connection.

For the tested phone setup in this guide, the server runs **Xray 26.7.28** and the link includes **`keyshare=classical`**. This selects how the app starts the encrypted connection. The scripts already add it; the [manual account instructions](server-inbound.md#5-export-the-connection) show how to add it yourself.

Here, “server version” means the server **Hiddify connects to**: the only server for one-server mode, or Moscow for two-server mode. The foreign relay’s version is a separate choice. If Hiddify’s entry server runs **26.9.9**, don’t add that option: it requires the newer hybrid mode instead. If someone supplied your connection, keep their settings or ask them to confirm the server version. [Why the versions matter](handshakes-and-versions.md)


Open **Profiles → your profile’s ⋯ → Edit → Config Editor → Text**. Find **tls → reality**. For a classical profile, it should contain `"key_share": "classical"`. Keep a copy of the original link before editing anything. Close the editor without changes if you only wanted to check.



## Optional DNS check: IPv4 only

**Optional DNS check for a failed connection.** DNS looks up the internet address for a website name. This setting briefly helped an earlier Android test, but the problem returned. Use it when investigating a timeout, rather than changing it on a working connection.

1. Disconnect in Hiddify.
2. Open **Settings → DNS → Outbound domain strategy**.
3. Select **IPv4 only**, save if asked, and reconnect.
4. Repeat the website check. If it doesn’t help, restore your previous value.

This setting is on your device. The similarly named setting in the server dashboard controls the server’s connections to websites. They are separate. For Wi-Fi working while mobile data fails, start with [the mobile checks](troubleshooting.md#wi-fi-works-but-mobile-data-hangs).


## If the connection fails: try these settings

**Use this only if the connection fails.** The options below are additional troubleshooting choices from the earlier Windows investigation. Try one at a time, reconnect, and repeat the browser check. For the investigated REALITY timeout, check [the client fingerprint](troubleshooting.md#reality-chrome-times-out-but-safari-works) before changing more unrelated settings.

| Open | Set |
|---|---|
| **Settings → DNS** | **Fake DNS → Off** |
| **Settings → Routing**, region selector at the top | **Region → Other** |
| **Settings → Routing → ⋯** | **IPv6 routing → IPv4 only** |

DNS turns website names into IP addresses. **Fake DNS** is an extra feature that substitutes artificial addresses; leave it off for this setup. **Other** avoids adding country-based rules that can send some requests outside your VPN. **IPv4 only** simplifies the address types used on your device. The server can still choose an IPv6 exit; changing that is [an optional server setting](force-ipv4.md).

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

**Windows-only fallback. Skip if the connection works.** First check the connection link and [server compatibility](handshakes-and-versions.md#match-the-client-option-to-the-server). The preference changes below were made together during an earlier Windows investigation; they were not isolated as the cause and are not a confirmed fix for mobile connections.

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
