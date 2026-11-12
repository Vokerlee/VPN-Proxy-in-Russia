[← Guide index](../README.md) · [Practical client setup](clients.md) · [Troubleshooting](troubleshooting.md)

# Inside Xray: follow one request through the tunnel

A browser asks for a page. Somewhere between a localhost listener and a VPS abroad, several protocols agree on identity, transport, encryption, and destination. The GUI compresses all of that into a Connect button.

This chapter opens that box. You can follow the ordinary setup without reading it, but understanding the layers makes failures much easier to localize—and explains why a perfectly valid connection link can stop working after a core update.

## Before you read

This is the optional technical chapter. You don’t need it to set up the VPN. If you want the next button to press, use [the one-server guide](single-server.md) or [two-server guide](two-hop-vpn.md).

A **client** is the app on your device; a **server** is the rented computer it connects to. **3x-ui** is the server’s dashboard, and **Xray** is the program that actually forwards the traffic. A **profile** is the private connection link carrying your account’s settings. The diagrams below describe the connections, not a copy of a settings screen.

Start with the two-minute picture, then pick the topic you’re curious about. There’s no need to read every protocol detail in order.

## The two-minute picture

Xray is a programmable proxy engine. A configuration gives it **inbounds** that accept traffic, a dispatcher/router that chooses a path, and **outbounds** that carry traffic onward. The same executable can be a local client or a remote server because those are configuration roles.

For this guide, the Windows/Linux client accepts local proxy requests and sends VLESS over RAW/TCP with REALITY to the VPS. The VPS accepts that inbound, authenticates the account, and usually chooses a freedom/direct outbound to the destination.

```text
Browser or application
      | HTTP CONNECT or SOCKS
      v
Local client inbound
      |
      v
Client routing
      | VLESS + Vision / REALITY / TCP
      | through your provider and internet networks
      v
Server inbound (public VPN port)
      |
      v
Server routing
      |
      v
freedom / direct outbound
      | through hosting and internet networks
      v
Destination website
```

The application still talks to the destination website. The tunnel changes the path that carries those bytes and which machine opens the final connection.

## Keep the control plane separate from the data plane

3x-ui is a management application: it stores accounts, templates, policies, and statistics, then generates configuration and controls an Xray process. It is not the engine forwarding each browser byte.

```text
Administrator's browser
      |
      v
3x-ui panel
      |
      v
Panel database and templates
      |
      v
Generated Xray configuration
      | configures
      v
Running Xray process <---- VPN client traffic
      |
      v
Websites
```

This separation explains three familiar surprises. The panel can load while the VPN core is broken. Xray may be a child of `x-ui` without a separate systemd service. A hand edit to the generated `bin/config.json` can disappear the next time the panel rebuilds it. Persistent changes belong in the panel's configuration source.

Client GUIs have a similar split. Their profile import is only the first stage; they add DNS, routing, selectors, monitoring, and OS integration before the engine runs. A minimal profile test and the application's full configuration test exercise different systems.

## VLESS, REALITY, RAW and Vision each have a job

| Layer | Job in this setup | Example setting |
|---|---|---|
| VLESS | Identify the account and describe the destination request | UUID and destination host/port |
| RAW/TCP | Carry the connection over an ordinary TCP stream | `type=tcp` in many share links |
| REALITY | Authenticate and protect the client/server transport with a TLS-derived handshake | Public/private key, SNI, short ID |
| Vision | Handle the initial traffic shape and eligible encrypted payload copying | `flow=xtls-rprx-vision` |
| Routing | Decide which outbound gets a request | `outboundTag: direct` |

A transport name is not an encryption algorithm, and a client's display name is not an authentication identity. The [transport documentation](https://xtls.github.io/en/config/transport.html) describes the combinable layers. An imported link serializes parameters; it does not negotiate away incompatible choices.

### The VLESS request has a small envelope

At the protocol level, the conventional VLESS request header describes a version, account UUID, optional addons, command, destination port, address type, and address, followed by request data. Addons carry features such as flow-related metadata. The response has its own short header before response data.

That means the proxy can request `example.com:443`, not merely an already-resolved IP. Where resolution happens becomes a configuration decision. It also explains why accepting a TCP socket is not evidence that the server accepted a VLESS account.

In this guide's profile, `encryption=none` refers to the VLESS-layer encryption option. REALITY supplies transport protection. Newer Xray also has separate VLESS Encryption features; they are not enabled by this example. Do not generalize this configuration into “VLESS is always plaintext” or confuse a UUID with the REALITY key pair. See the [wire format](https://xtls.github.io/en/development/protocols/vless.html) and [VLESS outbound settings](https://xtls.github.io/en/config/outbounds/vless.html).

