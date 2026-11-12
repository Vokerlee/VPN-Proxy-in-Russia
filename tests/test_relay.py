"""Offline relay tests: route isolation, fail-closed setup, exports and manual IPv6 prerequisites."""
import base64
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import bootstrap_relay as launcher
import relay_remote as remote
import ssh_http_connect as proxy

UUID = "123e4567-e89b-42d3-a456-426614174000"
PUBLIC = base64.urlsafe_b64encode(bytes(range(32))).decode().rstrip("=")


def link(host="2001:db8:2::1", port=443, label="Relay-nl"):
    host = "[" + host + "]" if ":" in host else host
    return ("vless://" + UUID + "@" + host + ":" + str(port) +
            "?flow=xtls-rprx-vision&security=reality&type=tcp&sni=www.google.com"
            "&fp=chrome&pbk=" + PUBLIC + "&sid=abcd&spx=%2Fexact-export#" + label)


def template():
    return {"outbounds": [
        {"tag": "direct", "protocol": "freedom", "settings": {"keep": True}},
        {"tag": "blocked", "protocol": "blackhole"},
        {"tag": "relay-de", "protocol": "vless", "settings": {"keep": "country two"}}],
        "routing": {"rules": [
            {"type": "field", "inboundTag": ["api"], "outboundTag": "api"},
            {"type": "field", "inboundTag": ["in-443-tcp"], "outboundTag": "relay-de"},
            {"type": "field", "ip": ["geoip:private"], "outboundTag": "blocked"}]}}


