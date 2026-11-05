"""Offline regression checks for guide navigation and invalid diagnostic inputs."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("check_docs",ROOT/"scripts/check_docs.py")
docs=importlib.util.module_from_spec(spec)
spec.loader.exec_module(docs)


class GuideChecks(unittest.TestCase):
    def test_headings_inside_examples_are_not_real_targets(self):
        text="# Page\n\n## A button's label\n\n```bash\n# Fake heading\n```\n"
        self.assertEqual(docs.anchors(text),{"page","a-buttons-label"})

    def test_missing_images_and_anchors_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"README.md").write_text("# Start\n\n[Broken](other.md#missing)\n\n![Missing](images/no.svg)\n")
            (root/"other.md").write_text("# Other\n")
            _,_,errors=docs.check_repo(root)
            self.assertEqual(len(errors),2)

    def test_repository_navigation_is_consistent(self):
        _,_,errors=docs.check_repo(ROOT)
        self.assertEqual(errors,[])

    def test_server_helper_rejects_bad_values_before_checks(self):
        for args in [["--port","65536"],["--port","bad"],["--port"],["--target","https://example.com/"]]:
            result=subprocess.run(["bash",str(ROOT/"scripts/server-check.sh"),*args],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertNotIn("Panel service:",result.stdout)


if __name__=="__main__":
    unittest.main()
