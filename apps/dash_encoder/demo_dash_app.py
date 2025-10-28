#!/usr/bin/env python3
"""
Demo script for GNOME Encoder Interactive Dashboard

This script demonstrates how to launch and use the interactive encoder visualization tool.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['dash', 'plotly', 'dash_bootstrap_components']
    missing = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print("Install with: pip install dash plotly dash-bootstrap-components")
        return False
    return True

def main():
    print("=" * 60)
    print("GNOME Encoder Interactive Dashboard Demo")
    print("=" * 60)
    print()

    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        print("Please install missing dependencies and try again.")
        return

    print("✓ All dependencies found")
    print()

    # Show what the demo includes
    print("This interactive dashboard includes:")
    print("• Real-time encoder parameter controls (n, w, period, offset)")
    print("• Interactive encoder bin visualization")
    print("• Similarity heatmaps with hover information")
    print("• Support for multiple encoder types")
    print("• Responsive web interface")
    print()

    # Check if we're in the right directory
    app_dir = Path(__file__).parent / "dash_encoder_app"
    if not app_dir.exists():
        print(f"Error: Cannot find dash_encoder_app directory at {app_dir}")
        return

    print(f"Starting dashboard from: {app_dir}")
    print("The application will open in your default web browser.")
    print("Press Ctrl+C in this terminal to stop the server.")
    print()

    try:
        # Start the app
        app_script = app_dir / "run_app.py"
        if app_script.exists():
            print("Launching dashboard...")
            print("Dashboard will be available at: http://localhost:8050")

            # Give a moment for user to read the message
            time.sleep(2)

            # Try to open browser
            try:
                webbrowser.open('http://localhost:8050')
            except:
                print("Could not automatically open browser. Please navigate to http://localhost:8050 manually.")

            # Run the app from the app directory
            subprocess.run([sys.executable, str(app_script), "--debug"], cwd=str(app_dir))
        else:
            print(f"Error: Cannot find run_app.py at {app_script}")
            return

    except KeyboardInterrupt:
        print("\n\nShutting down dashboard...")
        print("Demo completed. Thank you!")
    except Exception as e:
        print(f"Error running dashboard: {e}")

if __name__ == "__main__":
    main()