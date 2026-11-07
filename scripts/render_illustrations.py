#!/usr/bin/env python3
"""Render the guide's original SVG navigation diagrams.

Run from any directory: python3 scripts/render_illustrations.py
See images/README.md for the versioned sources and screenshot capture checklist.
These are labeled illustrations, never represented as genuine screenshots.
"""
from html import escape
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
FIGURES = [
    ("3x-ui-installation", "Keep the installer output", "3x-ui installation", [], "", [
        ("SSH into the VPS", "ssh root@YOUR_SERVER_IP", "Use the provider's console to verify the first host fingerprint."),
        ("Run the official installer", "Choose an unused panel port", "The administration port is separate from the VPN listener."),
        ("Save the complete result", "Panel URL + credentials", "Store the URL path, username and password privately.")]),
    ("3x-ui-panel-login", "Open the administration panel", "3x-ui 3.8.5", [], "", [
        ("Keep the SSH forwarding window open", "http://127.0.0.1:18080/YOUR_PATH/", "Open this on your computer. Replace YOUR_PATH with the saved panel path."),
        ("Enter the panel credentials", "Username + password", "Use the panel login, not the root password."),
        ("Sign in", "Login", "Confirm the panel and Xray versions on the dashboard.")]),
    ("3x-ui-add-inbound", "Create the public VPN listener", "3x-ui 3.8.5", ["Dashboard", "Inbounds", "Clients", "Outbounds", "Routing", "Xray Settings"], "Inbounds", [
        ("Open the main sidebar", "Inbounds", "Use the menu button if the sidebar is collapsed."),
        ("Open the form", "Add Inbound", "Protocol: vless. Public port: 443 if available."),
        ("Configure before saving", "REALITY + Vision", "The next diagram shows the transport and account fields.")]),
    ("3x-ui-reality-settings", "Fill in the REALITY form", "3x-ui 3.8.5", ["Inbounds", "New inbound", "Client account", "Transport"], "Transport", [
        ("Select transport and security", "RAW / TCP  |  REALITY", "Target: www.google.com:443; SNI: www.google.com for this example."),
        ("For a new inbound only", "Get New Key", "Keep generated short IDs. Never regenerate a working profile's keys."),
        ("Set the client flow", "xtls-rprx-vision", "Use the generated UUID and VLESS encryption=none."),
        ("Save the new listener", "Create / Save", "The selected public port must be allowed by both firewalls.")]),
    ("3x-ui-client-info", "Find the account's share action", "3x-ui 3.8.5", ["Inbounds", "Personal VPN", "Client: laptop"], "Client: laptop", [
        ("Expand the inbound", "Client list", "Use the account you intend to connect, not another device's row."),
        ("Open the row's action", "Info (i) / Share / QR", "Some layouts put the actions inside the three-dot menu."),
        ("Continue to connection details", "VLESS URL", "Export from the panel; do not type keys from a screenshot.")]),
    ("3x-ui-client-share", "Copy a usable client profile", "3x-ui 3.8.5", [], "", [
        ("In client connection details", "Copy VLESS URL", "vless://YOUR_UUID@YOUR_SERVER_IP:443?..."),
        ("On another device", "Show QR code", "A QR code grants the same access as the complete connection link."),
        ("In Hiddify", "+  >  Add from clipboard", "Select the newly imported profile before pressing Connect.")]),
    ("3x-ui-force-ipv4", "Choose IPv4 on the VPS outbound", "3x-ui 3.8.5", ["Dashboard", "Inbounds", "Outbounds", "Routing", "Xray Settings"], "Outbounds", [
        ("Use the separate main menu item", "Outbounds", "It is outside the Xray Settings submenu in this version."),
        ("Find tag direct, protocol freedom", "Edit", "Choose the outbound your routing actually uses."),
        ("Open Strategy / Domain Strategy", "ForceIPv4", "This is not Routing > Domain Strategy."),
        ("Apply the change", "Save", "Restart Xray if prompted, then run a fresh exit-IP test.")]),
    ("hiddify-import", "Bring your account into Hiddify", "Hiddify 5.5.5", ["Home", "Profiles", "Settings", "Logs"], "Profiles", [
        ("Copy the panel's real VLESS URL", "+  New profile", "The panel's browser URL is not a VPN profile."),
        ("Read your clipboard", "Add from clipboard", "Or scan the client's QR code on your phone."),
        ("Pick the new profile", "Personal VPN", "Check the server and port before connecting.")]),
    ("hiddify-outbound-ipv4", "Hiddify: the outbound IPv4 fix", "Hiddify 5.5.5 labels | Android fix reported 2026-11-07", ["Home", "Settings", "DNS"], "DNS", [
        ("Disconnect, then open Settings > DNS", "Outbound domain strategy", "Use this DNS field, not Routing > IPv6 routing."),
        ("Choose the exact value", "IPv4 only", "This is in Hiddify; server ForceIPv4 is a different setting."),
        ("Return home and reconnect", "Connect", "Open a website to check the connection. No Windows repair script is needed.")]),
    ("hiddify-settings", "Optional: further client troubleshooting", "Hiddify 5.5.5", ["Settings", "DNS", "Routing", "Inbound"], "DNS", [
        ("Settings > DNS", "Fake DNS: Off", "Start with ordinary DNS; add special features after the tunnel works."),
        ("Settings > Routing > Region", "Other", "Temporarily avoid country-specific bypass rules while diagnosing."),
        ("Settings > Routing > ...", "IPv6 routing: IPv4 only", "The server exit address is a separate setting.")]),
    ("hiddify-modes", "Choose what Connect will change", "Hiddify 5.5.5", ["Settings", "Inbound", "Service mode"], "Service mode", [
        ("Test without taking over Windows", "Proxy (manual)", "Applications must explicitly choose 127.0.0.1:12334."),
        ("Use Windows' proxy selection", "System Proxy", "Proxy-aware applications follow the local Hiddify listener."),
        ("Capture traffic through routing", "VPN / TUN", "Uses a virtual interface; Windows may request elevation.")]),
    ("windows-proxy", "Point Windows at the running listener", "Windows 11 navigation", ["Settings", "Network & internet", "Proxy"], "Proxy", [
        ("Under Manual proxy setup", "Set up / Edit", "Make sure Hiddify is already connected."),
        ("Enable Use a proxy server", "127.0.0.1  |  12334", "Use the local client port, not the VPS port or control API port."),
        ("Apply the selected endpoint", "Save", "This selects one system proxy; it does not combine two clients.")]),
    ("hiddify-connect", "Connect and check a website", "Hiddify 5.5.5", ["Home", "Personal VPN", "VPN / TUN"], "Personal VPN", [
        ("Select your profile in VPN / TUN mode", "Connect", "Accept the operating system VPN or administrator permission request."),
        ("Open an IP-check page in your browser", "cloudflare.com/cdn-cgi/trace", "Find the line starting with ip= and compare it with your server exit."),
        ("Try the website you wanted to use", "Open your website", "If the address check and website work, your first connection is complete.")]),
    ("3x-ui-first-visit", "Your first visit to the prepared panel", "3x-ui 3.8.5", ["Dashboard", "Inbounds", "Clients", "Outbounds", "Routing", "Xray Settings"], "Inbounds", [
        ("Sign in through the forwarded local URL", "Login", "Use the generated panel account, not the SSH root password."),
        ("Open the existing listener", "Inbounds  >  Personal VPN", "The setup helper already created it; do not add a duplicate."),
        ("Expand the first-device client", "Info / Share  >  Copy", "Or use the generated private hiddify-profile.txt export.")]),
    ("hostvds-new-server", "Example: create a server on HostVDS", "HostVDS navigation example; provider labels may change", ["Servers", "New Instance", "Configuration", "Operating Systems"], "Servers", [
        ("Open the server list", "Servers  >  New Instance", "This starts the provider's server-creation form."),
        ("Choose where it runs and its size", "Region + configuration", "Example: Europe / USA; a small personal-server plan."),
        ("Choose the server operating system", "Operating Systems  >  Ubuntu", "Use a supported offered release and include public IPv4."),
        ("Create it, then save its access details", "Deploy", "Wait for running status; check server details and registration email.")]),
]


