[← Single-server overview](single-server.md) · Step 2 of 4

# Install and prepare the VPN server

Here we’ll put a browser dashboard on your rented server, so you can manage the VPN without editing configuration files for every device.

Have the server’s **IP address**, **login name** and **password or SSH key** from your hosting company ready. The IP address tells your computer which server to contact. If you don’t have a server yet, [rent one first](choose-server.md).

Start on your own Windows, Linux or Mac computer. After you log in, the commands run on the rented server. A **terminal** is the command window you type them into; on Windows, use PowerShell.

We’ll install **3x-ui**, the dashboard you’ll open in your browser to manage the VPN. First get that dashboard working; we’ll set up the program behind it afterward.

These button instructions use **3x-ui 3.8.5**. The installer command below selects that dashboard version.

If you already have a working dashboard on this server, keep it. You won’t need to run the installer again. The version check later on this page still applies.

**Follow steps 1–4 in order.** They prepare this server for the VPN. We’ll explain each tool or setting when you reach it. Sections marked **Optional** are alternatives or background; you can leave them closed.

## 1. Choose which server you are preparing

First identify the server you’re about to change. The two-server route uses a separate dashboard on each machine, so keeping the roles straight prevents you from creating a phone account on the foreign relay by mistake.

Follow this page once for a one-server VPN. For a two-server VPN, follow it **twice**, once in Moscow’s SSH terminal and once in the foreign server’s SSH terminal. Install a separate dashboard on each server and save each panel’s URL and login separately.

