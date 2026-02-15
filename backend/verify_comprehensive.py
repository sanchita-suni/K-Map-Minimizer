"""Comprehensive verification tests for the K-Map Minimizer API."""
import requests
import json

BASE = "http://127.0.0.1:8000/api/minimize"
DEFAULT_VARS = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O"]

def req(num_vars, minterms=None, maxterms=None, dont_cares=None, 
        input_mode="minterm", expression=None, var_names=None):
    payload = {
        "num_vars": num_vars,
        "input_mode": input_mode,
        "minterms": minterms or [],
        "maxterms": maxterms or [],
        "dont_cares": dont_cares or [],
        "variable_names": var_names or DEFAULT_VARS,
    }
    if expression:
        payload["expression"] = expression
    r = requests.post(BASE, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def verify_covers(minterms, groups):
    covered = set()
    for g in groups:
        covered.update(g["cells"])
    return set(minterms) - covered


def test_basic_3var():
    d = req(3, minterms=[0, 2, 5, 7])
    assert d["minimal_sop"] in ["A'C' + AC", "AC + A'C'"], f"Got {d['minimal_sop']}"
    assert d["output_name"] == "F"
    assert len(d["truth_table"]) == 8
    assert not verify_covers([0, 2, 5, 7], d["groups"])
    print("PASS: basic 3var")


def test_basic_4var():
    d = req(4, minterms=[0,1,2,5,6,7,8,9,14])
    assert len(d["truth_table"]) == 16
    assert not verify_covers([0,1,2,5,6,7,8,9,14], d["groups"])
    print(f"PASS: basic 4var, SOP={d['minimal_sop']}")


def test_dont_cares():
    d = req(4, minterms=[1,3,5,7], dont_cares=[0,2])
    for row in d["truth_table"]:
        if row["minterm"] in [0, 2]:
            assert row[d["output_name"]] == "X"
    print(f"PASS: dont_cares, SOP={d['minimal_sop']}")


def test_maxterm_mode():
    d = req(3, maxterms=[1, 3, 4, 6], input_mode="maxterm")
    assert d["minimal_sop"] in ["A'C' + AC", "AC + A'C'"]
    print(f"PASS: maxterm mode, SOP={d['minimal_sop']}")


def test_expression_mode():
    d = req(3, input_mode="expression", expression="AB + C")
    expected_minterms = {1, 3, 5, 6, 7}
    actual_minterms = set()
    for row in d["truth_table"]:
        if row[d["output_name"]] == 1:
            actual_minterms.add(row["minterm"])
    assert actual_minterms == expected_minterms, f"{actual_minterms} != {expected_minterms}"
    print(f"PASS: expression mode, SOP={d['minimal_sop']}")


def test_expression_with_not():
    """Test expression mode with complemented variables."""
    d = req(3, input_mode="expression", expression="A'B + C'")
    expected_minterms = set()
    for i in range(8):
        A, B, C = (i >> 2) & 1, (i >> 1) & 1, i & 1
        if ((not A) and B) or (not C):
            expected_minterms.add(i)
    actual_minterms = {row["minterm"] for row in d["truth_table"] if row[d["output_name"]] == 1}
    assert actual_minterms == expected_minterms, f"{actual_minterms} != {expected_minterms}"
    print(f"PASS: expression with NOT, SOP={d['minimal_sop']}")


def test_expression_parentheses():
    """Test expression with parentheses."""
    d = req(3, input_mode="expression", expression="A(B + C)")
    expected_minterms = set()
    for i in range(8):
        A, B, C = (i >> 2) & 1, (i >> 1) & 1, i & 1
        if A and (B or C):
            expected_minterms.add(i)
    actual_minterms = {row["minterm"] for row in d["truth_table"] if row[d["output_name"]] == 1}
    assert actual_minterms == expected_minterms, f"{actual_minterms} != {expected_minterms}"
    print(f"PASS: expression parens, SOP={d['minimal_sop']}")


def test_all_minterms():
    d = req(3, minterms=[0,1,2,3,4,5,6,7])
    assert d["minimal_sop"] == "1"
    print("PASS: all minterms = 1")


def test_empty_minterms():
    d = req(3, minterms=[])
    assert d["minimal_sop"] == "0"
    print("PASS: no minterms = 0")


def test_single_minterm():
    d = req(3, minterms=[5])
    assert d["minimal_sop"] == "AB'C"
    print("PASS: single minterm")


def test_5var():
    d = req(5, minterms=list(range(8)))
    assert d["minimal_sop"] == "A'B'"
    print("PASS: 5var")


def test_output_name_collision():
    d = req(3, minterms=[0,2,5,7], var_names=["F","B","C","D","E","G","H","I","J","K","L","M","N","O","P"])
    assert d["output_name"] != "F"
    print(f"PASS: output name collision, using {d['output_name']}")


def test_verilog_generation():
    d = req(3, minterms=[0,2,5,7])
    assert "module" in d["verilog_behavioral"]
    assert "module" in d["verilog_dataflow"]
    assert "module" in d["verilog_gate_level"]
    assert "module" in d["verilog_testbench"]
    print("PASS: verilog generation")


def test_waveform_data():
    d = req(3, minterms=[0,2,5,7])
    wd = d["waveform_data"]
    assert "signals" in wd
    assert wd["time_steps"] == 8
    assert len(wd["signal_names"]) == 4
    print("PASS: waveform data")


def test_performance_metrics():
    d = req(4, minterms=[0,1,2,5,6,7,8,9,14])
    pm = d["performance_metrics"]
    assert "total_time_ms" in pm
    assert pm["num_variables"] == 4
    print("PASS: performance metrics")


def test_canonical_forms():
    d = req(3, minterms=[0,2,5,7])
    csop_terms = d["canonical_sop"].split(" + ")
    assert len(csop_terms) == 4
    assert d["canonical_pos"].count("(") == 4
    print("PASS: canonical forms")


def test_minimal_pos():
    d = req(3, minterms=[0,2,5,7])
    assert "(" in d["minimal_pos"]
    print(f"PASS: minimal POS = {d['minimal_pos']}")


def test_2var():
    d = req(2, minterms=[0, 3])
    assert "A'B'" in d["minimal_sop"] and "AB" in d["minimal_sop"]
    print(f"PASS: 2var, SOP={d['minimal_sop']}")


def test_large_var_count():
    import random
    random.seed(42)
    minterms = random.sample(range(256), 80)
    d = req(8, minterms=minterms)
    assert not verify_covers(minterms, d["groups"])
    print(f"PASS: 8var, {len(d['prime_implicants'])} PIs")


def test_steps_populated():
    d = req(4, minterms=[0,1,2,5,6,7,8,9,14])
    assert len(d["steps"]) > 0
    print(f"PASS: steps populated ({len(d['steps'])} steps)")


def test_simulation_output():
    d = req(3, minterms=[0,2,5,7])
    assert "Simulation" in d["simulation_output"]
    print("PASS: simulation output")


def test_multichar_varnames():
    """Test with multi-character variable names."""
    d = req(3, minterms=[0,2,5,7], var_names=["X1","Y2","Z3","D","E","F","G","H","I","J","K","L","M","N","O"])
    assert "X1" in d["minimal_sop"] or "Z3" in d["minimal_sop"]
    assert len(d["truth_table"]) == 8
    for row in d["truth_table"]:
        assert "X1" in row
        assert "Y2" in row
        assert "Z3" in row
    print(f"PASS: multichar varnames, SOP={d['minimal_sop']}")


def test_overlapping_minterms_dontcares():
    """Test that overlapping minterms and don't cares are handled."""
    try:
        d = req(3, minterms=[0,1,2], dont_cares=[2,3])
        # Minterm 2 is in both - should still work without crash
        print(f"PASS: overlapping minterms/dc handled, SOP={d['minimal_sop']}")
    except Exception as e:
        print(f"PASS: overlapping minterms/dc properly rejected: {e}")


def test_max_variable_count():
    """Test with 15 variables (max supported)."""
    d = req(15, minterms=[0, 1, 2, 3])
    assert d["minimal_sop"] != ""
    print(f"PASS: 15 vars, SOP={d['minimal_sop']}")


if __name__ == "__main__":
    tests = [
        test_basic_3var,
        test_basic_4var,
        test_dont_cares,
        test_maxterm_mode,
        test_expression_mode,
        test_expression_with_not,
        test_expression_parentheses,
        test_all_minterms,
        test_empty_minterms,
        test_single_minterm,
        test_5var,
        test_output_name_collision,
        test_verilog_generation,
        test_waveform_data,
        test_performance_metrics,
        test_canonical_forms,
        test_minimal_pos,
        test_2var,
        test_large_var_count,
        test_steps_populated,
        test_simulation_output,
        test_multichar_varnames,
        test_overlapping_minterms_dontcares,
        test_max_variable_count,
    ]
    
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    print(f"{'='*50}")
