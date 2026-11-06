[← Guide index](../README.md) · Previous: [Linux Xray client](linux-xray.md)

# Share a working proxy without turning it into a public relay

**Optional: only for borrowing a proxy from another Linux machine.** For a normal desktop or phone VPN, [use Hiddify directly](clients.md) and skip this entire page. Choose **one** sharing method below; direct LAN access is an alternative to SSH forwarding.

Sometimes one Linux machine already has the right route, and a second device just needs to borrow it. You can do that without giving the whole internet an unauthenticated proxy port.

First complete the [Linux client walkthrough](linux-xray.md). The proxy host should already pass an HTTPS exit test through `127.0.0.1:10801`. Keep the public VPN server, this intermediate proxy host, and the device using it conceptually separate—even if one deployment combines some roles.

## The easy private path: forward it over SSH

Leave Xray bound to loopback on the proxy host. On the device that wants access, run:

```bash
ssh -N -L 18081:127.0.0.1:10801 YOUR_ADMIN@YOUR_PROXY_HOST
```

Choose an unused local port; 18081 is just an example. Verify SSH host identity as usual. The terminal stays open because it is carrying the forward. This command does not expose the proxy host's 10801 port publicly.

Then test from that same device:

```bash
curl --noproxy '' --proxy http://127.0.0.1:18081 https://www.cloudflare.com/cdn-cgi/trace
```

In PowerShell, use `curl.exe` and `--noproxy localhost,127.0.0.1` for this external URL. Programs on the borrowing device can use `127.0.0.1:18081` while the SSH session is running.

```text
Borrowing device :18081 → encrypted SSH → proxy host :10801
                                          → VLESS/REALITY → VPS → website
```

Close the SSH forwarding session to remove this access. A phone can usually use its own VLESS profile more conveniently than managing this desktop forwarding arrangement.

## Share directly only on an intentionally restricted network

If SSH forwarding is not suitable, the proxy host can listen on a LAN address. This is a separate exposure decision, not a required VPN setup step.

Before changing the listener:

1. Choose the specific trusted device/IP or private network that may reach it.
2. Restrict both the provider firewall, when relevant, and the host firewall to that source.
3. Preserve administration/SSH access. Inspect existing rule order rather than resetting a firewall remotely.
4. Configure proxy authentication if the clients support it; an allowlist is not a substitute for authentication on an untrusted network.

For example, with an already-managed UFW policy and no earlier broad allow rule for this port:

```bash
sudo ufw allow from YOUR_TRUSTED_DEVICE_IP to any port 10801 proto tcp
sudo ufw deny 10801/tcp
sudo ufw status numbered
```

The specific allow must precede the broad deny. Do not enable UFW remotely before allowing your actual SSH access, and do not assume a new deny overrides a pre-existing earlier allow. Check provider-side rules too.

Only then change the Xray client's local inbound `listen` from `127.0.0.1` to the intended LAN address, validate the configuration, and restart that client's Xray service. Binding `0.0.0.0` listens on every IPv4 interface, including public ones; it is broader than choosing one private address.

On the borrowing device, the proxy address becomes **the proxy host's reachable IP**, not `127.0.0.1`:

```text
http://YOUR_PROXY_HOST_IP:10801
```

Verify an allowed device works and a disallowed device cannot connect. Do not add an “allow everyone” firewall rule as a convenience step.

## Know what the shared proxy protects

An HTTP proxy can carry HTTPS CONNECT requests, so the website's TLS still protects HTTPS content. A bare LAN HTTP proxy does not itself encrypt the local hop or hide all connection metadata from that network. SSH forwarding protects that hop and keeps authentication in a familiar place.

This proxy is not a general UDP VPN. The borrowing program must use the proxy, and Windows System Proxy still only selects it for applications that honor that setting. For an entire device's routed traffic, use an appropriate VPN/TUN client and verify its routing policy.

If the exit test shows the proxy host's direct IP rather than the VPS, stop and inspect which listener/configuration the request reached. If it shows the VPS's IPv6, that may be normal egress; [ForceIPv4](force-ipv4.md) is a server-side choice.
