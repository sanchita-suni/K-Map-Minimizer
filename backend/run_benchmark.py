"""
Comprehensive 50-example benchmark for Optimized BitSlice QM.
Same 50 test cases as Naive QM for direct comparison.
"""

import time
import random
import sys
import threading

from server import BitSliceQuineMcCluskey

TIMEOUT_SEC = 30

DEFAULT_VARS = list("ABCDEFGHIJKLMNO")

def var_names(n):
    return DEFAULT_VARS[:n]

def verify_coverage(num_vars, minterms, selected_pis):
    covered = set()
    for term_str, mint_list in selected_pis:
        covered.update(mint_list)
    return set(minterms).issubset(covered)

def run_one(label, num_vars, minterms, dont_cares=None):
    if dont_cares is None:
        dont_cares = []
    vn = var_names(num_vars)

    result_holder = [None]
    error_holder = [None]

    def worker():
        try:
            start = time.perf_counter()
            qm = BitSliceQuineMcCluskey(num_vars, minterms, dont_cares)
            expr, pi_list, epi_list, sel_list = qm.minimize(vn)
            elapsed_ms = (time.perf_counter() - start) * 1000

            correct = verify_coverage(num_vars, minterms, sel_list) if minterms else True

            result_holder[0] = {
                "label": label,
                "vars": num_vars,
                "minterms": len(minterms),
                "dc": len(dont_cares),
                "pis": len(pi_list),
                "epis": len(epi_list),
                "sel": len(sel_list),
                "expr": expr,
                "time_ms": round(elapsed_ms, 3),
                "correct": correct,
                "method": "branch-bound" if "Branch" in " ".join(qm.steps) else (
                    "greedy" if "greedy" in " ".join(qm.steps).lower() else "essential-only"),
            }
        except Exception as e:
            error_holder[0] = str(e)

    t = threading.Thread(target=worker, daemon=True)
    start_wall = time.perf_counter()
    t.start()
    t.join(timeout=TIMEOUT_SEC)

    if t.is_alive():
        elapsed_ms = (time.perf_counter() - start_wall) * 1000
        return {
            "label": label, "vars": num_vars, "minterms": len(minterms),
            "dc": len(dont_cares), "pis": -1, "epis": -1, "sel": -1,
            "expr": f"TIMEOUT (>{TIMEOUT_SEC}s)",
            "time_ms": round(elapsed_ms, 3),
            "correct": None, "method": "timeout",
        }

    if error_holder[0]:
        return {
            "label": label, "vars": num_vars, "minterms": len(minterms),
            "dc": len(dont_cares), "pis": -1, "epis": -1, "sel": -1,
            "expr": f"ERROR: {error_holder[0]}",
            "time_ms": -1, "correct": False, "method": "error",
        }

    return result_holder[0]


# ── Same 50 test cases (same seed!) ──────────────────────────────────────
random.seed(42)

tests = []

# 2-variable
tests.append(("2v: single minterm",       2, [1], []))
tests.append(("2v: two minterms",         2, [0, 3], []))
tests.append(("2v: all minterms",         2, [0,1,2,3], []))

# 3-variable
tests.append(("3v: textbook SOP",         3, [1,2,5,6,7], []))
tests.append(("3v: with don't-cares",     3, [0,2,5,7], [1,6]))
tests.append(("3v: XOR pattern",          3, [1,2,4,7], []))
tests.append(("3v: single minterm",       3, [5], []))
tests.append(("3v: all minterms",         3, list(range(8)), []))

# 4-variable
tests.append(("4v: textbook ex1",         4, [0,1,2,5,6,7,8,9,14], [3,11]))
tests.append(("4v: textbook ex2",         4, [4,8,10,11,12,15], [9,14]))
tests.append(("4v: sparse",              4, [0,5,10,15], []))
tests.append(("4v: dense",               4, [0,1,2,3,4,5,6,7,8,9,10,11], []))
tests.append(("4v: checkerboard",        4, [0,2,5,7,8,10,13,15], []))
tests.append(("4v: one group",           4, [0,1,2,3], []))
tests.append(("4v: only don't-cares",    4, [1], [0,2,3,4,5,6,7]))
tests.append(("4v: adjacent pairs",      4, [0,1,4,5,8,9,12,13], []))
tests.append(("4v: primes pattern",      4, [2,3,5,7,11,13], []))

