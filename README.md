# Your own VPN, one step at a time

You rent a small Linux server, create an account, and import its private connection link into Hiddify on your phone or computer. You can start with one server or connect through a nearby server to an exit in another country.

## Check the versions first

The **3x-ui panel** is the browser dashboard. **Xray** is the server's network engine. **Hiddify** is the client app. Their version numbers are separate.

| Tested setup | What happened |
|---|---|
| Entry server Xray **26.7.28**, Hiddify **5.5.5**, **classical** key share | NL mobile connection worked; all three desktop country profiles passed |
| Entry server Xray **26.9.9**, Hiddify **5.5.5**, hybrid key share | Desktop and Wi-Fi worked; the reported mobile connection failed |
| Moscow Xray **26.7.28** → exit Xray **26.9.9**, **XHTTP + REALITY over IPv6** | NL, FR and FI HTTPS and UDP relay checks passed |

For the working mobile setup, the Hiddify link includes **`keyshare=classical`**. Xray 26.9.9 rejects that smaller handshake. Match the profile to the server before importing it.

Our local comparison measured **534–598 bytes** for the older client's opening TLS record and **1,788–1,820 bytes** for Hiddify's hybrid one. The newer message includes a large post-quantum key share. [Why the sizes differ, the tests and version limits](docs/handshakes-and-versions.md)

## Path 1 — One server

```text
Phone or computer ── encrypted IPv4 connection ──> Foreign server ──> Website
```

Choose this when you want the fewest parts to rent and maintain. Your device needs a working route directly to the foreign server.

1. **Rent a server and save its login details.** A VPS is a rented remote computer. [Choose a server](docs/choose-server.md)
2. **Install 3x-ui and select the Xray version.** SSH is the terminal connection used for administration. [Prepare the server](docs/server-setup.md)
3. **Create a desktop or phone account.** Start with RAW + REALITY + Vision and the compatible classical profile. XHTTP is available as an optional transport experiment. [Create the inbound](docs/server-inbound.md)
4. **Import the link into Hiddify and open a website.** Test Wi-Fi and mobile data separately. [Connect your device](docs/clients.md)

<details>
<summary>Set up one server with scripts</summary>

On Linux/macOS, start with the plan:

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
Phone or computer ── IPv4 ──> Moscow ── XHTTP over IPv6 ──> Foreign exit ── IPv4 ──> Website
```

Choose this when a nearby entry works better than a direct foreign connection, or when you want several exit countries behind one entry. You rent and maintain both servers.

1. **Rent a Moscow entry and a foreign exit.** Enable IPv6 in both provider dashboards and configure each OS using that provider's instructions. [IPv6 prerequisites](docs/two-hop-vpn.md#1-configure-ipv6-yourself-using-your-vps-providers-instructions)
2. **Prepare both panels and versions.** The tested entry uses Xray 26.7.28 for classical phone profiles; the exits use 26.9.9. [Two-server walkthrough](docs/two-hop-vpn.md)
3. **Connect the panels.** Create an XHTTP relay account on the exit, import its link into Moscow's outbound, then add the routing rule. [Link the panels](docs/two-hop-vpn.md#how-the-two-3x-ui-panels-connect)
4. **Give devices their Moscow links.** A country profile selects the exit through account-based routing. Check the exit IP, then test mobile data. [Connect your device](docs/clients.md)

<details>
<summary>Set up two servers with scripts</summary>

Configure IPv6 on both VPSs first. Then preview the route from the repository folder:

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

A Russian entry can give you a reachable first hop while keeping the foreign exit out of the device's direct connection. In our investigation, Moscow could reach a foreign server over IPv6 while IPv4 access failed. That gives us another route to use. A domestic IP, a Russian SNI and IPv6 can all still be filtered; we have no measured blocking probability to attach to this design. [Connection maps and tradeoffs](docs/schemes/README.md)

## Someone already gave you a link

Install Hiddify, copy the entire link, choose **+ → Clipboard**, select the profile and tap **Connect**. Your link contains credentials, so keep it private. [Client walkthrough](docs/clients.md)

If Wi-Fi works and mobile data hangs, start with [versions and handshakes](docs/handshakes-and-versions.md), then [troubleshooting](docs/troubleshooting.md). [Real screenshots we need](images/README.md#screenshots-to-send-in-order)
