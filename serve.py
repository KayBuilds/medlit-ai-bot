#!/usr/bin/env python3
"""
MedLit AI - Local Server
Serve the landing page locally for testing
"""

import http.server
import socketserver
import os

PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

if __name__ == "__main__":
    os.chdir(WEB_DIR)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌐 MedLit AI server running at:")
        print(f"   Local: http://localhost:{PORT}")
        print(f"   Network: http://0.0.0.0:{PORT}")
        print(f"\n   Landing Page: http://localhost:{PORT}/index.html")
        print(f"   Samples: http://localhost:{PORT}/samples.html")
        print(f"\nPress Ctrl+C to stop")
        httpd.serve_forever()
