# Working in this repository

This repository is both a human VPN walkthrough and a small set of opt-in setup/diagnostic helpers. Start with `README.md`; read the guide relevant to the requested task before running its script. Keep user-facing documentation readable as a practical article with button illustrations, required values, expected results, and recovery steps. Put protocol/implementation depth in the separate expert guide.

## Human-first documentation rules

The default reader path is manual and starts with no server: choose/rent a server, install its browser dashboard, create a connection account, then install/connect the client app. Keep automation explicitly optional. Do not make setup scripts, preview/apply flags, PowerShell execution policy, or agent instructions a prerequisite for the ordinary walkthrough.

Define names before relying on them: VPS means a rented remote server; root is an administrator account; 3x-ui is the browser dashboard; Xray is the network engine; Hiddify is the connection app; a profile is the private connection link. Introduce ports, SSH and proxy modes where the reader needs them. Do not send a beginner to an expert glossary to complete a required step. Each guide must also make sense when opened directly: define an app or technical term at its first substantive use on that page. Use full product names, including Invisible Man - XRay Client. Keep migration-only app references out of the ordinary beginner steps. Explain a setting through its effect and the reader’s next action; avoid arguments about what a test does not prove unless the limitation changes that action.

Support Windows and Linux as administration/client platforms without calling the guide Windows-only. Ubuntu 24.04 was an example/test environment, not a universal server requirement; describe actual helper dependencies and supported Ubuntu/Debian deployments separately from the ordinary manual guide. Preserve the original sequential, practical writing style.

## Repository map

```text
README.md                       Short entry point and guide index
AGENTS.md                       This repository's agent workflow
.gitignore                      Excludes private profiles, exports, backups and test artifacts
docs/
  choose-server.md              From zero: what a VPS is, how to rent it and save login details
  quick-start.md                Optional automated VPS path: IP/root authentication -> panel -> Hiddify
  server-setup.md               Manual VPS preparation and recoverable administration
  server-inbound.md             3x-ui VLESS/REALITY/Vision form and exported profile
  force-ipv4.md                 Server egress selection through the UI, verification and undo
  clients.md                    Hiddify walkthrough, tested settings, legacy-client compatibility
  ports-and-modes.md            Windows proxy selection, local/public ports, Connect/TUN behavior
  linux-xray.md                 Standalone Linux client, service permissions and program proxies
  share-proxy.md                SSH forwarding and intentionally restricted proxy sharing
  troubleshooting.md            Layer-by-layer failure isolation and the recorded investigation
  network-path-debugging.md       Direct/alternate-path controls and anonymous investigations
  automation.md                 Commands, prerequisites, output and rollback for each helper
  xray-internals.md             Architecture, wire layers, REALITY, Vision, DNS and routing
images/
  *.svg                         Original version-labeled navigation diagrams, not screenshots
  README.md                     Rebuild instructions and genuine screenshot capture/redaction list
scripts/
  Setup-Vpn.ps1                 Windows launcher; no local Python required; default plan only
  bootstrap_server.py           Python launcher; default plan only; native OpenSSH authentication
  provision_remote.py           Remote fresh-VPS payload; never run as local setup
  Repair-Hiddify.ps1            Preference preview; explicit apply with backup; never stops apps
  vpn_profile.py                Inspect, generate config, isolated authenticated tunnel test
  server-check.sh               Read-only Linux VPS health/config summary
  render_illustrations.py       Deterministic SVG navigation-diagram renderer
  check_docs.py                 Offline local links, anchors, SVG and accidental-profile checks
tests/
  test_bootstrap.py             Input boundaries, fresh-install guard, payload/export behavior
  test_vpn_profile.py           Profile validation, overwrite/backup and NO_PROXY regression
  test_docs_and_server_check.py Guide navigation and diagnostic argument validation
  check-powershell.ps1          Syntax/fixture checks; simulated process guard; no real app access
.secrets/                       Ignored local exports; never add to Git
```

## Automatic setup when the user supplies a VPS IP and root access

The automatic path targets a **fresh Ubuntu/Debian systemd VPS**. An explicit request to set up that server authorizes the documented setup steps; do not ask for repetitive confirmations already covered by that request. Tool/sandbox approvals still apply. A request to edit docs or inspect a repository is not permission to provision a server.

