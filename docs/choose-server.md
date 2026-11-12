[← Single-server overview](single-server.md) · Step 1 of 4

# Get the computer that will run your VPN

You do not need to buy a physical machine or leave a laptop running at home. You rent a small virtual server in a data center. Providers call this a **VPS**, **VDS**, or **cloud server**. For this guide, it is a remote Linux computer that stays online and carries your VPN traffic.

The server’s **IP address** is its numeric address on the internet. **root** is its administrator account. **SSH** is the secure terminal connection you will use to manage it; an SSH key can be used instead of a login password.

Your own computer remains as it is. You can rent and administer an Ubuntu server from Windows, Linux, or macOS.

**Do this page only if you need a server.** Already have a running Ubuntu server and its login details? Skip this page and [open Step 2: install or open the dashboard](server-setup.md).

For one server, rent a machine abroad. For two servers, rent one in Russia and one abroad. Choose the provider for each role below, then save their login details separately.

For the [two-server path](two-hop-vpn.md), rent both the Moscow entry and foreign exit, and save each server's login separately. Return to that path for its provider-specific IPv6 checks and panel-linking steps. For the [single-server path](single-server.md), one foreign server is enough.

## Choose a provider and a location

The original setup in this project used **HostVDS for the foreign server**. For the two-server setup, you also need somewhere to rent the Russian server.

