import copy
import json
import unittest
from pathlib import Path
from third_possibility import analyse, dominates_robustly

BASE=json.loads((Path(__file__).parent/"scenario_fictional.json").read_text(encoding="utf-8"))

class TestThirdPossibility(unittest.TestCase):
    def test_better_on_synthetic_example(self):
        result=analyse(BASE)
        self.assertIn({"better":"samen_ontwerpen","than":"afsluiten"},result["robust_dominance"])
        self.assertEqual(result["undominated_eligible"],["samen_ontwerpen"])
    def test_perfect_but_unproven_is_excluded(self):
        self.assertIn("hypothetisch_perfect",analyse(BASE)["excluded"])
    def test_conclusion_disappears_when_assumption_worsens(self):
        case=copy.deepcopy(BASE)
        case["alternatives"][1]["public_benefit"]=[60,75]
        self.assertIn("samen_ontwerpen",analyse(case)["excluded"])
    def test_overlapping_bounds_are_not_proof(self):
        a=copy.deepcopy(BASE["alternatives"][1])
        a["public_benefit"]=[76,88]
        self.assertFalse(dominates_robustly(a,BASE["alternatives"][0]))
    def test_rights_gate_cannot_be_bypassed(self):
        case=copy.deepcopy(BASE)
        case["alternatives"][1]["rights_compatible"]=False
        self.assertIn("samen_ontwerpen",analyse(case)["excluded"])
    def test_invalid_interval_is_rejected(self):
        case=copy.deepcopy(BASE)
        case["alternatives"][0]["harm"]=[80,40]
        with self.assertRaises(ValueError): analyse(case)

if __name__=="__main__": unittest.main()
