import socketserver
import http.server


class RedirectHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(301)
        self.send_header('Location', 'http://localhost:40342' + self.path)
        self.end_headers()


PORT = 8000  # Change this to the desired port number

with socketserver.TCPServer(("", PORT), RedirectHandler) as httpd:
    print(f"Redirecting traffic from port {PORT} to localhost:40342...")
    httpd.serve_forever()
