"""Unit tests for generate_seed.py. Run from the repo root:

  python3 -m unittest discover -s scripts -v
"""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_seed as gs

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
SEED = REPO / "data" / "circumscriptions.json"
TYPES = REPO / "data" / "circumscription_types.json"


class Validate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = json.loads(SEED.read_text(encoding="utf-8"))["entries"]
        cls.known = {t["id"] for t in
                     json.loads(TYPES.read_text(encoding="utf-8"))["entries"]}

    def bad_copy(self):
        return copy.deepcopy(self.entries[:50])

    def test_accepts_the_committed_seed(self):
        gs.validate(self.entries, self.known)  # must not raise

    def test_accepts_null_type(self):
        # The seed is untyped pending an authoritative pass; null must pass.
        entries = self.bad_copy()
        self.assertIsNone(entries[0]["type"])
        gs.validate(entries, self.known)

    def test_rejects_duplicate_id(self):
        entries = self.bad_copy()
        entries[1]["id"] = entries[0]["id"]
        with self.assertRaises(ValueError) as ctx:
            gs.validate(entries, self.known)
        self.assertIn("duplicate ids", str(ctx.exception))

    def test_rejects_unknown_circumscription_type(self):
        entries = self.bad_copy()
        entries[0]["type"] = "ctype:bogus"
        with self.assertRaises(ValueError) as ctx:
            gs.validate(entries, self.known)
        self.assertIn("ctype:bogus", str(ctx.exception))

    def test_rejects_malformed_church_sui_iuris(self):
        # "esi:" is the case that a startswith() check let through: it carries
        # no slug and resolves to nothing.
        for value in ("esi:", "latin", "esi:Latin", "esi:-latin", "esi:latin-", ""):
            with self.subTest(value=value):
                entries = self.bad_copy()
                entries[0]["church_sui_iuris"] = value
                with self.assertRaises(ValueError) as ctx:
                    gs.validate(entries, self.known)
                self.assertIn("malformed church_sui_iuris", str(ctx.exception))

    def test_accepts_other_well_formed_esi_references(self):
        # CESIDR mints 24; the seed only uses esi:latin so far.
        for value in ("esi:ukrainian", "esi:syro-malabar", "esi:italo-albanian"):
            with self.subTest(value=value):
                entries = self.bad_copy()
                entries[0]["church_sui_iuris"] = value
                gs.validate(entries, self.known)

    def test_reports_every_problem_at_once(self):
        entries = self.bad_copy()
        entries[1]["id"] = entries[0]["id"]
        entries[2]["type"] = "ctype:bogus"
        entries[3]["church_sui_iuris"] = "esi:"
        with self.assertRaises(ValueError) as ctx:
            gs.validate(entries, self.known)
        message = str(ctx.exception)
        self.assertIn("duplicate ids", message)
        self.assertIn("ctype:bogus", message)
        self.assertIn("malformed church_sui_iuris", message)


class SurvivesOptimizedMode(unittest.TestCase):
    """The regression this module exists for.

    Python strips `assert` under -O. When these guards were assertions, running
    the generator with -O skipped validation entirely: it exited 0 and wrote
    unresolvable cross-references. Any future reintroduction of `assert` here
    must fail this test.
    """

    def run_validate(self, flags, snippet):
        code = ("import sys; sys.path.insert(0, %r); import generate_seed as gs; %s"
                % (str(SCRIPTS), snippet))
        return subprocess.run([sys.executable, *flags, "-c", code],
                              capture_output=True, text=True)

    def test_every_guard_still_raises_under_dash_O(self):
        ok = {"id": "circ:xx-a", "type": None, "church_sui_iuris": "esi:latin"}
        cases = {
            "duplicate id": ([ok, dict(ok)], "set()"),
            "unknown type": ([dict(ok, type="ctype:bogus")], "set()"),
            "malformed esi": ([dict(ok, church_sui_iuris="esi:")], "set()"),
        }
        for name, (entries, known) in cases.items():
            snippet = "gs.validate(%r, %s)" % (entries, known)
            for flags in ([], ["-O"], ["-OO"]):
                with self.subTest(guard=name, flags=flags or ["(none)"]):
                    result = self.run_validate(flags, snippet)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("ValueError", result.stderr)

    def test_valid_input_passes_under_dash_O(self):
        entry = {"id": "circ:xx-a", "type": None, "church_sui_iuris": "esi:latin"}
        snippet = "gs.validate([%r], set()); print('ok')" % entry
        result = self.run_validate(["-O"], snippet)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "ok")


