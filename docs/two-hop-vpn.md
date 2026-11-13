[← What a VPN does](../README.md) · [One-server setup](single-server.md)

# Connect through Russia to a server abroad

We’ll make two VPN connections work together. Your phone connects to a server in Russia. That server connects to your server abroad, which opens websites for you. You’ll still press **Connect once** in Hiddify.

Our example uses **Moscow**, rented from FirstVDS, and the **Netherlands**, rented from HostVDS. We call the Netherlands server **NL** below. If yours is in another foreign country, use that server’s addresses in the same steps.

```text
        Your phone / PC
               |
               | VPN 1 over IPv4
               v
     Your internet provider
               |
               v
+--------------------------------+
|       Moscow / FirstVDS        |
|     VPN 1 ends; VPN 2 starts    |
+--------------------------------+
               |
               | VPN 2 over IPv6
               v
 Hosting providers / internet
               |
               v
+--------------------------------+
|   Foreign server / HostVDS     |
|          VPN 2 ends            |
+--------------------------------+
               |
               | IPv4, through its hosting network
               v
            Website
```

Your provider carries the first encrypted connection; the servers’ providers carry the second. **Your phone doesn’t need IPv6.** IPv6 is used only between the rented servers.

You need **both rentals**. First [rent Moscow from FirstVDS](choose-server.md#rent-the-russian-server-firstvds-example), then [rent the foreign server from HostVDS](choose-server.md#rent-the-foreign-server-hostvds-example). Buying Moscow alone doesn’t give it a connection abroad. If you already own one suitable server, rent only the missing one.

We’ll prepare their addresses, install a dashboard on each, then set up the foreign server before Moscow. That order matters: Moscow needs a connection link from the foreign server before it can send traffic there.

## 1. Configure IPv6 yourself using your VPS provider's instructions

The two servers need a way to reach each other. We use **IPv6**, an internet address with colons, such as `2001:db8:2::1`. Your device reaches Moscow using **IPv4**, the dotted address supplied by the provider.

The hosting companies may set up IPv6 differently. For each rented server, open its provider’s control panel, get the assigned IPv6 details and follow that provider’s activation instructions. Some images already have it working; others need an operating-system change or help from support. The scripts don’t configure IPv6 for you.

Save these addresses in two separate private notes:

| Note | Addresses you’ll use |
|---|---|
| **Moscow — FirstVDS** | Public IPv4 for your devices; assigned IPv6 for the connection to NL |
| **NL — HostVDS** | Public IPv4 for opening its dashboard; assigned IPv6 for receiving Moscow’s connection |

You’ll enter the actual **host address**, without its subnet suffix. For example, if the provider shows `2001:db8:2::1/64`, the address to enter in the VPN forms is `2001:db8:2::1`. The example isn’t a real address to copy.

IPv6 activation and network configuration remain your task, using each provider’s instructions. The [separate IPv6 reference](ipv6-networking.md) explains network files if you need that help. Nothing on your phone needs changing for this step.

## 2. Install a dashboard on each server

Right now these are two rented computers. We need a way to create their VPN connections and accounts. **3x-ui** provides a dashboard you open in a browser, so most of the work below will be clicking forms.

1. Follow [installing the dashboard](server-setup.md) on **Moscow**, using its IPv4 login details.
2. Follow the same page on **NL**, using NL’s different IPv4 login details.
3. Save each panel’s full browser address, username and password in that server’s private note. These panel logins are separate from the SSH logins used to install them.

That installation page also explains **Xray**, the program carrying the VPN traffic, and shows how to install **26.7.28**. Use **26.7.28 on both servers**.

Open both dashboards in separate browser tabs. Name the tabs or bookmarks **Moscow** and **NL**. Use each server’s saved public address:

```text
http://SERVER_PUBLIC_IP:PANEL_PORT/PANEL_PATH/
```

Every action below says which tab to use. Stay in that tab until the instructions say to switch. You should now have both dashboards open, with **26.7.28** and **Running** on their Overview pages.

If you prefer scripts, complete the IPv6 setup first, then open [the optional automation section](#optional-preview-and-apply-the-relay-helper). It creates the connections described below; you won’t need to repeat those forms manually.

## How the two 3x-ui panels connect

The panels don’t discover or link to one another automatically. We’ll create a receiving account on NL, then give its connection link to Moscow. That is **VPN 2**.

Then we’ll create phone and computer accounts on Moscow and tell Moscow to send their traffic through VPN 2. Those device accounts are **VPN 1**.

The dashboard calls a receiving connection an **inbound**, a sending connection an **outbound**, and the instruction joining them a **routing rule**. We’ll use each of those screens when we reach it.

### On NL, create the relay account

**Use the NL browser tab for this whole section.** We’re preparing NL to receive a connection from Moscow. Your phone accounts come later, on Moscow.

#### Create the place where Moscow connects

We’ll make an inbound at NL’s assigned IPv6 address. A **port** is the number identifying this entry point on the server. Use **443** here: it is the usual HTTPS port. **8443** is a common HTTPS alternative and can carry the same VPN setup. These familiar web ports fit REALITY’s browser-like connection setup, but the number alone doesn’t disguise traffic.

1. In NL’s left sidebar, click **Inbounds**. On a narrow screen, open the sidebar using the menu button first.
2. Click **Add Inbound**. A form opens with tabs such as **Basics**, **Stream** and **Security**.
3. In **Basics**, fill in these fields:

| Field | Enter |
|---|---|
| **Enable** | Off while you fill in the connection |
| **Remark** | `Relay nl` — the name you’ll recognize in the dashboard |
| **Protocol** | `vless` — the connection format used by this guide |
| **Address** | NL’s assigned IPv6 address, without brackets or `/64` |
| **Port** | `443` |
| **Share address strategy** | **Custom** |
| **Custom share address** | The same NL IPv6 address, without brackets or a port |
| **Disable XTLS flow** | On for this XHTTP relay |

**Address** tells NL where to accept connections. **Custom share address** tells the panel what address to write into the connection link. We set both explicitly so Moscow receives the IPv6 address, even though you opened the dashboard over IPv4.

Leave the form open. We still need to choose how this connection carries and protects the traffic.

#### Set up the encrypted connection

A **transport** is the way a VPN carries its traffic. **RAW**, also called TCP, sends it directly over a TCP connection. **XHTTP** packages it into HTTP requests and streams. Both can use REALITY encryption; neither is a guarantee against blocking.

We’ll use **XHTTP** between the servers because that is the relay mode tested in this guide. Your phone will use RAW to Moscow, so it doesn’t need to use the same transport as this second connection. **REALITY** protects the inter-server connection. There is no extra app to install.

1. In the same inbound form, click **Stream**.
2. Set **Network** to **XHTTP**. The XHTTP fields appear.
3. Set **Path** to `/relay-nl` and **Mode** to `auto`. The path is a connection setting both servers must share; it isn’t a folder you need to create.
4. Click **Security** and select **REALITY**.
5. Fill in:

| Field | Enter |
|---|---|
| **Target** | `www.google.com:443` |
| **SNI** | `www.google.com` |
| **uTLS** | `chrome` |

The target website is used during REALITY connection setup. It doesn’t restrict which websites you can visit later. **uTLS** shapes the first connection message to resemble a browser’s; `chrome` doesn’t require installing Chrome on either server.

REALITY also needs keys so Moscow can recognize your server:

6. Click **Get New Cert** below the key fields. In 3x-ui 3.8.5 this button generates the REALITY key pair. It doesn’t ask you to buy a certificate or domain. You should see **Public Key** and **Private Key** filled in.
7. Keep the generated **Short IDs**. If that field is empty, use the circular regenerate button beside it to generate them. These values will be included in the exported link.
8. Leave other settings unchanged and click **Create** at the bottom of the form.

You should now see **Relay nl** in NL’s Inbounds list. The receiving connection exists, but Moscow doesn’t have an account for it yet.

#### Give Moscow its own account

The inbound is a shared entry point. An account supplies the credentials needed to use it. We’ll create one named **relay-nl** for Moscow. This name is just a label, not an email address or Linux login.

In this panel version, accounts are created through **Clients**, separately from the inbound form:

1. In NL’s sidebar, click **Clients**, then **Add Client**.
2. On **Basics**, replace the generated **Email** value with `relay-nl`.
3. In **Attached inbounds**, select **Relay nl**. This is what connects the account to the inbound you just created.
4. Leave the account’s **Enable** switch on. For the initial setup, keep **Traffic Limit (GB)** and **IP Limit** at `0` and leave expiry unset; this avoids a test connection stopping because of a new limit.
5. Open **Credentials**. Keep the generated **UUID**; it is the account’s private identifier.
6. For this XHTTP connection, leave **Flow** empty/None if the field is shown. It does not use Vision.
7. Click **Create**.

The **Clients** page should now show **relay-nl**, enabled and attached to **Relay nl**. Keep its credentials private.

#### Make NL open websites using IPv4

Moscow will reach NL over IPv6, but we want the website connection leaving NL to use IPv4. Those are separate connections, so receiving over IPv6 doesn’t decide the outgoing address.

1. In NL’s sidebar, click **Outbounds**.
2. Find the row with tag **direct** and protocol **freedom**. This is the connection NL uses to open websites.
3. Click that row’s **Edit** action.
4. On **Basics**, find **Strategy** / **Domain Strategy** and select **ForceIPv4**.
5. Click **Save Changes**. Apply the settings or accept a restart if prompted.

NL will now choose IPv4 addresses when opening websites by name. We’ll also reject explicitly requested IPv6 destinations in the access rules below, to keep this relay’s exit on IPv4.

#### Let Moscow use the relay and block other sources

We know which machine should use this account: Moscow, at its assigned IPv6 address. We’ll add rules so this relay only forwards traffic from that source. Rules are checked in order, so the order below matters.

1. In NL’s sidebar, click **Routing**.
2. Open the **Routing Rules** tab, then click the **+ Routing Rules** button to create a rule.
3. In **Inbound tags**, select **Relay nl**. The list may show its generated tag beside the name. Selecting it means the rule applies to this relay, rather than all traffic on the server.

Create the following three rules, one at a time. Keep **Enable** on, leave unmentioned match fields empty, and click **Create** after filling each rule:

- **First rule — keep the website exit on IPv4.** Set **Comment** to `NL relay: block IPv6 destinations`, **IP** to `::/0`, and **Outbound tag** to `blocked`. Here **IP** means the destination address. `::/0` matches all IPv6 destinations.
- **Second rule — let Moscow reach websites.** Click **+ Routing Rules** again and select **Relay nl** under **Inbound tags** again. Set **Comment** to `NL relay: allow Moscow`, **Source IPs** to `MOSCOW_IPV6/128`, and **Outbound tag** to `direct`. Replace `MOSCOW_IPV6` with Moscow’s actual IPv6 host address. `/128` means this one address. Leave **IP** empty.
- **Third rule — reject other sources on this relay.** Add another rule for **Relay nl**. Set **Comment** to `NL relay: block other sources` and **Outbound tag** to `blocked`. Leave both **Source IPs** and **IP** empty, so it catches any remaining request on this inbound.

The `direct` and `blocked` choices refer to existing outbounds. `direct` opens the website connection; `blocked` rejects it. If the rejecting outbound has a different tag in your panel, select its blackhole outbound instead.

After creating the rules:

4. Use each rule’s **⋯ → Move up / Move down**, or its drag handle, to put these three rules in the order above, before broader rules that could match them. Keep the panel’s existing **api** rule in place.
5. Click **Save** on the routing page to apply the rule list. Accept a restart if the panel requests it.

The rule comments should now appear together in this order: **block IPv6 destinations → allow Moscow → block other sources**.

#### Save the link Moscow will use

NL now has a receiving connection and an account. We’ll turn that inbound on and copy its account link. The link contains the address and keys Moscow needs; you won’t need to copy those values separately.

1. Open **Inbounds** in NL’s sidebar. Edit **Relay nl**, turn **Enable** on and click **Save Changes**. Accept a restart if prompted.
2. Open **Clients**, find **relay-nl**, and click its **ⓘ Client Information** action.
3. In the information window, scroll to **Copy URL**. Find the VLESS link for **Relay nl** and click the **Copy** icon beside it. This is the connection link, not the dashboard URL or subscription URL.
4. Paste it into a private text file so you can use it in the other tab.

Its server address should be NL’s IPv6 address, written in brackets and followed by `:443`. For example, the address part has the shape `@[NL_IPV6]:443`. The brackets are added by the panel; you entered the host address without them.

**Keep this link for Moscow.** It doesn’t go into Hiddify. Next we’ll use it to create the sending connection on Moscow.

### On Moscow, connect the device inbound to NL

**Switch to the Moscow browser tab now.** NL is ready to receive VPN 2. We’ll make Moscow open it, then create the first connection for your devices.

#### Give Moscow the NL connection link

Moscow acts as a client for the second VPN connection, just as Hiddify acts as a client on your phone. Its **outbound** stores the settings used to connect to NL. Importing the link copies the account and keys correctly without typing them by hand.

1. In Moscow’s sidebar, click **Outbounds**.
2. Click **+ Outbounds** to open the new-outbound form.
3. Open the **JSON** tab. Paste the private NL relay link into the link field at the top and click **Import**. The JSON underneath is filled in automatically; you don’t need to edit it.
4. Switch to the form’s **Basics** tab. The imported values should now be available as ordinary fields.
5. Set **Tag** to `relay-nl`. This is the name we’ll select in the routing rule later.

We also need Moscow to use the source address allowed by NL’s rule, and keep this connection on IPv6:

6. Set **Send Through** to Moscow’s assigned IPv6 host address, without `/128`.
7. Set **Target Strategy** to **ForceIPv6**. This selects IPv6 for the connection to NL.
8. In the imported server fields, keep NL’s **IPv6 address** and **443** port. Keep the imported UUID, public key and short ID.
9. Find the outbound’s **Network** settings. Keep **XHTTP**, set **Path** to `/relay-nl` and **Mode** to `stream-one`. The path matches NL’s inbound; `stream-one` is the sending mode used here, while NL accepts it with `auto`.
10. Keep **REALITY**, SNI `www.google.com` and uTLS `chrome` from the imported link. Leave **Flow** empty/None if shown.
11. Click **Create**.

You should now see an outbound tagged **relay-nl** on Moscow. It knows how to connect to NL. Your phone still needs its own inbound and account on Moscow, which we’ll create next.

#### Create the place where your devices connect

Your phone will connect to Moscow over IPv4. We’ll make that receiving entry and name it **VLESS RU**. Keep it off while creating its accounts and route, so it won’t start accepting device traffic before the foreign route is ready.

1. In Moscow’s sidebar, click **Inbounds → Add Inbound**.
2. On **Basics**, enter:

| Field | Enter |
|---|---|
| **Enable** | Off for now |
| **Remark** | `VLESS RU` |
| **Protocol** | `vless` |
| **Address** | Moscow’s public IPv4 address |
| **Port** | `443` |
| **Share address strategy** | **Custom** |
| **Custom share address** | Moscow’s public IPv4 address |
| **Disable XTLS flow** | Off |

Using port 443 on Moscow doesn’t conflict with port 443 on NL: they are different servers with different addresses. If the panel reports a conflict with another service, use [the port-conflict fix](troubleshooting.md#the-vpn-port-is-already-in-use) and keep the actual port consistent in later links.

3. Open **Stream** and set **Network** to **RAW** (called TCP in some versions). This is the transport used for your device connection.
4. Open **Security**, select **REALITY**, and enter:

| Field | Enter |
|---|---|
| **Target** | `yandex.ru:443` |
| **SNI** | `yandex.ru` |
| **uTLS** | `safari` |

These fields serve the same jobs as on NL: target/SNI describe the connection setup website, and uTLS chooses the browser-style opening message. We use the device preset that worked in the guide’s tests. It doesn’t require installing Safari.

5. Click **Get New Cert** to generate this new inbound’s own REALITY keys. Keep its generated **Short IDs**, or generate them with the adjacent circular button if empty. Don’t copy NL’s private key into Moscow.
6. Click **Create**. **VLESS RU** should appear in Moscow’s Inbounds list, still disabled.

#### Create your phone and computer accounts

Now we’ll give each device its own credentials. You can later remove one device’s access without changing the other. We’ll use **desktop** and **phone** as example labels; you can choose other names.

1. In Moscow’s sidebar, click **Clients → Add Client**.
2. On **Basics**, put `desktop` in **Email**. It is a label, not an email address.
3. Under **Attached inbounds**, select **VLESS RU**. Keep **Enable** on, the initial limits at `0`, and expiry unset.
4. Open **Credentials** and keep its generated **UUID**.
5. Select **Flow → xtls-rprx-vision**. Vision is the flow used by this guide’s RAW device connection. This differs from the XHTTP connection between the servers, where Flow stays empty.
6. Click **Create**.
7. Click **Add Client** again and repeat for `phone`, attaching it to **VLESS RU** too. Keep its own generated UUID rather than copying the desktop value.

Moscow’s Clients page should now show both device accounts attached to **VLESS RU**. The receiving inbound remains disabled until we join it to the NL outbound below.

#### Tell Moscow to send those accounts through NL

Moscow now has both parts: **VLESS RU** receives device traffic and **relay-nl** sends traffic to NL. A routing rule joins them. It means “when traffic arrives through this device entry, send it using that foreign connection.”

1. In Moscow’s sidebar, click **Routing** and open **Routing Rules**.
2. Click **+ Routing Rules**.
3. Set **Comment** to `Devices through NL` so you recognize the rule later.
4. In **Inbound tags**, select **VLESS RU**. The menu may also show its generated tag.
5. In **Outbound tag**, select **relay-nl**.
6. Leave the other match fields empty and **Enable** on. Click **Create**.
7. In the rule list, use **⋯ → Move up** or the drag handle to put the new rule before general rules that might match the same traffic. Keep the panel’s existing **api** rule in place.
8. Click **Save** on the routing page. Accept a restart if prompted.

The new rule should show **VLESS RU → relay-nl**. That is the instruction connecting VPN 1 to VPN 2.

#### Turn the device connection on and copy its links

The route is ready, so we can let devices connect. Then we’ll copy the account settings into Hiddify.

1. In Moscow’s sidebar, open **Inbounds** and edit **VLESS RU**.
2. On **Basics**, turn **Enable** on and click **Save Changes**. Accept a restart if prompted.
3. Open **Clients** and find **phone**.
4. Click its **ⓘ Client Information** action. In **Copy URL**, copy the VLESS link for **VLESS RU**.
5. Paste it into a private text editor. Save a copy of the original before changing it.

The server address in this link should be **Moscow’s public IPv4** and its VPN port. This is the link your phone uses for VPN 1. The NL relay account belongs only in Moscow’s outbound.

For Xray **26.7.28**, Hiddify can use the shorter opening message that worked in our phone test. We’ll select it by adding one option to the device link:

6. Find the `#` just before the link’s display name and insert **`&keyshare=classical`** immediately before it. If `keyshare=` already exists, change its value to `classical` rather than adding it twice.
7. Copy the whole adjusted line for your phone. Repeat the export and adjustment with **desktop** for your computer.

For example, the end of a link changes from:

```text
...&spx=%2F#VLESS-RU-phone
```

to:

```text
...&spx=%2F&keyshare=classical#VLESS-RU-phone
```

Leave the address, UUID, keys and other fields unchanged. The [advanced TLS explanation](handshakes-and-versions.md) is optional; you don’t need it to finish the connection.

## 3. Verify the complete device path

Both server connections are configured. Now we’ll use your phone or computer to see whether they carry a website request through to NL.

1. Follow [installing Hiddify](clients.md) on the device you want to connect.
2. Copy that device’s **adjusted Moscow link**, then use **+ → Clipboard** in Hiddify and select the imported connection.
3. On a computer, choose **Settings → Inbound → Service mode → VPN / TUN**. On a phone, use normal VPN mode.
4. Press **Connect** and accept the system’s VPN permission if asked.
5. Open [the address page](https://www.cloudflare.com/cdn-cgi/trace) in your browser. The **ip=** line should show the foreign server’s **IPv4** address, not Moscow’s.
6. Open a website you wanted to use. On your phone, try again with Wi-Fi off so you also test mobile data.

If the website opens and the address is the foreign server’s, **you’re done**. Your device opens VPN 1; Moscow opens VPN 2. You don’t need to keep either dashboard or your setup computer switched on for the phone to use the VPN.

If it doesn’t work, use [the troubleshooting table](troubleshooting.md#first-choose-the-symptom-that-matches-yours). Don’t apply extra settings to a working connection.

Everything below is optional. The scripts are an alternative way to create the same setup; extra exit countries mean renting another foreign server.

## Optional: preview and apply the relay helper

<details>
<summary>Open the commands for the same two-server setup</summary>

Download the repository and open a terminal in it using [these preparation steps](quick-start.md#before-the-first-command). This optional helper needs Python 3.8+ and native OpenSSH on your computer. The existing Windows single-server launcher still works without local Python. The servers need Python 3, supported Ubuntu/Debian and systemd.

The script creates the same two-server route as the manual steps: dashboards if missing, the foreign relay account, Moscow device accounts, and the routing between them. It saves private backups and links. It leaves IPv6 activation to you. Use it as an alternative to the manual setup, rather than running both for the same new route.

Replace these example values before running:

| Argument | Your value |
|---|---|
| **--hub-host** | Moscow’s public IPv4 address, used for SSH setup |
| **--exit-host** | The foreign server’s public IPv4 address, used for SSH setup |
| **--exit-ipv6** | The foreign server’s configured IPv6 host address, used by the relay |
| **--route** | A short country label, such as `nl`; also names the saved route |
| **--entry-port** | Moscow’s device port, `443` here |
| **--exit-port** | The foreign relay port, `443` here; it is on a different server |
| **--clients** | Your chosen comma-separated account names |

The version, classical option and XHTTP transport flags select the settings just explained in the manual path. Keep them for this setup. Here is the command with example addresses:

```bash
python3 scripts/bootstrap_relay.py \
  --hub-host 203.0.113.10 \
  --exit-host 198.51.100.20 \
  --exit-ipv6 2001:db8:2::1 \
  --route nl \
  --entry-port 443 \
  --exit-port 443 \
  --hub-core-version 26.7.28 \
  --exit-core-version 26.7.28 \
  --entry-key-share classical \
  --relay-transport xhttp \
  --clients desktop,phone \
  --plan
```

**`--clients desktop,phone` is the list of VPN account names to create on Moscow.** Those are example labels; choose names such as `alex,anna,laptop` for three accounts. Separate them with commas, without spaces. Each gets its own credentials and a link saved as **NAME.txt**, for example **alex.txt**. [Naming rules](automation.md#choose-the-vpn-account-names)

Plan mode makes no network requests or changes. Repeat the same command with **--apply** to deploy. On Windows PowerShell, use `py` or `python` and put the arguments on one line.

The helper:

1. Authenticates to both servers through OpenSSH with normal host-key verification and hidden root-password prompts.
2. Checks that IPv6 addresses and default routes already exist.
3. Installs pinned 3x-ui and the selected, checksum-verified Xray core only when that server has no panel. An existing core must match the requested version. Panel-only installation creates no temporary VPN account.
4. Saves private SQLite and routing backups before changing an existing panel.
5. Adds the foreign IPv6 relay inbound and a dedicated relay account; existing direct accounts remain.
6. Tests two consecutive authenticated HTTPS requests from Moscow to the foreign IPv6 endpoint and checks the foreign IPv4 exit. A bounded retry allows the newly restarted listener to settle.
7. Adds the Moscow inbound and routes it to that foreign outbound. New inbounds remain disabled until their routing is ready; setup failures disable the new inbound when possible.
8. Retrieves and saves the panel-generated links. Device files add the requested Hiddify key-share option; `panel-profiles.json` preserves the original exports. Both stay in the ignored `.secrets/` directory.

A fresh panel's generated credentials are in the private relay.json result. Open its printed public HTTP panel URL directly in a browser, as described in the [panel guide](server-setup.md#open-the-dashboard-in-your-browser).

The helper’s IPv6 check does not configure provider networking. If it fails there, complete section 1 manually before retrying.

### Explicit management access through an existing proxy

The helper normally connects directly to each server over SSH. If you deliberately want to administer one through an existing HTTP proxy on your computer, pass its address explicitly:

```text
--exit-ssh-proxy 127.0.0.1:10801
```

There is a separate `--hub-ssh-proxy` option. These are explicit loopback proxy endpoints, not root-password arguments. The helper keeps its own SSH connections separate from old multiplexed sessions.

**This proxy is only for the setup connection.** After deployment, Moscow talks to the foreign server over its own IPv6 connection. Your phone doesn’t need your computer or its proxy to stay on.

</details>

## Optional: add another exit country

<details>
<summary>Reuse Moscow for FI or another foreign server</summary>

This adds a **third rented server**: a new foreign server in Finland (**FI**). Keep the existing Moscow and NL servers. Rent the FI server, configure its IPv6, then use route key `fi` and Moscow’s other allowed port, 8443.

The command below reuses Moscow and configures the new FI server; run it on your setup computer from the repository folder. It assumes the first country uses **Moscow port 443** and **8443 is free**. If the first country already uses 8443, set `--entry-port 443` instead, only if that port is free. Preserve existing listeners. The foreign server has its own ports; its relay port doesn’t have to equal Moscow’s entry port.

This is a script alternative to repeating the manual foreign-inbound and Moscow-outbound steps.

```bash
python3 scripts/bootstrap_relay.py \
  --hub-host 203.0.113.10 \
  --exit-host 198.51.100.30 \
  --exit-ipv6 2001:db8:3::1 \
  --route fi \
  --entry-port 8443 \
  --exit-port 8443 \
  --hub-core-version 26.7.28 \
  --exit-core-version 26.7.28 \
  --entry-key-share classical \
  --relay-transport xhttp \
  --clients desktop,phone \
  --plan
```

Apply only after that foreign server's IPv6 is configured. The helper reuses Moscow's panel, attaches existing owner accounts without rotating their UUIDs, and adds a separate inbound-to-outbound rule for the new country. It preserves the first country's route.

With one public IPv4 address and this separate-listener design, 8443 and 443 provide **two country entry points**. More countries can share an existing inbound with [Xray user routing](https://xtls.github.io/en/config/routing#ruleobject). Give each device/country combination a distinct account, such as `desktop` for NL and `FR-desktop` for FR, and route its account label to the corresponding foreign outbound. Put the account-specific rules above the inbound's general rule. For FR, first rent another foreign server in France and configure its IPv6. Keep the existing Moscow, NL and FI servers. The helper supports the shared-port layout through `--shared-entry`. For example, use `--route fr --entry-port 443 --shared-entry --clients FR-desktop,FR-phone` with FR's server addresses. It checks the existing RAW entry and SNI, then inserts the account rule before the general NL rule. The new account labels must be distinct. Public entries still use only 443 and 8443.

Reapplying the same route with unchanged settings reuses it. A route key already bound to different settings is refused; do not delete its registry or reinstall the hub to force a change.

</details>

## What we verified

<details>
<summary>Read the recorded tests and version results</summary>


From the Moscow server, direct TCP to the foreign IPv4 SSH, VPN and panel ports timed out. The foreign IPv6 ports were reachable, and both the original foreign VPN over IPv6 and the new relay authenticated. The new path returned the foreign IPv4 exit. From a desktop, the complete chain passed six isolated Windows Hiddify HTTPS requests, two requests using Hiddify's actual VPN Connect button, and a separate UDP DNS request. The test watchdog then disconnected Hiddify and restored the previous Windows proxy settings. A second country's live route was not part of this test.

All four NL accounts passed HTTPS checks after moving Moscow’s entry to port 443. Hiddify’s Connect button passed two more checks on port 443. FI was added on port 8443, and all four FI device profiles returned the expected FI exit. FR now shares Moscow port 443 with NL. The FR account rule runs before the general NL rule for that inbound. All four FR profiles returned the expected FR exit in isolated Windows Hiddify checks. The NL and FI desktop profiles also returned their expected exits after FR was added.

A later live test switched the inter-server IPv6 links for NL, FR and FI to XHTTP + REALITY, using `stream-one` on Moscow’s outbounds and `auto` on the foreign inbounds. Each relay kept its existing address, port and account. XHTTP uses an empty client flow on that leg. All twelve device profiles passed isolated Windows Hiddify HTTPS requests through their expected exits, and UDP DNS passed through each XHTTP relay. Device entry uses RAW + REALITY + Vision. The helper defaults to this XHTTP relay. Select `--relay-transport raw` for the older RAW relay mode, whose relay account uses Vision flow.

The owner subsequently reported that the NL phone profile worked over mobile data when Moscow ran Xray 26.7.28 and Hiddify 5.5.5 used `keyshare=classical`. All three saved Windows desktop profiles were then updated to classical mode and each passed two HTTPS checks. Hiddify’s Connect button passed three further NL HTTPS checks. This is a version-specific result: classical key shares require a compatible server, and Xray 26.9.9 rejects them. Check the server version before changing this field. [Hiddify investigation and compatibility caveat](https://github.com/hiddify/hiddify-app/issues/2463#issuecomment-6750196534)

</details>

## Add another phone or computer

For another device using an existing country, make a new **device account on Moscow**. You don’t need another foreign relay account for every device.

On **Moscow**, open **Clients → Add Client**. In **Basics**, enter your chosen label in **Email** and select the device entry in **Attached inbounds**. Keep the account enabled and leave limits at `0` and expiry unset unless you want a limit. Open **Credentials**, keep its new generated UUID, select **Flow → xtls-rprx-vision**, then click **Create**. If that country uses a shared port and a user-specific routing rule, add the new account label to that country’s rule too. An account left out of the FR rule on shared port 443 would follow the general NL rule.

Open that account’s **ⓘ Client Information → Copy URL**, copy its VLESS link, add `&keyshare=classical` before `#` for the 26.7.28 entry version, and [import it into Hiddify](clients.md). Test the exit country. Leave other users’ accounts and keys alone.

## Recovery and evidence

If you used the scripts, private server backups are under **/root/vpn-relay-backups**, and the local **relay.json** records completed stages and backup locations. The route registry is **/etc/vpn-guide-relay/routes.json**. If a run stopped, inspect its saved stage and disabled inbound before retrying; don’t erase the panel or registry to force it through.

For a manual change, keep a panel backup before editing an existing route. If the new route fails, disable its new device inbound and restore the settings you changed from that backup. Preserve other countries’ rules and accounts. [Checks for the first failing connection](troubleshooting.md)

IPv6 and a two-hop chain do not guarantee that a destination IP or prefix will remain reachable. Distinguish direct, proxy-assisted management, inter-server and final device tests. Record their actual exit addresses and keep live account links and keys out of the repository.

**Back to the device steps:** [import and connect in Hiddify](clients.md).

## GUI references

These button paths follow the official **3x-ui 3.8.5** source: [inbound forms](https://github.com/MHSanaei/3x-ui/tree/v3.8.5/frontend/src/pages/inbounds), [client account forms](https://github.com/MHSanaei/3x-ui/tree/v3.8.5/frontend/src/pages/clients), [outbound forms](https://github.com/MHSanaei/3x-ui/blob/v3.8.5/frontend/src/pages/xray/outbounds/OutboundFormModal.tsx) and [routing rule forms](https://github.com/MHSanaei/3x-ui/blob/v3.8.5/frontend/src/pages/xray/routing/RuleFormModal.tsx).
