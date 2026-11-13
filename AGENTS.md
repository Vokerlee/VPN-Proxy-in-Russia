# Working in this repository

This repository is both a human VPN walkthrough and a small set of opt-in setup/diagnostic helpers. Start with `README.md`; read the guide relevant to the requested task before running its script. Keep user-facing documentation readable as a practical article with real screenshots where available, required values, expected results, and recovery steps. Put protocol/implementation depth in the separate expert guide.

## Human-first documentation rules

The README gives equal space and a complete starting sequence to the single-server and two-server paths. Start by explaining what a VPN does, what a server and client are, how traffic travels through one or two servers, and where a reader at each starting point should go. Link the server-rental page before asking the reader to have a VPS. Use natural, friendly language, as when helping a friend through their first setup. Explain each path’s cost, prerequisites and first connection in everyday words. Keep the tested core/key-share table in a collapsed reference section below the starting paths; retain version checks in the setup instructions where they are needed. Explain where the two panels connect and how to test each leg. Keep the single-server walkthrough in docs/single-server.md and keep its existing automation available. Use plain ASCII diagrams in fenced text blocks for connection maps, so they are readable without a renderer. Keep routes vertical. For the VPN comparison, place two vertical routes side by side: without VPN on the left, with VPN on the right. In “One server or two?”, place the two ASCII routes side by side: one server on the left, two servers on the right. Label them as one VPN connection versus two VPN connections, mark where each tunnel ends, and explain that the client connects once while the Russian server opens the second connection. Avoid repeating those diagrams in the later setup summaries. Use visual emphasis deliberately: box the components the current explanation focuses on and leave supporting steps plain. In the VPN comparison, highlight the rented VPN server and its hosting network. In other maps, emphasize the server, rule or connection being explained rather than boxing every step. Show internet providers in both VPN and non-VPN comparisons; explain when intermediate networks are omitted in a simplified routing map. Make clear that the encrypted tunnel travels through those networks; use real screenshots for UI instructions in the relevant guide. Keep automation optional.

Audit instructions by following both complete reading routes, including pages opened directly. Every required step must identify its machine/account, inputs, action, expected result and next destination. A shared page must give separate handoffs for single-server, Moscow-entry and foreign-relay roles. Rental instructions must state that the two-server example needs BOTH a FirstVDS Moscow order AND a HostVDS foreign order; after the Moscow order, explicitly link the foreign order. Having just one server never satisfies a two-server prerequisite. Qualify “already have a server,” “server version,” “server IP” and “next step” by role. Keep the one-server port, two-server ports, profile ownership and exit-address expectations consistent across linked pages. Prefer a specific instruction to leaving a necessary choice for the reader to infer.

Use Xray 26.7.28 as the only server-version preset in the setup guides and both relay defaults. Show how to read the installed version, install exactly v26.7.28 in the dashboard, and verify 26.7.28 plus Running afterward. Preserve actual earlier-version tests as labelled historical evidence. Explain first that 443 is the standard HTTPS port and 8443 a common HTTPS alternative, chosen to fit REALITY’s browser-like TLS connection setup. Do not claim the port number alone disguises a protocol. Explain that 443 and 8443 perform the same VPN role; their selection is about availability and consistent settings, not an inherent safety or camouflage advantage. Put provider-firewall changes only in failure troubleshooting; let readers try the public panel address and VPN connection first.

For the 3x-ui 3.8.5 GUI walkthrough, name the sidebar page and form tab before its fields. Create accounts through Clients → Add Client, attach an inbound in Basics, then set Flow in Credentials. Export through Client Information → Copy URL. Keep account creation separate from inbound creation. The REALITY key button is Get New Cert. Use Custom share address to export the desired host address, even when the panel is opened through IPv4. Configure Moscow outbound Send Through and Target Strategy in Basics rather than requiring manual JSON edits. Teach the two-server sequence as fully as the single-server sequence, without an upfront unexplained protocol table. Explain RAW versus XHTTP before choosing a transport, and place optional transport experiments and automation commands inside details sections. Explain what each setup script changes, replacement arguments, plan/apply, output files and the final connection check.

