import http.server
import socketserver
import json
import base64

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Authorization')
        self.end_headers()

    def do_POST(self):
        if self.path == '/log':
            auth = self.headers.get('Authorization')
            if auth and auth.startswith('Bearer '):
                token = auth.split(' ')[1]
                header = token.split('.')[0]
                header_padded = header + '=' * (-len(header) % 4)
                decoded = base64.urlsafe_b64decode(header_padded).decode('utf-8')
                with open('token_header.json', 'w') as f:
                    f.write(decoded)
                print("Captured header:", decoded)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'OK')

with socketserver.TCPServer(('', 9999), Handler) as httpd:
    httpd.handle_request()  # Handle just one request
