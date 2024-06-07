import socketserver
import httpx
import http.server

TARGET_ADDRESS = "http://localhost:40342"


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.forward_request()

    def do_POST(self):
        self.forward_request()

    def do_PUT(self):
        self.forward_request()

    def do_DELETE(self):
        self.forward_request()

    def forward_request(self):
        # Forward the request to the target address
        url = TARGET_ADDRESS + self.path
        headers = dict(self.headers)
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))

        with httpx.Client() as client:
            response = client.request(self.command, url, headers=headers, data=body)

        # Send the response back to the client
        self.send_response(response.status_code)
        for header, value in response.headers.items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(response.content)


if __name__ == "__main__":
    server_address = ("", 8000)
    httpd = socketserver.TCPServer(server_address, ProxyHandler)
    print(f'Listening on {server_address[0]}:{server_address[1]} and forwarding requests to {TARGET_ADDRESS}')
    httpd.serve_forever()
