[← What a VPN does and where to start](../README.md) · [Two-server route](two-hop-vpn.md)

# Your first VPN: one server

We’ll rent a computer abroad, set up the VPN on it, and connect your phone or computer. You’ll end up with a connection you can switch on in Hiddify whenever you need it.

That rented computer is the **server**. Hiddify is the **client** app on your device. The server stays on in the hosting company’s data centre; your own computer can be switched off once setup is done.

```text
            One server
         1 VPN connection

         Your phone / PC
                |
                | VPN over IPv4
                v
      Your internet provider
                |
                v
        Internet networks
                |
                v
+--------------------------------+
|       Your server abroad       |
|    VPN connection ends here    |
+--------------------------------+
                |
                v
   Hosting provider / internet
                |
                v
             Website
```

The box marks the server you rent. There is **one VPN connection**, from Hiddify on your device to that server. Your internet provider and the networks in between carry its encrypted traffic. The server then opens a separate connection to the website through its hosting provider. Replies come back through the same stages.

This walkthrough connects to the server over **IPv4**, so your device doesn’t need IPv6. If you later want to connect directly to the server’s **IPv6 address**, your device and its current internet connection must both support IPv6. Hiddify can’t add native IPv6 connectivity that your network doesn’t provide. The [two-server route](two-hop-vpn.md) keeps IPv6 between the servers and lets devices connect over IPv4.

## What you need

- A Windows, Linux or Mac computer for the setup. It doesn’t have to run the same operating system as the server.
- A server rental. If you don’t have one, the first page below shows you how to get one and what to pay attention to.
- Your phone too, if that’s where you want to use the VPN.

We’ll choose Ubuntu, a Linux operating system, for the rented server. You don’t need to install Ubuntu on your own computer. The guide uses **3x-ui**, a browser dashboard, to manage the VPN, and **Hiddify** to connect your devices.

## Follow these steps in order

Each link opens the instructions for that step. Finish the page, check the result at the bottom, and follow its next link. You don’t need to read the whole guide before starting.

### 1. Get a server

Follow the **HostVDS foreign-server section** on the rental page, or choose another provider abroad. Rent one small foreign server and save its address and login details. Skip the FirstVDS Moscow section; that belongs to the two-server route.

**[Rent a server →](choose-server.md)**

Already have a server and its login? Start with step 2.

### 2. Install the server’s control panel

You’ll open a terminal on your computer, connect to the server, and paste the installation commands. Then you’ll open the new dashboard in your browser.

**[Install and open the dashboard →](server-setup.md)**

Already able to sign in to 3x-ui? Start with step 3.

### 3. Make a link for each device

In the dashboard, create a phone account and a computer account. Each gets a private connection link. The instructions show which fields to fill in and which to leave alone.

**[Create your connection links →](server-inbound.md)**

### 4. Connect your computer or phone

Install Hiddify, add your device’s link, and press Connect. Open a website and check that the connection uses your server. On a phone, try both Wi-Fi and mobile data.

**[Set up Hiddify and connect →](clients.md)**

That’s the whole route. Once your websites open and the address check matches your server, you can stop.

## Set this up with scripts

<details>
<summary>Open the commands for the same single-server setup</summary>

Use your **fresh foreign server**, such as the HostVDS rental, with Ubuntu/Debian, systemd and a public IPv4 address. Run these commands on **your setup computer**, after [downloading the repository and opening a terminal in its folder](quick-start.md#before-the-first-command). An existing 3x-ui installation needs the manual path. Save the root login from your provider.

**Windows PowerShell**, from the repository folder:

```powershell
.\scripts\Setup-Vpn.ps1 -ServerIp 203.0.113.10 -VpnPort 8443 -Target www.apple.com -CoreVersion 26.7.28 -KeyShare classical -Fingerprint safari -Clients desktop,phone
```

This prints the plan. Check the address, then repeat the command with **`-Apply`**.

**Linux/macOS terminal**, from the repository folder:

```bash
python3 scripts/bootstrap_server.py --host 203.0.113.10 \
  --vpn-port 8443 --target www.apple.com --core-version 26.7.28 \
  --key-share classical --fingerprint safari --clients desktop,phone --plan
```

**`--clients desktop,phone` / `-Clients desktop,phone` is a list of names you choose for the new VPN accounts.** `desktop` and `phone` are examples. Use `alex,anna,laptop` if you want three accounts with those names. Each name gets separate credentials and a link; separate names with commas and no spaces. [Name rules and filenames](automation.md#choose-the-vpn-account-names)

Check the plan, then replace **`--plan`** with **`--apply`**. Replace the documentation address with your own VPS address in either example.

SSH asks for the root password privately. The helper installs the panel, verifies the selected core download, creates the accounts you listed and prints the panel address and private output directory. With the example names, open **client-desktop.txt** or **client-phone.txt** there. With your own names, open **client-YOUR_NAME.txt**. Then copy its whole link, and import it into Hiddify with **+ → Clipboard**.

Press **Connect**, open an IP-check page and confirm the server's exit address. Try a real website on Wi-Fi and mobile data. If a provider firewall blocks the printed VPN or panel port, allow that specific port in the provider dashboard.

For an XHTTP experiment, add `-Transport xhttp` or `--transport xhttp` before applying. That profile uses an empty flow and path `/vpn`. [All options and recovery](automation.md#start-with-only-a-vps-ip-and-root-password)

</details>

## If something does not work

Start with [the symptom table](troubleshooting.md#first-choose-the-symptom-that-matches-yours). It helps you check the failed part without changing everything at once.

If Wi-Fi works but mobile data doesn’t, read [the mobile connection checks](troubleshooting.md#wi-fi-works-but-mobile-data-hangs). The app and server versions matter here; the setup pages tell you which tested versions to use.

## Optional XHTTP entry

XHTTP is another way to carry the VPN traffic. The working phone setup in this guide uses RAW, so keep that for your first connection. If you want to test XHTTP later, use a separate account and follow [the XHTTP settings](server-inbound.md#optional-xhttp-instead-of-raw). Changing transport also means importing a matching new link.

## Optional shortcuts and deeper reading

- [Use scripts for a fresh server](quick-start.md).
- [Understand one server versus two](schemes/README.md).
- [Choose the address websites see](force-ipv4.md).
- [Understand Hiddify’s connection modes](ports-and-modes.md).
- [Use the VPN from Linux terminal programs](linux-xray.md).
- [Read how the protocols work](xray-internals.md).

**Next:** if you’re starting from nothing, [rent your server](choose-server.md).