# 5-variable
tests.append(("5v: random 10 minterms",  5, sorted(random.sample(range(32), 10)), []))
tests.append(("5v: random 16 minterms",  5, sorted(random.sample(range(32), 16)), []))
tests.append(("5v: first half",          5, list(range(16)), []))
tests.append(("5v: even minterms",       5, list(range(0,32,2)), []))
tests.append(("5v: with 5 DCs",          5, sorted(random.sample(range(32), 12)),
              sorted(random.sample(list(set(range(32)) - set(random.sample(range(32),12))), 5))))

# 6-variable
tests.append(("6v: random 20 minterms",  6, sorted(random.sample(range(64), 20)), []))
tests.append(("6v: random 32 minterms",  6, sorted(random.sample(range(64), 32)), []))
tests.append(("6v: lower quarter",       6, list(range(16)), []))
tests.append(("6v: every 4th",           6, list(range(0,64,4)), []))
tests.append(("6v: with 8 DCs",          6, sorted(random.sample(range(64), 25)),
              sorted(random.sample(list(set(range(64)) - set(random.sample(range(64),25))), 8))))

# 7-variable
tests.append(("7v: random 30 minterms",  7, sorted(random.sample(range(128), 30)), []))
tests.append(("7v: random 50 minterms",  7, sorted(random.sample(range(128), 50)), []))
tests.append(("7v: random 64 minterms",  7, sorted(random.sample(range(128), 64)), []))

# 8-variable
tests.append(("8v: random 40 minterms",  8, sorted(random.sample(range(256), 40)), []))
tests.append(("8v: random 80 minterms",  8, sorted(random.sample(range(256), 80)), []))
tests.append(("8v: random 128 minterms", 8, sorted(random.sample(range(256), 128)), []))
tests.append(("8v: with 20 DCs",         8, sorted(random.sample(range(256), 60)),
              sorted(random.sample(list(set(range(256)) - set(random.sample(range(256),60))), 20))))

# 9-variable
tests.append(("9v: random 50 minterms",  9, sorted(random.sample(range(512), 50)), []))
tests.append(("9v: random 100 minterms", 9, sorted(random.sample(range(512), 100)), []))
tests.append(("9v: random 200 minterms", 9, sorted(random.sample(range(512), 200)), []))

# 10-variable
tests.append(("10v: random 80 minterms",  10, sorted(random.sample(range(1024), 80)), []))
tests.append(("10v: random 150 minterms", 10, sorted(random.sample(range(1024), 150)), []))
tests.append(("10v: random 300 minterms", 10, sorted(random.sample(range(1024), 300)), []))

# 11-variable
tests.append(("11v: random 100 minterms", 11, sorted(random.sample(range(2048), 100)), []))
tests.append(("11v: random 200 minterms", 11, sorted(random.sample(range(2048), 200)), []))

# 12-variable
tests.append(("12v: random 100 minterms", 12, sorted(random.sample(range(4096), 100)), []))
tests.append(("12v: random 300 minterms", 12, sorted(random.sample(range(4096), 300)), []))

# Special patterns
tests.append(("4v: all-zeros expr",       4, [], []))
tests.append(("4v: all-ones (tautology)", 4, list(range(16)), []))
tests.append(("5v: power-of-2 minterms", 5, [1,2,4,8,16], []))
tests.append(("6v: bit-count=3",         6, [m for m in range(64) if bin(m).count('1') == 3], []))
tests.append(("5v: maxterm-complement",   5, [m for m in range(32) if m not in [0,5,10,15,20,25,30]], []))
tests.append(("6v: alternating nibbles",  6, [m for m in range(64) if (m >> 3) % 2 == 0], []))

assert len(tests) == 50, f"Expected 50 tests, got {len(tests)}"

# ── run all ──────────────────────────────────────────────────────────────
print(f"Running {len(tests)} benchmark cases on Optimized BitSlice QM (timeout={TIMEOUT_SEC}s per test) ...\n")

results = []
for i, (label, nv, mt, dc) in enumerate(tests, 1):
    sys.stdout.write(f"  [{i:2d}/50] {label:<30s} ... ")
    sys.stdout.flush()
    r = run_one(label, nv, mt, dc)
    results.append(r)

    if r["method"] == "timeout":
        print(f"TIMEOUT  {r['time_ms']:>10.3f} ms")
    elif r["method"] == "error":
        print(f"ERROR: {r['expr']}")
    else:
        tag = "OK" if r["correct"] else "FAIL"
        print(f"{tag}  {r['time_ms']:>10.3f} ms")

