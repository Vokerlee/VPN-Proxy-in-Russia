[← Guide index](../README.md) · Next: [Install the control panel](server-setup.md)

# Get the computer that will run your VPN

You do not need to buy a physical machine or leave a laptop running at home. You rent a small virtual server in a data center. Providers call this a **VPS**, **VDS**, or **cloud server**. For this guide, it is a remote Linux computer that stays online and carries your VPN traffic.

Your own computer remains as it is. You can rent and administer an Ubuntu server from Windows, Linux, or macOS.

## Choose a provider and a location

The original setup in this project used [HostVDS](https://hostvds.com/) for a server abroad. It is an example, not a requirement. Any provider with suitable Linux servers, a public IP, enough transfer allowance, and working access from your network can fit this guide.

Choose the location where you want traffic to leave the VPN, such as a European or US location offered by your provider. A nearby location may reduce latency, but an actual connection test is more useful than geography alone. Check current payment methods, included traffic, and whether the provider accepts customers from your location before purchasing.

A second server in Russia is **not needed** for the ordinary setup. The [optional sharing chapter](share-proxy.md) describes cases where an intermediate proxy host is useful. Do not buy two servers just because a diagram in an advanced chapter shows two machines.

## Create a small Ubuntu server

Provider dashboards use different labels, so use the matching action rather than expecting identical screenshots everywhere:

1. Register or sign in to the provider's website and add funds/payment details if required.
2. Open **Servers / Cloud / Instances** and choose **Create server**, **Create instance**, or **Order**.
3. Select the desired country or data center.
4. For the operating system, choose **Ubuntu Server**. A supported LTS release is a straightforward choice. Ubuntu 22.04 and 24.04 are examples; the guide does not require 24.04 specifically. Debian is another supported option for the optional setup helper, but this manual walkthrough uses Ubuntu commands.
5. Choose a small general-purpose plan. One CPU core, about 1 GiB RAM, and around 10 GiB disk are reasonable starting values for a personal setup. Actual capacity depends on load and the panel version.
6. Include a **public IPv4 address** and check the traffic allowance. You need an address your devices can reach from the internet, not only a private-network address.
7. If offered, select a root password or an SSH key that you know how to use. Save the login information privately.
8. Click **Create / Deploy / Order** and wait until the server shows **Running / Active**.

You do not need Windows Server, a desktop environment, a hosting control-panel bundle, a GPU, or a domain name for the basic VPN. The server's Ubuntu version and your laptop's operating system are separate choices.

If you already have a server with other software or files, do not reinstall its operating system to follow this guide. Check the existing installation and available ports, then add only what is needed.

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

You are ready when the server is running and you have its IP and login method. Continue with [connecting to it and installing the panel](server-setup.md#2-connect-over-ssh).

## A firewall note before leaving the provider dashboard

A **firewall** decides which incoming connections the server accepts. Some providers put an extra one in their web dashboard, often called **Firewall**, **Security group**, or **Network rules**.

Keep the supplied SSH access allowed. Later, you will allow the actual VPN TCP port chosen during setup, usually 443 or 8443. If you use a public browser panel, its separate access rule and HTTPS setup matter too. The next chapter explains those ports when you reach them; there is no need to open every port in advance.

## Provider references

- [HostVDS website](https://hostvds.com/) and [knowledge base](https://hostvds.com/knowledge/1)
- [Ubuntu cloud-server tutorial](https://ubuntu.com/tutorials/launch-and-terminate-cloud-instances), for readers who want to understand the underlying cloud terminology

Provider forms and billing offers change. The actions above describe the task; consult the selected provider's current instructions for its exact form labels.
