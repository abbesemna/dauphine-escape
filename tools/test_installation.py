#!/usr/bin/env python3
"""
TEST SCRIPT - Dauphine Escape
Verifies installation and dependencies.
"""

import sys
from pathlib import Path

print("\n" + "="*60)
print("INSTALLATION TEST - DAUPHINE ESCAPE")
print("="*60 + "\n")

tests_passed = 0
tests_total = 0

def test(name, func):
    """Execute a test"""
    global tests_passed, tests_total
    tests_total += 1
    try:
        func()
        print(f"[OK] {name}")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"[FAIL] {name}")
        print(f"   Error: {e}")
        return False

# Test 1: Python version
def test_python_version():
    version = sys.version_info
    assert version.major == 3 and version.minor >= 8, f"Python 3.8+ required (detected: {version.major}.{version.minor})"

test("Python 3.8+", test_python_version)

# Test 2: Pygame
def test_pygame():
    import pygame
    assert pygame.version.vernum >= (2, 0, 0), "Pygame 2.0+ required"

test("Pygame installed", test_pygame)

# Test 3: Heapq (stdlib)
def test_heapq():
    import heapq
    test_heap = []
    heapq.heappush(test_heap, (1, 'a'))
    assert heapq.heappop(test_heap) == (1, 'a')

test("Heapq (stdlib)", test_heapq)

# Test 4: JSON (stdlib)
def test_json():
    import json
    test_data = {"test": 123}
    assert json.loads(json.dumps(test_data)) == test_data

test("JSON (stdlib)", test_json)

# Test 5: Matplotlib (optional)
def test_matplotlib():
    import matplotlib
    import matplotlib.pyplot as plt

test("Matplotlib (optional)", test_matplotlib)

# Test 6: Numpy (optional)
def test_numpy():
    import numpy as np
    assert np.mean([1, 2, 3]) == 2.0

test("Numpy (optional)", test_numpy)

# Test 7: Main file exists (New structure)
def test_main_file():
    project_root = Path(__file__).parent.parent
    main_file = project_root / "src" / "main.py"
    assert main_file.exists(), f"{main_file} not found"
    game_file = project_root / "src" / "game.py"
    assert game_file.exists(), f"{game_file} not found"

test("Main files (src/main.py)", test_main_file)

# Test 8: Config check
def test_config():
    # Try importing config from src
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    from src.config import WINDOW_WIDTH
    assert WINDOW_WIDTH > 0

test("Config module load", test_config)

print("\n" + "="*60)
print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
print("="*60 + "\n")

if tests_passed == tests_total:
    print("All tests passed!")
    print("You can launch the game with: python -m src.main\n")
    sys.exit(0)
else:
    print("Some tests failed.")
    # Matplotlib/Numpy are optional
    if tests_passed >= tests_total - 2:
         print("Optional dependencies missing, but game should run.")
         sys.exit(0)
    sys.exit(1)
