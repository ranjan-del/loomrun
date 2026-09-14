# bench

Load scripts and report generators. Every number in `docs/benchmarks/` is produced by
something in this directory, on named hardware, and can be rerun.

## Phase 0 exercise: baseline load script (engineer writes this)

`bench/baseline.py`, 40 to 60 lines, asyncio plus httpx, no framework:

1. Send N concurrent requests to Ollama `POST /api/chat` with `"stream": true` and a fixed
   prompt. Use the same prompt every time so runs are comparable.
2. Per request record: time to first token (first streamed chunk), total time, and the
   `eval_count` and `eval_duration` fields from the final chunk (Ollama reports them).
3. Print p50 and p95 for time to first token and total time, and tokens per second,
   for N = 1, 4, 16 with the small model.
4. Then alternate the small and medium model request by request, 10 requests, and print the
   time of each. The slow ones are the swaps.
5. Print the hardware line (`sysctl -n machdep.cpu.brand_string`, memory) at the top of the output.

Review follows. The reviewed script becomes `loomrun bench` in Phase 1.

Do not average. Averages hide the tail, and the tail is what users feel.