| Server you need | Where to rent it |
|---|---|
| One-server VPN, or the foreign half of the two-server route | [HostVDS](https://hostvds.com/) or another provider with a suitable location abroad |
| Russian entry server for the two-server route | [FirstVDS](https://firstvds.ru/products/vds_vps_hosting), choosing **Moscow**, or another provider with servers physically in Russia |

**HostVDS doesn’t list a Russian location**, so don’t look there for the Moscow server. Use it for the foreign part of the route. [HostVDS’s published regions](https://hostvds.com/knowledge/1)

**HostVDS and FirstVDS are different companies.** FirstVDS offers Moscow locations as well as locations abroad, so check you’ve selected **Moscow** when ordering the Russian entry. [FirstVDS locations](https://firstvds.ru/technology/data-centry-firstvds)

These are examples used by this guide. Another provider with a suitable Linux server, public IP, enough included traffic and working access from your network can also fit.

Choose the location where you want traffic to leave the VPN, such as a European or US location offered by your provider. A nearby location may reduce latency, but an actual connection test is more useful than geography alone. Check current payment methods, included traffic, and whether the provider accepts customers from your location before purchasing.

For one server, choose a country abroad. For two servers, rent one in Russia and one abroad; the example uses Moscow and the Netherlands (**NL**). Before paying for the two-server route, check that **both plans include IPv6** and that the providers explain how to configure it. IPv6 is a second kind of internet address used for the connection between these servers. [Compare the routes](../README.md#one-server-or-two)

Check the total recurring price, including any extra charge for IPv4, traffic and tax. Keep the server while you use the VPN; deleting your local setup folder does not cancel its rental. To stop paying later, follow the hosting company’s cancellation or deletion procedure.

## Rent the Russian server: FirstVDS example

**For the two-server route only.** If you’re setting up one server abroad, skip to the HostVDS example below.

1. Open [FirstVDS’s VPS plans](https://firstvds.ru/products/vds_vps_hosting) and start a server order.
2. Choose **Moscow** as the location. This will be the server your phone connects to first.
3. Choose a small plan and **Ubuntu** as the operating system. Use a plain server image; we’ll install 3x-ui, the VPN dashboard, ourselves.
4. Check that you’ll have a **public IPv4 address** and can get an **IPv6 address** for this server. IPv6 may be a separate option or charge; confirm it before paying.
5. Finish the order and save the server’s IP address, SSH login and password or key. Save its assigned IPv6 details too. [Which details to keep](#save-the-details-you-will-use-next)

You’ll configure IPv6 using FirstVDS’s instructions after the server is running. The foreign server needs its own working IPv6 too. The two providers may use different network settings; don’t copy one server’s configuration onto the other.

Then rent the foreign server below, or use the foreign server you already have.

## Create one server: HostVDS example

**This example rents the foreign server**, for either setup. Use [HostVDS](https://hostvds.com/) if its locations and plans fit your needs. The provider's [own walkthrough](https://hostvds.com/knowledge/6) uses this creation flow:

1. Sign in, open **Servers**, and click **New Instance**.
2. Choose an available European or US region for the VPN exit. Check the current region list; you do not need one particular city.
3. Choose a small configuration—for a first personal setup, around **1 CPU / 1 GB RAM / 10 GB disk** is a starting point. Check the selected plan's current transfer allowance and public IPv4 option.
4. Select **Operating Systems → Ubuntu**. Use a supported release offered there; 24.04 is not mandatory.
5. Click **Deploy** and wait for the server to show as running in **Servers**.
6. Open its access details and check your registration email for the IP and root credentials.

Choose the plain Ubuntu operating-system image for the manual installation in this guide. HostVDS also offers application templates that may include 3x-ui already. If you deliberately use one, follow its supplied panel access instructions and skip reinstalling a panel that already exists.

If no root password arrives, HostVDS documents **Servers → Actions: Security → Change root password → Save new password** in its [access troubleshooting guide](https://hostvds.com/knowledge/7). Keep the resulting password private.

<details>
<summary>Using another provider? Open these alternative creation steps. Skip if you already created your server.</summary>

Use these instead of the HostVDS steps, then continue with “Save the details” below:

1. Register or sign in to the provider's website and add funds/payment details if required.
2. Open **Servers / Cloud / Instances** and choose **Create server**, **Create instance**, or **Order**.
3. Select the desired country or data center.
4. For the operating system, choose **Ubuntu Server**. A supported LTS release is a straightforward choice. Ubuntu 22.04 and 24.04 are examples; the guide does not require 24.04 specifically. Debian is another supported option for the optional setup helper, but this manual walkthrough uses Ubuntu commands.
5. Choose a small general-purpose plan. One CPU core, about 1 GiB RAM, and around 10 GiB disk are reasonable starting values for a personal setup. Actual capacity depends on load and the panel version.
6. Include a **public IPv4 address** and check the traffic allowance. You need an address your devices can reach from the internet, not only a private-network address.
7. If offered, select a root password or supply your SSH public key if that is your usual login method. Save the login information privately.
8. Click **Create / Deploy / Order** and wait until the server shows **Running / Active**.

You do not need Windows Server, a desktop environment, a hosting control-panel bundle, a GPU, or a domain name for the basic VPN. The server's Ubuntu version and your laptop's operating system are separate choices.

If you already have a server with other software or files, do not reinstall its operating system to follow this guide. Check the existing installation and available ports, then add only what is needed.

</details>

## Save the details you will use next

Open the new server's **Details / Access / Credentials** page. The provider may also email them. You need:

| Detail | Example or meaning |
|---|---|
| Public IPv4 | The server's numeric address, such as `203.0.113.10` in documentation |
| Login user | Often `root`; some providers use an account such as `ubuntu` |
| Password or SSH key | The credential for that user |
| SSH port | Usually `22`, unless the provider says otherwise |
| Provider web console | Useful if a later network setting prevents a normal login |

`root` is the administrator account, not a password. A provider that creates an `ubuntu` user and an SSH key does not necessarily enable root-password login; follow the supplied access method instead of repeatedly guessing a root password.

## A firewall note before leaving the provider dashboard

A **firewall** decides which incoming connections the server accepts. Some providers put an extra one in their web dashboard, often called **Firewall**, **Security group**, or **Network rules**.

Keep the supplied SSH access allowed. Later, you will allow the actual VPN TCP port chosen during setup, usually 443 or 8443. The browser dashboard will use its own separate port. The next chapter explains those ports when you reach them; there is no need to open every port in advance.

## Provider references

- [HostVDS website](https://hostvds.com/) and [published regions / knowledge base](https://hostvds.com/knowledge/1)
- [FirstVDS VPS plans](https://firstvds.ru/products/vds_vps_hosting) and [Moscow data centres](https://firstvds.ru/technology/data-centry-firstvds)
- [Ubuntu cloud-server tutorial](https://ubuntu.com/tutorials/launch-and-terminate-cloud-instances), for readers who want to understand the underlying cloud terminology

Provider forms and billing offers change. The actions above describe the task; consult the selected provider's current instructions for its exact form labels.

**Step 1 is complete when:** your server is running and you have its IP address and login method.

**For one server:** [install and open its dashboard →](server-setup.md)

**For two servers:** rent the second server too, then [return to the IPv6 checks →](two-hop-vpn.md#1-configure-ipv6-yourself-using-your-vps-providers-instructions).