1. Read `docs/quick-start.md` and `docs/automation.md`. Verify the requested host and whether it is fresh or already managed. Use the given SSH port if nonstandard.
2. Run the local plan first:

   ```bash
   python3 scripts/bootstrap_server.py --host VPS_IPV4 --plan
   ```

3. For an authorized fresh setup, run the launcher with `--apply`. Use an interactive terminal/PTY for OpenSSH's host-key and password prompts. On a Windows machine without Python, use `scripts/Setup-Vpn.ps1 -ServerIp VPS_IPV4 -Apply`.
4. OpenSSH must verify host identity using its normal known-host behavior. Never disable strict host-key checking or silently accept a changed key. The launchers let SSH read the root password; never add a password argument, write it into scripts/configs, or print it.
5. The payload refuses existing `/usr/local/x-ui/x-ui` or `/etc/x-ui/x-ui.db` before installation. Do not bypass that guard, delete the installation to retry, or rotate an existing account's credentials. For an existing deployment, use the manual guide and read-only diagnostics, then make only changes authorized by the user.
6. The helper installs pinned 3x-ui, creates one REALITY/Vision account, applies ForceIPv4 to the new direct outbound, selects a free public VPN port, and puts the panel on loopback. During Apply only, it resolves the public VPS IP's country and selects Safari for US or Chrome elsewhere; explicit country/fingerprint options override lookup/policy. A failed unresolved lookup stops before installation instead of guessing. Export the exact panel-generated URI. It adds only the selected VPN allow rule if UFW is already active; it does not enable/reset a firewall or harden SSH blindly.
7. Save the returned private exports under `.secrets/` or another user-approved private location. The VPS's recovery result is `/root/vpn-guide-bootstrap-result.json`; installer logs are root-only. Do not paste these files or raw logs into public output.
8. Check the actual selected port. A busy 443 can select 8443. If the external TCP check fails, report the exact provider/custom-firewall action; root access is not provider-account access. Do not claim authentication from a TCP success.
9. Explain panel access with the printed SSH-forward command, the local browser URL (new automated installations use the root path `/`), and the separate panel credentials. The root password is not the new panel login. Keep the forward open while using the browser; no public panel HTTP port needs to be opened.
10. Import the generated `hiddify-profile.txt` into the client and follow the complete settings/verification path. Test a real HTTPS request through the local proxy and compare egress. Report what was tested and what remains unverified.

Keep a working SSH session during any separately authorized access-control change. Do not disable root login or password authentication before a replacement administrator/key has been tested.

## Existing clients and desktop networking

- Never stop/restart Invisible Man - XRay Client (the Windows Xray-based VPN app used in the original guide) or another running VPN client, replace its configuration, or alter Windows proxy/routes unless the user explicitly requests that action. A separate local port is sufficient for an isolated test.
- The temporary client test terminates only the child it starts. Do not extend it to discover/kill existing clients or claim it tests their GUI integration.
- `Repair-Hiddify.ps1` defaults to preview, requires Hiddify to be closed before applying, and preserves a backup. Let the user close the app; the helper must never kill it. Manual mode keeps another client's Windows proxy selection separate.
- A Hiddify build containing Xray libraries does not prove it has an executable Xray traffic backend. Check the actual implementation/core behavior. Preserve the version-specific nuance in `docs/clients.md`.

## Fast workflow for an existing server and Hiddify

Read this section before making live changes. The repository is a reusable guide, not a place to store live credentials. If working on the maintainer's existing machine, first locate private deployment `STATE.md` files under `$HOME/.config/` with a read-only search and read the file matching the requested deployment. Verify it against the live system; do not assume an earlier investigation's temporary profiles or ports still exist.

### Identify ownership and the requested final state

Distinguish three objects: a server **inbound** (listener), a central 3x-ui **client account** (credentials), and a Hiddify **profile** (an imported export). Removing an inbound can leave orphaned central client records. An account name is an ownership label, not interchangeable with another person's credentials. This PC must use its owner's `DEVICE_ACCOUNT` account; their phone uses `SECOND_DEVICE_ACCOUNT`. Keep other people's separately named accounts separate. Preserve accounts outside the requested deletion scope.

Before replacing an account, verify a new account with isolated requests, migrate any active Linux transport that uses the old UUID, and only then revoke the old account. Keep a recoverable private backup and a working administrative SSH connection. Do not leave several confusing diagnostic profiles in Hiddify after a requested cleanup.