# ── summary ──────────────────────────────────────────────────────────────
completed = [r for r in results if r["method"] not in ("timeout", "error")]
timed_out = [r for r in results if r["method"] == "timeout"]
errored = [r for r in results if r["method"] == "error"]
valid_times = [r["time_ms"] for r in completed]

print()
print("=" * 130)
print(f"{'#':>3s}  {'Test Case':<30s}  {'Vars':>4s}  {'Mint':>5s}  {'DC':>4s}  "
      f"{'PIs':>5s}  {'EPIs':>5s}  {'Sel':>4s}  {'Method':<15s}  {'Time (ms)':>12s}  {'OK?':>5s}")
print("-" * 130)
for i, r in enumerate(results, 1):
    if r["method"] == "timeout":
        ok = "T/O"
        time_str = f">{TIMEOUT_SEC*1000:.0f}"
    elif r["method"] == "error":
        ok = "ERR"
        time_str = "N/A"
    elif r["correct"]:
        ok = "Y"
        time_str = f"{r['time_ms']:.3f}"
    else:
        ok = "N"
        time_str = f"{r['time_ms']:.3f}"

    pis = str(r["pis"]) if r["pis"] >= 0 else "-"
    epis = str(r["epis"]) if r["epis"] >= 0 else "-"
    sel = str(r["sel"]) if r["sel"] >= 0 else "-"

    print(f"{i:3d}  {r['label']:<30s}  {r['vars']:4d}  {r['minterms']:5d}  {r['dc']:4d}  "
          f"{pis:>5s}  {epis:>5s}  {sel:>4s}  {r['method']:<15s}  {time_str:>12s}  {ok:>5s}")
print("-" * 130)

total_correct = sum(1 for r in results if r["correct"] is True)
total_fail = sum(1 for r in results if r["correct"] is False)
total_timeout = len(timed_out)
total_error = len(errored)
print(f"\nResults: {total_correct} passed, {total_fail} failed, {total_timeout} timed out, {total_error} errors  (out of {len(results)} total)")
if completed:
    print(f"Accuracy on completed tests: {total_correct}/{len(completed)} ({100*total_correct/len(completed):.1f}%)")

if valid_times:
    print(f"\nTiming Statistics (across {len(completed)} completed tests):")
    print(f"  Average : {sum(valid_times)/len(valid_times):12.3f} ms")
    print(f"  Median  : {sorted(valid_times)[len(valid_times)//2]:12.3f} ms")
    print(f"  Min     : {min(valid_times):12.3f} ms")
    print(f"  Max     : {max(valid_times):12.3f} ms")
    print(f"  Total   : {sum(valid_times):12.3f} ms")

    sorted_times = sorted(valid_times)
    p90_idx = int(len(sorted_times) * 0.9)
    p95_idx = int(len(sorted_times) * 0.95)
    print(f"  P90     : {sorted_times[min(p90_idx, len(sorted_times)-1)]:12.3f} ms")
    print(f"  P95     : {sorted_times[min(p95_idx, len(sorted_times)-1)]:12.3f} ms")

print("\nBreakdown by Variable Count:")
print(f"  {'Vars':>4s}  {'Tests':>5s}  {'Done':>4s}  {'T/O':>3s}  {'Avg (ms)':>12s}  {'Min (ms)':>12s}  {'Max (ms)':>12s}")
print(f"  {'----':>4s}  {'-----':>5s}  {'----':>4s}  {'---':>3s}  {'--------':>12s}  {'--------':>12s}  {'--------':>12s}")
for nv in sorted(set(r["vars"] for r in results)):
    group_all = [r for r in results if r["vars"] == nv]
    group_done = [r for r in group_all if r["method"] not in ("timeout", "error")]
    group_to = [r for r in group_all if r["method"] == "timeout"]
    if group_done:
        times_g = [r["time_ms"] for r in group_done]
        print(f"  {nv:4d}  {len(group_all):5d}  {len(group_done):4d}  {len(group_to):3d}  "
              f"{sum(times_g)/len(times_g):12.3f}  {min(times_g):12.3f}  {max(times_g):12.3f}")
    else:
        print(f"  {nv:4d}  {len(group_all):5d}  {len(group_done):4d}  {len(group_to):3d}  "
              f"{'N/A':>12s}  {'N/A':>12s}  {'N/A':>12s}")

print("\nCovering Method Used:")
method_counts = {}
for r in results:
    m = r["method"]
    method_counts[m] = method_counts.get(m, 0) + 1
for m, c in sorted(method_counts.items()):
    print(f"  {m:<20s}: {c} tests")

print("\n" + "=" * 130)
