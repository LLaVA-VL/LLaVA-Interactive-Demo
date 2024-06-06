import socketserver
import http.server

TARGET_ADDRESS = "localhost:40342"


class RedirectHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(301)
        self.send_header('Location', f'http://{TARGET_ADDRESS}' + self.path)
        self.end_headers()


ADDRESS = "0.0.0.0"
PORT = 8000

with socketserver.TCPServer((ADDRESS, PORT), RedirectHandler) as httpd:
    print(f"Redirecting traffic from {ADDRESS}:{PORT} to {TARGET_ADDRESS}...")
    httpd.serve_forever()
