[← Guide index](../README.md) · [Client walkthrough](clients.md) · [Troubleshooting](troubleshooting.md)

# Let the scripts do the repetitive work

**Optional toolbox.** Pick only the helper for your task; this page is not a sequence to run from top to bottom. For setup without repository helpers, [start with the manual guide](../README.md#follow-these-steps-in-order).

The examples use a rented remote server (**VPS**), its administrator account (**root**), the **3x-ui** browser dashboard, and the **Hiddify** VPN app. **Xray** is a network engine used on the server and in standalone client tests. A **profile** or **share link** is the private link containing an account’s connection settings.

Once you know which step you want to automate, the helpers can handle repetitive tasks such as generating a configuration or checking a connection. A helper is not an extra requirement for using the VPN.

The **setup helper** installs server software only when explicitly applied. The diagnostic and client-preference helpers do not install software. None of the helpers changes a provider firewall or stops existing clients. Run them from the repository root—the folder containing `README.md` and `scripts/`. Python helpers require **Python 3.8+**, the server helper uses Bash, and the Windows repair helper uses PowerShell 5.1+.

## Start with only a VPS IP and root password

Follow the [illustrated quick start](quick-start.md) for the full sequence, including opening the panel and importing the generated profile. Windows users run `scripts/Setup-Vpn.ps1`; Linux/macOS users run `scripts/bootstrap_server.py`. Both default to a plan; `-Apply` / `--apply` is the explicit provisioning action.

The launchers use **SSH**, an encrypted terminal connection, through the operating system’s **OpenSSH** program. They prompt for the IP if omitted, then SSH prompts for the root password and a new host key. Root passwords are never accepted as flags or stored. The scripts refuse existing panel installations and preserve occupied listeners. A busy 443 falls back to 8443; provider-firewall work is reported as a separate action when needed.

The private panel is reached through the SSH-forward command printed at completion. Generated panel credentials and the Hiddify share link are written under `.secrets/`; do not publish them. The server also retains a root-only result file for recovery. No launcher stops a local VPN client or changes Windows' proxy or routes.

The helper retrieves the **actual 3x-ui client export**, including its display name and `spx` value, rather than constructing a lookalike link. Keep that name when importing: for example, an inbound named `Personal VPN` with account `first-device` may export **Personal VPN-first-device**. Different people and devices must receive their own account's export; the inbound name alone does not identify whose credentials a profile uses.

The pinned remote payload is `scripts/provision_remote.py`; it is not a workstation setup program and refuses direct invocation without the launcher's supplied options. Review the code and pinned installer before applying it. This path installs 3x-ui and its bundled Xray version; it does not silently upgrade an existing installation or promise automatic compatibility with every future client.

### Choose the client fingerprint by server country

During Apply, the shared payload looks up the **VPS IP**, not your computer's location, using [Country's public-IP API](https://country.is/). The default policy selects **Safari for `US`** and **Chrome for other countries**. The panel's exported client metadata and the generated share link receive the same choice. The resolved country and fingerprint are also saved in private `server.json`.

Use these options to skip geolocation or override its answer. The examples show plan mode; add `-Apply` / `--apply` only for the fresh server you intend to provision.

```powershell
.\scripts\Setup-Vpn.ps1 -ServerIp YOUR_SERVER_IP -ServerCountry US
.\scripts\Setup-Vpn.ps1 -ServerIp YOUR_SERVER_IP -ServerCountry DE -Fingerprint firefox
```

```bash
python3 scripts/bootstrap_server.py --host YOUR_SERVER_IP --server-country US --plan
python3 scripts/bootstrap_server.py --host YOUR_SERVER_IP --server-country DE --fingerprint firefox --plan
```

An explicit fingerprint always wins and does not require geolocation. Available explicit presets are `chrome`, `safari`, `firefox`, `edge`, `ios`, `android`, `random`, `randomized`, `360`, and `qq`; client-core support must still be checked. With both choices left at `auto`, an unavailable, malformed, or unknown-country lookup stops setup before package installation instead of guessing. Supply the provider's country code or an explicit preset to continue. Plan mode remains offline.

This regional policy is an initial selection, not evidence that all US networks reject Chrome or that every other preset works everywhere else. The controlled investigation isolated a Chrome/Safari difference on one US-server path. Test a real HTTPS request after import; see [what a TLS fingerprint changes](xray-internals.md#what-a-tls-fingerprint-changes-and-why-chrome-can-fail). Helpers that inspect or convert an existing profile preserve its selected fingerprint rather than silently replacing it according to geography.

## Pick the helper for the job

| Your next step | Helper | Changes by default |
|---|---|---|
| Prepare a fresh VPS from its IP and root password | `scripts/Setup-Vpn.ps1` or `python3 scripts/bootstrap_server.py` | Plan only; apply provisions the fresh VPS |
| Check the VPS service, listener and effective settings | `bash scripts/server-check.sh` | None; local checks only |
| Inspect a private share link | `python3 scripts/vpn_profile.py inspect` | None; values that grant access are hidden |
| Create a Linux/standalone Xray client file | `python3 scripts/vpn_profile.py config` | Writes only the explicit output file |
| Compare a profile using an installed Xray core | `python3 scripts/vpn_profile.py test` | Temporary loopback client/files; removed afterward |
| Recover Hiddify's saved settings | `scripts/Repair-Hiddify.ps1` | Preview only; `-Apply` saves a backup and writes preferences |
| Rebuild the guide's button diagrams | `python3 scripts/render_illustrations.py` | Rewrites the known SVGs in `images/` |
| Check documentation links and image references | `python3 scripts/check_docs.py` | None |

Each helper's `--help` or comment-based help points back to the guide explaining its choices. The scripts are readable source, not downloaded code hidden behind an installer.

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

This helper intentionally supports the guide's **VLESS + RAW/TCP + REALITY + Vision + encryption=none** profile. It rejects other transports/encryption choices instead of silently producing an unsuitable configuration.

## Generate a client configuration

```bash
python3 scripts/vpn_profile.py config --output .secrets/client.json --port 10801
```

Paste the link at the hidden prompt. Or add `--link-file .secrets/profile.txt`. The generated file listens on **127.0.0.1 only** and contains the account credentials, so do not publish it. The helper's default port is **10809**; the command above explicitly selects the Linux walkthrough's **10801**.

Existing output is refused. If you deliberately want to replace it, `--overwrite` first saves a uniquely named backup. No service is restarted. To install the result as a Linux service configuration, follow [the Linux walkthrough](linux-xray.md#put-your-account-settings-in-a-client-file).

## Test a real authenticated tunnel

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

The default endpoint returns `ip=`. Compare that with the expected VPS exit. To require one exact known exit address, use `--expect-ip EXPECTED_EXIT_IP`. If your VPS can choose IPv6, do not compare its IPv6 result with the IPv4 inbound address and call that a failure; [configure egress](force-ipv4.md) first if you require IPv4.

Use `--show-core-log` for a redacted excerpt when a test fails. Redaction is a convenience, not permission to publish an unchecked log. You can set `--url` to another HTTPS endpoint if the default site is unavailable. An exit-IP expectation requires the default trace-style response.

A Linux test from WSL and a Windows test exercise different native cores and OS integration. Use the binary for the shell's operating system: run the Windows command from Windows Python/PowerShell. Do not assume a Linux success proves the GUI's system proxy works.

## Repair Hiddify preferences on Windows

**Optional fallback, not the first Hiddify fix.** First set [Hiddify → Settings → DNS → Outbound domain strategy → IPv4 only](clients.md#3-important-set-outbound-domain-strategy-to-ipv4-only) and reconnect. That resolved the author’s Android connection; this Windows-only helper does not set that option.

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

Rebuild button illustrations with:

```bash
python3 scripts/render_illustrations.py
```

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
