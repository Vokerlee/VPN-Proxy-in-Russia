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

### Four screens used by both paths

| Order | Open this screen | What should be visible | Suggested filename |
|---|---|---|---|
| 1 | **3x-ui Dashboard** | Panel version, **Xray version button** and running status. Also capture **Xray Updates**, the release selection circle and **Confirm** dialog. For the device server, show **26.7.28**. | `entry-core-version.png` |
| 2 | **Inbounds → device entry → Edit** | Remark, listen address, **443 or 8443**, **VLESS**, **RAW/TCP**, **REALITY**, target, server names and fingerprint. A second crop can show the device's **Vision** flow. | `entry-raw-reality.png` |
| 3 | **Inbounds → expand device clients → phone → Info / Share** | Which account is being exported and the **Copy** action. Cover the whole private URL and QR. | `device-profile-copy.png` |
| 4 | **Hiddify → Profiles → ⋯ → Edit → Config Editor → Text** | A crop around **tls → reality → key_share: classical**. Also capture **+ → Clipboard** and the home screen with the selected profile and **Connect** button if possible. | `hiddify-classical-profile.png` |

These take the newcomer from checking the core to importing the right account. The single-server guide uses them directly. For that path, choose its foreign server panel for screenshots 1–3.

### Four additional screens for the two-server path

| Order | Panel and screen | What should be visible | Suggested filename |
|---|---|---|---|
| 5 | **Foreign exit → Inbounds → Relay nl → Edit** | Assigned **IPv6 Listen IP**, port **443**, **VLESS**, **XHTTP**, path **/relay-nl**, mode **auto**, REALITY target/SNI and the relay client's **empty flow**. Use two crops if needed. | `exit-xhttp-inbound.png` |
| 6 | **Moscow → Outbounds → + Outbounds → JSON** | The share-link input and **Import** button inside the add-outbound form. Cover any pasted profile. | `moscow-import-relay.png` |
| 7 | **Moscow → Outbounds → relay-nl → Edit** | The foreign **IPv6 address**, port, XHTTP path, **stream-one**, empty flow and REALITY SNI/fingerprint. An extra JSON crop can show `sendThrough` and `sockopt.domainStrategy: ForceIPv6`. | `moscow-xhttp-outbound.png` |
| 8 | **Moscow → Routing** | The rule list in order and an open rule with **Inbound Tags**, optional **User** account labels and **Outbound Tag**. Show the specific FR user rule above the general NL rule when sharing port 443. | `moscow-country-routing.png` |

For the two-server path, screenshot 1 should come from Moscow. An additional exit-dashboard capture showing core **26.9.9** helps explain why the two cores have different versions.

### Useful follow-up screens

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
