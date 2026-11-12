#!/usr/bin/env bash
# Read-only VPS checks. Guide: docs/troubleshooting.md#server-checks
# Install/setup explanation: docs/server-setup.md#6-verify-services-before-creating-a-client
set -u

usage() {
    cat <<'EOF'
Usage: bash scripts/server-check.sh [--port 443] [--config PATH] [--xray PATH]
                                    [--network] [--target www.google.com]

Read-only checks for a Linux VPS running 3x-ui. No installs, restarts, firewall
changes, database changes, or private-key/client-ID output.
--network  Also make direct IPv4/IPv6 HTTPS requests to the chosen target.
--target   Hostname for those optional requests (no URL or credentials).

Read docs/troubleshooting.md#server-checks and docs/server-setup.md.
https://github.com/Vokerlee/VPN-Proxy-in-Russia/blob/master/docs/automation.md
Exit: 0=no critical check failed, 1=check failed, 2=invalid arguments.
EOF
}
port=443
config=/usr/local/x-ui/bin/config.json
xray_binary=""
network=0
target=www.google.com
failed=0
while (($#)); do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        --port|--config|--xray|--target)
            if (($# < 2)); then printf 'Missing value for %s\n' "$1" >&2; exit 2; fi
            case "$1" in
                --port) port=$2 ;;
                --config) config=$2 ;;
                --xray) xray_binary=$2 ;;
                --target) target=$2 ;;
            esac
            shift 2 ;;
        --network) network=1; shift ;;
        *) printf 'Unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
done
if [[ ! $port =~ ^[0-9]{1,5}$ ]] || ((10#$port < 1 || 10#$port > 65535)); then
    printf 'Port must be between 1 and 65535.\n' >&2; exit 2
fi
port=$((10#$port))
if [[ ! $target =~ ^[A-Za-z0-9.-]+$ ]] || [[ $target == -* ]]; then
    printf 'Target must be a hostname, without a scheme or port.\n' >&2; exit 2
fi
printf '3x-ui VPS check; VPN TCP port %s. No configuration will be changed.\n' "$port"
if command -v systemctl >/dev/null 2>&1; then
    printf '\nPanel service: '
    if ! systemctl is-active x-ui; then failed=1; fi
    systemctl --failed --no-pager || failed=1
else
    printf 'systemctl is unavailable; run this helper on the VPS.\n' >&2
    failed=1
fi
printf '\nPublic listener check:\n'
if command -v ss >/dev/null 2>&1; then
    if listener=$(ss -H -lnt "sport = :$port" 2>/dev/null) && [[ -n $listener ]]; then
        printf '%s\n' "$listener"
        if ! printf '%s\n' "$listener" | awk '{print $4}' | grep -Eq '(^|\[)(0\.0\.0\.0|::)|^\*:'; then
            printf 'Check the bind address: a loopback-only listener is not public.\n'
        fi
    else
        printf 'No TCP listener found on %s, or ss could not inspect it.\n' "$port"
        failed=1
    fi
else
    printf 'ss is unavailable; listener not checked.\n'; failed=1
fi
printf '\nClock:\n'
if command -v timedatectl >/dev/null 2>&1; then
    timedatectl show -p NTPSynchronized -p Timezone || failed=1
fi
if [[ -x /usr/local/x-ui/x-ui ]]; then
    printf '\nPanel version: '
    /usr/local/x-ui/x-ui -v || failed=1
fi
if [[ -z $xray_binary ]]; then
    xray_binary=$(command -v xray 2>/dev/null || true)
    if [[ -z $xray_binary ]]; then
        for candidate in /usr/local/x-ui/bin/xray-*; do
            if [[ -f $candidate && -x $candidate ]]; then xray_binary=$candidate; break; fi
        done
    fi
fi
printf '\nXray version/config syntax:\n'
if [[ -n $xray_binary && -x $xray_binary && -r $config ]]; then
    "$xray_binary" version || failed=1
    env XRAY_LOCATION_ASSET="$(dirname "$xray_binary")" "$xray_binary" run -test -config "$config" || failed=1
else
    printf 'Need a readable config and executable Xray path; use --config and --xray.\n'
    failed=1
fi
if command -v python3 >/dev/null 2>&1 && [[ -r $config ]]; then
    printf '\nRedacted configuration summary:\n'
    python3 - "$config" <<'PYCODE' || failed=1
import json,sys
with open(sys.argv[1], encoding="utf-8") as f:
    c=json.load(f)
for inbound in c.get("inbounds", []):
    s=inbound.get("streamSettings") or {}
    print("Inbound:", {k:inbound.get(k) for k in ("tag","listen","port","protocol")},
          "transport=",s.get("network"),"security=",s.get("security"),
          "accounts=",len((inbound.get("settings") or {}).get("clients",[])),
          "flows=", sorted({client.get("flow", "") for client in (inbound.get("settings") or {}).get("clients", [])}),
          "xhttp_mode=", (s.get("xhttpSettings") or {}).get("mode"))
for outbound in c.get("outbounds", []):
    if outbound.get("protocol")=="freedom":
        sock=((outbound.get("streamSettings") or {}).get("sockopt") or {})
        print("Direct outbound:",outbound.get("tag"),"family strategy=",
              sock.get("domainStrategy") or (outbound.get("settings") or {}).get("domainStrategy") or "AsIs")
    elif outbound.get("protocol")=="vless":
        stream=outbound.get("streamSettings") or {}
        peers=(outbound.get("settings") or {}).get("vnext", [])
        print("VLESS outbound:",outbound.get("tag"),"transport=",stream.get("network"),
              "xhttp_mode=",(stream.get("xhttpSettings") or {}).get("mode"),
              "IPv6_endpoint=",bool(peers and ":" in peers[0].get("address", "")))
print("Classical/hybrid key share is a client-profile setting. Match it to the printed core version; see docs/handshakes-and-versions.md.")
PYCODE
fi
if ((network)); then
    printf '\nDirect VPS HTTPS reachability (not an authenticated VPN test):\n'
    if command -v curl >/dev/null 2>&1; then
        for family in 4 6; do
            printf 'IPv%s: ' "$family"
            if ! curl "-$family" --noproxy '' --silent --show-error --output /dev/null \
                --write-out 'HTTP %{http_code}\n' --connect-timeout 5 --max-time 8 "https://$target/"; then
                printf 'Unreachable over IPv%s. IPv6 may intentionally be unavailable.\n' "$family"
            fi
        done
    else
        printf 'curl is unavailable; optional network checks skipped.\n'; failed=1
    fi
fi
printf '\nProvider firewalls and client authentication are not established by these checks.\n'
printf 'Next: docs/troubleshooting.md and an authenticated client request.\n'
exit "$failed"
