from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8') # Also good practice to set charset in header
        self.end_headers()
        # Write strings and encode them to utf-8 bytes
        self.wfile.write("<html><head><title>Hello Docker!</title></head>".encode('utf-8'))
        self.wfile.write("<body><h1>Hello Docker! 🐳</h1>".encode('utf-8'))
        self.wfile.write("<p>My first Docker image is running.</p></body></html>".encode('utf-8'))

def run():
    print('Starting server...')
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleServer)
    print('Server running on port 8000...')
    httpd.serve_forever()

run()