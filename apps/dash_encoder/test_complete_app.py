#!/usr/bin/env python3
"""
Test script for the complete Dash application
Verifies that the debugged app works correctly
"""

import sys
import os
from pathlib import Path

def test_complete_app_import():
    """Test that the complete app can be imported without errors."""
    print("Testing complete app import...")

    try:
        sys.path.append(str(Path("").absolute()))
        import app_complete_fixed
        print("✓ app_complete_fixed imports successfully")

        # Test that app has required attributes
        if hasattr(app_complete_fixed, 'app'):
            print("✓ App instance exists")
        else:
            print("✗ App instance missing")
            return False

        # Test layout exists
        if hasattr(app_complete_fixed.app, 'layout'):
            print("✓ App has layout")
        else:
            print("✗ App missing layout")
            return False

        return True
    except Exception as e:
        print(f"✗ Complete app import failed: {e}")
        return False

def test_component_imports():
    """Test that all required components can be imported."""
    print("\nTesting component imports...")

    required_imports = [
        "components.encoder_controls",
        "components.plotly_plots",
        "components.comparison_dashboard",
        "components.preset_configs",
        "components.animation_controls",
        "utils.encoder_factory",
        "utils.export_utils"
    ]

    sys.path.append(str(Path("").absolute()))

    success_count = 0
    for import_name in required_imports:
        try:
            __import__(import_name)
            print(f"✓ {import_name}")
            success_count += 1
        except ImportError as e:
            print(f"✗ {import_name}: {e}")

    print(f"Component imports: {success_count}/{len(required_imports)} successful")
    return success_count == len(required_imports)

def test_encoder_creation():
    """Test that encoders can be created successfully."""
    print("\nTesting encoder creation...")

    try:
        sys.path.append(str(Path("").absolute()))
        from utils.encoder_factory import create_encoder_from_params

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
        if hasattr(result, '__len__') or isinstance(result, (int, float)):
            print("✓ Encoding test successful")
            return True
        else:
            print(f"✗ Unexpected encoding result type: {type(result)}")
            return False

    except Exception as e:
        print(f"✗ Encoder creation failed: {e}")
        return False

def test_visualization_creation():
    """Test that visualizations can be created."""
    print("\nTesting visualization creation...")

    try:
        sys.path.append(str(Path("").absolute()))
        from utils.encoder_factory import create_encoder_from_params
        from components.plotly_plots import create_encoder_visualization, create_heatmap_visualization

        # Create test encoder and parameters
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

        # Test encoder visualization
        encoder_fig = create_encoder_visualization(encoder, params)
        if hasattr(encoder_fig, 'data'):
            print("✓ Encoder visualization created")
        else:
            print("✗ Invalid encoder visualization")
            return False

        # Test heatmap visualization
        heatmap_fig = create_heatmap_visualization(encoder, params)
        if hasattr(heatmap_fig, 'data'):
            print("✓ Heatmap visualization created")
        else:
            print("✗ Invalid heatmap visualization")
            return False

        return True

    except Exception as e:
        print(f"✗ Visualization creation failed: {e}")
        return False

def test_app_startup():
    """Test that the app can start up without immediate errors."""
    print("\nTesting app startup readiness...")

    try:
        sys.path.append(str(Path("").absolute()))
        import app_complete_fixed

        # Test that the app object exists and has expected attributes
        app = app_complete_fixed.app

        if hasattr(app, 'callback'):
            print("✓ App has callback decorator")
        else:
            print("✗ App missing callback decorator")
            return False

        if hasattr(app, 'layout'):
            print("✓ App has layout")
        else:
            print("✗ App missing layout")
            return False

        if hasattr(app, 'run'):
            print("✓ App has run method")
        else:
            print("✗ App missing run method")
            return False

        print("✓ App ready for startup")
        return True

    except Exception as e:
        print(f"✗ App startup test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("GNOME Encoder Complete App - Debug Verification")
    print("=" * 60)

    tests = [
        ("Complete App Import", test_complete_app_import),
        ("Component Imports", test_component_imports),
        ("Encoder Creation", test_encoder_creation),
        ("Visualization Creation", test_visualization_creation),
        ("App Startup Readiness", test_app_startup)
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"Running: {test_name}")
        print(f"{'-' * 40}")
        results[test_name] = test_func()

    # Summary
    print(f"\n{'=' * 60}")
    print("DEBUG VERIFICATION SUMMARY")
    print(f"{'=' * 60}")

    passed = 0
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<45} {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 All tests passed! The debugged app is ready to use.")
        print("\nTo start the working application:")
        print("  cd dash_encoder_app")
        print("  python app_complete_fixed.py")
        print("\nThen navigate to: http://localhost:8052")
    else:
        print(f"\n⚠️  {len(tests) - passed} test(s) failed.")
        print("Check the error messages above for debugging guidance.")

    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)