# Your own two-hop VPN

Your phone or computer connects to Moscow. Moscow passes the connection to a second server, and that server opens the website.

```text
Your device  →  Moscow  →  NL  →  Website
```

We built this after our direct connection to the NL server stopped working. The server was still up, and Moscow could reach it over IPv6. The guide shows how we connected the two.

## Someone gave you a link

Install Hiddify, copy the link and choose **+ → Clipboard**. Select the saved profile and tap **Connect**. Open a website to check it. Treat your link like a password. [Hiddify walkthrough](docs/clients.md)

## You want to run it yourself

You need two rented servers, also called VPSs. **3x-ui** is the browser dashboard where you set up accounts. **Hiddify** is the app your device uses to connect.

1. Set up IPv6 on both servers. Get the address and gateway from each provider and follow its instructions for your OS. [IPv6 setup](docs/two-hop-vpn.md#1-configure-ipv6-yourself-using-your-vps-providers-instructions)
2. Copy the relay account link from the exit server into Moscow’s **Outbounds**. Moscow uses that link to pass traffic to the exit. [Connect the panels](docs/two-hop-vpn.md#how-the-two-3x-ui-panels-connect)
3. Copy your device’s link from Moscow into Hiddify. Open an [IP check page](https://www.cloudflare.com/cdn-cgi/trace) and look for the exit server’s IPv4 address next to `ip=`.

[Full setup](docs/two-hop-vpn.md) · [Pictures and connection maps](docs/schemes/README.md) · [Setup scripts](docs/automation.md)

[Single-server walkthrough](docs/single-server.md) · [Troubleshooting](docs/troubleshooting.md)
