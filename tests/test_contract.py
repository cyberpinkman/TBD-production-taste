"""Shared timeline and caption contracts, using fictional data only."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tbd", ROOT / "scripts/tbd.py")
tbd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tbd)
spec_install = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install_skills.py")
installer = importlib.util.module_from_spec(spec_install)
spec_install.loader.exec_module(installer)


class TimelineContract(unittest.TestCase):
    def setUp(self):
        self.project = json.loads((ROOT / "examples/synthetic/project.json").read_text(encoding="utf-8"))

    def test_single_map_derives_cut_and_intro_without_mutating_source(self):
        before = deepcopy(self.project)
        result = tbd.validate(self.project)
        self.assertEqual(result["final_frames"], 250)
        self.assertEqual([(c["start_frame"], c["end_frame"]) for c in result["captions"]],
                         [(55, 85), (90, 140), (155, 165), (170, 235)])
        self.assertEqual(self.project, before)
        self.assertEqual(tbd.srt(result), (ROOT / "examples/synthetic/captions.srt").read_text(encoding="utf-8"))
        self.assertNotIn("字段", tbd.srt(result))

    def test_structure_rejects_shared_invariant_failures(self):
        # Each mutant represents a failure class, not a historical episode.
        mutants = [
            ("gap", lambda p: p["segments"][1].update(body_start_frame=101)),
            ("duration", lambda p: p["segments"][1].update(body_end_frame=250)),
            ("source_bounds", lambda p: p["segments"][1].update(source_end_seconds=25)),
            ("cue_crosses_cut", lambda p: p["captions"][0].update(source_end_seconds=7)),
            ("duplicate_id", lambda p: p["captions"][1].update(id="caption-01")),
            ("mixed_turn", lambda p: p["captions"][1].update(turn_id="turn-01")),
            ("resumed_turn", lambda p: p["captions"][2].update(turn_id="turn-01")),
            ("overlap", lambda p: p["captions"][1].update(source_start_seconds=3.2)),
            ("placeholder", lambda p: p["captions"][0].update(text="[待核]")),
            ("short_intro", lambda p: p["profile"].update(format="short")),
            ("unhashed_real_source", lambda p: p.update(kind="episode")),
        ]
        for name, mutate in mutants:
            with self.subTest(name=name):
                project = deepcopy(self.project)
                mutate(project)
                with self.assertRaises(ValueError):
                    tbd.validate(project)

    def test_unknown_is_independent_but_not_printed_as_identity(self):
        self.project["captions"][0]["speaker_id"] = None
        self.assertNotIn("None", tbd.srt(tbd.validate(self.project)))
        self.project["captions"][1].update(speaker_id=None, turn_id="turn-01")
        with self.assertRaisesRegex(ValueError, "independent turn"):
            tbd.validate(self.project)

    def test_fractional_frame_rate_and_frame_quantization(self):
        self.project["profile"].update(fps_num=30000, fps_den=1001, intro_frames=60)
        self.project["segments"][0].update(body_end_frame=120)
        self.project["segments"][1].update(body_start_frame=120, body_end_frame=240)
        result = tbd.validate(self.project)
        self.assertEqual(result["captions"][0]["start_frame"], 65)
        self.assertEqual(result["captions"][0]["end_frame"], 102)
        self.assertEqual(tbd.timestamp(30000, result["fps"]), "00:16:41,000")

    def test_local_workspace_initialization_refuses_existing_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "episode"
            tbd.initialize(destination)
            original = (destination / "project.json").read_bytes()
            with self.assertRaises(FileExistsError):
                tbd.initialize(destination)
            self.assertEqual((destination / "project.json").read_bytes(), original)


class SkillInstallation(unittest.TestCase):
    def test_installs_all_skills_and_refuses_overwrite_before_any_copy(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "skills"
            installer.install(destination)
            self.assertEqual(len(list(destination.glob("tbd-*/SKILL.md"))), 6)
            marker = destination / "tbd-production/local-note.txt"
            marker.write_text("user changes", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nothing installed"):
                installer.install(destination)
            self.assertEqual(marker.read_text(encoding="utf-8"), "user changes")


if __name__ == "__main__":
    unittest.main()
