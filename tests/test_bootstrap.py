"""Offline bootstrap checks. No SSH calls or server installations are performed."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

def load(name):
    spec=importlib.util.spec_from_file_location(name, ROOT/"scripts"/(name+".py"))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

bootstrap=load("bootstrap_server")
remote=load("provision_remote")


class BootstrapTests(unittest.TestCase):
    def test_untrusted_inputs_cannot_become_shell_options(self):
        for host in ["-oProxyCommand=evil", "example.com;echo x", "2001:db8::1"]:
            with self.assertRaises(ValueError):
                bootstrap.validate_options(host)
        with self.assertRaises(ValueError):
            bootstrap.validate_options("203.0.113.10",vpn_port=22)
        with self.assertRaises(ValueError):
            bootstrap.validate_options("203.0.113.10",target="example.com;echo x")

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
        opts=bootstrap.validate_options("203.0.113.10",vpn_port=8443)
        value=remote.inbound_payload(opts,"PRIVATE_PLACEHOLDER","PUBLIC_PLACEHOLDER","UUID_PLACEHOLDER","abcd")
        self.assertEqual(value["port"],8443)
        self.assertEqual(json.loads(value["settings"])["clients"][0]["flow"],"xtls-rprx-vision")
        self.assertIn("@203.0.113.10:8443?",remote.share_link(opts,"UUID_PLACEHOLDER","PUBLIC_PLACEHOLDER","abcd"))

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