def text(x, y, value, size=18, color="#172b4d", weight="400"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'


def rect(x,y,w,h,color,stroke="none",radius=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color}" stroke="{stroke}"/>'


def render(name,title,version,nav,selected,steps):
    height = 168 + len(steps)*115 + 58
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="{height}" viewBox="0 0 1120 {height}" role="img" aria-labelledby="title desc">',
         f'<title id="title">{escape(title)}</title>',
         '<desc id="desc">Numbered navigation illustration. This is not a captured screenshot. Exact positions may differ by version.</desc>',
         '<g font-family="DejaVu Sans,Arial,sans-serif">',rect(0,0,1120,height,"#f4f7fb"),
         rect(20,20,1080,112,"#14283f"),text(44,60,title,27,"#ffffff","700"),
         text(44,96,version+"  |  Navigation diagram, not a screenshot",16,"#c7d7eb")]
    x=44
    if nav:
        out.append(rect(28,152,216,len(steps)*115,"#ffffff","#d8e1ed"))
        out.append(text(48,185,"NAVIGATION",13,"#60738d","700"))
        for n,label in enumerate(nav):
            yy=205+n*43
            chosen=label==selected
            if chosen: out.append(rect(38,yy-20,196,35,"#dbeafe"))
            for k,line in enumerate(textwrap.wrap(label,22)):
                out.append(text(49,yy+k*15,line,14,"#114b91" if chosen else "#53657d","700" if chosen else "400"))
        x=272
    w=1120-x-30
    for idx,(caption,button,helptext) in enumerate(steps,1):
        yy=152+(idx-1)*115
        out.extend([rect(x,yy,w,102,"#ffffff","#d8e1ed"),
                    f'<circle cx="{x+25}" cy="{yy+29}" r="16" fill="#0b62b9"/>',
                    text(x+20,yy+35,str(idx),16,"white","700"),text(x+51,yy+31,caption,17)])
        bw=min(w-80,max(180,len(button)*8.8+30))
        out.extend([rect(x+51,yy+42,bw,30,"#e7f1fd","#6a9dd4",7),text(x+64,yy+63,button,15,"#074985","700")])
        lines=textwrap.wrap(helptext, int((w-70)/7.2))
        for n,line in enumerate(lines[:1]): out.append(text(x+51,yy+91,line,13,"#53657d"))
    out.append(text(34,height-22,"Follow the adjacent guide for checks and version-specific alternatives. All values shown are placeholders.",14,"#53657d"))
    out.extend(["</g>","</svg>\n"])
    return "\n".join(out)


