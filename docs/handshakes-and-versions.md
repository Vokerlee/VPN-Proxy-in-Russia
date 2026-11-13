[← Choose a setup](../README.md) · [Single server](single-server.md) · [Two servers](two-hop-vpn.md)

# When an update changes the connection

Use this page if a connection works on Wi-Fi but fails on mobile data, or if an app update stopped a previously working connection. A **profile** is the private link your VPN app uses to connect. The address and account can stay the same while a new app version changes how it starts the connection.

For the short version, [check the matching app and server settings](#match-the-client-option-to-the-server). The sections below explain why those settings matter. If you’re just setting up your first connection, [follow the device steps](clients.md); they include the required choice.

**Xray** is the network engine on the server. **3x-ui** is its browser dashboard. **Hiddify** is the client app; Hiddify 5.5.5 reports a Hiddify sing-box traffic engine. Installing a different panel version does not by itself select the Xray version.

## The opening message

Before carrying website requests, the client sends a TLS **ClientHello**. TLS protects the connection; ClientHello advertises versions, encryption algorithms, a website name called **SNI**, and key shares used to establish encryption.

The **uTLS fingerprint** controls the browser-shaped ClientHello. The fingerprint belongs to the client opening that connection. For a phone → Moscow connection, Hiddify sends it. For Moscow → NL, Moscow acts as the client. The fingerprint field in 3x-ui also supplies metadata for exported links.

Keep SNI and browser fingerprint separate. Safari or Firefox can connect to a Russian website. The site name does not require a browser from the same country.

## What we captured

We compared two client engines using the same account, **RAW** transport (a direct TCP connection), Chrome fingerprint and `www.google.com` SNI. One was the older **Invisible Man - XRay Client**, a Windows VPN app using Xray. The other was Hiddify 5.5.5. Separate test processes collected their first messages; the existing VPN app stayed running.

| Captured ClientHello TLS record | Invisible Man's Xray 25.1.30 | Hiddify 5.5.5 |
|---|---|---|
| Size across the captured samples | 534–598 bytes | 1,788–1,820 bytes |
| Classical X25519 share | 32 bytes | 32 bytes |
| Additional X25519MLKEM768 share | Absent | 1,216 bytes |
| Advertised application protocols | h2 and http/1.1 | h2 and http/1.1 |
| Cipher-suite list | Same 16 entries | Same 16 entries |

These are whole TLS-record sizes from a local collector, including its five-byte record header. They do not measure packet segmentation on the phone's mobile route. Random extensions and fingerprint versions can change the size.

Against an older foreign server, six alternating Windows Hiddify tests using Chrome produced **hybrid 1/6 successful HTTPS requests** and **classical 6/6**. Later, the owner reported mobile success through the Moscow entry after selecting Xray 26.7.28 and classical mode. Other operators and phones still need their own tests.

## Why the newer key share is larger

**X25519MLKEM768** combines X25519 with **ML-KEM-768**, a post-quantum key-encapsulation mechanism. ML-KEM is designed to resist future attacks using quantum computers. Its public encapsulation key is 1,184 bytes; adding the 32-byte X25519 component gives the 1,216-byte hybrid share seen in the capture. [NIST ML-KEM standard](https://csrc.nist.gov/pubs/fips/203/final), [key sizes in Table 3](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.203.pdf)

The capture records advertised key shares. The negotiated protection depends on both endpoints.

A larger ClientHello can span more TCP packets, and its contents give filtering systems another pattern to recognize. The captures establish the size difference. A synchronized mobile capture is needed to attribute a failure to filtering, packet loss or an implementation problem.

**Classical mode keeps X25519 and omits the ML-KEM share.** TLS encryption still protects the connection. This choice gives up that hybrid post-quantum component in exchange for the smaller handshake in the tested deployment. [Hiddify investigation](https://github.com/hiddify/hiddify-app/issues/2463#issuecomment-6730522122)

## Why newer versions can fail on some networks

**26.7.28 is our chosen compatibility version, not a claim that every higher version fails.** The recorded newer-server failure involved **26.9.9**, Hiddify 5.5.5 and the affected mobile connection. The same deployment could work on desktop or Wi-Fi. There are two separate changes to understand: the message the client sends and the messages the server accepts.

### 1. A client update can enlarge ClientHello

The client constructs ClientHello before the VPN carries a website request. Its engine, browser fingerprint and key-share setting determine the bytes sent. Updating Hiddify or its TLS implementation can therefore change the opening message even when you import the same account link.

The hybrid **X25519MLKEM768** option adds post-quantum key-exchange material. This is a change to how the shared secret is established, rather than simply choosing a different bulk-data cipher such as AES. In our comparison, the cipher-suite lists matched while the key shares differed.

ML-KEM is designed to protect key establishment against future quantum-computer attacks. That protection has a size cost: its ML-KEM-768 public encapsulation key is **1,184 bytes**, combined here with **32 bytes** for X25519. The result is the **1,216-byte hybrid share**. A separate classical X25519 share may also be advertised. Those shares sit inside ClientHello along with its other extensions. [NIST’s ML-KEM standard](https://csrc.nist.gov/pubs/fips/203/final), [FIPS 203 key sizes, Table 3](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.203.pdf)

Our measured opening TLS records grew from **534–598 bytes** in the older Xray client to **1,788–1,820 bytes** in the compared Hiddify configuration. These are samples from specific engines with Chrome selected, not universal sizes for Chrome, Safari or all classical profiles.

### 2. A server update can reject the smaller alternative

A newer REALITY implementation added a check requiring the expected **X25519MLKEM768** key-share layout, with a possible standalone X25519 share afterward. A classical-only client doesn’t satisfy that check. This is the compatibility change associated with the **26.9.8/26.9.9** period; it isn’t a rule applying to every release after 26.7.28. [The upstream REALITY change](https://github.com/XTLS/REALITY/commit/8cdf7bf9c7f09cb9814bf08c3eb877f68b85fba8)

That creates a practical conflict on an affected path: the hybrid message fails to get a working connection, but selecting classical mode makes the newer server reject the handshake. Changing only the UUID, SNI or display name doesn’t remove that requirement.

The guide pairs **server 26.7.28** with **Hiddify `keyshare=classical`** because this server accepts the smaller alternative. **Both settings matter.** Installing the older server doesn’t automatically remove the hybrid share from a client’s default message. Changing only the client option doesn’t make an incompatible newer server accept it. [Hiddify discussion and classical-mode compatibility](https://github.com/hiddify/hiddify-app/issues/2463#issuecomment-6750196534)

### 3. A larger message changes what the network has to deliver

A TLS record doesn’t have to fit in one TCP segment. Splitting it across segments is normal. For illustration, if a path carries around 1,400 bytes of TCP data per segment, a roughly 1,800-byte message needs more than one segment. The server needs the complete message to continue the handshake.

```text
Illustration only; not a mobile packet capture:

ClientHello: about 1,800 bytes
      |
      +-- first segment: about 1,400 bytes --> server
      |
      +-- remaining bytes ----------------> server

Both parts must arrive for the complete message to be read.
```

Packet loss, a faulty network device or traffic filtering can interrupt that delivery. Filtering can also match message contents and extension layout, rather than just its size. A timeout by itself doesn’t identify which happened.

Earlier captures in this project showed incomplete handshakes arriving at a server while the missing bytes were retransmitted at the client. However, that fingerprint comparison changed several message properties at once. A successful Safari REALITY record there was about **1,533 bytes**, so we did **not** establish a universal “large messages are blocked” threshold. That was also a separate experiment from the local old/new-client size comparison above.

### How to distinguish the failures

| What the fresh checks show | What to investigate |
|---|---|
| The TCP connection itself never opens | Address, route, listening port or firewall; ClientHello hasn’t been exchanged yet |
| TCP opens, but the server capture lacks part of ClientHello | Delivery between the capture points; a server setting can’t validate bytes it hasn’t received |
| The complete message arrives, but the server rejects classical mode | REALITY version and key-share compatibility |
| An isolated account test works, but Hiddify’s browser traffic fails | The app’s generated settings, selected profile and device routing |

Record the app and engine versions, server version, fingerprint, key-share mode and fresh request result. Compare the same account on Wi-Fi and mobile data before attributing the failure to an operator. The successful classical test supports the guide’s workaround on that path; it doesn’t establish that post-quantum algorithms are generally blocked in Russia.

## Match the client option to the server

**Current guide preset: Xray 26.7.28 on every server.** Use classical mode for device links and the guide’s XHTTP settings between servers. The table below records earlier tests with other versions; those numbers are historical results, not instructions to install a different version on the foreign server.

For a device profile, check the server **the device connects to**. That is your only foreign server for the one-server route, or Moscow for the two-server route. In the two-server route, the foreign exit also uses **26.7.28** in this guide, but its client is Moscow rather than your phone. Its inter-server profile can therefore have different handshake settings.

| Server role and version | Client key share | Result in this project |
|---|---|---|
| Device entry, Xray 26.7.28 | Classical | Working mobile NL test and desktop profiles |
| Device entry, Xray 26.9.9 | Hybrid | Desktop/Wi-Fi working; mobile failure reported |
| Device entry, Xray 26.9.9 | Classical | Rejected by the server's REALITY handshake requirements |
| Foreign exit, Xray 26.9.9 | Hybrid from Moscow | Working XHTTP IPv6 relays |

The thread's last comment explains that classical mode requires a compatible older server. Browser fingerprint changes alone can leave the hybrid share present. [Compatibility caveat](https://github.com/hiddify/hiddify-app/issues/2463#issuecomment-6750196534)

For Hiddify, add `keyshare=classical` to the query part of the intended account's exported link, before `#`. In its JSON configuration, the equivalent field is `tls.reality.key_share` with value `classical`. The scripts save the original panel link alongside this Hiddify variant. Keep its UUID, keys, address and account name.

The server field is the **core version**, not a server-side uTLS setting. Record the current version and back up the binary and panel before an existing-server change. The fresh-server helper pins its selected core; the relay helper checks an existing core before adding a route.

Xray 26.7.28 is an older compatibility choice. Later releases contain security fixes, including a change disabling MPTCP by default. The helper sets `GODEBUG=multipathtcp=0` for its core service. Keep the OS patched and reassess this version choice as compatible fixes become available. [Xray release notes](https://github.com/XTLS/Xray-core/releases/tag/v26.10.31)

## RAW or XHTTP

**RAW** carries the VLESS connection directly over TCP. With this guide's RAW profile, the account flow is `xtls-rprx-vision`.

**XHTTP** carries traffic through HTTP requests and supports different connection patterns. The tested inter-server setup uses `stream-one` on Moscow, `auto` on the exit and an empty account flow on that leg. It still establishes a TLS/REALITY handshake. [XHTTP design](https://github.com/XTLS/Xray-core/discussions/4113)

Both setup helpers offer XHTTP. Single-server XHTTP and device-to-Moscow XHTTP are optional experiments; the mobile success recorded here used RAW at device entry. Re-export the account after changing its transport, path or flow, then test the matching client profile.

**Next:** [make the matching device link](server-inbound.md#5-export-the-connection), [import it into Hiddify](clients.md), or [continue troubleshooting](troubleshooting.md).

## Installation interface references

The beginner guide’s exact version-installation actions were checked against [the version button in 3x-ui 3.8.5](https://github.com/MHSanaei/3x-ui/blob/v3.8.5/frontend/src/pages/index/OverviewActionBar.tsx) and [its release-selection and confirmation dialog](https://github.com/MHSanaei/3x-ui/blob/v3.8.5/frontend/src/pages/index/VersionModal.tsx).
