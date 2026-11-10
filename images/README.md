# Images in this guide

The SVGs are original **navigation diagrams and conceptual network schemes**, not captured screenshots. Button diagrams are version-labeled. They show button names and the order of actions rather than claiming pixel-perfect layouts. They contain only placeholder values. The old screenshots were removed from the current tree because their layouts and credential displays no longer made a reliable guide; Git history retains them.

The 3x-ui diagrams describe 3.8.5; Hiddify diagrams describe 5.5.5. Windows shows the Windows 11 navigation path. Source-backed text next to each image explains alternatives when labels move.

## Rebuild the illustrations

```bash
python3 scripts/render_illustrations.py
```

Run that command from the repository root. Only the known generated SVGs in this folder are rewritten. No image-generation service, browser login, or application access is needed.

## Add real screenshots when available

Fresh screenshots can supplement these diagrams. Capture the actual version, keep visible button labels readable, and record the version/date in the caption. Do not pass diagrams off as screenshots.

## 3x-ui screens for the two-hop guide

Capture these screens in 3x-ui **3.8.5**. Keep the page heading, the relevant form fields and the save or copy button in frame. Use a demo account where possible. Suggested filenames below tell you where each image belongs.

| Panel | Open this screen | Keep visible | Suggested file |
|---|---|---|---|
| NL | **Inbounds → Relay nl → Edit** | Remark, Listen IP, port 443 and protocol VLESS | `nl-relay-listener.png` |
| NL | In the same form, scroll to **Transport / Security → REALITY** | TCP or RAW, REALITY, Target, Server Names, fingerprint if shown and the key generation button. Cover key values and short IDs. | `nl-relay-reality.png` |
| NL | **Inbounds → Relay nl → expand clients → relay-nl → Info / Share** | The account row and the Copy button. Cover the entire link and QR code. | `nl-relay-share.png` |
| NL | **Outbounds → direct → Edit** | Tag `direct`, protocol `freedom` and Strategy set to `ForceIPv4` | `nl-ipv4-exit.png` |
| NL | **Routing → edit the rule for the NL relay** | Inbound Tags, Source IP with the Moscow source represented by a placeholder, and Outbound Tag `direct`. Capture the rule list separately if showing the order of the allow and blocked rules. | `nl-relay-source-rule.png` |
| Moscow | **Outbounds → + Outbounds → JSON** | The empty share-link field and its **Import** button. Open the add form first. | `moscow-import-relay.png` |
| Moscow | **Outbounds → relay-nl → Edit → Basic** | Tag, IPv6 address field, port 443, VLESS and Vision flow. Cover the account UUID and any keys. | `moscow-relay-outbound.png` |
| Moscow | **Inbounds → VLESS Moscow NL → Edit** | Remark, the listen address field, port 443, REALITY, Yandex target and Safari fingerprint if shown. A separate crop can show the client’s Vision flow. | `moscow-nl-listener.png` |
| Moscow | **Routing → edit the NL route** | **Inbound Tags** set to the Moscow NL entry and **Outbound Tag** set to `relay-nl`. Include the rule’s position if the list fits in a separate capture. | `moscow-nl-routing.png` |
| Moscow | **Inbounds → VLESS Moscow NL → expand clients → desktop → Info / Share** | The device account row and the Copy button. Cover the entire link and QR code. | `moscow-device-share.png` |

If you are starting with three screenshots, capture **NL relay Share**, **Moscow + Outbounds → JSON**, and **Moscow Routing**. Together they show where the relay link comes from, where it goes, and how device traffic reaches it. Place the NL screenshots under **On NL, create the relay account** and the Moscow screenshots under **On Moscow, connect the device inbound to NL**. [Two-hop panel steps](../docs/two-hop-vpn.md#how-the-two-3x-ui-panels-connect)

## Other useful captures

For the single-server guide, capture **Inbounds → Add Inbound**, the REALITY fields, the client’s Vision flow and the account’s Copy action. For the client guide, capture **Hiddify → + → Clipboard**, the selected profile and the **Connect** button. Capture **Settings → Inbound → Service mode** or **Settings → DNS → Outbound domain strategy** for the corresponding troubleshooting steps.

Redact private keys, UUIDs, whole VLESS links, QR codes, passwords, tokens, subscription URLs, panel URL paths, and account identifiers. Crop the browser address bar and cover sensitive fields with solid opaque redactions. A public key alone is not a private key, but a complete profile still needs protection. Prefer documentation/demo accounts over production data.

Keep originals with credentials out of the repository, including Git history. Genuine new screenshots require a contributor's captures; none were taken from the user's applications during this repository-only update.

`hiddify-outbound-ipv4.svg` illustrates the author’s initial Android DNS check, whose reported improvement later stopped working: **Hiddify → Settings → DNS → Outbound domain strategy → IPv4 only**, then reconnect. Keep this distinct from `3x-ui-force-ipv4.svg`, which changes the server’s website connections. Both are navigation diagrams, not captured screenshots.