SCHEMES = [
    ("connection-path", "What you are building", "Your device reaches websites through the server you control.", [
        ("After connecting", [("Your computer or phone", "Runs the connection app"),
                              ("Your rented server", "Carries the protected connection"),
                              ("The website", "Sees the server's exit address")])]),
    ("setup-roadmap", "The whole setup in four steps", "Start at the first step you have not completed. Scripts are optional.", [
        ("The manual walkthrough", [("1. Get a server", "Choose Ubuntu and save login details"),
                                    ("2. Install its dashboard", "Open the dashboard in a browser"),
                                    ("3. Create an account", "Copy the private connection link"),
                                    ("4. Connect your device", "Import the link and check the result")])]),
    ("ports-paths", "VPN traffic and panel access take different paths", "These are example ports, not values every installation must use.", [
        ("Website traffic through the VPN", [("Browser / application", "Uses the selected local proxy"),
                                               ("This computer :12334", "Hiddify's local proxy listener"),
                                               ("VPS :443 or :8443", "Public VPN listener"),
                                               ("Website :443", "The destination's HTTPS service")]),
        ("Private browser access to the server dashboard", [("Browser :18080", "Your computer's forwarded port"),
                                                             ("SSH to VPS :22", "Encrypted administration connection"),
                                                             ("VPS loopback :27297", "Private dashboard listener")])]),
    ("connection-modes", "One Connect button, three scopes", "Choose the scope deliberately; a running app does not automatically capture every request.", [
        ("Proxy / manual mode", [("Chosen application", "Explicitly uses the local proxy"),
                                  ("Local proxy", "Forwards this application's requests"),
                                  ("Rented server", "Opens the destination connection")]),
        ("System Proxy mode", [("Proxy-aware apps", "Follow Windows' proxy setting"),
                                ("Selected local proxy", "One chosen endpoint, not two merged clients"),
                                ("Rented server", "Carries the selected requests")]),
        ("VPN / TUN mode", [("Routed app traffic", "Subject to route and bypass rules"),
                            ("Virtual interface", "Captures traffic using OS networking"),
                            ("Rented server", "Carries the configured traffic")])]),
    ("troubleshooting-path", "Find the first stage that fails", "A successful early check does not prove that the later stages work.", [
        ("Follow the request", [("1. Local app", "Is the intended proxy listening?"),
                                 ("2. Server port", "Can this network reach the VPN port?"),
                                 ("3. Account handshake", "Does the profile authenticate?"),
                                 ("4. Website request", "Does HTTPS work through the proxy?")]),
        ("Then check the application you actually use", [("Explicit proxy test works", "The profile and that route are usable"),
                                                         ("Browser still unchanged", "Check system proxy or application rules"),
                                                         ("IP is unexpected", "Compare direct and server egress")])]),
]


