# Set up your own VPN

This guide takes you from having nothing set up to connecting your computer or phone through your own server in another country.

The idea is simple: your device connects to that server, and the server connects to websites for you. You control the server and the accounts that can use it. Network filtering can still affect the connection; the guide includes checks to help you find and fix problems.

## What you need

- **A computer for the initial setup.** Windows or Linux both work; you do not need to install Linux on your Windows computer. You can connect a phone afterward too.
- **A rented Linux server**, often called a **VPS**. This is a small computer running in a provider's data center. You pay the provider to keep it running. **If you do not have one, start with Step 1 below.**
- **The server's login details.** The provider supplies an IP address and either a password or an SSH key. The main administrator account is usually called **root**. You get these details after creating the server.

We use Ubuntu as the server's operating system. You do not need one specific Ubuntu version: choose a supported release available from your provider. The version used for the examples is not a requirement for your own computer or server.

## Follow these steps in order

### 1. Get a server

Choose a provider, select a location outside the network restrictions you want to avoid, and create a small server with Ubuntu. The walkthrough explains what to select and which login details to save.

**[Start here: choose and create your server →](docs/choose-server.md)**

Already have a suitable server? Continue with Step 2.

### 2. Install the server's control panel

The control panel is a website on your server where you can create connection accounts and change settings. We use a free panel called **3x-ui**.

You will connect to the server through **SSH**, a secure way to administer it from a terminal, run the installation commands, and open the panel in your browser. The walkthrough shows the commands for both Windows and Linux and explains the installer prompts.

**[Install 3x-ui and open it in your browser →](docs/server-setup.md)**

### 3. Create your connection account

In 3x-ui, click **Inbounds → Add Inbound** and fill in the settings shown in the guide. An *inbound* is the server entry point that accepts your device's connection.

The guide uses a connection type called **VLESS + REALITY**. You can follow its field-by-field instructions without learning the protocol first.

When you finish, the panel gives you a **connection profile**: a link containing the server address and the account's connection settings. You will import that link into the app on your device.

**[Create the account and copy its connection link →](docs/server-inbound.md)**

![3x-ui: choose Inbounds and click Add Inbound](images/3x-ui-add-inbound.svg)

### 4. Connect your computer or phone

You now need an app on your device to use the profile. We use **Hiddify**, a free VPN/proxy client available for Windows, Linux, macOS, Android, and iOS.

Install it, import your connection link using **+ → Add from clipboard**, select the profile, and connect. The guide explains which connection mode to choose, what each setting does, and how to check that websites see your server's address.

**[Install Hiddify and make your first connection →](docs/clients.md)**

![Hiddify: add a profile from the clipboard and select it](images/hiddify-import.svg)

Already received a working connection profile from someone else? You can start at this step; you do not need to rent or configure another server.

## If something does not work

Start with [the troubleshooting guide](docs/troubleshooting.md). It helps you distinguish a blocked server port, an incompatible client, a wrong profile, and a Windows proxy setting that still points at another app.

Two common follow-up questions have their own illustrated pages:

- [Make websites see the server's IPv4 address](docs/force-ipv4.md).
- [Understand the ports and what the Connect button changes](docs/ports-and-modes.md).

## Optional shortcuts and deeper reading

**Scripts are optional.** Everything above can be done manually. If you prefer a helper to prepare a new server from its IP and root login, use the [optional automatic setup walkthrough](docs/quick-start.md). The [automation guide](docs/automation.md) explains each helper before you run it.

For other setups:

- [Use Xray directly on a Linux machine](docs/linux-xray.md).
- [Let another device use your proxy](docs/share-proxy.md).
- [How Xray, REALITY, and routing work—for programmers and network engineers](docs/xray-internals.md).

The UI examples were checked with 3x-ui 3.8.5 and Hiddify 5.5.5. Pictures are labeled navigation diagrams, not captured screenshots. Button positions may change between versions; the linked walkthroughs include alternatives.