### Use the exact panel-generated export and display name

**Never hand-build the final client URI or invent a replacement display name when 3x-ui already exports it.** On the checked 3x-ui 3.8.5 API, `GET panel/api/clients/links/{email}` returns the panel-generated link list. Select the requested inbound's link and preserve its complete query and fragment, including `spx`, `fp`, port, and account identity. For an inbound named `Personal VPN` and client `DEVICE_ACCOUNT`, the panel's display name is **`Personal VPN-DEVICE_ACCOUNT`**; import that exact name, rather than shortening it to `DEVICE_ACCOUNT` or substituting the inbound name alone. Use the corresponding panel export for `SECOND_DEVICE_ACCOUNT` and other owners too.

Save private exports outside Git, import the actual panel link, and verify the selected Hiddify account UUID matches that export without printing UUIDs in routine logs. A JSON generated manually for a test is not automatically the final panel export. Provide a requested private link/QR to the user, but never commit it.

### Inspect the live state before changing settings

- Read the panel API's inbound and central client lists. In 3x-ui 3.8.5, the relevant routes are `panel/api/inbounds/list`, `panel/api/inbounds/update/{id}`, `panel/api/inbounds/del/{id}`, `panel/api/clients/list`, `panel/api/clients/links/{email}`, and `panel/api/clients/del/{email}`. URL-encode account names. Do not assume legacy `inbounds/addClient` exists. API responses may already contain objects for settings/stream settings; do not blindly call `json.loads` on a dict. Normalize the type before editing and serialize for the expected request schema.
- The effective server config is conventionally `/usr/local/x-ui/bin/config.json`; do not print its credentials or private keys. Prefer supported API mutations to direct database writes. Back up SQLite consistently with its backup API, not a live bare file copy that ignores WAL.
- Read Hiddify's selected profile, mode, actual local listeners, and Windows' selected proxy. A running process or green button does not prove applications use that route. Windows may still have Invisible Man - XRay Client's manual proxy selected even while another app's VPN is active.
- Inspect fresh logs for the actual engine. Hiddify's privileged Windows VPN engine can use `%ProgramData%\Hiddify\AdminBgService\core\work\data\box.log` and `current-config.json`; AppData files can be stale. Use timestamps and the new request's error rather than historical errors.

### Isolate the failure with controlled tests

Use an unused loopback port and a child process you own. Change one variable at a time. Alternate real HTTPS requests between cases and record success, elapsed time, and exit address. Keep account, endpoint, SNI, flow, and engine constant when comparing fingerprints. Test a real site as well as the app's latency badge; the badge can disagree with working traffic. A longer curl timeout does not override the engine's internal timeout.

For an explicit Windows proxy request, use a nonempty exclusion argument such as `curl.exe --noproxy does-not-match.invalid --proxy http://127.0.0.1:PORT ...`. Windows PowerShell can lose an empty-string native argument, creating a false direct-path success. For a full Windows VPN test, use `curl.exe --noproxy '*' ...` and verify the actual exit. On Linux, explicitly disable inherited application proxies for a route-based VPN test.

The controlled US result was fingerprint-dependent: Chrome 0/12 vs Safari 12/12 with the original REALITY account. Google SNI stayed unchanged. Do not claim that Google sites or all US servers are blocked, or that message size alone was isolated. Safari's successful REALITY ClientHello was about 1,533 bytes; the 517-byte Safari hello belonged to a separate Trojan/TLS test. Do not transfer stock sing-box compatibility failures to Hiddify's fork without testing that implementation.

A later non-US endpoint reproduced Windows Hiddify Chrome 0/4 versus Safari 4/4; actual GUI VPN mode passed 2/2 after importing its canonical Safari export. Native Linux Xray 26.10.31 passed both fingerprints. Country is only an automation default, not proof of compatibility. Use an explicit Safari override for this live endpoint. Its earlier complete TCP unreachability later cleared; repeat fresh TCP probes before relying on old captures, and do not claim AiProtection caused that recovery without a controlled comparison. Read the matching private STATE.md for the latest result.

### Protect the current connection during Windows VPN tests

When the user requests timed tests, **arm an independent Windows-local disconnect watchdog before Connect**. A local deadline must not depend on chat or network connectivity. The checked CLI supports `HiddifyCli.exe admin_bgservice disconnect`; verify it works first. Preserve and restore the prior Windows proxy settings. If closing Hiddify is needed for a requested reset, target only that application and keep automatic reconnect disabled during testing. Never stop Invisible Man - XRay Client.