def render_scheme(name, title, subtitle, rows):
    height=180+len(rows)*175+42
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="{height}" viewBox="0 0 1120 {height}" role="img" aria-labelledby="title desc">',
         f'<title id="title">{escape(title)}</title>',
         f'<desc id="desc">{escape(subtitle)} Conceptual network and setup diagram.</desc>',
         '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#236bb0"/></marker></defs>',
         '<g font-family="DejaVu Sans,Arial,sans-serif">',rect(0,0,1120,height,"#f4f7fb"),
         rect(20,20,1080,112,"#14283f"),text(44,60,title,26,"#ffffff","700"),
         text(44,98,subtitle,15,"#c7d7eb")]
    for row,(label,nodes) in enumerate(rows):
        y=162+row*175
        out.append(text(40,y,label,17,"#203c5a","700"))
        gap=38
        width=(1040-gap*(len(nodes)-1))/len(nodes)
        for n,(heading,body) in enumerate(nodes):
            x=40+n*(width+gap)
            out.append(rect(x,y+18,width,118,"#ffffff","#9bb8d7"))
            for line_no,line in enumerate(textwrap.wrap(heading,max(12,int((width-28)/9)))):
                out.append(text(x+14,y+47+line_no*21,line,17,"#114b91","700"))
            heading_lines=len(textwrap.wrap(heading,max(12,int((width-28)/9))))
            start_y=y+55+(heading_lines-1)*21
            for line_no,line in enumerate(textwrap.wrap(body,max(16,int((width-28)/7.5)))):
                out.append(text(x+14,start_y+line_no*18+20,line,14,"#53657d"))
            if n<len(nodes)-1:
                out.append(f'<line x1="{x+width+4}" y1="{y+77}" x2="{x+width+gap-5}" y2="{y+77}" stroke="#236bb0" stroke-width="2.5" marker-end="url(#arrow)"/>')
    out.append(text(40,height-20,"Conceptual scheme. Follow the adjacent guide for exact settings, button paths and verification.",14,"#53657d"))
    out.extend(["</g>","</svg>\n"])
    return "\n".join(out)


def main():
    folder=ROOT/"images"
    folder.mkdir(exist_ok=True)
    for entry in FIGURES:
        (folder/(entry[0]+".svg")).write_text(render(*entry),encoding="utf-8")
    for entry in SCHEMES:
        (folder/(entry[0]+".svg")).write_text(render_scheme(*entry),encoding="utf-8")
    print(f"Rendered {len(FIGURES)} button diagrams and {len(SCHEMES)} visual schemes in {folder.relative_to(ROOT)}")


if __name__=="__main__":
    main()
