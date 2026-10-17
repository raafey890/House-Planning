"""
MASTER VERIFICATION SUITE: PHASE 6C.8A
=======================================
Orchestrates both:
  CATEGORY A: Canonical Regression Tests (strictly loads canonical JSON records)
  CATEGORY B: Fresh Solver Validation Tests (dynamic CP-SAT solves, clearly labeled)
"""
import sys
import os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

import test_canonical_regression
import test_fresh_solver_validation

def run_all():
    print("=" * 80)
    print("MASTER VERIFICATION SUITE — PHASE 6C.8A")
    print("=" * 80)

    # 1. Run Category A: Canonical Regression Tests
    print("\n" + "#" * 80)
    print("CATEGORY A: CANONICAL REGRESSION TESTS (FROZEN SOURCE OF TRUTH)")
    print("#" * 80)
    for filename, spec in test_canonical_regression.CANONICAL_SPECS.items():
        test_canonical_regression.verify_canonical_file(filename, spec)
    test_canonical_regression.test_canonical_svg_exports()

    # 2. Run Category B: Fresh Solver Validation Tests
    print("\n" + "#" * 80)
    print("CATEGORY B: FRESH SOLVER VALIDATION TESTS (LIVE CP-SAT SOLVES)")
    print("#" * 80)
    test_fresh_solver_validation.test_outdoor_spaces_cannot_increase_indoor_room_count()
    test_fresh_solver_validation.test_fresh_solver_50x80()
    test_fresh_solver_validation.test_fresh_solver_30x40()

    print("\n" + "=" * 80)
    print("ALL TESTS IN BOTH CATEGORIES (CANONICAL & FRESH SOLVER) PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_all()
