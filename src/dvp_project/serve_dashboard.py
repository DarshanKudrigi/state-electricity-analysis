"""Dashboard server launcher for State Electricity Analysis.

Serves the interactive web dashboard on a local port and automatically opens the browser.
"""

from __future__ import annotations

import functools
import http.server
import shutil
import socketserver
import sys
import webbrowser
from pathlib import Path

# Ensure package root 'src' is discoverable
_src_dir = str(Path(__file__).resolve().parents[1])
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from dvp_project.dashboard_data import export_dashboard_data


def run_dashboard_server(port: int = 8080) -> None:
    """Start local HTTP server serving the dashboard directory."""
    project_root = Path(__file__).resolve().parents[2]
    dashboard_dir = project_root / "dashboard"
    figures_source = project_root / "outputs" / "figures"
    figures_dest = dashboard_dir / "figures"

    # Ensure dashboard data exists
    data_json = dashboard_dir / "data.json"
    if not data_json.exists():
        print("[*] Generating dashboard data JSON...")
        export_dashboard_data(data_json)

    # Sync figures
    if figures_source.exists():
        figures_dest.mkdir(parents=True, exist_ok=True)
        for fig in figures_source.glob("*.png"):
            shutil.copy2(fig, figures_dest / fig.name)

    # Find open port
    current_port = port
    max_attempts = 10
    httpd = None

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(dashboard_dir))

    for attempt in range(max_attempts):
        try:
            httpd = socketserver.TCPServer(("", current_port), handler)
            break
        except OSError:
            current_port += 1

    if httpd is None:
        print(f"[-] Could not bind server on ports {port} - {port + max_attempts}.", file=sys.stderr)
        sys.exit(1)

    url = f"http://localhost:{current_port}/"
    print("=" * 65)
    print("STATE ELECTRICITY INTELLIGENCE DASHBOARD")
    print("=" * 65)
    print(f"  [+] Local server active at: {url}")
    print("  [+] Press Ctrl+C in terminal to stop the server.")
    print("=" * 65)

    webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down dashboard server.")
        httpd.server_close()


def main() -> None:
    run_dashboard_server()


if __name__ == "__main__":
    main()
