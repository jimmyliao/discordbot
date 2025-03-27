import http.server
import socketserver
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        message = "Hello, World!"
        self.wfile.write(bytes(message, "utf8"))
        logging.info(f"Sent: {message}")

def run_server(port):
    """Runs a simple HTTP server that displays 'Hello, World!'."""
    with socketserver.TCPServer(("", port), MyHandler) as httpd:
        logging.info(f"Serving at: http://0.0.0.0:{port}")
        print(f"Serving at: http://0.0.0.0:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    port = 8080  # You can change the port here
    run_server(port)
