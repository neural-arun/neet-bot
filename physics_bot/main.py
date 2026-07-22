import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

import logging
import threading
import json
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from bot_handlers import build_app
from db import init_db
import questions as qs
from ai_analyzer import analyze_performance
import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

PORT = int(os.getenv('PORT', 8080))
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')

class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ['/', '/index.html']:
            self._serve_file(os.path.join(WEB_DIR, 'index.html'), 'text/html; charset=utf-8')
        elif path == '/style.css':
            self._serve_file(os.path.join(WEB_DIR, 'style.css'), 'text/css; charset=utf-8')
        elif path == '/app.js':
            self._serve_file(os.path.join(WEB_DIR, 'app.js'), 'application/javascript; charset=utf-8')
        elif path == '/logo.png':
            self._serve_file(os.path.join(WEB_DIR, 'logo.png'), 'image/png')
        elif path == '/api/chapters':
            chapters = qs.get_chapter_list()
            self._json_response({'chapters': chapters, 'total': len(chapters)})
        elif path == '/api/questions':
            params = parse_qs(parsed.query)
            ch_param = params.get('chapters', [''])[0]
            count = int(params.get('count', [15])[0])

            if '||' in ch_param:
                chapters_list = ch_param.split('||')
            else:
                chapters_list = [ch_param] if ch_param else []

            if not chapters_list or chapters_list == ['']:
                q_list = []
            elif len(chapters_list) == 1:
                q_list = qs.get_random_questions(chapters_list[0], count)
            else:
                q_list = qs.get_random_questions_multi(chapters_list, count)

        elif path in ['/admin', '/admin.html', '/dashboard']:
            self._serve_file(os.path.join(WEB_DIR, 'admin.html'), 'text/html; charset=utf-8')
        elif path == '/api/analytics':
            params = parse_qs(parsed.query)
            provided_pass = params.get('pass', [''])[0]
            if provided_pass != config.ADMIN_PASSWORD:
                self._json_response({'error': 'Unauthorized: Invalid Admin Password'}, status=401)
                return
            summary = db.get_analytics_summary()
            self._json_response(summary)
        elif path == '/api/track':
            params = parse_qs(parsed.query)
            event = params.get('event', [''])[0]
            if event in ['site_visit', 'telegram_click', 'web_test_start', 'web_test_complete']:
                db.increment_stat(event)
            self._json_response({'status': 'ok'})
        elif path in ['/health', '/healthz']:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/analyze':
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len)
            try:
                req_data = json.loads(body)
                ch = req_data.get('chapter', 'NEET Biology')
                correct = req_data.get('correct', 0)
                total = req_data.get('total', 0)
                wrong_answers = req_data.get('wrong_answers', [])

                analysis = analyze_performance(ch, correct, total, wrong_answers)
                self._json_response({'analysis': analysis})
            except Exception as e:
                self._json_response({'error': str(e)}, status=500)
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_file(self, file_path, content_type):
        if not os.path.exists(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File Not Found')
            return
        with open(file_path, 'rb') as f:
            content = f.read()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass

def run_single_server(port):
    try:
        server = HTTPServer(('0.0.0.0', port), WebServerHandler)
        logging.info(f"Web & Health server active on 0.0.0.0:{port}")
        server.serve_forever()
    except Exception as e:
        logging.debug(f"Port {port} skipped: {e}")

def run_health_servers():
    env_port = int(os.getenv('PORT', 8080))
    ports = [env_port, 8080, 7860, 8000, 80]
    bound = set()
    for p in ports:
        if p not in bound:
            bound.add(p)
            t = threading.Thread(target=run_single_server, args=(p,), daemon=True)
            t.start()

def main():
    run_health_servers()

    init_db()
    logging.info("Starting NEET Practice Bot & Web Server...")

    while True:
        try:
            app = build_app()
            logging.info("Bot started polling Telegram...")
            app.run_polling(allowed_updates=['message', 'callback_query'])
        except Exception as e:
            logging.error(f"Telegram polling error: {e}. Web server remains active. Retrying in 15 seconds...")
            time.sleep(15)

if __name__ == '__main__':
    main()