Explain a setting immediately before the reader uses it. VPN port selection belongs beside the inbound’s Port field, not in a separate server-preparation step before fail2ban. Do not tell the reader to choose or remember a setting for an unrelated later section when it can be chosen in the form itself.

Keep the normal server setup short. Do not add proactive port probes, listener commands, log inspections, target curl requests or fail2ban status commands to the normal setup walkthrough. Let the reader create the connection in the panel and test it in Hiddify; move command-line diagnostics to troubleshooting. Keep IPv6 configuration manual and provider-specific, with detailed Netplan examples in docs/ipv6-networking.md. Keep Hiddify repair and comparison commands in docs/hiddify-troubleshooting.md. Normal panel browser access must always use the public server IP. Keep one browser-access path: http://YOUR_SERVER_IP:YOUR_PANEL_PORT/YOUR_PANEL_PATH/. Remove optional branches that do not help finish the chosen setup. Put detailed failure recovery in troubleshooting instead of making a successful first setup pass through it. Introduce Xray only after the dashboard is installed: explain that it is the program carrying VPN connections, then give the reason for the selected version and the exact UI actions to install it. In 3x-ui 3.8.5, click the version beside Xray status, select the release’s radio circle in Xray Updates, confirm, and verify the version and Running status. Keep version tables out of the initial preparation step. Use the original simple fail2ban steps for SSH login protection. Keep UFW commands, firewall-state decision trees and administrator-account/SSH-lockdown detours out of the normal installation page; put failure diagnostics in troubleshooting. Fail2ban protects login attempts; it does not replace provider port access rules.

Do not interrupt a normal sequence with links such as “go to choosing the port.” Finish the current task, explain in plain words what the next task will accomplish, then let the reader encounter the next heading naturally. A conditional “already installed” case should say to leave the existing setting alone, not send the reader to an unexplained later task.

Every required step must first explain why it is needed and what it will accomplish, then give the commands or clicks, then give an observable result. Put explanations before actions, never after a command the reader was expected to run without context. Teach one concept, use it, then introduce the next. Do not front-load version tables, port tables or product names before the reader needs them. Mark the main sequence as required and each detour as optional or symptom-specific. Mark the point at which a working setup is finished; additional countries are optional and require additional rentals. Avoid making users collect terms or change settings whose role has not been explained. Explain script arguments beside their first setup example: --clients desktop,phone is a user-chosen comma-separated list of VPN account labels, not fixed device types; one label creates one account/link, and custom names change output filenames.

Define names before relying on them: VPS means a rented remote server; root is an administrator account; 3x-ui is the browser dashboard; Xray is the network engine; Hiddify is the connection app; a profile is the private connection link. Introduce ports, SSH and proxy modes where the reader needs them. Do not send a beginner to an expert glossary to complete a required step. Each guide must also make sense when opened directly: define an app or technical term at its first substantive use on that page. Use full product names, including Invisible Man - XRay Client. Keep migration-only app references out of the ordinary beginner steps. Explain a setting through its effect and the reader’s next action; avoid arguments about what a test does not prove unless the limitation changes that action.

Support Windows and Linux as administration/client platforms without calling the guide Windows-only. Ubuntu 24.04 was an example/test environment, not a universal server requirement; describe actual helper dependencies and supported Ubuntu/Debian deployments separately from the ordinary manual guide. Preserve the original sequential, practical writing style.

## Repository map

