# Let’s set up your own VPN

If you’ve used a VPN app before, you know the usual routine: choose a country, press Connect, and hope it works. Here we’ll set up a VPN you manage yourself. You’ll still use an app on your phone or computer, but you’ll decide which server it connects to and who can use it.

You don’t need previous experience with servers. You will need a computer for the setup, a paid server rental, and a little patience with the first few steps. We’ll explain the unfamiliar bits as we go.

## What does a VPN actually do?

Without a VPN, your device connects to websites through your internet provider. With this setup, it first opens an encrypted connection to a computer you rent. That computer connects to the websites for you and sends their replies back.

```text
Without a VPN:  Your phone → Internet provider → Website
With this VPN:  Your phone → Your VPN server → Website
               (the connection to your server is encrypted)
```

Your internet provider still carries the connection and can see that you’re talking to the server. Websites normally see the server’s internet address instead of yours. This can help you reach sites that don’t open on your usual connection. It doesn’t make you anonymous: a website can still recognize an account you sign in to, and a provider can still block the connection to your server.

## What are the server and client?

The **server** is a computer in a hosting company’s data centre. You rent it by the provider’s billing period and leave it running. You don’t need to buy a physical computer or keep your laptop on. Hosting companies often call it a **VPS**.

The **client** is the app on your phone or computer that connects to that server. We use **Hiddify**. You’ll give it a private connection link containing the address and login settings it needs. Your phone and computer will each get their own link.

There’s also a **control panel**: a website where you manage the server’s VPN accounts. We use one called **3x-ui**. We’ll install it together. You don’t need to know its settings yet.

## One server or two?

**One server is the easier place to start.** You rent a server abroad, and your device connects straight to it:

```text
Your device → Server abroad → Website
```

**Two servers give you another route.** Your device connects to a server in Russia, and that server passes the traffic to your server abroad:

```text
Your device → Server in Russia → Server abroad → Website
```

This is useful when the foreign server is hard to reach directly. It costs more and takes more setup. In our example, the servers talk using IPv6—another kind of internet address—which you’ll configure using each hosting company’s instructions. Two servers can still be blocked; this is another route to try, not a promise that it will always work.

## Where do I start?

