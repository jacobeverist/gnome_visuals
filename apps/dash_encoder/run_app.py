#!/usr/bin/env python3
"""
Launch script for GNOME Encoder Interactive Dashboard

Usage:
    python run_app.py [--port PORT] [--debug]

Options:
    --port PORT    Port to run the server on (default: 8050)
    --debug        Run in debug mode (default: False)
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    parser = argparse.ArgumentParser(description='GNOME Encoder Interactive Dashboard')
    parser.add_argument('--port', type=int, default=8050,
                       help='Port to run the server on (default: 8050)')
    parser.add_argument('--debug', action='store_true',
                       help='Run in debug mode')

    args = parser.parse_args()

    try:
        from app import app
        print(f"Starting GNOME Encoder Dashboard on http://localhost:{args.port}")
        print("Press Ctrl+C to stop the server")

        app.run(debug=args.debug, port=args.port, host='0.0.0.0')

    except ImportError as e:
        print(f"Error: Could not import required modules: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r ../requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()