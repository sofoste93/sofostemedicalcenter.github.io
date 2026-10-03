from __future__ import annotations

import argparse
import socket
import threading
import webbrowser

from waitress import serve

from . import __version__
from .web import create_app


def _lan_address() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.0.2.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description="Sofoste Medical Center")
    command.add_argument("--lan", action="store_true", help="allow trusted LAN devices")
    command.add_argument("--no-browser", action="store_true", help="do not open a browser")
    command.add_argument("--port", type=int, default=8765, help="HTTP port (default: 8765)")
    command.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if not 1024 <= args.port <= 65535:
        parser().error("--port must be between 1024 and 65535")
    host = "0.0.0.0" if args.lan else "127.0.0.1"
    visible_host = _lan_address() if args.lan else host
    url = f"http://{visible_host}:{args.port}"
    print("\n  Sofoste Medical Center · Python Edition 2.0")
    print(f"  Open: {url}")
    if args.lan:
        print("  LAN mode: use only on a trusted private network.")
    print("  Stop: Ctrl+C\n")
    if not args.no_browser:
        threading.Timer(0.8, webbrowser.open, args=(url,)).start()
    try:
        serve(create_app(), host=host, port=args.port, threads=4, clear_untrusted_proxy_headers=True)
    except KeyboardInterrupt:
        print("\n  Session closed. In-memory records are gone.")
    return 0
