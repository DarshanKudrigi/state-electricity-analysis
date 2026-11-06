"""Dashboard server launcher for State Electricity Analysis.

Serves the interactive web dashboard on a local port, handles dynamic user data API requests,
and automatically opens the browser.
"""

from __future__ import annotations

import functools
import http.server
import json
import shutil
import socketserver
import sys
import webbrowser
from pathlib import Path
from typing import Any, Dict

# Ensure package root 'src' is discoverable
_src_dir = str(Path(__file__).resolve().parents[1])
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from dvp_project.dashboard_data import export_dashboard_data
from dvp_project.dynamic_analyzer import (
    analyze_user_dataset,
    generate_custom_figures,
    load_user_data,
)


class DashboardAPIHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler serving static dashboard assets and dynamic data API endpoints."""

    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/status":
            self._send_json({"status": "online", "mode": "dynamic_data_enabled"})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path in ["/api/analyze", "/api/upload"]:
            self._handle_analyze()
            return
        elif self.path == "/api/generate-figures":
            self._handle_generate_figures()
            return
        self.send_error(404, "Endpoint not found")

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def _handle_analyze(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length).decode("utf-8")
            
            # Check if JSON wrapper or raw CSV
            if raw_body.strip().startswith("{"):
                payload = json.loads(raw_body)
                content = payload.get("data", "")
                dataset_name = payload.get("name", "User Uploaded Data")
            else:
                content = raw_body
                dataset_name = "User Uploaded Data"

            df = load_user_data(content)
            analysis = analyze_user_dataset(df, dataset_name=dataset_name)

            self._send_json({"status": "success", "analysis": analysis})
        except Exception as err:
            self._send_json({"status": "error", "message": str(err)}, status=400)

    def _handle_generate_figures(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(raw_body) if raw_body.strip().startswith("{") else {"data": raw_body}
            
            content = payload.get("data", "")
            dataset_name = payload.get("name", "User Dataset")
            df = load_user_data(content)
            analysis = analyze_user_dataset(df, dataset_name=dataset_name)

            project_root = Path(__file__).resolve().parents[2]
            output_dir = project_root / "dashboard" / "figures"
            figs = generate_custom_figures(df, analysis, output_dir=output_dir)

            fig_urls = [f"figures/{f.name}" for f in figs]
            self._send_json({"status": "success", "figures": fig_urls})
        except Exception as err:
            self._send_json({"status": "error", "message": str(err)}, status=400)


def run_dashboard_server(port: int = 8080, open_browser: bool = True) -> None:
    """Start local HTTP server serving the dashboard directory and dynamic API."""
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

    handler_factory = functools.partial(DashboardAPIHandler, directory=str(dashboard_dir))

    for attempt in range(max_attempts):
        try:
            httpd = socketserver.TCPServer(("", current_port), handler_factory)
            break
        except OSError:
            current_port += 1

    if httpd is None:
        print(f"[-] Could not bind server on ports {port} - {port + max_attempts}.", file=sys.stderr)
        sys.exit(1)

    url = f"http://localhost:{current_port}/"
    print("=" * 65)
    print("STATE ELECTRICITY INTELLIGENCE & DYNAMIC DATA DASHBOARD")
    print("=" * 65)
    print(f"  [+] Local server active at: {url}")
    print(f"  [+] Dynamic Data Upload API: {url}api/analyze")
    print("  [+] Press Ctrl+C in terminal to stop the server.")
    print("=" * 65)

    if open_browser:
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