```text
README.md                       VPN basics, starting choices and guide index
AGENTS.md                       This repository's agent workflow
.gitignore                      Excludes private profiles, exports, backups and test artifacts
docs/
  two-hop-vpn.md                IPv6 prerequisites, panel linking, relay helper, second country
  single-server.md              Original one-server walkthrough and navigation
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
  hiddify-troubleshooting.md      App checks, isolated proxy tests and older client migration
  ipv6-networking.md             Provider-specific network examples and IPv6 diagnostics
  network-path-debugging.md       Direct/alternate-path controls and anonymous investigations
  automation.md                 Commands, prerequisites, output and rollback for each helper
  xray-internals.md             Architecture, wire layers, REALITY, Vision, DNS and routing
images/
  *.svg                         Original version-labeled navigation diagrams, not screenshots
  README.md                     Rebuild instructions and genuine screenshot capture/redaction list
scripts/
  Setup-Vpn.ps1                 Windows launcher; no local Python required; default plan only
  bootstrap_server.py           Python launcher; default plan only; native OpenSSH authentication
  provision_remote.py           Fresh single-server or panel-only payload
  bootstrap_relay.py            Two-hop launcher; default plan, preserve existing routes
  relay_remote.py               Remote 3x-ui relay configuration and verification
  ssh_http_connect.py           Explicit loopback HTTP CONNECT for SSH management
  Repair-Hiddify.ps1            Preference preview; explicit apply with backup; never stops apps
  vpn_profile.py                Inspect, generate config, isolated authenticated tunnel test
  server-check.sh               Read-only Linux VPS health/config summary
  render_illustrations.py       Deterministic SVG navigation-diagram renderer
  check_docs.py                 Offline local links, anchors, SVG and accidental-profile checks
tests/
  test_bootstrap.py             Input boundaries, fresh-install guard, payload/export behavior
  test_relay.py                 Relay routing, account reuse, IPv6 preflight and safe failure
  test_vpn_profile.py           Profile validation, overwrite/backup and NO_PROXY regression
  test_docs_and_server_check.py Guide navigation and diagnostic argument validation
  check-powershell.ps1          Syntax/fixture checks; simulated process guard; no real app access
.secrets/                       Ignored local exports; never add to Git
```

## Direct SSH first; stop on failure

For every newly requested server and every new server setup or troubleshooting session, the **first network action must be a direct SSH login to that server**. Use the supplied login and SSH port, or the documented defaults when none were supplied. Success means completing authentication and a harmless command such as `true`; an open TCP port or an SSH banner is insufficient.

Bypass configured SSH ProxyCommand/ProxyJump settings and do not reuse a multiplexed connection established through another VPN, proxy or jump host. Verify that the connection uses the intended direct route without stopping or reconfiguring the user's existing VPN applications. Preserve normal SSH host-key checking and hidden password entry. Bound the attempt, including a possible key-exchange stall. A local sandbox/network-permission denial is not a server result: obtain the required tool approval and make the actual direct attempt before deciding.

**If direct SSH fails at any stage, report the failure and stop work on that server.** This includes connection refusal, timeout, stalled key exchange and authentication failure. Do not fall back to the existing VPN/proxy, SSH forwarding, a jump host or an old connected session. Do not continue with panel access, provisioning, account/inbound creation, VPN-port probes, target/SNI/uTLS comparisons, packet captures or alternate-path experiments. Do not ask to bypass the rule as the routine next step.

Apply this gate to both fresh and existing servers. An earlier successful proxy connection or an existing installation does not satisfy it. Historical alternate-path experiments in `docs/network-path-debugging.md` document evidence; they do not authorize continuing after a failed direct SSH check.

## Allowed public VPN inbound ports

**Never create, move or test a public VPN inbound on a port other than TCP 443 or 8443.** This is the repository owner's explicit rule. Use Moscow port 443 for NL and FR, with account-based routing for FR. Use 8443 for FI. Preserve existing listeners. If neither allowed port is available, stop provisioning and report the conflict rather than selecting a random/high port. This restriction applies to public VPN inbounds, not SSH, the administration panel, or temporary loopback client proxies. Historical investigations on other ports are evidence only and do not authorize repeating those configurations.

## Single-server automation

The automatic path targets a **fresh Ubuntu/Debian systemd VPS**. The launchers default to Xray 26.7.28, Safari, classical Hiddify variants and separate desktop/phone accounts. RAW is the device-entry default. XHTTP entry is optional and uses empty flow. Explicit auto fingerprint selection retains the old country policy. An explicit request to set up that server authorizes the documented setup steps; do not ask for repetitive confirmations already covered by that request. Tool/sandbox approvals still apply. A request to edit docs or inspect a repository is not permission to provision a server.