class RelayTests(unittest.TestCase):
    def test_shared_entry_normal_apply_reuses_listener_and_exports_country_accounts(self):
        inbound = {"id": 3, "enable": True, "port": 443, "listen": "0.0.0.0", "protocol": "vless",
                   "remark": "VLESS RU", "tag": "in-443-tcp", "settings": {"clients": [{"email": "desktop"}]},
                   "streamSettings": {"network": "tcp", "realitySettings": {"serverNames": ["www.google.com"]}}}
        options = {"role": "hub", "port": 443, "listen": "0.0.0.0", "target": "www.google.com",
                   "fingerprint": "chrome", "hub_ipv6": "2001:db8:1::2", "route": "fr", "remark": "VLESS RU",
                   "clients": ["FR-phone"], "exit_link": link(), "shared_entry": True,
                   "export_host": "203.0.113.10"}
        panel = mock.Mock()
        panel.api.side_effect = lambda endpoint, *args: [inbound] if endpoint == "inbounds/list" else None
        panel.template.return_value = template()
        panel.export.return_value = link("203.0.113.10", label="VLESS-RU-FR-phone")
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(remote, "STATE", Path(directory) / "routes.json"), \
                mock.patch.object(remote, "Panel", return_value=panel), \
                mock.patch.object(remote, "validate_runtime"), \
                mock.patch.object(remote, "assert_free", side_effect=AssertionError("shared listener is occupied")), \
                mock.patch.object(remote, "backup", return_value="/private/backup"), \
                mock.patch.object(remote, "check_core"), \
                mock.patch.object(remote.time, "sleep"), \
                mock.patch.object(remote.shutil, "which", return_value=None):
            result = remote.apply_route(options)
        self.assertEqual(result["inbound_id"], 3)
        self.assertIn("FR-phone", result["links"])
        panel.attach.assert_called_once_with(3, ["FR-phone"])
        panel.activate.assert_not_called()
        changed = panel.set_template.call_args.args[0]
        self.assertEqual(changed["routing"]["rules"][1]["user"], ["FR-phone"])
        self.assertFalse(any(call.args[0] == "inbounds/add" for call in panel.api.call_args_list))

    def test_shared_entry_refuses_to_reroute_an_existing_country_account(self):
        inbound = {"id": 3, "enable": True, "port": 443, "listen": "0.0.0.0", "protocol": "vless",
                   "settings": {"clients": [{"email": "desktop"}]},
                   "streamSettings": {"network": "tcp", "realitySettings": {"serverNames": ["yandex.ru"]}}}
        panel = mock.Mock()
        panel.api.return_value = [inbound]
        options = {"role": "hub", "port": 443, "listen": "0.0.0.0", "target": "yandex.ru",
                   "fingerprint": "safari", "hub_ipv6": "2001:db8:1::2", "route": "fr", "remark": "VLESS RU",
                   "clients": ["desktop"], "exit_link": link(), "shared_entry": True}
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(remote, "STATE", Path(directory) / "routes.json"), \
                mock.patch.object(remote, "Panel", return_value=panel), \
                mock.patch.object(remote, "validate_runtime"), \
                mock.patch.object(remote, "backup") as backup:
            with self.assertRaisesRegex(ValueError, "distinct country"):
                remote.apply_route(options)
        backup.assert_not_called()
        panel.attach.assert_not_called()

    def test_defaults_select_the_tested_core_pair_and_xhttp_relay(self):
        args = launcher.validate(launcher.parser().parse_args([
            "--hub-host", "203.0.113.10", "--exit-host", "198.51.100.20",
            "--exit-ipv6", "2001:db8:2::1", "--route", "nl"]))
        self.assertEqual((args.hub_core_version, args.entry_key_share, args.relay_transport,
                          args.exit_core_version), ("26.7.28", "classical", "xhttp", "26.9.9"))
        args.hub_core_version = "26.9.9"
        with self.assertRaisesRegex(ValueError, "classical"):
            launcher.validate(args)

    def test_shared_rule_is_user_scoped_and_precedes_general_route(self):
        result = remote.hub_template(template(), "in-443-tcp", "fr", link(),
                                     "2001:db8:1::2", ["FR-desktop", "FR-phone"])
        rules = result["routing"]["rules"]
        self.assertEqual(rules[1]["user"], ["FR-desktop", "FR-phone"])
        self.assertEqual(rules[1]["outboundTag"], "relay-fr")
        self.assertEqual(rules[2]["outboundTag"], "relay-de")

    def test_xhttp_relay_account_and_inbound_use_empty_flow_and_path(self):
        options = {"target": "www.google.com", "fingerprint": "chrome", "port": 443,
                   "remark": "Relay nl", "listen": "2001:db8:2::1", "transport": "xhttp",
                   "xhttp_path": "/relay-nl"}
        with mock.patch.object(remote, "key_pair", return_value=("PRIVATE", PUBLIC)):
            value = remote.new_inbound(options)
        self.assertEqual(json.loads(value["streamSettings"])["xhttpSettings"],
                         {"path": "/relay-nl", "mode": "auto"})
        panel = remote.Panel.__new__(remote.Panel)
        panel.options = options
        panel.api = mock.Mock(side_effect=[[], None])
        panel.attach(1, ["relay-nl"])
        self.assertEqual(panel.api.call_args_list[-1].args[1]["client"]["flow"], "")

    def test_existing_core_mismatch_stops_before_panel_mutation(self):
        ssh = mock.Mock(description="hub directly")
        with self.assertRaisesRegex(ValueError, "differs"):
            launcher.ensure_panel(ssh, {"panel_present": True, "core_version": "Xray 26.9.9 build"},
                                  "203.0.113.10", 22, 27297, 443, "yandex.ru", "safari")
        ssh.payload.assert_not_called()

    def test_plan_never_connects_or_creates_exports(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "absent"
            args = ["--hub-host", "203.0.113.10", "--exit-host", "198.51.100.20",
                    "--exit-ipv6", "2001:db8:2::1", "--route", "nl",
                    "--output-dir", str(output)]
            with mock.patch.object(launcher, "SSH", side_effect=AssertionError("network")):
                with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
                    self.assertEqual(launcher.main(args), 0)
            self.assertFalse(output.exists())
            self.assertIn("Plan only", stdout.getvalue())

    def test_inputs_and_proxy_are_explicit_and_bounded(self):
        args = launcher.parser().parse_args(["--hub-host", "203.0.113.10",
            "--exit-host", "198.51.100.20", "--exit-ipv6", "2001:db8:2::1", "--route", "nl"])
        for field, value in [("entry_port", 38457), ("exit_port", 2096),
                             ("route", "../../replace"), ("entry_target", "site;command"),
                             ("exit_ipv6", "fe80::1"), ("exit_ipv6", "2001:db8::/64"),
                             ("clients", "desktop,desktop"), ("clients", "desktop;command"),
                             ("exit_ssh_proxy", "198.51.100.1:10801")]:
            changed = copy.deepcopy(args)
            setattr(changed, field, value)
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    launcher.validate(changed)
        self.assertEqual(proxy.proxy_address("127.0.0.1:10801"), ("127.0.0.1", 10801))

    def test_new_hub_route_preserves_second_country_and_has_no_direct_fallback(self):
        before = template()
        saved = copy.deepcopy(before)
        result = remote.hub_template(before, "in-8443-tcp", "nl", link(), "2001:db8:1::2")
        self.assertEqual(before, saved)
        self.assertEqual(result["routing"]["rules"][0], saved["routing"]["rules"][0])
        self.assertEqual(result["routing"]["rules"][1],
                         {"type": "field", "inboundTag": ["in-8443-tcp"], "outboundTag": "relay-nl"})
        self.assertEqual(result["routing"]["rules"][2], saved["routing"]["rules"][1])
        outgoing = result["outbounds"][-1]
        self.assertEqual(outgoing["tag"], "relay-nl")
        self.assertEqual(outgoing["sendThrough"], "2001:db8:1::2")
        self.assertEqual(outgoing["settings"]["vnext"][0]["address"], "2001:db8:2::1")
        self.assertEqual(outgoing["streamSettings"]["sockopt"]["domainStrategy"], "ForceIPv6")
        with self.assertRaisesRegex(ValueError, "already exists"):
            remote.hub_template(result, "in-443-tcp", "nl", link(), "2001:db8:1::2")
        with self.assertRaisesRegex(ValueError, "literal IPv6"):
            remote.hub_template(before, "in-8443-tcp", "nl",
                                link("198.51.100.20"), "2001:db8:1::2")

    def test_exit_accepts_only_hub_source_and_rejects_ipv6_destinations(self):
        before = template()
        saved = copy.deepcopy(before)
        result = remote.exit_template(before, "relay-in", "2001:db8:1::2")
        self.assertEqual(before, saved)
        rules = result["routing"]["rules"]
        self.assertEqual(rules[1]["ip"], ["::/0"])
        self.assertEqual(rules[1]["outboundTag"], "blocked")
        self.assertEqual(rules[2]["source"], ["2001:db8:1::2/128"])
        self.assertEqual(rules[2]["outboundTag"], "direct")
        self.assertEqual(rules[3], {"type": "field", "inboundTag": ["relay-in"], "outboundTag": "blocked"})
        self.assertEqual(result["outbounds"][0]["settings"]["keep"], True)
        self.assertEqual(result["outbounds"][0]["streamSettings"]["sockopt"]["domainStrategy"], "ForceIPv4")
        self.assertEqual(result["outbounds"][2], saved["outbounds"][2])

    def test_inbound_stays_disabled_until_route_is_ready(self):
        options = {"target": "yandex.ru", "fingerprint": "safari", "port": 8443,
                   "remark": "Moscow NL", "listen": "0.0.0.0"}
        with mock.patch.object(remote, "key_pair", return_value=("PRIVATE", PUBLIC)):
            value = remote.new_inbound(options)
        self.assertFalse(value["enable"])
        self.assertEqual(json.loads(value["settings"])["clients"], [])
        self.assertEqual(json.loads(value["streamSettings"])["realitySettings"]["serverNames"], ["yandex.ru"])

    def test_existing_owner_account_is_attached_without_rotating_uuid(self):
        panel = remote.Panel.__new__(remote.Panel)
        calls = []
        def api(endpoint, payload=None):
            calls.append((endpoint, payload))
            if endpoint == "clients/list":
                return [{"email": "desktop", "uuid": UUID}]
        panel.api = api
        panel.attach(3, ["desktop", "phone"])
        self.assertIn(("clients/desktop/attach", {"inboundIds": [3]}), calls)
        added = [p for ep, p in calls if ep == "clients/add"]
        self.assertEqual(len(added), 1)
        self.assertEqual(added[0]["client"]["email"], "phone")
        self.assertNotEqual(added[0]["client"]["id"], UUID)

    def test_export_returns_exact_panel_link_and_checks_account_identity(self):
        panel = remote.Panel.__new__(remote.Panel)
        panel.options = {"target": "www.google.com", "public_host": "198.51.100.20"}
        panel.inbound = lambda _: {"port": 443, "settings": {"clients": [{"email": "relay-nl", "id": UUID}]}}
        original = link()
        panel.api = lambda *a, **k: [link(port=8443), original]
        self.assertEqual(panel.export(1, "relay-nl", "2001:db8:2::1", "chrome"), original)
        panel.api = lambda *a, **k: [original.replace(UUID, str(__import__("uuid").uuid4()))]
        with self.assertRaisesRegex(RuntimeError, "canonical"):
            panel.export(1, "relay-nl", "2001:db8:2::1", "chrome")

    def test_ipv6_preflight_does_not_modify_network_configuration(self):
        options = {"role": "hub", "port": 8443, "hub_ipv6": "2001:db8:1::2"}
        with mock.patch.object(remote, "global_ipv6", return_value=[]):
            with mock.patch.object(remote.subprocess, "run", side_effect=AssertionError("mutation")):
                with self.assertRaisesRegex(ValueError, "not configured"):
                    remote.validate_runtime(options)

    def test_failed_account_setup_leaves_new_inbound_disabled_and_old_routes_intact(self):
        options = {"role": "hub", "port": 8443, "listen": "0.0.0.0", "target": "yandex.ru",
                   "fingerprint": "safari", "hub_ipv6": "2001:db8:1::2", "route": "nl",
                   "remark": "Moscow NL", "clients": ["desktop"], "exit_link": link()}
        original = template()
        panel = mock.Mock()
        panel.template.return_value = original
        panel.api.side_effect = lambda ep, data=None: (
            [{"id": 9, "port": 8443, "listen": "0.0.0.0", "remark": "Moscow NL", "tag": "in-8443-tcp"}]
            if ep == "inbounds/list" else None)
        panel.attach.side_effect = RuntimeError("fixture account failure")
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(remote, "STATE", Path(d) / "routes.json"):
                with mock.patch.object(remote, "Panel", return_value=panel):
                    with mock.patch.object(remote, "validate_runtime"):
                        with mock.patch.object(remote, "assert_free"):
                            with mock.patch.object(remote, "backup", return_value="/private/backup"):
                                with mock.patch.object(remote, "new_inbound", return_value={}):
                                    with self.assertRaisesRegex(RuntimeError, "disabled"):
                                        remote.apply_route(options)
        panel.activate.assert_called_once_with(9, False)
        panel.set_template.assert_called_once_with(original)

    def test_changed_foreign_endpoint_is_not_silently_reused(self):
        options = {"role": "hub", "port": 8443, "listen": "0.0.0.0", "target": "yandex.ru",
                   "fingerprint": "safari", "hub_ipv6": "2001:db8:1::2", "route": "nl",
                   "remark": "Moscow NL", "clients": ["desktop"], "exit_link": link()}
        first = remote.route_identity(options)
        changed = dict(options, exit_link=link("2001:db8:3::1"))
        self.assertNotEqual(first, remote.route_identity(changed))


if __name__ == "__main__":
    unittest.main()