An SSH-backed temporary transport needs the real SSH server address outside TUN routing; a loopback forwarding address alone does not protect its outer connection. Verify the physical route before enabling TUN. A Windows host-route change needs real administrator rights; Codex full filesystem access is not Windows UAC elevation. Explain an actual OS permission requirement instead of asking repeatedly for permissions already granted.

Keep disposable probes separate from persistent working state. Linux TUN may internally feed a local SOCKS engine while still providing real routed TCP/UDP/DNS; distinguish that implementation detail from an application-only proxy. Prove both TCP and UDP before claiming whole-device functionality. A WSL/SSH-dependent profile is not a portable phone solution.

### Close the task cleanly

Verify the final inbound count, account ownership, profile count, selected panel-export name, endpoint, and fingerprint. Keep only profiles the user requested; retain backups privately, not as extra active profiles. Verify the GUI Connect button separately from isolated core tests, with the requested rollback deadline. Leave the final connection state explicit. A phone that cannot be controlled remotely still needs its exact new export imported by its owner; do not claim to have erased phone profiles from Windows.

Record sanitized current state in the private state file, update guide claims when new evidence supersedes an initial success, and commit each logical repository change separately. Do not publish private links or push commits without authorization.

## Version and evidence rules

The checked UI baseline is **3x-ui 3.8.5** and **Hiddify 5.5.5**, dated **2026-11-06**. The bootstrap deliberately pins the panel release. Do not silently change that pin without rechecking installer variables, CLI flags, API paths, payload schema, UI instructions and integration behavior together.

Use official release notes, documentation and version-pinned source for changing software behavior. Distinguish a reproduced result, a source-derived explanation, and a hypothesis. On 2026-11-07 the initial Android improvement after **Hiddify → Settings → DNS → Outbound domain strategy → IPv4 only** later stopped working. Keep it as a DNS check, not a confirmed universal fix. The controlled original VLESS/REALITY/Vision comparison using the installed Hiddify 5.5.5 engine on the US server produced **Chrome 0/12 successful HTTPS requests; Safari 12/12**, with only the fingerprint changed. Prefer Safari for this guide's US-server Hiddify setup and keep the optional provisioner's export consistent. The Google target/SNI stayed unchanged; distinguish browser fingerprint from website name. Do not claim all US servers block Chrome or that the responsible filtering operator was identified. Other client engines and versions need separate verification. The earlier Windows preference repair changed several settings together and did not isolate one causal option. Do not label REALITY undetectable or guarantee that every provider/engine version works.

Never claim fresh-VPS provisioning was live-tested when only the offline suite was run. A disposable, user-authorized VPS integration run is separate from unit, syntax and dry-run checks.

## Credentials, examples and illustrations

Keep deployment names, account labels and personal filesystem paths anonymous in tracked investigation reports; retain exact values only in private state files. Use placeholders or reserved documentation addresses such as `203.0.113.10` and `2001:db8::10`. Keep UUIDs, complete live VLESS links, QR codes, private keys, panel paths, passwords, tokens and subscription URLs out of tracked files and commit messages. Prefer a hidden prompt or a private input file to a literal URI in shell history.

All current SVGs are explicitly labeled navigation diagrams. Rebuild them with `python3 scripts/render_illustrations.py`. Do not represent them as captured screenshots. Actual new screenshots need authorized access or contributor captures; follow `images/README.md` and redact credentials opaquely before adding them. Do not invent current UI buttons that the checked version does not expose.

## Validation and commits

Run the checks appropriate to changed files:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B scripts/check_docs.py
bash -n scripts/server-check.sh
```

For PowerShell changes, run `tests/check-powershell.ps1` from Windows PowerShell. It uses repo-local fixtures and a mocked process lookup; it does not inspect or change real VPN apps. For diagram changes, regenerate the SVGs, check determinism, and visually inspect a rendered preview. Keep preview/test artifacts untracked.

Make **one commit for every logical change**, as requested by the repository owner. Keep the working tree clean after a completed step, preserve unrelated edits, and do not squash this step-by-step history without a request. Do not push, deploy, or change branch policy unless authorized. Mention unpushed local commits before the working folder is deleted.