- **I have nothing set up.** Open [the one-server walkthrough](docs/single-server.md). Its first step is [renting a server](docs/choose-server.md).
- **I want the two-server route.** Open [the two-server walkthrough](docs/two-hop-vpn.md). It starts with what to rent and which details to save.
- **I already have a server.** Go to [installing its control panel](docs/server-setup.md). If the panel already opens, go to [creating device accounts](docs/server-inbound.md).
- **Someone gave me a VPN link.** You only need [the Hiddify setup page](docs/clients.md).
- **My VPN stopped working.** Start with [the troubleshooting table](docs/troubleshooting.md#first-choose-the-symptom-that-matches-yours).

The two routes are outlined below. Follow one of them. The script shortcuts stay folded away unless you want to use them.

## Path 1 — One server

```text
Your phone or computer ──> Your server abroad ──> Website
```

You pay for one server abroad. Your phone or computer connects to it, and it opens websites for you. Start here if you haven’t tried running your own VPN before.

1. **Choose where your VPN will be.** Rent a server in the country you want to connect through. [Choose a server](docs/choose-server.md)
2. **Open its control panel.** Install the dashboard you’ll use to manage your VPN. The guide includes the commands and settings. [Prepare the server](docs/server-setup.md)
3. **Make a connection link for each device.** Create separate phone and computer accounts in the dashboard, then copy their links. [Create your links](docs/server-inbound.md)
4. **Connect.** Add the link to Hiddify, press Connect and check that websites open. Try both Wi-Fi and mobile data on your phone. [Connect your device](docs/clients.md)

<details>
<summary>Set up one server with scripts</summary>

First [download the repository and open a terminal in its folder](docs/quick-start.md#before-the-first-command). On Linux/macOS, start with the plan:

```bash
python3 scripts/bootstrap_server.py --host 203.0.113.10 --vpn-port 8443 --target www.apple.com --core-version 26.7.28 --key-share classical --fingerprint safari --clients desktop,phone --plan
```

On Windows PowerShell:

```powershell
.\scripts\Setup-Vpn.ps1 -ServerIp 203.0.113.10 -VpnPort 8443 -Target www.apple.com -CoreVersion 26.7.28 -KeyShare classical -Fingerprint safari -Clients desktop,phone
```

Use your fresh VPS address. After checking the plan, replace `--plan` with `--apply`, or add `-Apply`. Import the printed output folder's **client-desktop.txt** or **client-phone.txt** into Hiddify, then test a website. [Full script walkthrough](docs/single-server.md#set-this-up-with-scripts)

</details>

[Full single-server walkthrough](docs/single-server.md) · [Optional single-server automation](docs/quick-start.md)

## Path 2 — Two servers

```text
Your phone or computer ──> Your server in Russia ──> Your server abroad ──> Website
```

You pay for two servers. Your device connects to the one in Russia, which passes the connection to the one abroad. Websites see the foreign server’s address. Our example uses Moscow; you can also connect that server to several countries later.

1. **Get both servers ready.** This route needs IPv6, an additional kind of internet address, working on both servers. Each hosting company has its own setup instructions; the guide explains what to check. [Prepare the addresses](docs/two-hop-vpn.md#1-configure-ipv6-yourself-using-your-vps-providers-instructions)
2. **Open a control panel for each server.** Keep the two dashboards in separate browser tabs. [Start the two-server walkthrough](docs/two-hop-vpn.md)
3. **Link the servers.** Copy a connection link from the foreign server into the Russian server’s dashboard and tell it to send traffic there. [Follow the panel steps](docs/two-hop-vpn.md#how-the-two-3x-ui-panels-connect)
4. **Connect your devices to the Russian server.** Add their links to Hiddify and check that websites see the country you chose. Test mobile data too. [Connect your device](docs/clients.md)

<details>
<summary>Set up two servers with scripts</summary>

Configure IPv6 on both servers first. [Download the repository and open a terminal in its folder](docs/quick-start.md#before-the-first-command), then preview the route:

```bash
python3 scripts/bootstrap_relay.py \
  --hub-host 203.0.113.10 --exit-host 198.51.100.20 \
  --exit-ipv6 2001:db8:2::1 --route nl --entry-port 443 \
  --hub-core-version 26.7.28 --exit-core-version 26.9.9 \
  --entry-key-share classical --relay-transport xhttp \
  --clients desktop,phone --plan
```

Use your own server addresses. On Windows, use `py` and put the arguments on one line. After checking the plan, replace `--plan` with `--apply`. Import **desktop.txt** or **phone.txt** from the printed private output folder, then check the foreign exit IP. [Full script walkthrough](docs/two-hop-vpn.md#3-preview-and-apply-the-relay-helper)

</details>

[Full two-server walkthrough](docs/two-hop-vpn.md) · [Optional relay automation](docs/automation.md#set-up-the-two-hop-relay)

In our tests, the Moscow server could reach a foreign server using IPv6 when its IPv4 connection failed. That made this route useful for us; it can still be blocked. [Connection maps and tradeoffs](docs/schemes/README.md)

## Someone already gave you a link

Install Hiddify, copy the entire link, choose **+ → Clipboard**, select the profile and tap **Connect**. Your link contains credentials, so keep it private. [Client walkthrough](docs/clients.md)

If Wi-Fi works and mobile data hangs, start with [versions and handshakes](docs/handshakes-and-versions.md), then [troubleshooting](docs/troubleshooting.md). [Real screenshots we need](images/README.md#screenshots-to-send-in-order)

## Versions used by this guide

The setup pages tell you which versions to select when you reach that step. If you already have a VPN and are comparing settings, the test results are below.

<details>
<summary>Show tested versions and the mobile connection fix</summary>

## Check the versions first

The **3x-ui panel** is the browser dashboard. **Xray** is the server's network engine. **Hiddify** is the client app. Their version numbers are separate.

| Tested setup | What happened |
|---|---|
| Entry server Xray **26.7.28**, Hiddify **5.5.5**, **classical** key share | NL mobile connection worked; all three desktop country profiles passed |
| Entry server Xray **26.9.9**, Hiddify **5.5.5**, hybrid key share | Desktop and Wi-Fi worked; the reported mobile connection failed |
| Moscow Xray **26.7.28** → exit Xray **26.9.9**, **XHTTP + REALITY over IPv6** | NL, FR and FI HTTPS and UDP relay checks passed |

For the working mobile setup, the Hiddify link includes **`keyshare=classical`**. Xray 26.9.9 rejects that smaller handshake. Match the profile to the server before importing it.

Our local comparison measured **534–598 bytes** for the older client's opening TLS record and **1,788–1,820 bytes** for Hiddify's hybrid one. The newer message includes a large post-quantum key share. [Why the sizes differ, the tests and version limits](docs/handshakes-and-versions.md)

</details>