## What makes REALITY more than a TLS checkbox

Ordinary HTTPS proves a server's identity through certificates and their trust chain. REALITY adds a different authorization path for the tunnel while arranging plausible behavior for connections that are not authorized clients. The configured **target** is part of that behavior; it is not automatically the website the user is visiting.

The server holds a REALITY private key. A client receives the corresponding public key, a short ID, a server name, and other parameters. The client handshake uses an ephemeral key exchange and derived authentication material; protocol metadata includes version/time information and the short ID. The server validates the expected values using its own key material and policy. These details are implementation-specific; use the [official REALITY implementation](https://github.com/XTLS/REALITY) rather than designing a lookalike handshake from this explanation.

The server name affects the TLS-looking handshake and target behavior. The short ID participates in recognition; it is not a replacement for the VLESS UUID. A complete share link carries both transport parameters and account access.

```text
Client: TCP connection + ClientHello
      |
      v
VPS: REALITY listener
      |  Target interaction supports handshake / fallback
      |
      +-- Authorized REALITY + valid VLESS account
      |       |
      |       v
      |   Requested website, through the selected outbound
      |       |
      |       v
      |   Response returns to client through the VPS
      |
      +-- Not an authorized tunnel connection
              |
              v
          Forward to configured target
              |
              v
          Target response returns to client
```

The diagram deliberately omits record-level exchange details. A successful generic TLS probe can follow the lower branch. It does not prove the upper branch works.

### The target is not a magic cloak

A usable target needs compatible TLS behavior and must be reachable from the VPS. The chosen SNI should fit the intended target/certificate behavior. A server in one data center and its target in another also have measurable timing and path properties.

REALITY is intended to reduce recognizable proxy behavior; it cannot promise that the IP, traffic timing, implementation bugs, or a particular network's policies will never expose or block the connection. Operational reachability is an observed property of a deployment, not a permanent property of a protocol name.

## Vision: the interesting part of TLS inside a tunnel

An HTTPS request already carries an inner TLS connection between the application and website. A conventional TLS proxy can wrap that encrypted stream in another encrypted stream, adding processing and a particular record/length structure.

Vision examines the beginning of the carried stream, adds protocol padding while handling the initial exchange, and can switch eligible TLS 1.3 traffic to a more direct copying path. It does not decrypt the website's application content, and it does not discard protection for arbitrary plaintext payloads. Compatibility, recognized traffic, and the transport path determine which optimization is available. The [VLESS inbound documentation](https://xtls.github.io/en/config/inbounds/vless.html#userobject) describes the supported flow combinations.

For a programmer, the useful distinction is between the **protocol state machine** and the **copy optimization**. In [Xray 26.10.31's implementation](https://github.com/XTLS/Xray-core/blob/v26.10.31/proxy/proxy.go), `VisionReader` and `VisionWriter` track traffic state; TLS filtering and padding/unpadding decide when the protocol can move on. Direct-copy eligibility is tracked separately, and the copy helper can use a more efficient path where both connections and the platform allow it.

On Linux, eligible sockets may benefit from `splice`-style copying. Seeing `CopyRawConn splice` in a debug log is useful evidence about that transfer path; its absence is not itself a tunnel failure. “Zero copy” is not an unconditional end-to-end guarantee, and the Windows path is not the Linux kernel path.

## Three different DNS decisions can affect one page

The application may resolve a name before it asks a proxy for a connection. A SOCKS client can either send an IP or ask the proxy to resolve a hostname; an HTTP CONNECT request can carry a hostname too. The local client may also resolve names for routing. Finally, the VPS may resolve the requested hostname when opening its direct outbound.

```text
Application resolver     → may produce an IP before proxying
Client routing resolver → may influence which outbound is selected
Server outbound resolver→ chooses the destination address at egress
```

A remote DNS setting on the client does not automatically control all three. Fake DNS adds a mapping from synthetic addresses back to domain names; it only works properly when the relevant DNS and traffic paths pass through the machinery maintaining that mapping. It is not a universal repair for a TLS authentication error. See [Xray DNS](https://xtls.github.io/en/config/dns.html) and [FakeDNS](https://xtls.github.io/en/config/fakedns.html).

This explains how a connection to an IPv4 server address can produce an IPv6 exit. The client reached the VPS over IPv4, but a hostname request still allowed the VPS to choose IPv6. [ForceIPv4 on the server's actual freedom outbound](force-ipv4.md) controls that hostname-resolution decision. A literal IPv6 destination and a routing rule blocking IPv6 are separate cases.

### The reported Android fix: Hiddify’s outbound domain strategy

On **2026-11-07**, the author reported that **Hiddify → Settings → DNS → Outbound domain strategy → IPv4 only** resolved the Android failure after the earlier client changes had not helped. In Hiddify 5.5.5’s [English labels](https://github.com/hiddify/hiddify-app/blob/v5.5.5/assets/translations/en.i18n.json), this control is `directDnsDomainStrategy`; its [stored option](https://github.com/hiddify/hiddify-app/blob/v5.5.5/lib/features/settings/data/config_option_repository.dart) is `direct-dns-domain-strategy`.

This selects IPv4 for the client’s direct/outbound name resolution. It is separate from the routing IPv6 mode and from Xray’s server-side freedom strategy. A numeric IPv4 server address alone does not constrain every other hostname lookup made by the client.

The initial improvement later stopped working. It did not isolate an IPv6 route or resolver as the cause. A later controlled experiment on the same US REALITY connection isolated the client fingerprint: Chrome failed in 12/12 requests, while Safari succeeded in 12/12, with endpoint, credentials, SNI, and protocol unchanged. Both authenticated through SSH. Captures showed missing Chrome-style handshake bytes between client and VPS. This supports fingerprint-dependent path interference, without identifying the dropping operator or making a universal claim about US servers. The Google SNI stayed unchanged. See the [practical fingerprint steps](troubleshooting.md#reality-chrome-times-out-but-safari-works).

## Routing is ordered policy, not a list of wishes

Routing associates a request with an outbound. A broad earlier match can make a later rule unreachable. A country bypass can send some traffic directly even while the selected VPN profile is healthy. Multiple address-family and DNS rules can change which address is available by the time a match is attempted.

The useful debugging unit is therefore not just “this hostname.” Record the inbound, address representation, matching rule, chosen outbound, resolver, and effective configuration. Preserve the panel's API rules when changing server routing. The [routing documentation](https://xtls.github.io/en/config/routing.html) describes rule evaluation.

The freedom outbound has its own final checks too. An allowed routing decision does not necessarily override its destination policy; keep existing `finalRules` when changing a family preference. See [freedom](https://xtls.github.io/en/config/outbounds/freedom.html).

## What a TLS fingerprint changes, and why Chrome can fail

A **TLS fingerprint** is the observable shape of the client's initial TLS handshake, particularly its **ClientHello** message. A uTLS preset such as `chrome` or `safari` asks the client engine to construct a browser-like handshake. It does not select a remote browser, contact that browser's vendor, or change the account's password.

Several fields contribute to that shape:

- Cipher suites, signature algorithms, and their ordering.
- Supported TLS versions and key-exchange groups.
- The `key_share` extension, including any large hybrid post-quantum key share.
- Extension order, padding, and GREASE values: deliberately reserved values used to exercise extension compatibility.
- ALPN, which advertises application protocols such as HTTP/2 and HTTP/1.1.

JA3/JA4-style summaries describe aspects of this observable handshake. They are not account credentials or complete representations of every byte. A fingerprint label is not a fixed packet size either: engine versions, preset implementations, and randomized fields can change the emitted message.

### Google SNI is different from the Chrome fingerprint

| Setting | What it controls | Example |
|---|---|---|
| REALITY target | The endpoint the VPS contacts for its REALITY handshake/fallback behavior | `www.google.com:443` |
| SNI / server name | The website name advertised during TLS setup | `www.google.com` |
| Client fingerprint | The browser-style ClientHello constructed by the client engine | `chrome` or `safari` |
| REALITY key and short ID | The connection's REALITY authentication parameters | Private account values |

Choosing Safari does not require choosing an Apple website. Likewise, choosing a Google target does not require the Chrome fingerprint. In 3x-ui, the REALITY fingerprint dropdown supplies **client export metadata**. The checked running server's REALITY configuration had no server fingerprint field. An imported phone profile keeps its old `fp=chrome` until it is edited or a new export is imported.

### The controlled US experiment

On **2026-11-07**, the installed Windows **Hiddify 5.5.5** engine was tested against the original US server's **VLESS + REALITY + Vision** account. Two isolated local proxy listeners used identical server IP, remote port, UUID, public key, short ID, SNI, transport, and Flow. Only the client fingerprint differed. Requests alternated between the two listeners rather than running all of one preset before the other.

| Client fingerprint | Real HTTPS requests that succeeded |
|---|---|
| Chrome | **0/12** |
| Safari | **12/12** |

Successful responses contained the expected server exit address. Both fingerprints also authenticated through the SSH control path. The Google target/SNI stayed unchanged. These observations isolate a fingerprint-dependent failure on the tested direct path; they do not establish that Google sites are unusable from US servers, that all US servers block Chrome, or that a particular operator is responsible.

```text
Same REALITY account
      |
      +-- Direct, Chrome --> Missing handshake bytes
      |
      +-- Direct, Safari --> Complete handshake; HTTPS works
      |
      +-- SSH control path --> Both presets authenticate
```

### A second Windows comparison outside the US

A second, non-US endpoint tested on **2026-11-07** reproduced the fingerprint distinction in Windows Hiddify 5.5.5: **Chrome 0/4, Safari 4/4**, alternating the same account, endpoint, SNI, keys, transport and Flow. Firefox also passed one exploratory request. Re-exporting Safari from 3x-ui and importing it into Hiddify’s full VPN mode then passed **2/2** HTTPS requests with that endpoint’s exit address. No UUID, key, SNI or port change was needed.

Native Linux Xray 26.10.31 passed 2/2 requests for each of Chrome, Safari and Firefox against that second endpoint. Thus a fingerprint label alone does not describe the complete handshake across different engines. This second case does not establish that its dropped bytes or filtering rule were identical to the original US packet capture below.

Earlier in the second investigation, TCP SYNs themselves did not reach the VPS. That reachability failure later cleared before the successful TCP/failing-Hiddify comparison. It must remain separate from the fingerprint result: an initially unreachable port cannot be repaired by changing a later TLS message. The precise cause of the earlier path recovery was not isolated.

### What the packet captures prove

Captures at the client and VPS showed failed Chrome-style handshakes declaring roughly **1.7–1.8 KB**, while only the first **1.35 KB** reached the VPS. The client repeatedly retransmitted the missing small segment, but it remained absent from the server capture. The server therefore lacked the complete message needed to continue TLS/REALITY setup. A successful SYN exchange or ICMP ping cannot prove that these later bytes are delivered.

This is more specific than a failed latency badge. It supports selective loss or interference **between the capture points**, before the VPS can process the complete handshake. Traffic inspection is a plausible explanation; a faulty middlebox is another. The experiment did not locate the dropping device or identify its matching rule. Wrapping traffic in SSH changes both its visible bytes and its outer connection behavior, so SSH success alone would not prove a particular DPI algorithm.

**Size alone is not the established cause.** The successful Safari REALITY ClientHello was about **1,533 bytes**, still large enough to span TCP segments on this path. Safari's **517-byte** handshake in the separately tested Trojan/TLS setup belonged to a different protocol/configuration. It must not be presented as the Safari REALITY handshake. Smaller TCP MSS values and the tested fragmentation options did not give a reliable cure. The controlled fingerprint change affects message contents, order, layout, and size together; it does not isolate one extension or a simple MTU threshold.

For another investigation, match TCP sequence ranges across the two captures and distinguish retransmissions from new bytes. NAT can change source ports, host clocks can differ, and segmentation/coalescing offloads can make a capture show a different packet layout from the physical wire. A single capture's apparent large packet is not proof that an oversized physical packet was transmitted.

### Repeat the comparison without changing the whole desktop network

Keep a working connection for administration. Make two private copies of the same profile, changing only `fp=chrome` to `fp=safari`, and test them through separate unused local proxy ports. Alternate real HTTPS requests and compare their exit address, not just their latency label. Record app/core versions, timeout settings, and fresh errors; a client engine's internal timeout can end a request before curl's longer timeout expires. Keep credentials and raw captures private.

For Hiddify's Windows VPN service, the checked privileged engine also wrote logs under `%ProgramData%\Hiddify\AdminBgService\core\work\data\box.log`. AppData logs could be stale while that engine was running. Reproduce the failure and verify the log timestamp before drawing conclusions.

The [beginner fingerprint walkthrough](troubleshooting.md#reality-chrome-times-out-but-safari-works) shows how to select Safari and re-export the profile. Compatibility still depends on the actual client implementation: a preset working in Hiddify's fork does not establish that stock sing-box or every Xray release emits the same compatible handshake.

## Classical and hybrid key shares

The browser preset and the key-share mode are separate parts of ClientHello. In our controlled capture, Chrome from Xray 25.1.30 produced a 534–598-byte TLS record. Hiddify 5.5.5's Chrome record was 1,788–1,820 bytes and included a 1,216-byte X25519MLKEM768 share. Both advertised the same cipher list, SNI and ALPN.

Hiddify's classical mode removes the ML-KEM component while retaining X25519 and TLS encryption. The server must accept it. The full [handshake and version guide](handshakes-and-versions.md) explains the post-quantum algorithm, exact measurements, compatibility boundary and matching profile options.

## Why a valid profile can stop working after an update

Configuration compatibility and wire compatibility are different contracts. A parser can accept `security=reality` and `fp=chrome` while the engine emits a ClientHello that the server's newer policy rejects.

A concrete example: the [REALITY change adopted in the 26.9.8/26.9.9 period](https://github.com/XTLS/REALITY/commit/8cdf7bf9c7f09cb9814bf08c3eb877f68b85fba8) rejects older/atypical ClientHello key-share layouts that omit the expected X25519MLKEM768 share before an optional standalone X25519 share. Client implementation and fingerprint handling therefore matter. A string named `chrome` is not a frozen byte sequence across engines or releases.

**sing-box** is another proxy engine; **Hiddify**, the VPN app in the practical guide, uses a modified version of it. The [sing-box compatibility report](https://github.com/SagerNet/sing-box/issues/4520) tracks affected implementations and experimental fixes. For the recorded setup, Hiddify 5.5.5’s own engine connected successfully. Compare actual engine versions and results when applying that report to another installation.

The reproduced comparison used the same profile, provider, destination, and server: Xray **25.1.30** failed; **26.10.31** succeeded against server **26.9.9**. That is evidence for a core-dependent failure, not evidence that the UUID needed regeneration. A separate comparison then showed Hiddify's plain profile working while its full generated configuration failed; the [recorded Windows preference changes](clients.md#advanced-recovery-when-the-normal-settings-are-not-enough) were followed by success without isolating one causal option. The earlier Android DNS improvement didn’t last; the later mobile success used the compatible classical handshake described above.

Similarly, finding an Xray module in a GUI binary proves a build dependency, not that its traffic is carried by an Xray backend. Inspect the actual execution path or test it. The checked Hiddify fork's [Xray outbound constructor](https://github.com/hiddify/hiddify-sing-box/blob/1614c5edb52dd44a4cc079201ba1e790fdfad8a0/protocol/hiddify/xray/outbound.go) returned an unimplemented error.

## TCP, UDP and the meaning of a local proxy

The example Linux HTTP inbound carries HTTP proxy traffic, including HTTPS CONNECT streams. A JSON flag saying `udp: true` does not turn that HTTP proxy into a general UDP tunnel. Browser QUIC, games, and DNS have their own behavior and may require SOCKS UDP support, XUDP-capable paths, or TUN integration.

Multiplexing, UDP encapsulation, and RAW/TCP transport are different choices. Sending many logical flows over one TCP connection changes loss and head-of-line behavior; it is not automatically a performance improvement. Keep the documented simple flow working before adding mux, transport wrappers, or fragmentation.

At the OS boundary, System Proxy selects a proxy for applications that honor it, while TUN captures traffic through routing/interface integration. That distinction survives regardless of how sophisticated the remote protocol is. The [ports and modes walkthrough](ports-and-modes.md) shows the concrete Windows settings.

## Turn a mystery into an experiment

For each test, write an explicit hypothesis and the observation that would falsify it:

| Hypothesis | A useful experiment | What it does not prove |
|---|---|---|
| The server IP is unreachable | ICMP/SSH/TCP comparison | Protocol authentication |
| The public VPN port is blocked | TCP connect from the affected network | REALITY and VLESS correctness |
| The profile is invalid | Compare export, then authenticate using a compatible core | The original GUI's integration works |
| The GUI's added config is the problem | Same native core with minimal versus generated config | Which optional setting alone caused it |
| Windows selected the wrong client | Read proxy endpoint, then explicitly test both local listeners | Every application follows system proxy |
| IPv6 is leaking locally | Compare direct and proxied exit addresses and paths | An IPv6 exit is inherently a leak |

Use local loopback, external-network, and real application tests for the layers each can observe. Keep a working baseline, change one variable when practical, and keep secrets out of logs and Git. The [automation helpers](automation.md) make the repeatable parts less tedious without deciding network policy for you.

**Back to setup:** [one server](single-server.md) · [two servers](two-hop-vpn.md) · [connect a device](clients.md).
