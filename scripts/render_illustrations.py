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
        ("Paste the full panel URL", "https://PANEL_HOST:PANEL_PORT/PATH/", "Keep the URL path printed by the installer."),
        ("Enter the panel credentials", "Username + password", "These are not the client's UUID or REALITY keys."),
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
    ("hiddify-settings", "Build a simple starting configuration", "Hiddify 5.5.5", ["Settings", "DNS", "Routing", "Inbound"], "DNS", [
        ("Settings > DNS", "Fake DNS: Off", "Start with ordinary DNS; add special features after the tunnel works."),
        ("Settings > Routing > Region", "Other", "Temporarily avoid country-specific bypass rules while diagnosing."),
        ("Settings > Inbound > Local proxy", "Port: 12334", "Keep another client's 10801 listener separate.")]),
    ("hiddify-modes", "Choose what Connect will change", "Hiddify 5.5.5", ["Settings", "Inbound", "Service mode"], "Service mode", [
        ("Test without taking over Windows", "Proxy (manual)", "Applications must explicitly choose 127.0.0.1:12334."),
        ("Use Windows' proxy selection", "System Proxy", "Proxy-aware applications follow the local Hiddify listener."),
        ("Capture traffic through routing", "VPN / TUN", "Uses a virtual interface; Windows may request elevation.")]),
    ("windows-proxy", "Point Windows at the running listener", "Windows 11 navigation", ["Settings", "Network & internet", "Proxy"], "Proxy", [
        ("Under Manual proxy setup", "Set up / Edit", "Make sure Hiddify is already connected."),
        ("Enable Use a proxy server", "127.0.0.1  |  12334", "Use the local client port, not the VPS port or control API port."),
        ("Apply the selected endpoint", "Save", "This selects one system proxy; it does not combine two clients.")]),
    ("hiddify-connect", "A green button is only the beginning", "Hiddify 5.5.5", ["Home", "Personal VPN", "Proxy mode"], "Personal VPN", [
        ("Start the selected profile", "Connect", "In manual mode, Windows' proxy selection stays unchanged."),
        ("Make an explicit proxy request", "HTTPS exit test", "PowerShell: curl.exe --proxy http://127.0.0.1:12334 ..."),
        ("Read the response", "ip=THE_VPS_EXIT_IP", "An IPv6 result may be the VPS's legitimate outgoing address.")]),
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


def main():
    folder=ROOT/"images"
    folder.mkdir(exist_ok=True)
    for entry in FIGURES:
        (folder/(entry[0]+".svg")).write_text(render(*entry),encoding="utf-8")
    print(f"Rendered {len(FIGURES)} navigation diagrams in {folder.relative_to(ROOT)}")


if __name__=="__main__":
    main()