1. Read `docs/quick-start.md` and `docs/automation.md`, then pass the direct-SSH gate above before any other network action or remote work. Only after successful direct SSH, verify whether the requested host is fresh or already managed. Use the given SSH port if nonstandard.
2. Run the local plan first:

   ```bash
   python3 scripts/bootstrap_server.py --host VPS_IPV4 --vpn-port 8443 --target www.apple.com --fingerprint safari --plan
   ```

3. For an authorized fresh setup, run the launcher with `--apply`, preserving the guide's explicit `--vpn-port 8443 --target www.apple.com --fingerprint safari --core-version 26.7.28 --key-share classical` preset unless the user chooses other values. Use an interactive terminal/PTY for OpenSSH's host-key and password prompts. On a Windows machine without Python, use `scripts/Setup-Vpn.ps1 -ServerIp VPS_IPV4 -Apply`.
4. OpenSSH must verify host identity using its normal known-host behavior. Never disable strict host-key checking or silently accept a changed key. The launchers let SSH read the root password; never add a password argument, write it into scripts/configs, or print it.
5. The payload refuses existing `/usr/local/x-ui/x-ui` or `/etc/x-ui/x-ui.db` before installation. Do not bypass that guard, delete the installation to retry, or rotate an existing account's credentials. For an existing deployment, use the manual guide and read-only diagnostics, then make only changes authorized by the user.
6. The helper installs pinned 3x-ui, independently pins Xray using official release SHA-256 metadata, creates the requested device accounts, applies ForceIPv4 to the new direct outbound, selects a free public VPN port, and enables direct public HTTP panel access. With an explicit auto fingerprint request during Apply, it resolves the public VPS IP's country and selects Safari for US or Chrome elsewhere. Explicit presets skip lookup. A failed unresolved lookup stops before installation instead of guessing. Export the exact panel-generated URI. It adds the VPN and panel TCP allow rules if UFW is already active; it does not enable/reset a firewall or harden SSH blindly.
7. Save the returned private exports under `.secrets/` or another user-approved private location. The VPS's recovery result is `/root/vpn-guide-bootstrap-result.json`; installer logs are root-only. Do not paste these files or raw logs into public output.
8. Check the actual selected port. A busy 443 can select 8443. If the external TCP check fails, report the exact provider/custom-firewall action; root access is not provider-account access. Do not claim authentication from a TCP success.
9. Give the complete public browser URL, including scheme, server IP, panel port and saved path (new automated installations use `/`), plus the separate panel credentials. The root password is not the panel login. The normal setup uses public HTTP as requested by the repository owner; do not silently replace it with SSH-only access or HTTPS. Do not add HTTPS certificate or SSH-forwarding alternatives to the beginner guide unless the user explicitly asks for them. Verify public reachability and login. Never publish live credentials in tracked files.
10. Import the generated `hiddify-profile.txt` into the client and follow the complete settings/verification path. Test a real HTTPS request through the local proxy and compare egress. Report what was tested and what remains unverified.

Keep a working SSH session during any separately authorized access-control change. Do not disable root login or password authentication before a replacement administrator/key has been tested.

## Primary two-hop setup

Read docs/two-hop-vpn.md before using scripts/bootstrap_relay.py. The working device-entry baseline is Xray 26.7.28 with Hiddify 5.5.5 and keyshare=classical. The guide and setup defaults use Xray 26.7.28 on every server, including foreign XHTTP exits. Keep the recorded 26.9.9 measurements clearly historical; do not rewrite actual test results or claim a new all-26.7.28 deployment was live-tested. Existing cores must not be silently replaced by a route-add command. Keep panel, server core and client-engine versions distinct. When the user requests a live setup, get the live chain working before spending time on script or guide polish. The original single-server mode remains available. Use NL, FR and FI in route names and diagrams. Document the Moscow port map and the manual IPv6 prerequisites in docs/schemes/README.md. A hub may have separate country inbounds on 443 and 8443; preserve other routes and account identities when adding a country. More countries can use account-based routing on a shared RAW entry through --shared-entry with distinct account labels. Put the account rule before the general route. Inter-server XHTTP is the helper default; --relay-transport raw preserves the older mode. Use the exact panel exports.

IPv6 activation and OS network configuration are the user's manual responsibility. The relay automation must only inspect addresses/routes and fail if prerequisites are absent. Never guess a gateway, assume all providers use the same Netplan file, or automatically edit Netplan, add addresses or install routes.

