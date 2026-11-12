[← Choose a setup](../README.md) · [Single server](single-server.md) · [Two servers](two-hop-vpn.md)

# When an update changes the connection

A VPN profile can keep the same address and password while the client changes the bytes it sends. That is what we investigated after Hiddify worked on Wi-Fi and failed on mobile data.

**Xray** is the network engine on the server. **3x-ui** is its browser dashboard. **Hiddify** is the client app; Hiddify 5.5.5 reports a Hiddify sing-box traffic engine. Installing a different panel version does not by itself select the Xray version.

## The opening message

Before carrying website requests, the client sends a TLS **ClientHello**. TLS protects the connection; ClientHello advertises versions, encryption algorithms, a website name called **SNI**, and key shares used to establish encryption.

The **uTLS fingerprint** controls the browser-shaped ClientHello. The fingerprint belongs to the client opening that connection. For a phone → Moscow connection, Hiddify sends it. For Moscow → NL, Moscow acts as the client. The fingerprint field in 3x-ui also supplies metadata for exported links.

Keep SNI and browser fingerprint separate. Safari or Firefox can connect to a Russian website. The site name does not require a browser from the same country.

## What we captured

We ran separate local test processes with the same account, RAW transport, Chrome fingerprint and `www.google.com` SNI. The installed Invisible Man - XRay Client stayed active during the comparison.

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

## Match the client option to the server

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
