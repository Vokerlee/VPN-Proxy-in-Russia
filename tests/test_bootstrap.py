"""Offline bootstrap checks. No SSH calls or server installations are performed."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parents[1]

def load(name):
    spec=importlib.util.spec_from_file_location(name, ROOT/"scripts"/(name+".py"))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

bootstrap=load("bootstrap_server")
remote=load("provision_remote")


def panel_link_fixture(port=8443, fingerprint="safari"):
    return (f"vless://ACCOUNT@203.0.113.10:{port}?encryption=none&flow=xtls-rprx-vision"
            f"&fp={fingerprint}&pbk=PUBLIC&security=reality&sid=abcd&sni=www.google.com"
            "&spx=%2Fpanel-exported-path&type=tcp#Personal%20VPN-first-device")


class BootstrapTests(unittest.TestCase):
    def test_untrusted_inputs_cannot_become_shell_options(self):
        for host in ["-oProxyCommand=evil", "example.com;echo x", "2001:db8::1"]:
            with self.assertRaises(ValueError):
                bootstrap.validate_options(host)
        with self.assertRaises(ValueError):
            bootstrap.validate_options("203.0.113.10",vpn_port=22)
        with self.assertRaises(ValueError):
            bootstrap.validate_options("203.0.113.10",target="example.com;echo x")
        with self.assertRaises(ValueError):
            bootstrap.validate_options("203.0.113.10",server_country="US;echo x")
        with self.assertRaises(ValueError):
            bootstrap.validate_options("203.0.113.10",fingerprint="chrome;echo x")

    def test_public_inbound_ports_are_limited_to_443_and_8443(self):
        for port in (443,8443):
            self.assertEqual(bootstrap.validate_options("203.0.113.10",vpn_port=port)["vpn_port"],port)
        for port in (80,2096,38457,51837,65535):
            with self.subTest(port=port):
                with self.assertRaisesRegex(ValueError,"443 or 8443"):
                    bootstrap.validate_options("203.0.113.10",vpn_port=port)
                with mock.patch.object(remote.os,"geteuid",return_value=0):
                    with mock.patch.object(remote,"assert_fresh") as guard:
                        with self.assertRaisesRegex(ValueError,"443 or 8443"):
                            remote.run({"vpn_port":port})
                        guard.assert_not_called()

    def test_native_ssh_prompt_and_host_key_check_are_preserved(self):
        opts=bootstrap.validate_options("203.0.113.10")
        command=bootstrap.ssh_command("ssh",opts)
        self.assertIn("StrictHostKeyChecking=ask",command)
        self.assertIn("root@203.0.113.10",command)
        self.assertNotIn("password",json.dumps(command).lower())

    def test_existing_panel_is_refused_before_configuration(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"etc/x-ui").mkdir(parents=True)
            (root/"etc/x-ui/x-ui.db").write_text("keep me")
            with self.assertRaises(RuntimeError):
                remote.assert_fresh(root)
            self.assertEqual((root/"etc/x-ui/x-ui.db").read_text(),"keep me")

    def test_ipv4_update_preserves_unrelated_rules_and_outbounds(self):
        template={"routing":{"rules":[{"outboundTag":"api"}]},"outbounds":[
            {"tag":"direct","protocol":"freedom","settings":{"finalRules":[{"action":"block"}]}},
            {"tag":"blocked","protocol":"blackhole"}]}
        result=remote.set_ipv4(template)
        self.assertEqual(result["routing"]["rules"],[{"outboundTag":"api"}])
        self.assertEqual(result["outbounds"][0]["settings"]["finalRules"],[{"action":"block"}])
        self.assertEqual(result["outbounds"][0]["streamSettings"]["sockopt"]["domainStrategy"],"ForceIPv4")

    def test_api_payload_and_share_link_use_the_actual_port(self):
        opts=bootstrap.validate_options("203.0.113.10",vpn_port=8443,server_country="US")
        value=remote.inbound_payload(opts,"PRIVATE_PLACEHOLDER","PUBLIC_PLACEHOLDER","UUID_PLACEHOLDER","abcd")
        self.assertEqual(value["port"],8443)
        self.assertEqual(json.loads(value["settings"])["clients"][0]["flow"],"xtls-rprx-vision")
        link=panel_link_fixture()
        self.assertEqual(remote.panel_share_link(opts,"ACCOUNT","PUBLIC","abcd",[panel_link_fixture(443),link]),link)

    def test_regional_selection_and_explicit_override_reach_both_exports(self):
        for country,requested,expected in [("US","auto","safari"),("DE","auto","chrome"),
                                            ("JP","auto","chrome"),("US","firefox","firefox"),
                                            ("DE","safari","safari")]:
            with self.subTest(country=country,requested=requested):
                opts=bootstrap.validate_options("203.0.113.10",server_country=country,fingerprint=requested)
                payload=remote.inbound_payload(opts,"PRIVATE","PUBLIC","ACCOUNT","abcd")
                saved=json.loads(payload["streamSettings"])["realitySettings"]["settings"]["fingerprint"]
                link=panel_link_fixture(443,expected)
                exported=remote.panel_share_link(opts,"ACCOUNT","PUBLIC","abcd",[link])
                shared=parse_qs(urlsplit(exported).query)["fp"][0]
                self.assertEqual((saved,shared),(expected,expected))

    def test_panel_export_preserves_exact_name_and_spiderx_and_checks_identity(self):
        opts=bootstrap.validate_options("203.0.113.10",vpn_port=8443,server_country="US")
        link=panel_link_fixture()
        self.assertEqual(remote.panel_share_link(opts,"ACCOUNT","PUBLIC","abcd",[link]),link)
        implicit_none=link.replace("encryption=none&", "")
        self.assertEqual(remote.panel_share_link(opts,"ACCOUNT","PUBLIC","abcd",[implicit_none]),implicit_none)
        for links in [[link.replace("ACCOUNT@","OTHER@")],[panel_link_fixture(443)],
                      [panel_link_fixture(fingerprint="chrome")],[link.split("#")[0]],
                      [link.replace("encryption=none", "encryption=unsupported")],None]:
            with self.subTest(links=links):
                with self.assertRaisesRegex(RuntimeError,"panel did not export"):
                    remote.panel_share_link(opts,"ACCOUNT","PUBLIC","abcd",links)

    def test_country_lookup_is_validated_and_override_needs_no_lookup(self):
        opener=mock.Mock()
        opener.open.return_value=io.BytesIO(b'{"ip":"203.0.113.10","country":"US"}')
        with mock.patch.object(remote.urllib.request,"build_opener",return_value=opener):
            result=remote.resolve_fingerprint_options(bootstrap.validate_options("203.0.113.10"))
        self.assertEqual((result["server_country"],result["fingerprint"]),("US","safari"))
        opener.open.assert_called_once_with("https://api.country.is/203.0.113.10",timeout=5)
        for body in [b'{"ip":"203.0.113.11","country":"US"}',b'{"ip":"203.0.113.10","country":null}',
                     b'{"ip":"203.0.113.10","country":"XX"}',b'not JSON']:
            opener.open.return_value=io.BytesIO(body)
            with mock.patch.object(remote.urllib.request,"build_opener",return_value=opener):
                with self.assertRaisesRegex(RuntimeError,"country lookup failed"):
                    remote.resolve_fingerprint_options(bootstrap.validate_options("203.0.113.10"))
        with mock.patch.object(remote,"detect_server_country",side_effect=AssertionError("must not look up")):
            result=remote.resolve_fingerprint_options(bootstrap.validate_options("203.0.113.10",fingerprint="safari"))
            self.assertEqual(result["fingerprint"],"safari")
            result=remote.resolve_fingerprint_options(bootstrap.validate_options("203.0.113.10",server_country="DE"))
            self.assertEqual(result["fingerprint"],"chrome")

    def test_public_panel_url_and_optional_forward_preserve_saved_paths(self):
        for path in ("/", "", "saved-path", "/saved-path/"):
            result={"host":"203.0.113.10","panel_port":27297,"web_path":path}
            suffix=path.strip("/")
            suffix=suffix+"/" if suffix else ""
            self.assertEqual(bootstrap.panel_url(result), "http://203.0.113.10:27297/"+suffix)
            self.assertEqual(bootstrap.panel_url(result,18082), "http://127.0.0.1:18082/"+suffix)

    def test_result_files_cannot_overwrite_an_existing_export(self):
        result={"client_link":"vless://PLACEHOLDER"}
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/"private"
            bootstrap.save_result(result,output)
            with self.assertRaises(FileExistsError):
                bootstrap.save_result(result,output)
            self.assertEqual(json.loads((output/"server.json").read_text()),result)


if __name__=="__main__":
    unittest.main()
