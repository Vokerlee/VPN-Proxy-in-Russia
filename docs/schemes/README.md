[← Start here](../../README.md) · [Set up the two servers](../two-hop-vpn.md)

# A map of the VPN

If you’re wondering which machine does what, start here. A **server** is a rented computer that stays online. The **client** is Hiddify on your phone or computer. A **connection link** tells the client which server to contact and which account to use.

With one server, your device talks to the server abroad. With two, it talks to a Russian server first. The examples below use **Moscow** in Russia, **NL** for the Netherlands, **FR** for France and **FI** for Finland. IPv4 and IPv6 are two kinds of internet address; the two-server route uses IPv6 for the middle connection.

## Follow one request

**One server means one VPN connection. Two servers mean two VPN connections in a row.** Here’s where each one ends:

```text
            One server                           Two servers
         1 VPN connection                     2 VPN connections

         Your phone / PC                       Your phone / PC
                |                                     |
                | VPN over IPv4                       | VPN 1 over IPv4
                v                                     v
      Your internet provider                Your internet provider
                |                                     |
                v                                     v
        Internet networks                     Internet networks
                |                                     |
                v                                     v
+--------------------------------+    +--------------------------------+
|       Your server abroad       |    |     Your server in Russia      |
|    VPN connection ends here    |    |    VPN 1 ends; VPN 2 starts    |
+--------------------------------+    +--------------------------------+
                |                                     |
                v                                     | VPN 2 over IPv6
   Hosting provider / internet                        v
                |                        Hosting providers / internet
                v                                     |
             Website                                  v
                                      +--------------------------------+
                                      |       Your server abroad       |
                                      |        VPN 2 ends here         |
                                      +--------------------------------+
                                                      |
                                                      | IPv4
                                                      v
                                         Hosting provider / internet
                                                      |
                                                      v
                                                   Website
```

The boxes mark the servers you rent. Internet providers and other networks carry the connections in both layouts. The arrows show the request going out; replies come back through the same stages.

With **one server**, Hiddify opens an encrypted VPN connection to the server abroad. That server opens the website connection.

With **two servers**, Hiddify opens **VPN 1** to the Russian server. That server opens **VPN 2** to the foreign server and passes the traffic into it. The foreign server opens the website connection. You still press **Connect once** in Hiddify; the Russian server handles the second VPN.

