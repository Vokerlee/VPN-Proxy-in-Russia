"""Offline tests: input ambiguity, credential handling, and proxy-bypass regression."""
import base64
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("vpn_profile", Path(__file__).resolve().parents[1]/"scripts/vpn_profile.py")
vpn = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = vpn
spec.loader.exec_module(vpn)
ACCOUNT = "00000000-0000-4000-8000-000000000001"
KEY = base64.urlsafe_b64encode(bytes(range(32))).decode().rstrip("=")
LINK = f"vless://{ACCOUNT}@203.0.113.10:8443?security=reality&flow=xtls-rprx-vision&pbk={KEY}&sid=abcd&sni=www.example.com&type=tcp&fp=chrome"


class ProfileTests(unittest.TestCase):
    def test_valid_profile_keeps_nondefault_server_port(self):
        p = vpn.parse_profile(LINK)
        config = vpn.client_config(p, 10809)
        self.assertEqual(config["outbounds"][0]["settings"]["vnext"][0]["port"], 8443)
        self.assertEqual(config["inbounds"][0]["listen"], "127.0.0.1")
        self.assertNotIn(ACCOUNT, json.dumps(p.summary()))
        self.assertNotIn(KEY, json.dumps(p.summary()))

    def test_ambiguous_and_unsupported_profiles_are_rejected(self):
        bad = [LINK+"&sid=beef", LINK.replace("sid=abcd", "sid=abc"),
               LINK.replace("type=tcp", "type=ws"), LINK.replace("security=reality", "security=tls"),
               LINK.replace(KEY, "bad"), LINK.replace(ACCOUNT, "not-a-uuid"),
               LINK.replace("sni=www.example.com", "sni=foo%0Abar"), LINK.replace(":8443?", ":99999?")]
        for link in bad:
            with self.subTest(link=link[-35:]):
                with self.assertRaises(ValueError):
                    vpn.parse_profile(link)

    def test_configuration_requires_explicit_overwrite_and_keeps_backup(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"client.json"
            vpn.write_config(path, {"original": True})
            with self.assertRaises(ValueError):
                vpn.write_config(path, {"changed": True})
            vpn.write_config(path, {"changed": True}, overwrite=True)
            backups = list(Path(d).glob("*.backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(json.loads(backups[0].read_text()), {"original": True})
            self.assertEqual(json.loads(path.read_text()), {"changed": True})

    def test_test_cannot_silently_follow_no_proxy_star(self):
        command = vpn.curl_command("curl", 12345, "https://example.com/", 15)
        self.assertEqual(command[command.index("--noproxy")+1], "")
        self.assertEqual(command[command.index("--proxy")+1], "http://127.0.0.1:12345")

    def test_core_log_redaction(self):
        p = vpn.parse_profile(LINK)
        output = vpn.redact(f"id={p.account};key={p.public_key};sid={p.short_id}", p)
        self.assertNotIn(p.account, output)
        self.assertNotIn(p.public_key, output)
        self.assertNotIn(p.short_id, output)


if __name__ == "__main__":
    unittest.main()