Direct SSH remains the default gate. An explicit user instruction to use an existing proxy takes precedence over the no-fallback rule above. In that case use only the explicitly authorized proxy, label management access as indirect, and do not claim direct access succeeded. The relay helper accepts explicit loopback HTTP-proxy options and opens its own connections; these are management-only. The deployed inter-server leg must use the actual foreign IPv6 address, not a local SSH forward or administration proxy.

Back up both existing panels before mutations. Create new inbounds disabled until routing is ready. Bind the foreign relay to its assigned IPv6 address, restrict the relay route to the hub IPv6 source, and verify foreign IPv4 egress. Test the existing foreign VPN from Moscow by address family when diagnosing reachability, then authenticate through the new IPv6 relay before enabling the Moscow entry. Scope the hub route to its own inbound tag so another country remains unchanged. Never add a direct Moscow fallback when the foreign relay is unavailable.

## Existing clients and desktop networking

- Never stop/restart Invisible Man - XRay Client (the Windows Xray-based VPN app used in the original guide) or another running VPN client, replace its configuration, or alter Windows proxy/routes unless the user explicitly requests that action. A separate local port is sufficient for an isolated test.
- The temporary client test terminates only the child it starts. Do not extend it to discover/kill existing clients or claim it tests their GUI integration.
- `Repair-Hiddify.ps1` defaults to preview, requires Hiddify to be closed before applying, and preserves a backup. Let the user close the app; the helper must never kill it. Manual mode keeps another client's Windows proxy selection separate.
- A Hiddify build containing Xray libraries does not prove it has an executable Xray traffic backend. Check the actual implementation/core behavior. Preserve the version-specific nuance in `docs/clients.md`.

## Fast workflow for an existing server and Hiddify

Read this section before making live changes, and pass the direct-SSH gate before starting live inspection or diagnostics. The repository is a reusable guide, not a place to store live credentials. If working on the maintainer's existing machine, first locate private deployment `STATE.md` files under `$HOME/.config/` with a read-only search and read the file matching the requested deployment. Verify it against the live system; do not assume an earlier investigation's temporary profiles or ports still exist.

### Identify ownership and the requested final state

Distinguish three objects: a server **inbound** (listener), a central 3x-ui **client account** (credentials), and a Hiddify **profile** (an imported export). Removing an inbound can leave orphaned central client records. An account name is an ownership label, not interchangeable with another person's credentials. This PC must use its owner's `DEVICE_ACCOUNT` account; their phone uses `SECOND_DEVICE_ACCOUNT`. Keep other people's separately named accounts separate. Preserve accounts outside the requested deletion scope.

Before replacing an account, verify a new account with isolated requests, migrate any active Linux transport that uses the old UUID, and only then revoke the old account. Keep a recoverable private backup and a working administrative SSH connection. Do not leave several confusing diagnostic profiles in Hiddify after a requested cleanup.

### Use the exact panel-generated export and display name

**Retrieve the panel's canonical client URI and preserve its account, endpoint, keys, query and display name.** For a compatible classical Hiddify profile, append only keyshare=classical before the fragment and save the canonical export separately. A user-requested display alias may change the fragment. Do not silently discard a key-share or transport option when converting a profile. On the checked 3x-ui 3.8.5 API, `GET panel/api/clients/links/{email}` returns the panel-generated link list. Select the requested inbound's link and preserve its complete query and fragment, including `spx`, `fp`, port, and account identity. For an inbound named `Personal VPN` and client `DEVICE_ACCOUNT`, the panel's display name is **`Personal VPN-DEVICE_ACCOUNT`**; import that exact name, rather than shortening it to `DEVICE_ACCOUNT` or substituting the inbound name alone. Use the corresponding panel export for `SECOND_DEVICE_ACCOUNT` and other owners too.

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

## README, screenshots and automation sections

Keep an optional script walkthrough collapsed inside each manual path with <details>. Show plan first, apply second, the private per-device output file and the final website check. IPv6 provisioning stays outside automation. The screenshot capture list in images/README.md should follow the same sequence and identify the panel, page, visible settings and private fields to cover.

