#!/usr/bin/env python3
"""
Test script for the Dash encoder application
Tests basic functionality without starting the full server
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        import dash
        print(f"✓ Dash {dash.__version__}")
    except ImportError as e:
        print(f"✗ Dash import failed: {e}")
        return False

    try:
        import plotly
        print(f"✓ Plotly {plotly.__version__}")
    except ImportError as e:
        print(f"✗ Plotly import failed: {e}")
        return False

    try:
        import dash_bootstrap_components
        print(f"✓ Dash Bootstrap Components")
    except ImportError as e:
        print(f"✗ Dash Bootstrap Components import failed: {e}")
        return False

    return True

def test_app_structure():
    """Test that the app directory structure is correct."""
    print("\nTesting application structure...")

    app_dir = Path("")
    required_files = [
        "app.py",
        "run_app.py",
        "README.md",
        "components/__init__.py",
        "components/encoder_controls.py",
        "components/plotly_plots.py",
        "utils/__init__.py",
        "utils/encoder_factory.py",
        "assets/styles.css"
    ]

    missing = []
    for file_path in required_files:
        full_path = app_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ Missing: {file_path}")
            missing.append(file_path)

    return len(missing) == 0

def test_app_import():
    """Test that the main app can be imported."""
    print("\nTesting app import...")

    try:
        sys.path.append(str(Path("").absolute()))
        from app import app
        print("✓ App imports successfully")

        # Test that app has required attributes
        if hasattr(app, 'layout'):
            print("✓ App has layout")
        else:
            print("✗ App missing layout")
            return False

        if hasattr(app, 'callback'):
            print("✓ App has callback decorator")
        else:
            print("✗ App missing callback decorator")
            return False

        return True
    except Exception as e:
        print(f"✗ App import failed: {e}")
        return False

def test_encoder_factory():
    """Test the encoder factory functionality."""
    print("\nTesting encoder factory...")

    try:
        from utils.encoder_factory import create_encoder_from_params, get_encoder_info

        # Test basic encoder creation
        params = {
            'encoder_type': 'periodic_scalar',
            'n': 8,
            'w': 3,
            'period': 1.0,
            'offset': 0.0,
            'xmin': -1.0,
            'xmax': 2.0
        }

        encoder = create_encoder_from_params(params)
        print("✓ Encoder created successfully")

        # Test encoding
        result = encoder.encode(0.5)
        print(f"✓ Encoding test: input=0.5, output shape={getattr(result, 'shape', len(result) if hasattr(result, '__len__') else 'scalar')}")

        # Test encoder info
        info = get_encoder_info(encoder)
        print(f"✓ Encoder info: type={info.get('type', 'Unknown')}")

        return True
    except Exception as e:
        print(f"✗ Encoder factory test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("GNOME Encoder Dash App - Test Suite")
    print("=" * 60)

    tests = [
        ("Import Test", test_imports),
        ("Structure Test", test_app_structure),
        ("App Import Test", test_app_import),
        ("Encoder Factory Test", test_encoder_factory)
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"Running: {test_name}")
        print(f"{'-' * 40}")
        results[test_name] = test_func()

    # Summary
    print(f"\n{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}")

    passed = 0
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 All tests passed! The Dash app is ready to run.")
        print("\nTo start the application:")
        print("  python demo_dash_app.py")
        print("  or")
        print("  cd dash_encoder_app && python run_app.py")
    else:
        print(f"\n⚠️  {len(tests) - passed} test(s) failed. Please fix issues before running.")

    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)