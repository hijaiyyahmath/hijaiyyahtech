"""
test_hvm.py — HVM Test Suite

Tests for the complete HVM pipeline:
IR compiler, HCPU execution, validator feedback loop, and owner-learning.
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from hijaiyahlang.dataset import load_mh28_csv, cod_word
from hijaiyahlang.core import audit_v18
from hijaiyahlang.ir import (
    Op, IRInst, compile_word, serialize_ir, deserialize_ir,
    letter_id, validate_letter, H28_SET,
)
from hijaiyahlang.hcpu import (
    HCPU, ConformanceMode, NonNormativeError, HCPUError, ExecResult,
)
from hijaiyahlang.validator_loop import ValidatorLoop, ErrorType
from hijaiyahlang.owner_learn import OwnerModel


def get_dataset():
    csv_path = os.path.join(ROOT, "MH-28-v1.0-18D.csv")
    return load_mh28_csv(csv_path)


class TestLetterID(unittest.TestCase):
    def test_nfc_identity(self):
        self.assertEqual(letter_id("ب"), "ب")

    def test_strip_tatweel(self):
        self.assertEqual(letter_id("بـ"), "ب")

    def test_h28_valid(self):
        for ch in H28_SET:
            validate_letter(ch)  # should not raise

    def test_non_h28_raises(self):
        with self.assertRaises(ValueError):
            validate_letter("A")

    def test_digit_raises(self):
        with self.assertRaises(ValueError):
            validate_letter("5")


class TestIRCompiler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds = get_dataset()

    def test_compile_single_letter(self):
        ir = compile_word("ا", self.ds, audit=False)
        self.assertEqual(len(ir), 2)  # LOAD + HALT
        self.assertEqual(ir[0].op, Op.LOAD)
        self.assertEqual(ir[0].arg, "ا")
        self.assertEqual(ir[1].op, Op.HALT)

    def test_compile_two_letters(self):
        """compile_word("فو") → [LOAD ف, LOAD و, ADD, AUDIT, HALT]"""
        ir = compile_word("فو", self.ds)
        ops = [i.op for i in ir]
        self.assertEqual(ops, [Op.LOAD, Op.LOAD, Op.ADD, Op.AUDIT, Op.HALT])
        self.assertEqual(ir[0].arg, "ف")
        self.assertEqual(ir[1].arg, "و")

    def test_compile_three_letters(self):
        ir = compile_word("بسم", self.ds)
        ops = [i.op for i in ir]
        # LOAD ب, LOAD س, ADD, LOAD م, ADD, AUDIT, HALT
        self.assertEqual(ops, [
            Op.LOAD, Op.LOAD, Op.ADD,
            Op.LOAD, Op.ADD,
            Op.AUDIT, Op.HALT,
        ])

    def test_compile_with_validate_learn(self):
        ir = compile_word("ا", self.ds, validate=True, learn=True)
        ops = [i.op for i in ir]
        self.assertIn(Op.VALIDATE, ops)
        self.assertIn(Op.LEARN, ops)
        # HALT must be last
        self.assertEqual(ops[-1], Op.HALT)

    def test_empty_word_raises(self):
        with self.assertRaises(ValueError):
            compile_word("", self.ds)

    def test_invalid_letter_raises(self):
        with self.assertRaises(ValueError):
            compile_word("A", self.ds)

    def test_serialize_roundtrip(self):
        ir = compile_word("فو", self.ds)
        data = serialize_ir(ir)
        ir2 = deserialize_ir(data)
        self.assertEqual(len(ir), len(ir2))
        for a, b in zip(ir, ir2):
            self.assertEqual(a.op, b.op)
            self.assertEqual(a.arg, b.arg)


class TestHCPU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds = get_dataset()

    def test_run_equals_cod_word(self):
        """HCPU run output must equal cod_word for same input."""
        word = "فو"
        ir = compile_word(word, self.ds)
        cpu = HCPU(self.ds)
        cpu.load(ir)
        result = cpu.run()
        self.assertTrue(result.ok, f"HCPU error: {result.error}")
        expected = cod_word(word, self.ds)
        self.assertEqual(result.result, expected)

    def test_run_three_letters(self):
        word = "بسم"
        ir = compile_word(word, self.ds)
        cpu = HCPU(self.ds)
        cpu.load(ir)
        result = cpu.run()
        self.assertTrue(result.ok)
        self.assertEqual(result.result, cod_word(word, self.ds))

    def test_audit_pass(self):
        ir = compile_word("فو", self.ds)
        cpu = HCPU(self.ds)
        cpu.load(ir)
        result = cpu.run()
        self.assertTrue(result.ok)
        self.assertIsNotNone(result.audit)
        self.assertTrue(result.audit.ok)

    def test_audit_nondestruct(self):
        """AUDIT must not pop the V18 from stack."""
        ir = compile_word("ب", self.ds)
        cpu = HCPU(self.ds)
        cpu.load(ir)
        result = cpu.run()
        self.assertTrue(result.ok)
        # After AUDIT, stack still has the V18
        self.assertEqual(result.result, self.ds.table["ب"])

    def test_core_rejects_learn(self):
        ir = compile_word("ا", self.ds, learn=True)
        cpu = HCPU(self.ds, mode=ConformanceMode.CORE)
        cpu.load(ir)
        result = cpu.run()
        self.assertFalse(result.ok)
        self.assertIn("LEARN rejected", result.error)

    def test_core_rejects_validate(self):
        ir = compile_word("ا", self.ds, validate=True)
        cpu = HCPU(self.ds, mode=ConformanceMode.CORE)
        cpu.load(ir)
        result = cpu.run()
        self.assertFalse(result.ok)
        self.assertIn("rejected", result.error)

    def test_feedback_mode_allows_validate(self):
        ir = compile_word("ا", self.ds, validate=True)
        cpu = HCPU(self.ds, mode=ConformanceMode.FEEDBACK)
        cpu.load(ir)
        result = cpu.run()
        self.assertTrue(result.ok)

    def test_feedback_mode_rejects_learn(self):
        ir = compile_word("ا", self.ds, learn=True)
        cpu = HCPU(self.ds, mode=ConformanceMode.FEEDBACK)
        cpu.load(ir)
        result = cpu.run()
        self.assertFalse(result.ok)
        self.assertIn("LEARN rejected", result.error)

    def test_owner_mode_allows_all(self):
        model = OwnerModel()
        ir = compile_word("ب", self.ds, validate=True, learn=True)
        cpu = HCPU(self.ds, mode=ConformanceMode.OWNER,
                   owner_model=model)
        cpu.load(ir)
        result = cpu.run()
        self.assertTrue(result.ok)

    def test_trace_entries(self):
        ir = compile_word("ا", self.ds)
        cpu = HCPU(self.ds)
        cpu.load(ir)
        cpu.run()
        trace = cpu.trace()
        self.assertGreater(len(trace), 0)
        self.assertEqual(trace[0].op, Op.LOAD)
        self.assertEqual(trace[-1].op, Op.HALT)

    def test_mod_output_range(self):
        """MOD 4 output must have all components in [0..3]."""
        ir = [
            IRInst(Op.LOAD, "ي"),
            IRInst(Op.MOD, 4),
            IRInst(Op.HALT),
        ]
        cpu = HCPU(self.ds)
        cpu.load(ir)
        result = cpu.run()
        self.assertTrue(result.ok)
        for x in result.result:
            self.assertIn(x, range(4))

    def test_single_letter_all_28(self):
        """Every letter must execute successfully on HCPU."""
        for letter in H28_SET:
            with self.subTest(letter=letter):
                ir = compile_word(letter, self.ds)
                cpu = HCPU(self.ds)
                cpu.load(ir)
                result = cpu.run()
                self.assertTrue(result.ok, f"{letter}: {result.error}")


class TestValidatorLoop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds = get_dataset()

    def test_valid_vector_pass(self):
        v = cod_word("ب", self.ds)
        vl = ValidatorLoop()
        fb = vl.validate(v)
        self.assertTrue(fb.ok)
        self.assertEqual(fb.error_type, ErrorType.NONE)

    def test_invalid_dim(self):
        vl = ValidatorLoop()
        fb = vl.validate([1, 2, 3])
        self.assertFalse(fb.ok)
        self.assertEqual(fb.error_type, ErrorType.INVALID_DIM)

    def test_negative_component(self):
        vl = ValidatorLoop()
        v = [0] * 18
        v[0] = -1
        fb = vl.validate(v)
        self.assertFalse(fb.ok)
        self.assertEqual(fb.error_type, ErrorType.NEGATIVE_COMPONENT)

    def test_stats_accumulate(self):
        vl = ValidatorLoop()
        v = cod_word("ا", self.ds)
        vl.validate(v)
        vl.validate(v)
        vl.validate([1, 2])  # bad
        self.assertEqual(vl.stats.total, 3)
        self.assertEqual(vl.stats.passed, 2)
        self.assertEqual(vl.stats.errors.get("INVALID_DIM"), 1)

    def test_validate_side_effect_stack_unchanged(self):
        """VALIDATE in HCPU must not change the stack."""
        vl = ValidatorLoop()
        ir = compile_word("ب", self.ds, audit=False, validate=True)
        cpu = HCPU(self.ds, mode=ConformanceMode.FEEDBACK,
                   validator_loop=vl)
        cpu.load(ir)
        result = cpu.run()
        self.assertTrue(result.ok)
        self.assertEqual(result.result, self.ds.table["ب"])
        self.assertEqual(len(result.feedback_log), 1)


class TestOwnerModel(unittest.TestCase):
    def test_observe_and_recognize(self):
        model = OwnerModel()
        model.observe("بسم")
        model.observe("بسم")
        model.observe("بسم")
        score1 = model.recognize("بسم")
        score2 = model.recognize("طظع")  # unseen pattern
        self.assertGreater(score1, score2,
                           "Trained word should score higher than unseen")

    def test_empty_model_score_zero(self):
        model = OwnerModel()
        self.assertEqual(model.recognize("ب"), 0.0)

    def test_save_load_roundtrip(self):
        model = OwnerModel()
        model.observe("فوق")
        model.observe("بسم")
        score_before = model.recognize("بسم")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False,
                                        mode="w") as tmp:
            tmp_path = tmp.name
        try:
            model.save(tmp_path)
            loaded = OwnerModel.load(tmp_path)
            score_after = loaded.recognize("بسم")
            self.assertAlmostEqual(score_before, score_after, places=6)
        finally:
            os.unlink(tmp_path)

    def test_learn_side_effect_in_hcpu(self):
        """LEARN in HCPU must update the owner model."""
        ds = get_dataset()
        model = OwnerModel()
        ir = compile_word("بسم", ds, audit=False, learn=True)
        cpu = HCPU(ds, mode=ConformanceMode.OWNER, owner_model=model)
        cpu.load(ir)
        result = cpu.run()
        self.assertTrue(result.ok)
        self.assertGreater(model._total_words, 0)

    def test_invalid_letter_in_observe_raises(self):
        model = OwnerModel()
        with self.assertRaises(ValueError):
            model.observe("ABC")


class TestFullPipeline(unittest.TestCase):
    """End-to-end: word → compile → execute → validate → learn."""

    @classmethod
    def setUpClass(cls):
        cls.ds = get_dataset()

    def test_full_pipeline(self):
        word = "فو"
        model = OwnerModel()
        vl = ValidatorLoop()

        # Compile
        ir = compile_word(word, self.ds, validate=True, learn=True)

        # Execute on HCPU in OWNER mode
        cpu = HCPU(self.ds, mode=ConformanceMode.OWNER,
                   validator_loop=vl, owner_model=model)
        cpu.load(ir)
        result = cpu.run()

        # Verify
        self.assertTrue(result.ok, f"Pipeline error: {result.error}")
        self.assertEqual(result.result, cod_word(word, self.ds))
        self.assertTrue(result.audit.ok)
        self.assertEqual(len(result.feedback_log), 1)
        self.assertTrue(result.feedback_log[0].ok)
        self.assertGreater(model._total_words, 0)

    def test_pipeline_all_28_letters(self):
        """Each letter individually through the full pipeline."""
        model = OwnerModel()
        vl = ValidatorLoop()
        for letter in sorted(H28_SET):
            with self.subTest(letter=letter):
                ir = compile_word(letter, self.ds,
                                  validate=True, learn=True)
                cpu = HCPU(self.ds, mode=ConformanceMode.OWNER,
                           validator_loop=vl, owner_model=model)
                cpu.load(ir)
                result = cpu.run()
                self.assertTrue(result.ok, f"{letter}: {result.error}")
        # After all 28, model should have 28 observations
        self.assertEqual(model._total_words, 28)
        self.assertEqual(vl.stats.passed, 28)


if __name__ == "__main__":
    unittest.main()
