[← Guide index](../README.md) · [Client walkthrough](clients.md) · [Troubleshooting](troubleshooting.md)

# Let the scripts do the repetitive work

**Optional toolbox.** Pick only the helper for your task; this page is not a sequence to run from top to bottom. For a manual setup, start with the [two-hop guide](two-hop-vpn.md) or the [single-server walkthrough](single-server.md).

The examples use a rented remote server (**VPS**), its administrator account (**root**), the **3x-ui** browser dashboard, and the **Hiddify** VPN app. **Xray** is a network engine used on the server and in standalone client tests. A **profile** or **share link** is the private link containing an account’s connection settings.

If you haven’t downloaded these files yet, follow [getting the repository and opening a terminal](quick-start.md#before-the-first-command). Pick a task from [the helper table](#pick-the-helper-for-the-job); don’t run every command on this page. Each script’s output tells you where it saved private files or which check failed.

The **setup helper** installs server software only when explicitly applied. The diagnostic and client-preference helpers do not install software. None of the helpers changes a provider firewall or stops existing clients. Run them from the repository root—the folder containing `README.md` and `scripts/`. Python helpers require **Python 3.8+**, the server helper uses Bash, and the Windows repair helper uses PowerShell 5.1+.

## Set up the two-hop relay

First rent **both** the Moscow server (FirstVDS in the example) and foreign server (HostVDS), then configure IPv6 on each. Use [the two-hop walkthrough](two-hop-vpn.md) and `python3 scripts/bootstrap_relay.py --help`. It supports a reusable Moscow hub, separate country routes on 443/8443, explicit management proxies, private backups and canonical client exports. Single-server and two-server setup are equal starting choices. IPv6 activation and OS configuration are the user's provider-specific task; the relay helper only checks existing addresses and routes.

The relay route starts at a Moscow IPv4 inbound, crosses to the foreign VPS on IPv6, then exits over IPv4. Use the foreign relay account only in Moscow's outbound; export separate Moscow device accounts for Hiddify. Pass `--entry-port 443` for NL and `--entry-port 8443` for FI. The shared NL and FR layout uses account-based rules on port 443 through `--shared-entry` and distinct FR account labels. [See the port map](schemes/README.md#add-a-country) Keep an existing single-server route as a separate mode.

## Start with only a VPS IP and root password

This section installs a **one-server VPN on the foreign server**, such as your HostVDS rental. For a Moscow-plus-foreign setup, use `bootstrap_relay.py` and supply **both** servers; don’t run the standalone installer on Moscow and expect it to create the foreign connection.

Follow the [script walkthrough](quick-start.md) for the full sequence, including opening the panel and importing the generated profile. Windows users run `scripts/Setup-Vpn.ps1`; Linux/macOS users run `scripts/bootstrap_server.py`. Both default to a plan; `-Apply` / `--apply` is the explicit provisioning action.

The launchers use **SSH**, an encrypted terminal connection, through the operating system’s **OpenSSH** program. They prompt for the IP if omitted, then SSH prompts for the root password and a new host key. Root passwords are never accepted as flags or stored. The scripts refuse existing panel installations and preserve occupied listeners. Public VPN inbound ports are restricted to **443 or 8443**. A busy default 443 falls back to 8443; provider-firewall work is reported as a separate action when needed. Allow the VPN port and the separate panel TCP port; the helper adds both rules only when UFW is already active.

The panel uses the root URL path `/` and listens publicly. Open the printed `http://SERVER_IP:PANEL_PORT/` directly in your browser; no SSH forward is required. Generated panel credentials and the Hiddify share link are written under `.secrets/`; do not publish them. The server also retains a root-only result file for recovery. No launcher stops a local VPN client or changes Windows' proxy or routes.

The helper retrieves the **actual 3x-ui client export**, including its display name and `spx` value. It saves that original in **panel-profile.txt** and adds the selected client-only key-share option to **hiddify-profile.txt**. Keep that name when importing: for example, an inbound named `Personal VPN` with account `desktop` may export **Personal VPN-desktop**. Different people and devices must receive their own account's export; the inbound name alone does not identify whose credentials a profile uses.

The pinned remote payload is `scripts/provision_remote.py`; it is not a workstation setup program and refuses direct invocation without the launcher's supplied options. Review the code and pinned installer before applying it. This path installs pinned **3x-ui 3.8.5**, then independently downloads the selected official Xray release, verifies its SHA-256 digest from GitHub release metadata and checks its configuration before activation. The previous binary is backed up on the VPS. The service uses `GODEBUG=multipathtcp=0`. Existing panel installations are refused by this fresh-server helper.

### Core version, key share and transport

The single-server defaults are **Xray 26.7.28**, **Safari**, **RAW**, **classical** Hiddify profiles and separate **desktop** and **phone** accounts. Set `--clients` / `-Clients` for other account labels. Select them explicitly when saving a reusable command:

```bash
python3 scripts/bootstrap_server.py --host 203.0.113.10 \
  --core-version 26.7.28 --key-share classical --fingerprint safari --transport raw --plan
```

```powershell
.\scripts\Setup-Vpn.ps1 -ServerIp 203.0.113.10 -CoreVersion 26.7.28 -KeyShare classical -Fingerprint safari -Transport raw
```

For the compatible newer-core path, select **`--core-version 26.9.9 --key-share hybrid`** or **`-CoreVersion 26.9.9 -KeyShare hybrid`**. The scripts reject a classical request with a core that requires the hybrid share.

Single-server XHTTP is optional. Add **`--transport xhttp --xhttp-path /vpn`** or **`-Transport xhttp -XhttpPath /vpn`**. It creates an empty-flow XHTTP account, while RAW accounts use Vision. Re-export the matching client after a transport change. The working mobile entry recorded in this guide used RAW. [Measurements and version limits](handshakes-and-versions.md)

The relay helper defaults to **`--hub-core-version 26.7.28 --entry-key-share classical --relay-transport xhttp --exit-core-version 26.9.9`**. Select **`--relay-transport raw`** for the older inter-server mode. An existing panel's core must match the requested version; this helper adds routes and refuses an implicit core replacement. IPv6 addresses and routes are always configured manually first.

For a third country sharing the RAW entry, use **`--route fr --entry-port 443 --shared-entry --clients FR-desktop,FR-phone`** with that country's server addresses. The helper inserts an account-specific rule above the inbound's general country route, reuses its existing listener and backs up its prior state.

### Recommended preset and legacy regional defaults

For this Hiddify walkthrough, explicitly select the tested preset:

```powershell
.\scripts\Setup-Vpn.ps1 -VpnPort 8443 -Target www.apple.com -Fingerprint safari
```

```bash
python3 scripts/bootstrap_server.py --vpn-port 8443 --target www.apple.com --fingerprint safari --plan
```

Add `-Apply` / `--apply` only for an authorized fresh VPS. This sets the new inbound and its export together. Keep existing accounts' UUIDs and keys when changing a target or fingerprint; re-export and replace the saved client profile afterward.

### Choose the client fingerprint by server country

<details>
<summary>Older automatic country policy — keep Safari for the normal walkthrough</summary>


During Apply, the shared payload looks up the **VPS IP**, not your computer's location, using [Country's public-IP API](https://country.is/). With **`--fingerprint auto`** or **`-Fingerprint auto`**, the legacy policy selects **Safari for `US`** and **Chrome for other countries**. The normal launcher default is explicit Safari. The panel's exported client metadata and the generated share link receive the same choice. The resolved country and fingerprint are also saved in private `server.json`.

Use these options to skip geolocation or override its answer. The examples show plan mode; add `-Apply` / `--apply` only for the fresh server you intend to provision.

```powershell
.\scripts\Setup-Vpn.ps1 -ServerIp YOUR_SERVER_IP -ServerCountry US
.\scripts\Setup-Vpn.ps1 -ServerIp YOUR_SERVER_IP -ServerCountry DE -Fingerprint firefox
```

```bash
python3 scripts/bootstrap_server.py --host YOUR_SERVER_IP --server-country US --plan
python3 scripts/bootstrap_server.py --host YOUR_SERVER_IP --server-country DE --fingerprint firefox --plan
```

An explicit fingerprint always wins and does not require geolocation. Available explicit presets are `chrome`, `safari`, `firefox`, `edge`, `ios`, `android`, `random`, `randomized`, `360`, and `qq`; client-core support must still be checked. With both choices explicitly set to `auto`, an unavailable, malformed, or unknown-country lookup stops setup before package installation instead of guessing. Supply the provider's country code or an explicit preset to continue. Plan mode runs locally.

This regional policy is an initial selection, not evidence that all US networks reject Chrome or that every other preset works everywhere else. The controlled comparisons found Chrome/Safari differences on both a US and a non-US endpoint. If your actual Hiddify test needs Safari, use the explicit `--fingerprint safari` / `-Fingerprint safari` override during fresh setup. For an existing server, change its export in the panel and reimport it; do not rerun the fresh-server installer. Test a real HTTPS request after import; see [what a TLS fingerprint changes](xray-internals.md#what-a-tls-fingerprint-changes-and-why-chrome-can-fail). Helpers that inspect or convert an existing profile preserve its selected fingerprint rather than silently replacing it according to geography.

</details>

## Pick the helper for the job

| Your next step | Helper | Changes by default |
|---|---|---|
| Prepare a fresh VPS from its IP and root password | `scripts/Setup-Vpn.ps1` or `python3 scripts/bootstrap_server.py` | Plan only; apply provisions the fresh VPS |
| Add a two-hop IPv6 route or a second country | `python3 scripts/bootstrap_relay.py` | Plan only; apply adds a route and preserves existing ones |
| Check the VPS service, listener and effective settings | `bash scripts/server-check.sh` | None; local checks only |
| Inspect a private share link | `python3 scripts/vpn_profile.py inspect` | None; values that grant access are hidden |
| Create a Linux/standalone Xray client file | `python3 scripts/vpn_profile.py config` | Writes only the explicit output file |
| Compare a profile using an installed Xray core | `python3 scripts/vpn_profile.py test` | Temporary loopback client/files; removed afterward |
| Recover Hiddify's saved settings | `scripts/Repair-Hiddify.ps1` | Preview only; `-Apply` saves a backup and writes preferences |
| Check documentation links and image references | `python3 scripts/check_docs.py` | None |

Each helper's `--help` or comment-based help points back to the guide explaining its choices. Open a script in a text editor if you want to see what it does before running it.

## Check the VPS without changing it

If the repository is on the VPS:

```bash
sudo bash scripts/server-check.sh --port 443
```

Otherwise copy just the helper from your computer, then run it there:

```bash
scp scripts/server-check.sh YOUR_ADMIN@YOUR_SERVER_IP:/tmp/vpn-server-check.sh
ssh YOUR_ADMIN@YOUR_SERVER_IP
sudo bash /tmp/vpn-server-check.sh --port 443
```

Replace 443 with your actual public VPN port. The helper reports panel/core versions, service state, the listener, clock synchronization, configuration syntax, and a summary that omits UUIDs and keys. It assumes a conventional 3x-ui layout; use `--config PATH --xray PATH` for another installation.

Optional direct VPS internet checks require an explicit flag:

```bash
sudo bash scripts/server-check.sh --port 8443 --network --target www.google.com
```

IPv6 may intentionally be unavailable. These requests are direct from the VPS; they are not authenticated VPN tests. A clean result does not inspect the provider's firewall or prove the client account works. Continue with [server checks and interpretation](troubleshooting.md#server-checks).

## Inspect a connection link without putting it in shell history

Interactive use hides the pasted connection link (also called a URI):

```bash
python3 scripts/vpn_profile.py inspect
```

On Windows, use `py` or `python` instead of `python3` if that is your installed Python command. Do not paste a live link as a positional command-line argument. The helper deliberately does not accept that form.

For noninteractive work, put the link in a private local file, or supply the **name** of an existing environment variable:

```bash
python3 scripts/vpn_profile.py inspect --link-file .secrets/profile.txt
python3 scripts/vpn_profile.py inspect --link-env VPN_LINK
```

The `.secrets/` directory is ignored by Git. Create it privately and use an editor/password manager to populate the file; a command containing the full URI can still enter history. On Linux:

```bash
mkdir -m 700 .secrets
```

If it already exists, check its permissions rather than assuming `mkdir` succeeded. Apply appropriate file permissions after editing. On Windows, keep the file in your account's private storage; the script cannot guarantee access control on an arbitrary shared drive.

Inspection validates the UUID, REALITY key shape, short ID, SNI, transport and flow. It does not verify that the server actually has those values. `inspect --connect` also attempts TCP to the selected VPN port; the output explicitly distinguishes this from authentication.

The helper supports **VLESS + REALITY + encryption=none** with RAW (Vision or empty flow) and basic XHTTP (empty flow, path, mode and optional Host). Advanced XHTTP `extra` settings require the client UI. Use the Hiddify engine for a classical profile.

## Generate a client configuration

All profile paths in this section are examples. Replace **.secrets/panel-profile.txt** with the actual original panel export you saved. A setup script may have put it in a dated output folder, not directly under `.secrets`. The original panel export uses hybrid mode; the adjusted Hiddify file can use classical mode. Choose the matching engine below.


```bash
python3 scripts/vpn_profile.py config --engine xray --link-file .secrets/panel-profile.txt --output .secrets/client.json --port 10801
```

The command above reads the link from **.secrets/panel-profile.txt**. If you leave out `--link-file`, it asks you to paste the link at a hidden prompt instead. The generated file listens on **127.0.0.1 only** and contains the account credentials, so do not publish it. The helper's default port is **10809**; the command above explicitly selects the Linux walkthrough's **10801**.

Existing output is refused. If you deliberately want to replace it, `--overwrite` first saves a uniquely named backup. No service is restarted. To install the result as a Linux service configuration, follow [the Linux walkthrough](linux-xray.md#put-your-account-settings-in-a-client-file).

### Classical profiles need the Hiddify engine

For the commands below, replace **.secrets/hiddify-profile.txt** with your actual adjusted device file: `client-desktop.txt` from the single-server output, or `desktop.txt` from the relay output, including its folder path. Use the matching phone file if that is the account you are testing.

The profile helper reads RAW, basic XHTTP and the key-share option. A classical profile needs **`--engine hiddify`**, because generating an ordinary Xray configuration cannot enforce Hiddify's classical-only setting. The helper rejects that mismatch instead of dropping the option.

```bash
python3 scripts/vpn_profile.py config --engine hiddify --link-file .secrets/hiddify-profile.txt --output .secrets/hiddify-test.json
python3 scripts/vpn_profile.py test --engine hiddify --hiddify /path/to/HiddifyCli --link-file .secrets/hiddify-profile.txt
```

On Windows, run Windows Python and pass the installed CLI path:

```powershell
py scripts/vpn_profile.py test --engine hiddify --hiddify 'C:\Program Files\Hiddify\HiddifyCli.exe' --link-file .secrets/hiddify-profile.txt
```

This starts a separate `HiddifyCli srun` child on a temporary loopback port and closes that child after the request. It exercises the saved profile's key share, transport, path and flow. The ordinary `--engine xray` path remains available for hybrid profiles.

## Test a real authenticated tunnel

**Choose the engine to match your link.** The default classical device links from this guide need [the Hiddify commands above](#classical-profiles-need-the-hiddify-engine). The commands in this section are for an original panel export or hybrid profile.

Use an already installed official Xray executable for your operating system. Download it from [XTLS/Xray-core releases](https://github.com/XTLS/Xray-core/releases), check the published hashes where available, and keep different versions in different directories when comparing them.

Linux:

```bash
python3 scripts/vpn_profile.py test --xray /usr/local/bin/xray
```

Windows PowerShell, with a separately downloaded Windows binary:

```powershell
py scripts/vpn_profile.py test --xray 'C:\Tools\Xray\xray.exe'
```

The helper prints the actual Xray version, finds a temporary unused local port, writes a private temporary configuration, starts that child process, and sends HTTPS through its HTTP proxy using curl. It explicitly overrides `NO_PROXY`, which could otherwise bypass the proxy and create a false success. Finally it terminates **its own child only** and removes the temporary files.

The default endpoint returns `ip=`. Compare it with the server that opens the website connection: the only foreign server for a one-server VPN, or the **foreign exit**, not Moscow, for a two-server VPN. To require one exact known exit address, use `--expect-ip EXPECTED_EXIT_IP`. If your VPS can choose IPv6, do not compare its IPv6 result with the IPv4 inbound address and call that a failure; [configure egress](force-ipv4.md) first if you require IPv4.

Use `--show-core-log` for a redacted excerpt when a test fails. Redaction is a convenience, not permission to publish an unchecked log. You can set `--url` to another HTTPS endpoint if the default site is unavailable. An exit-IP expectation requires the default trace-style response.

A Linux test from WSL and a Windows test exercise different native cores and OS integration. Use the binary for the shell's operating system: run the Windows command from Windows Python/PowerShell. Do not assume a Linux success proves the GUI's system proxy works.

## Repair Hiddify preferences on Windows

**Windows fallback for a failed app configuration.** Start with [the symptom table](troubleshooting.md#first-choose-the-symptom-that-matches-yours). A working connection doesn’t need a preference repair. For mobile handshake failures, check the [version and key-share table](handshakes-and-versions.md) first. This preferences helper changes DNS/service preferences; the profile's key-share field is a separate setting.

Read the [Hiddify recovery explanation](clients.md#advanced-recovery-when-the-normal-settings-are-not-enough) first. Start with a preview from PowerShell:

```powershell
.\scripts\Repair-Hiddify.ps1
```

If script execution is restricted, inspect the file and follow your organization's policy. Do not globally weaken execution policy just to run a helper. You can also make the visible UI changes manually; two of the recorded recovery preferences are not exposed as switches in the checked release.

The preview lists only the proposed settings, not the rest of your preferences or secret values. To apply it:

1. Save any Hiddify configuration work and **close Hiddify yourself**.
2. Leave other clients alone; the helper never stops them.
3. Run:

```powershell
.\scripts\Repair-Hiddify.ps1 -Apply -ServiceMode Manual
```

The script refuses to apply while Hiddify is running. It saves a timestamped backup beside `shared_preferences.json`, keeps unrelated preferences, and selects manual Proxy mode by default. For a portable/custom package, pass the actual `-SettingsPath`.

Open Hiddify again, select the intended profile, press Connect, and test port 12334 explicitly. A different local port remains unchanged by the helper; use the value shown under Inbound. Only choose `-ServiceMode SystemProxy` or `VPN` when you intentionally want that mode on the next connection. The helper itself does not start the app or change Windows networking.

To undo the repair, close Hiddify and copy the printed backup back over the preferences file. Open the app and reconnect afterward. Keep the backup private because it contains all original preferences.

## Maintain the guide itself

The setup pages use written steps while we collect real screenshots. See [the capture list](../images/README.md). The old generated SVG assets and their renderer are kept for history; don’t put them back into the walkthroughs.

A successful inspect command prints the server and selected protocol fields while hiding UUID/key/short-ID values. A successful tunnel test prints the actual Xray version, a success message, and the endpoint response containing `ip=`. On a failure, use the linked troubleshooting step instead of treating a completed process as a working tunnel.

Run the repository's offline checks with:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B scripts/check_docs.py
bash -n scripts/server-check.sh
```

On Windows, also run `.\tests\check-powershell.ps1` for syntax, fixture-only preview checks, and simulated running-app protection. It does not inspect or stop your VPN apps.

No server password, live profile, panel session, or working VPN is needed for these checks. Testing a live VPN still requires a real server and a webpage request through the client.

## Working with an assistant

The repository includes [AGENTS.md](../AGENTS.md), which maps the guides and scripts and describes the authorized fresh-server setup workflow. An assistant can use it to carry out setup from the supplied VPS details while keeping existing installations and desktop clients separate. You can still follow every setup page yourself; the ordinary guides do not depend on an assistant.
