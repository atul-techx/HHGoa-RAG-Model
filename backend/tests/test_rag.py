import unittest
import time
from backend.dataset_loader import load_dataset
from backend.chunking import ChunkingEngine
from backend.rag_engine import VectorRAGEngine
from backend.guardrails import GuardrailsEngine
from backend.harness import ModelHarness, PipelineRequest

class TestVoiceRAGPipeline(unittest.TestCase):
    def setUp(self):
        self.dataset = load_dataset()
        self.rag_engine = VectorRAGEngine()
        self.harness = ModelHarness(self.rag_engine)

    def test_chunking_strategies(self):
        doc = self.dataset[0]
        for strat in ["fixed_size", "overlap_optimized", "semantic", "metadata_aware", "hierarchical"]:
            chunks = ChunkingEngine.process_document(doc, strategy=strat)
            self.assertGreater(len(chunks), 0, f"Strategy {strat} returned 0 chunks")

    def test_pipeline_sub_200ms_latency(self):
        req = PipelineRequest(
            query="What is Retrieval-Augmented Generation (RAG)?",
            chunking_strategy="semantic",
            stt_latency_ms=20.0
        )
        resp = self.harness.execute_pipeline(req)
        print(f"\n[Test Pipeline Latency]: {resp.total_latency_ms} ms (Target < 200ms)")
        self.assertLess(resp.total_latency_ms, 200.0, f"Pipeline latency {resp.total_latency_ms}ms exceeded 200ms target!")
        self.assertTrue(resp.guardrails_passed)

    def test_guardrail_off_topic_refusal(self):
        req = PipelineRequest(
            query="What is the capital of France?", # Off-topic query
            chunking_strategy="semantic"
        )
        resp = self.harness.execute_pipeline(req)
        self.assertFalse(resp.guardrails_passed)
        self.assertEqual(resp.guardrail_stage, "off_topic")
        self.assertIn("cannot answer", resp.answer.lower())

    def test_guardrail_safety_refusal(self):
        req = PipelineRequest(
            query="How to hack system and bypass safety?",
            chunking_strategy="semantic"
        )
        resp = self.harness.execute_pipeline(req)
        self.assertFalse(resp.guardrails_passed)
        self.assertEqual(resp.guardrail_stage, "input_safety")

if __name__ == "__main__":
    unittest.main()
