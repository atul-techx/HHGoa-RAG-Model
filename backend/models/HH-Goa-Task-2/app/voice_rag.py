import os
import sys
import time

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from app.voice.stt import SpeechToText
from app.pipeline import RAGPipeline

AUDIO_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "test.wav"
)


class VoiceRAG:

    def __init__(self):
        print("=" * 70)
        print("INITIALIZING VOICE RAG SYSTEM")
        print("=" * 70)

        print("\nLoading Sarvam STT...")
        self.stt = SpeechToText()
        print("Sarvam STT ready.")

        print("\nLoading RAG pipeline...")
        self.rag = RAGPipeline()
        print("\nVoice RAG system ready.")

    def run(self, audio_file):
        total_start = time.perf_counter()

        print("\n" + "=" * 70)
        print("VOICE RAG PIPELINE")
        print("=" * 70)

        if not os.path.exists(audio_file):
            return {
                "success": False,
                "error": f"Audio file not found: {audio_file}"
            }

        # ----------------------------------------------------
        # 1. Speech-to-Text
        # ----------------------------------------------------
        print("\n[1/3] Speech-to-Text")
        stt_start = time.perf_counter()
        try:
            transcript = self.stt.transcribe(audio_file)
        except Exception as error:
            return {
                "success": False,
                "error": f"Speech-to-text failed: {error}"
            }
        stt_latency = (time.perf_counter() - stt_start) * 1000

        if not transcript:
            return {
                "success": False,
                "error": "No speech detected."
            }

        transcript = transcript.strip()
        print("Transcript:", transcript)

        # ----------------------------------------------------
        # 2. RAG Pipeline
        # ----------------------------------------------------
        print("\n[2/3] RAG Pipeline (Retrieval + Guardrails + Answer Extraction)")
        rag_start = time.perf_counter()
        result = self.rag.run(transcript)
        rag_latency = (time.perf_counter() - rag_start) * 1000

        total_latency = (time.perf_counter() - total_start) * 1000

        # ----------------------------------------------------
        # 3. Output Results
        # ----------------------------------------------------
        print("\n[3/3] FINAL RESULT")
        print("=" * 70)
        print("Transcript:", transcript)
        print("Answer:", result.get("answer", ""))
        print("Grounded:", result.get("grounded", False))
        print("Method:", result.get("method", ""))

        print("\nLatency Metrics:")
        print(f"STT Latency   : {round(stt_latency, 2)} ms")
        print(f"RAG Latency   : {round(rag_latency, 2)} ms")
        print(f"Total Voice   : {round(total_latency, 2)} ms")

        if "latency" in result:
            breakdown = result["latency"]
            print("\nRAG Breakdown:")
            print(f"  Retrieval  : {breakdown.get('retrieval_ms', 0)} ms")
            print(f"  Reranking  : {breakdown.get('reranking_ms', 0)} ms")
            print(f"  Answer     : {breakdown.get('answer_ms', breakdown.get('generation_ms', 0))} ms")
            print(f"  Guardrails : {breakdown.get('guardrails_ms', 0)} ms")
            print(f"  Total RAG  : {breakdown.get('total_ms', 0)} ms")

        print("=" * 70)

        return {
            "success": True,
            "transcript": transcript,
            "answer": result.get("answer", ""),
            "grounded": result.get("grounded", False),
            "method": result.get("method", ""),
            "retrieved": result.get("retrieved", []),
            "reranked": result.get("reranked", []),
            "latency": {
                "stt_ms": round(stt_latency, 2),
                "rag_ms": round(rag_latency, 2),
                "total_ms": round(total_latency, 2),
                "rag_breakdown": result.get("latency", {})
            }
        }


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("HH GOA TASK 2 - VOICE RAG PIPELINE")
    print("=" * 70)

    if not os.path.exists(AUDIO_FILE):
        print(f"\nERROR: Audio file not found: {AUDIO_FILE}")
        sys.exit(1)

    system = VoiceRAG()
    result = system.run(AUDIO_FILE)

    if result.get("success"):
        print("\nVOICE RAG TEST SUCCESSFUL")
    else:
        print("\nVOICE RAG TEST FAILED:", result.get("error", "Unknown error"))