In our example, the Russian server is Moscow and the foreign server is NL. VPN 1 uses **IPv4, VLESS + RAW + REALITY + Vision**. VPN 2 uses **IPv6, VLESS + XHTTP + REALITY**, with an empty flow. These are the settings used in [the two-server form steps](../two-hop-vpn.md#on-nl-create-the-relay-account).

The first connection uses a Yandex target name and Safari fingerprint. The second uses a Google target name and Chrome fingerprint. Those describe connection setup, not which websites you can visit. The phone’s classical setting must match the entry server’s version. [Handshake versions](../handshakes-and-versions.md)

## Where each link goes

An **inbound** accepts traffic into a server. An **outbound** sends it on. You’ll see these names in 3x-ui, the browser dashboard for managing the VPN. A **routing rule** connects an inbound or account to the outbound it should use.

```text
      Server-to-server link                      Device link

+--------------------------------+    +--------------------------------+
|        NL relay account        |    |     Moscow device account      |
+--------------------------------+    +--------------------------------+
                |                                     |
                | Copy link                           | Copy link
                v                                     v
+--------------------------------+    +--------------------------------+
|        Moscow outbound         |    |   Hiddify on your phone / PC   |
+--------------------------------+    +--------------------------------+
                |
                v
  Select it in the routing rule
```

The **relay link** gives Moscow the credentials for VPN 2. The **device link** gives Hiddify the credentials for VPN 1. Keep each device’s account separate, such as `desktop` and `phone`.

In Moscow’s **Routing** page, send traffic from the Moscow device inbound to the outbound named `relay-nl`. [The panel steps](../two-hop-vpn.md#how-the-two-3x-ui-panels-connect)

## Add a country

```text
+--------------------------------+
|    Moscow: VPN 1 ends here     |
|     Account chooses VPN 2      |
+--------------------------------+
      |
      +-- Port 443, NL account ----> [ NL server ]
      |
      +-- Port 443, FR account ----> [ FR server ]
      |
      +-- Port 8443, FI account ---> [ FI server ]
```

Each country profile uses Moscow plus **one** foreign server, so it still has **two VPN connections**. Choose the NL, FR or FI profile in Hiddify to pick that route.

This shows account routing only. Hosting providers and internet networks carry each server-to-server connection, as in the full route above.

This is the layout once all three exits are configured. On shared port 443, Xray matches the authenticated account label to its outbound. For example, NL and FR accounts such as `desktop` and `FR-desktop` use the same port and go to different exits. The helper creates a separate inbound by default. Use `--shared-entry` with distinct country account labels to add the user-based rule on an existing RAW entry. [Xray routing reference](https://xtls.github.io/en/config/routing#ruleobject)

## Find the link that stopped working

| Check | What you want to find out |
|---|---|
| Device → Moscow, VPN 1 | Can the device reach the entry port and connect using its account? |
| Moscow → foreign IPv6, VPN 2 | Can Moscow connect using the relay account? |
| Foreign server → website | Does a website load and show the expected foreign exit address? |

Test the connections in order. If the TCP port times out, check the address, route and firewall before changing fingerprints. [Reachability checks](../network-path-debugging.md)

## One server is also a complete setup

The left-hand route above needs one panel and one device link per phone or computer. It uses one VPN connection. The normal IPv4 setup doesn’t require IPv6 on your devices or network. [Single-server walkthrough](../single-server.md)

## What the second server adds

To build the right-hand route above, rent **Moscow from FirstVDS and the foreign server from HostVDS** in our example. They are two separate servers and two bills. After renting Moscow, you still need to [rent the foreign server](../choose-server.md#rent-the-foreign-server-hostvds-example) unless you already have it.

You can use the foreign server’s IPv6 address **without needing IPv6 on your phone or home network**. The phone reaches Moscow over IPv4, and Moscow opens the IPv6 connection. With a direct one-server IPv6 profile, both your device and the network it’s currently using would need working IPv6. Device support alone isn’t enough, and switching networks can change whether that connection works. A one-server profile using IPv4 doesn’t have this requirement.

The nearby entry and foreign exit give you two independently testable connections. Your phone reaches Moscow; Moscow reaches the exit over its configured IPv6 route. Add another country by creating another foreign relay account and a matching Moscow outbound.

In our tests, the IPv6 route was usable while the IPv4 route to the same foreign host failed. That is evidence for testing both address families on your own providers. A Russian entry can still be filtered, and we have no measured reduction in blocking probability for IPv6 or for the two-server design.

The extra server adds cost, another panel and another possible failure point. First verify phone → Moscow, then Moscow → foreign IPv6, then the foreign IPv4 exit. XHTTP between servers changes the middle connection. A phone's initial REALITY handshake is still part of the first connection.

**Ready to set it up?** Choose [one server](../single-server.md) or [two servers](../two-hop-vpn.md). If you haven’t rented anything yet, [start with the rental page](../choose-server.md).

## Why this can help with filtering

Your home or mobile provider sees the device connecting to the Russian server. The foreign server is the destination of a separate connection made by that server. The design aims to make direct foreign VPN use less obvious at the device’s first hop; it doesn’t establish that the traffic looks harmless to every filtering system. The hosting and transit networks can still observe the server-to-server connection.

IPv4 and IPv6 addresses are separate destinations. Blocking one IPv4 address doesn’t automatically block the same server’s IPv6 address, although an operator can block both or filter the protocol itself. Our recorded IPv6 success is a reason to test that route, rather than evidence that Russia generally leaves IPv6 unblocked.

Research has found differences between IPv4 and IPv6 censorship. However, the **ProtoScan** study’s method didn’t measure IP-address blocking and missed much of Russia’s provider-level censorship. It therefore doesn’t support a claim that IPv6 VPN addresses are usually unblocked in Russia. [ProtoScan: Measuring censorship in IPv6, methodology and Russia findings](https://hammas9.github.io/pdfs/foci.pdf)