| Your route and server | Example provider | After this page |
|---|---|---|
| One-server route: foreign server | HostVDS | [Make device accounts](server-inbound.md) |
| Two-server route: Moscow | FirstVDS | Prepare the foreign dashboard too, then return to the two-server guide |
| Two-server route: foreign server, NL example | HostVDS | [Link the two panels](two-hop-vpn.md#how-the-two-3x-ui-panels-connect) once both are ready |

Before the two-server installation, you should already have rented **both** servers and configured [IPv6 on both](two-hop-vpn.md#1-configure-ipv6-yourself-using-your-vps-providers-instructions). Renting only Moscow doesn’t complete the setup.

## 2. Connect over SSH

We need to install software on the rented server, not on your own computer. **SSH** opens a secure command window on that remote machine so the installation commands run in the right place.

On your own computer, open **PowerShell** on Windows or a **terminal** on Linux/macOS. The SSH command is the same on both.

Your provider supplies an IP address and a login method. If the login user is `root` (the administrator account), run:

```bash
ssh root@YOUR_SERVER_IP
```

Replace `YOUR_SERVER_IP` with the address from your provider. If the provider gave you a user such as `ubuntu`, use that name instead of `root`; after login, run `sudo -i` for the administrative installation commands below. If the provider supplied an SSH key or custom SSH port, follow its access instructions rather than assuming a root password exists.

If your SSH port is different from 22, the command is `ssh -p YOUR_SSH_PORT YOUR_LOGIN_USER@YOUR_SERVER_IP`. Replace all three placeholders with your provider’s values. With a key file, follow the provider’s instructions for selecting it.

On the first connection, SSH shows a **host fingerprint**, an identifier for the server’s SSH key. Compare it with the provider’s console when available, then accept the matching key. Enter the password at the prompt; nothing appears while you type. Keep the password out of commands and screenshots.

Once you see the server’s command prompt, you’re logged in. **root** means the server’s administrator; it is a username, not a password.

If login fails or stalls, check the hosting company’s web console and login details before continuing. None of the installation commands below can run until you are connected.

The installer needs a download tool and trusted website certificates. We’ll refresh Ubuntu’s package list and install those two small prerequisites now. Run these commands **in the server’s SSH terminal**, as root:

```bash
apt update
apt install -y curl ca-certificates
```

**Check:** both commands finish without an error and the server prompt returns. You’re ready to download the installer.

## 3. Install 3x-ui

Now we’ll add the dashboard that lets you create VPN accounts in a browser. The official installer puts the dashboard and the VPN program on the server. The first command downloads it; the second runs it and selects dashboard version **3.8.5**, which matches the buttons in this guide.

Run these in **the same server terminal**:

```bash
curl -fL https://raw.githubusercontent.com/MHSanaei/3x-ui/v3.8.5/install.sh -o /tmp/3x-ui-install.sh
bash /tmp/3x-ui-install.sh v3.8.5
```

### Save the installer’s login details

The installer will give you a browser address and a separate login for the dashboard. Save them so you can manage the VPN later without running the installer again.

When it asks for settings:

1. If asked for a database, keep **SQLite**. It stores your account settings locally, so you don’t need to set up another database service.
2. Choose an unused panel port, for example **27297**, when offered. A port is a numbered network entry point. This one is for managing the server, not for VPN traffic.
3. If asked about SSL/certificates, choose **Skip SSL / HTTP only**. This guide opens the panel using `http://`.
4. Save the printed **panel port, URL path, username, and password** in a password manager. The panel credentials are different from your root/SSH login.

### Open the dashboard in your browser

The dashboard is installed on the server. Next we’ll make it reachable from your own browser and sign in, so the remaining account setup can happen through its forms.

**1. In the server terminal**, tell the dashboard to accept connections from outside the server. `0.0.0.0` is a listening setting, not a browser address. The second command restarts the dashboard so that setting takes effect:

```bash
/usr/local/x-ui/x-ui setting -listenIP 0.0.0.0
systemctl restart x-ui
```

**2. In your computer or phone’s browser**, open the saved address, using the server’s **public IP**:

```text
http://YOUR_SERVER_IP:YOUR_PANEL_PORT/YOUR_PANEL_PATH/
```

Replace the IP, port and path with the installer result. For example, with port **27297** and path **mypanel**, use `http://YOUR_SERVER_IP:27297/mypanel/`. If the installer’s path is just `/`, use `http://YOUR_SERVER_IP:27297/`.

Enter the **panel username and password**, then click **Login**. These are separate from the root/SSH password.

**Check:** the login page opens and accepts your panel credentials. Keep the SSH terminal open for the fail2ban installation below. The browser panel itself doesn’t depend on that terminal staying open. If the page doesn’t open, [use the panel connection checks](troubleshooting.md#the-dashboard-doesnt-open-in-the-browser).

### Install the VPN program version used in this guide

You should now be signed in to the dashboard. There are two programs on the server: **3x-ui** gives you this control panel, and **Xray** carries the actual VPN connection. The installer has already put both on the server. Here we’ll use the dashboard to install the Xray version that matches the rest of this walkthrough.

Before a website can load, the app and server exchange opening messages to start their encrypted connection. In our tests, Hiddify worked on Wi-Fi but failed on mobile data with a newer server version. **26.7.28** accepts the shorter opening message that worked on the tested mobile connection. We’ll select that message option when making your device links on the next page. [Why newer versions sometimes fail — optional advanced explanation](handshakes-and-versions.md#why-newer-versions-can-fail-on-some-networks).

**Use Xray 26.7.28 on every server in this guide:** the only server for a one-server VPN, or both Moscow and the foreign server for a two-server VPN. There’s one version to install and check.

**Already serving other users?** Save a panel backup and the original version number before switching; the change can briefly interrupt their connections. Check their connections again afterward.

**First check what’s installed.** In your browser, open the dashboard’s main status page. Find **Xray** and read the number beside its running/stopped status. That is the installed version of the VPN program, not the dashboard version.

If it already says **26.7.28** and **Running**, leave it alone. There’s nothing to reinstall.

**If the number is different, install 26.7.28:**

1. Click the version number beside **Xray**. It opens **Xray Updates**, where the dashboard can download and install another release for you.
2. In the **Xray** section, find **v26.7.28** and click the circle beside it. This selects the exact release used in the guide.
3. Check that the confirmation names **v26.7.28**, then click **Confirm**. Wait for installation to finish without refreshing the tab.
4. Look at the main status page again. It should now say **26.7.28** and **Running**.

The version change happens on the server. You don’t download another program onto your phone or PC for this step, and the dashboard itself stays on **3x-ui 3.8.5**.

If the version list is empty, the requested release is missing, or installation reports an error, keep the exact message and [check the server](troubleshooting.md#server-checks) before continuing. Don’t choose a different number just because it’s nearby in the list.

The older version is a compatibility choice, not a guarantee that every mobile network will work. [The phone test, opening-message sizes and security tradeoffs](handshakes-and-versions.md#match-the-client-option-to-the-server) are explained separately.

The dashboard and VPN program are ready. Before leaving the server terminal, we’ll add protection against repeated SSH password guesses. After that, we’ll create the VPN connection in the browser.

## 4. Protect SSH logins with fail2ban

A public server can receive repeated password guesses against its SSH login. We’ll install **fail2ban** to watch for those failures and temporarily ban the source addresses. This protects the administration login; it doesn’t configure the VPN connection.

The commands install it, start it now, and enable it after server reboots. Run them in **this server’s SSH terminal**, as root:

```bash
apt install fail2ban -y
systemctl start fail2ban
systemctl enable fail2ban
```

For two servers, repeat these installation commands on both Moscow and the foreign server. If fail2ban reports an error, [use its troubleshooting section](troubleshooting.md#fail2ban-is-installed-but-ssh-protection-isnt-active).

You can close the SSH terminal after finishing this page; the installed programs keep running.

**This server is ready when:** its panel opens, the VPN program shows the version selected above and **Running**, and SSH still works. For the two-server route, check that list for **both servers** before linking them.

**For one server:** [make your device connection links →](server-inbound.md)

**For two servers:** prepare the other dashboard too, then [return to linking the panels →](two-hop-vpn.md#how-the-two-3x-ui-panels-connect).
