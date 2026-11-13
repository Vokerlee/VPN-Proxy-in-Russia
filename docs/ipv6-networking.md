[← Two-server walkthrough](two-hop-vpn.md)

# IPv6 configuration details

Use this reference if the hosting company’s IPv6 setup needs more explanation, or if the connection between the servers fails. The normal two-server walkthrough asks you to configure each server using its own provider’s instructions. These commands are for investigating that configuration, not a list every beginner must run.

Moscow and the foreign server each need an assigned IPv6 address and a working route. Addresses, prefixes, gateways and network tools differ between providers. Run the commands below only in the SSH terminal of the server you are configuring.

Different VPS providers require different configuration. Do not assume a configuration that works on one VPS works on another:

| Item | What to get from this server's provider |
|---|---|
| Activation | Whether IPv6 must first be enabled in the provider dashboard |
| Address | The exact assigned host address, not only the subnet |
| Prefix | The assigned prefix length, such as /64 or /124 |
| Gateway | The actual gateway; it may be global or link-local |
| Interface | The guest's interface name, such as eth0 or ens3 |
| Network manager | Netplan/networkd, NetworkManager, ifupdown or provider tooling |
| Firewall | IPv6 rules are separate from IPv4 rules in some tools |

A /124 contains **16 addresses**. A subnet allocation is not proof that the guest OS already has an address or route.

Open PowerShell or a terminal on your computer and connect using `ssh YOUR_LOGIN_USER@YOUR_SERVER_IP`. Replace both placeholders with that server’s login details. Add `-p YOUR_SSH_PORT` after `ssh` if the provider uses a custom port. [First SSH login, explained](server-setup.md#2-connect-over-ssh)

Run these commands after logging in to **each server**. They show its addresses, IPv6 routes and whether it has Netplan configuration files. Netplan is one tool Ubuntu uses to configure networking; a missing directory may simply mean your server uses another tool.

```bash
ip -br address
ip -6 route
ls /etc/netplan
```

Follow the provider's instructions for that server and operating system. For example, [MVPS's IPv6 instructions](https://www.mvps.net/docs/how-to-enable-ipv6-for-your-mvps-server) describe an assigned /124 and gateway fe80::1. That is a provider-specific example, not a universal gateway.

### Example only: an Ubuntu server using Netplan

Ubuntu 26 and other Netplan-based servers may use /etc/netplan/00-installer-config.yaml, a cloud-init file, or another filename. Inspect the existing configuration and use its actual interface. Preserve its existing IPv4 address, gateway and nameservers.

The following values are documentation placeholders. Replace every address and gateway with the provider's values:

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: false
      dhcp6: false
      accept-ra: false
      addresses:
        - 203.0.113.20/24
        - 2001:db8:2::1/124
      routes:
        - to: default
          via: 203.0.113.1
        - to: "::/0"
          via: fe80::1
      nameservers:
        addresses:
          - 8.8.8.8
          - 2001:4860:4860::8888
```

Back up the current file and keep the provider console available when changing networking. Validate with `sudo netplan generate`. Use `sudo netplan try` for a timed confirmation when supported, or the provider's documented `sudo netplan apply` procedure. These are manual administration steps; the relay helper does not run them. See [Netplan's configuration reference](https://netplan.readthedocs.io/en/latest/netplan-yaml/).

Do not copy this YAML onto an ifupdown or NetworkManager installation. Those need their own configuration.

### Check both IPv6 internet access and the server-to-server route

On both servers:

```bash
curl -6 --noproxy '*' --connect-timeout 5 --max-time 15 https://www.cloudflare.com/cdn-cgi/trace
```

Run the check separately in **Moscow’s SSH terminal** and **NL’s SSH terminal**. Both must return an IPv6 address on the `ip=` line. If the command times out, check the provider’s address, gateway and IPv6 firewall for that server. If the VPN still fails after creating the NL relay inbound, use [the server-to-server connection investigation](network-path-debugging.md#2-separate-server-access-from-account-authentication).

## After configuring both servers

Return to [installing the two dashboards](server-setup.md) or [linking them](two-hop-vpn.md#how-the-two-3x-ui-panels-connect) if they are already installed.
