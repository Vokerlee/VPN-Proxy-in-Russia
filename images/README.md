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

The useful capture list is:

1. 3x-ui main sidebar with **Inbounds** and **Outbounds** visible.
2. **Inbounds → Add Inbound**, with VLESS selected.
3. REALITY transport section showing Target, Server Names, short IDs, and **Get New Key**.
4. Client account section showing **Flow** and **Create / Save**.
5. Expanded client row with **Info / Share / QR** actions.
6. Client details with the **Copy** action; completely cover the URI and QR code.
7. **Outbounds → direct → Edit → Strategy**, dropdown open at **ForceIPv4**.
8. Hiddify **+ → Add from clipboard** and the imported profile.
9. Hiddify **Settings → Inbound → Service mode** and local port.
10. Hiddify DNS and Routing/Region pages.
11. Windows manual proxy address/port form.

Redact private keys, UUIDs, whole VLESS links, QR codes, passwords, tokens, subscription URLs, panel URL paths, and account identifiers. Use solid opaque redactions, not blur. A public key alone is not a private key, but a complete profile still needs protection. Prefer documentation/demo accounts over production data.

Keep originals with credentials out of the repository, including Git history. Genuine new screenshots require a contributor's captures; none were taken from the user's applications during this repository-only update.

`hiddify-outbound-ipv4.svg` illustrates the author’s reported Android fix: **Hiddify → Settings → DNS → Outbound domain strategy → IPv4 only**, then reconnect. Keep this distinct from `3x-ui-force-ipv4.svg`, which changes the server’s website connections. Both are navigation diagrams, not captured screenshots.