A domestic entry or IPv6 route can provide a useful alternative path. Describe the observed reachability and tradeoffs. Any claim of a lower blocking probability needs measurements; do not invent a percentage, promise immunity for Russian IPs or equate a domestic SNI with an allowed destination.

## Version and evidence rules

The checked UI baseline is **3x-ui 3.8.5** and **Hiddify 5.5.5**, with the classical/XHTTP follow-up dated **2026-11-12**. Device entry on Xray 26.7.28 with classical mode produced a reported NL mobile success. Device entry on 26.9.9 with hybrid mode worked on desktop/Wi-Fi and failed in the reported mobile test. This is historical evidence from the recorded deployment, not the current guide preset. The owner now requests 26.7.28 for every server in the reusable setup instructions.

Classical-only handshakes are rejected by the newer REALITY requirement introduced around 26.9.8. Validate version/key-share pairs before provisioning. An ordinary Xray client config cannot request Hiddify's classical mode; the profile helper must use its Hiddify engine or refuse the conversion. The older core compatibility choice has security tradeoffs; the fresh helper disables MPTCP with GODEBUG=multipathtcp=0, and the guide references upstream security notes. The bootstrap deliberately pins the panel release. Do not silently change that pin without rechecking installer variables, CLI flags, API paths, payload schema, UI instructions and integration behavior together.

Use official release notes, documentation and version-pinned source for changing software behavior. Distinguish a reproduced result, a source-derived explanation, and a hypothesis. On 2026-11-07 the initial Android improvement after **Hiddify → Settings → DNS → Outbound domain strategy → IPv4 only** later stopped working. Keep it as a DNS check, not a confirmed universal fix. The controlled original VLESS/REALITY/Vision comparison using the installed Hiddify 5.5.5 engine on the US server produced **Chrome 0/12 successful HTTPS requests; Safari 12/12**, with only the fingerprint changed. Prefer Safari for this guide's US-server Hiddify setup and keep the optional provisioner's export consistent. The Google target/SNI stayed unchanged; distinguish browser fingerprint from website name. Do not claim all US servers block Chrome or that the responsible filtering operator was identified. Other client engines and versions need separate verification. The earlier Windows preference repair changed several settings together and did not isolate one causal option. Do not label REALITY undetectable or guarantee that every provider/engine version works.

Never claim fresh-VPS provisioning was live-tested when only the offline suite was run. A disposable, user-authorized VPS integration run is separate from unit, syntax and dry-run checks.

## Credentials, examples and illustrations

Keep deployment names, account labels and personal filesystem paths anonymous in tracked investigation reports; retain exact values only in private state files. Use placeholders or reserved documentation addresses such as `203.0.113.10` and `2001:db8::10`. Keep UUIDs, complete live VLESS links, QR codes, private keys, panel paths, passwords, tokens and subscription URLs out of tracked files and commit messages. Prefer a hidden prompt or a private input file to a literal URI in shell history.

The generated SVG UI pictures have been removed from the reading paths. Keep their existing source assets only for history; do not embed them again or generate substitute mock screenshots. Use written button paths until genuine screenshots are available. Follow images/README.md for capture locations and opaque redaction. Do not invent current UI buttons that the checked version does not expose. Every setup page must say what the reader needs, whether commands run locally or on a server, how to check the result and where to go next. Put historical tests and advanced recovery behind details sections rather than interrupting the first connection.

## Validation and commits

Run the checks appropriate to changed files:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B scripts/check_docs.py
bash -n scripts/server-check.sh
```

For PowerShell changes, run `tests/check-powershell.ps1` from Windows PowerShell. It uses repo-local fixtures and a mocked process lookup; it does not inspect or change real VPN apps. For diagram changes, regenerate the SVGs, check determinism, and visually inspect a rendered preview. Keep preview/test artifacts untracked.

Make **one commit for every logical change**, as requested by the repository owner. Keep the working tree clean after a completed step, preserve unrelated edits, and do not squash this step-by-step history without a request. Do not push, deploy, or change branch policy unless authorized. Mention unpushed local commits before the working folder is deleted.
