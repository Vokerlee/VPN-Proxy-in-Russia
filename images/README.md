# Real screenshots for the guide

The guide needs pictures of the actual buttons and forms. The generated SVG UI pictures are no longer embedded in the walkthroughs. Their files remain here for history; don’t use them as replacements for screenshots.

## Match screenshots to the page

| Guide page | Screens to capture |
|---|---|
| [Rent a server](../docs/choose-server.md) | Provider’s create-server form, operating-system choice, then address/access details with secrets covered |
| [Install the panel](../docs/server-setup.md) | Panel login; the clickable version beside Xray status; Xray Updates with the chosen release’s circle; the Confirm dialog |
| [Make device links](../docs/server-inbound.md) | Add Inbound form, REALITY settings, desktop/phone client rows and account export action |
| [Connect a device](../docs/clients.md) | Hiddify’s add-from-clipboard action, service mode and home screen before/after Connect |
| [Link two servers](../docs/two-hop-vpn.md) | Foreign XHTTP inbound, Moscow link import, saved outbound and routing rule/order |
| [Choose an IPv4 exit](../docs/force-ipv4.md) | Outbounds → direct → Edit, with the Strategy selector open |

Take each screenshot at the point a reader would reach that screen. A full form can need two or three crops. Keep enough of the sidebar or page heading to show where you are.

## Screenshots to send in order

Use **3x-ui 3.8.5** and **Hiddify 5.5.5**, or include the version you actually run. Keep the page title and relevant button visible. Two crops of a long form are fine.

### Screens used by both paths

| Order | Open this screen | What should be visible | Suggested filename |
|---|---|---|---|
| 1 | **3x-ui → Overview** | Panel version, **Xray version button** and running status. Also capture **Xray Updates**, the release selection circle and **Confirm** dialog. For the device server, show **26.7.28**. | `entry-core-version.png` |
| 2 | **Inbounds → device entry → Edit** | Capture **Basics** (Remark, Address, port, Custom share address), **Stream** (RAW) and **Security** (REALITY, Target, SNI, uTLS). Cover private key and short IDs. | `entry-raw-reality.png` |
| 3 | **Clients → phone → ⓘ Client Information → Copy URL** | Which account is being exported and the **Copy** action. Cover the whole private URL and QR. | `device-profile-copy.png` |
| 4 | **Hiddify → + → Clipboard**, then the home screen | The import action, selected profile and **Connect** button; a second capture after connecting. | `hiddify-import-connect.png` |

Also capture **Clients → Add Client → Basics**, with **Email** and **Attached inbounds** visible, then **Credentials**, with **Flow → xtls-rprx-vision**. Cover the UUID. Suggested filename: `device-account.png`. This account form is separate from the inbound form.

These take the newcomer from checking the core to importing the right account. The single-server guide uses them directly. For that path, choose its foreign server panel for screenshots 1–3.

### Four additional screens for the two-server path

| Order | Panel and screen | What should be visible | Suggested filename |
|---|---|---|---|
| 5 | **Foreign exit → Inbounds → Relay nl → Edit** | In **Basics**, IPv6 **Address**, **Custom share address**, port **443** and **Disable XTLS flow** on; in **Stream**, XHTTP, path **/relay-nl**, mode **auto**; in **Security**, REALITY target/SNI. Capture the relay account separately under Clients, with empty flow. | `exit-xhttp-inbound.png` |
| 6 | **Moscow → Outbounds → + Outbounds → JSON** | The share-link input and **Import** button inside the add-outbound form. Cover any pasted profile. | `moscow-import-relay.png` |
| 7 | **Moscow → Outbounds → relay-nl → Edit** | The foreign **IPv6 address**, port, XHTTP path, **stream-one**, empty flow and REALITY SNI/fingerprint. Show **Basics → Send Through** (Moscow IPv6) and **Target Strategy → ForceIPv6**; no JSON editing is required. | `moscow-xhttp-outbound.png` |
| 8 | **Moscow → Routing → Routing Rules** | The rule list in order and an open rule with **Inbound tags**, optional **User** account labels and **Outbound tag**. Show the specific FR user rule above the general NL rule when sharing port 443. | `moscow-country-routing.png` |

For the two-server path, screenshot 1 should come from Moscow. Capture the foreign dashboard too, showing the same **26.7.28** version and **Running** status. Both servers use this version in the walkthrough.

### Useful follow-up screens

- **Hiddify → Profiles → ⋯ → Edit → Config Editor → Text**, around **tls → reality → key_share: classical**, for the advanced compatibility explanation. Cover the rest of the profile.

- **Foreign exit → Outbounds → direct → Edit**, with **ForceIPv4** visible.
- **Foreign exit → Routing**, showing the Moscow IPv6 source allow rule and the blocked rule below it.
- **Provider dashboard → IPv6**, showing where the assigned address/prefix and gateway are supplied. Replace values with documentation addresses before publishing.
- **Hiddify → Settings → Inbound → Service mode**, for the desktop VPN/TUN instructions.
- **Hiddify → Settings → DNS → Outbound domain strategy**, for the optional IPv4 DNS check.
- **Hiddify → Logs** after a failed mobile attempt, with the actual error and timestamp.

## Before sharing or committing

Cover UUIDs, private keys, short IDs, complete VLESS links, QR codes, passwords, API tokens, subscriptions and private panel paths with opaque blocks. Crop browser address bars containing credentials or panel paths. Use demo names such as `desktop`, `phone` and `FR-phone`.

For published examples, replace live addresses with `203.0.113.10` or `2001:db8:2::1`. Keep the original screenshots with secrets outside Git. Supply the app/panel version and capture date for each image.

## Adding the captures

Keep the originals outside Git. Add only redacted copies, with a short caption saying which panel/app version they show. Place each image beside the action it helps with, rather than adding a gallery at the top of a page. Until a screenshot is available, keep the written button steps; don’t add an empty image frame.
