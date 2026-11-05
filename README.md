# VPN + Proxy in Russia

Set up a personal VLESS + REALITY server, connect your devices, and verify where their traffic exits. This setup can help with network filtering, but reachability depends on the provider, network, client engine, and server version.

## Start here

| Your task | Guide |
|---|---|
| Choose a VPS and install 3x-ui | [Server setup](docs/server-setup.md) |
| Create an inbound and copy your connection link | [VLESS + REALITY settings](docs/server-inbound.md) |
| Make the server exit over IPv4 | [ForceIPv4 in the panel](docs/force-ipv4.md) |
| Connect a Windows PC or phone | [Client setup](docs/clients.md) |
| Connect a Linux machine using Xray | [Linux Xray client](docs/linux-xray.md) |
| Let another device use your local proxy | [Share a proxy](docs/share-proxy.md) |

For a new installation, follow server setup, inbound settings, then client setup. For an existing server, start with client setup and keep the existing server parameters.

## What runs where?

```text
Your application → client app / local proxy → encrypted tunnel → VPS → website
```

3x-ui manages the server. Xray carries its traffic. A desktop or phone client imports the connection parameters and decides which local applications use the tunnel.

The server's public VPN port and the client's local proxy port are different settings. Connecting a client does not automatically guarantee that every application uses it.

Keep connection links and QR codes private: they contain client credentials. All examples in this repository use placeholders.