class MainRefusesToWrite(unittest.TestCase):
    """main() must abort *before* writing, not merely detect the problem.

    The #11 regression was end-to-end: exit 0 plus a corrupted seed on disk.
    validate() raising is necessary but not sufficient, so these drive main()
    against a synthetic source and assert the output file is never created.
    """

    def build(self, dioceses):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        repo = tmp / "repo"
        (repo / "data").mkdir(parents=True)
        shutil.copy(TYPES, repo / "data" / "circumscription_types.json")
        src = tmp / "world_dioceses.json"
        src.write_text(json.dumps({"catholic_dioceses_latin_rite": [
            {"country_iso": "xx", "country_name_english": "Testland",
             "dioceses": dioceses}]}), encoding="utf-8")
        return src, repo, repo / "data" / "circumscriptions.json"

    def run_main(self, flags, src, repo, inject=""):
        code = ("import sys; sys.path.insert(0, %r); import generate_seed as gs; %s"
                "sys.argv = ['generate_seed.py', %r, %r]; gs.main()"
                % (str(SCRIPTS), inject, str(src), str(repo)))
        return subprocess.run([sys.executable, *flags, "-c", code],
                              capture_output=True, text=True)

    ALPHA_BETA = [{"diocese_name": "Alpha", "diocese_id": "alpha_xx"},
                  {"diocese_name": "Beta", "diocese_id": "beta_xx"}]
    # Two sees of the same name with no province: the generator cannot qualify
    # them, so both collapse onto circ:xx-alpha.
    HOMONYMS = [{"diocese_name": "Alpha", "diocese_id": "alpha1_xx"},
                {"diocese_name": "Alpha", "diocese_id": "alpha2_xx"}]

    def test_writes_when_input_is_sound(self):
        for flags in ([], ["-O"], ["-OO"]):
            with self.subTest(flags=flags or ["(none)"]):
                src, repo, out = self.build(self.ALPHA_BETA)
                result = self.run_main(flags, src, repo)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(out.exists())
                self.assertEqual(
                    json.loads(out.read_text(encoding="utf-8"))["entry_count"], 2)

    def test_duplicate_ids_abort_before_writing(self):
        for flags in ([], ["-O"], ["-OO"]):
            with self.subTest(flags=flags or ["(none)"]):
                src, repo, out = self.build(self.HOMONYMS)
                result = self.run_main(flags, src, repo)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("duplicate ids", result.stderr)
                self.assertFalse(out.exists(), "seed was written despite bad input")

    def test_unknown_type_aborts_before_writing(self):
        inject = "gs.MANUAL['alpha_xx'] = {'type': 'ctype:bogus'}; "
        for flags in ([], ["-O"], ["-OO"]):
            with self.subTest(flags=flags or ["(none)"]):
                src, repo, out = self.build(self.ALPHA_BETA)
                result = self.run_main(flags, src, repo, inject)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ctype:bogus", result.stderr)
                self.assertFalse(out.exists(), "seed was written despite bad input")

    def test_an_existing_seed_is_left_untouched_on_failure(self):
        src, repo, out = self.build(self.HOMONYMS)
        out.write_text("SENTINEL", encoding="utf-8")
        result = self.run_main(["-O"], src, repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(out.read_text(encoding="utf-8"), "SENTINEL")

    # `church_sui_iuris` has no main()-level counterpart: the value is a literal
    # in main() and no source input or MANUAL override can reach it, so it is
    # unreachable end-to-end by construction. It is covered at the validate()
    # level in SurvivesOptimizedMode instead.


class Slugify(unittest.TestCase):
    """Pins the strip rule, including the Italian case fixed in #2."""

    def test_strips_italian_archdiocesan_form(self):
        # "arcidiocesi", not "archdiocesi" — the bug that left 58 slugs wrong.
        self.assertEqual(gs.slugify("Arcidiocesi di Acerenza"), "acerenza")

    def test_strips_remaining_styled_forms(self):
        self.assertEqual(gs.slugify("Diocesi di Lanusei"), "lanusei")
        self.assertEqual(gs.slugify("Archdiocese of Boston"), "boston")
        self.assertEqual(gs.slugify("Diocese of Brooklyn"), "brooklyn")

    def test_leaves_bare_see_names_alone(self):
        self.assertEqual(gs.slugify("Lezhë"), "lezhe")
        self.assertEqual(gs.slugify("Shkodrë-Pult"), "shkodre-pult")

    def test_does_not_strip_type_words_mid_name(self):
        # Only the leading styled form is generic; "Diocese" elsewhere is not.
        self.assertEqual(gs.slugify("Archdiocese for the Military Services"),
                         "archdiocese-for-the-military-services")


if __name__ == "__main__":
    unittest.main()
