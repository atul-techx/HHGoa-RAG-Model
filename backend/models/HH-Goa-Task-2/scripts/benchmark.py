import os
import sys
import time
import json
import statistics

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from app.pipeline import RAGPipeline, METADATA_PATH

SEED_QUERIES = [
    "what is a corporation?",
    "why did Rachel Carson write The Obligation to Endure?",
    "what are foods low in potassium?",
    "what is artificial intelligence?",
    "what is a company?",
    "what is a computer?",
    "what is machine learning?",
    "what is a database?",
    "what is climate change?",
    "what is a university?",
    "what is photosynthesis?",
    "what is dark matter?",
    "what is quantum mechanics?",
    "what is global warming?",
    "what is clean energy?"
]


def load_benchmark_queries(num_queries=100):
    queries = list(SEED_QUERIES)

    if os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            for item in metadata:
                q = item.get("query", "").strip()
                if q and q not in queries:
                    queries.append(q)
                if len(queries) >= num_queries:
                    break
        except Exception as e:
            print(f"Warning: Could not load metadata queries: {e}")

    # Fallback padding if needed
    base_count = len(queries)
    index = 0
    while len(queries) < num_queries:
        queries.append(f"{queries[index % base_count]} (variant {index + 1})")
        index += 1

    return queries[:num_queries]


def percentile(values, percentage):
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = int((percentage / 100.0) * (len(sorted_vals) - 1))
    return sorted_vals[idx]


def run_benchmark():
    print("=" * 70)
    print("HH GOA TASK 2 - RAG LATENCY BENCHMARK (< 200 ms TARGET)")
    print("=" * 70)

    queries = load_benchmark_queries(100)
    print(f"\nLoaded {len(queries)} benchmark queries.")

    print("\nInitializing RAG Pipeline...")
    pipeline = RAGPipeline()

    print("\nWarming up pipeline before timing...")
    _ = pipeline.run("warmup question test")
    print("Warm-up completed.\n")

    print("=" * 70)
    print("RUNNING BENCHMARK (100 QUERIES)")
    print("=" * 70)

    total_latencies = []
    retrieval_latencies = []
    reranking_latencies = []
    answer_latencies = []
    guardrail_latencies = []
    grounded_count = 0

    for i, q in enumerate(queries, start=1):
        start_t = time.perf_counter()
        result = pipeline.run(q)
        end_t = time.perf_counter()

        measured_total = (end_t - start_t) * 1000.0

        lat = result.get("latency", {})
        ret_ms = lat.get("retrieval_ms", 0.0)
        rerank_ms = lat.get("reranking_ms", 0.0)
        ans_ms = lat.get("answer_ms", lat.get("generation_ms", 0.0))
        grd_ms = lat.get("guardrails_ms", 0.0)
        pipe_total = lat.get("total_ms", measured_total)

        total_latencies.append(pipe_total)
        retrieval_latencies.append(ret_ms)
        reranking_latencies.append(rerank_ms)
        answer_latencies.append(ans_ms)
        guardrail_latencies.append(grd_ms)

        if result.get("grounded", False):
            grounded_count += 1

        if i <= 5 or i % 25 == 0 or i == len(queries):
            print(f"Query {i:3d}/{len(queries)}: [{result.get('method', 'unknown'):20s}] "
                  f"Ret: {ret_ms:5.1f}ms | Ans: {ans_ms:5.1f}ms | Guard: {grd_ms:4.1f}ms | Total: {pipe_total:6.1f}ms")

    p50 = percentile(total_latencies, 50)
    p70 = percentile(total_latencies, 70)
    p90 = percentile(total_latencies, 90)
    p95 = percentile(total_latencies, 95)
    p100 = max(total_latencies)

    avg_total = statistics.mean(total_latencies)
    min_total = min(total_latencies)
    max_total = max(total_latencies)

    avg_ret = statistics.mean(retrieval_latencies)
    avg_rerank = statistics.mean(reranking_latencies)
    avg_ans = statistics.mean(answer_latencies)
    avg_grd = statistics.mean(guardrail_latencies)

    status = "PASS" if avg_total < 200.0 else "FAIL"

    print("\n" + "=" * 70)
    print("LATENCY BENCHMARK REPORT")
    print("=" * 70)

    print(f"\nQueries: {len(queries)}")
    print(f"Grounded Answers: {grounded_count}/{len(queries)}")

    print(f"\nP50 : {p50:.2f} ms")
    print(f"P70 : {p70:.2f} ms")
    print(f"P90 : {p90:.2f} ms")
    print(f"P95 : {p95:.2f} ms")
    print(f"P100: {p100:.2f} ms")

    print(f"\nAverage: {avg_total:.2f} ms")
    print(f"Minimum: {min_total:.2f} ms")
    print(f"Maximum: {max_total:.2f} ms")

    print("\nCOMPONENT LATENCY")
    print("-" * 35)
    print(f"Embedding / Retrieval Average : {avg_ret:.2f} ms")
    print(f"Reranking Average             : {avg_rerank:.2f} ms")
    print(f"Answer Average                : {avg_ans:.2f} ms")
    print(f"Guardrail Average             : {avg_grd:.2f} ms")
    print(f"TOTAL RAG AVERAGE             : {avg_total:.2f} ms")

    print("\nTARGET: < 200 ms")
    print("\nSTATUS:")
    print(status)
    print("=" * 70 + "\n")

    return status == "PASS"


if __name__ == "__main__":
    success = run_benchmark()
    if not success:
        sys.exit(1)