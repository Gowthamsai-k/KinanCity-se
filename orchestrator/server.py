import json, os, pathlib, subprocess, threading, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Compose sets /runtime inside the container.  A direct local run uses a
# repository-relative directory so it does not require write access to /.
ROOT = pathlib.Path(os.getenv('RUNTIME_DIR', 'runtime')); ROOT.mkdir(parents=True, exist_ok=True)
IMAGE = os.getenv('CORE_IMAGE', 'kinancity-core:local')
job = {'id': None, 'container': None, 'state': 'idle', 'message': ''}

def completed_csv():
    result = ROOT / 'result.csv'; links = ROOT / 'links.log'
    if not result.exists(): return '#username;password;email\n'
    activated = set()
    if links.exists():
        for line in links.read_text(errors='replace').splitlines():
            parts = line.split(';')
            if len(parts) >= 4 and parts[0] == 'ACTIVATION' and parts[3].upper() in ('OK','DONE'):
                activated.add(parts[2])
    rows = ['#username;password;email']
    for line in result.read_text(errors='replace').splitlines():
        if not line or line.startswith('#'): continue
        parts = line.split(';')
        if len(parts) >= 4 and parts[3].upper() == 'OK' and parts[2] in activated:
            rows.append(';'.join(parts[:3]))
    return '\n'.join(rows) + '\n'

def run_job(payload):
    global job
    if payload.get('confirm') != 'RUN':
        raise ValueError('confirmation must be RUN')
    batch = payload.get('batch_csv', '')
    if not batch:
        pattern = payload.get('pattern', '')
        count = int(payload.get('count', 0)); start = int(payload.get('start', 0))
        base_email = os.getenv('KINAN_BASE_EMAIL', '')
        account_password = os.getenv('KINAN_ACCOUNT_PASSWORD', '')
        if not pattern or '*' not in pattern or count < 1 or not base_email or not account_password:
            raise ValueError('configure KINAN_BASE_EMAIL and KINAN_ACCOUNT_PASSWORD, and provide pattern/count')
        width = pattern.count('*')
        if start + count - 1 > (10 ** width) - 1: raise ValueError('pattern width is too small')
        rows = ['#username;password;email']
        for n in range(start, start + count):
            username = pattern.replace('*' * width, str(n).zfill(width), 1)
            address = base_email.replace('@', '+' + username + '@', 1) if '@' in base_email else username + base_email
            rows.append(';'.join((username, account_password, address)))
        batch = '\n'.join(rows) + '\n'
    if not batch.startswith('#username;'):
        raise ValueError('batch_csv must contain a KinanCity CSV header')
    token = payload.get('captcha_value') or os.getenv('KC_CAPTCHA_VALUE', '')
    provider = payload.get('captcha_provider') or os.getenv('CAPTCHA_PROVIDER', 'local')
    jid = uuid.uuid4().hex[:12]; name = 'kinancity-core-' + jid
    (ROOT / 'kinancity-batch.csv').write_text(batch)
    job = {'id': jid, 'container': name, 'state': 'starting', 'message': ''}
    if os.getenv('DRY_RUN', '').lower() in ('1', 'true', 'yes'):
        # Safe local integration test: produce synthetic successful files and
        # never invoke Docker or contact a third-party service.
        records = []
        for line in batch.splitlines():
            if line and not line.startswith('#'):
                parts = line.split(';')
                if len(parts) >= 3:
                    records.append(parts[:3])
        (ROOT / 'result.csv').write_text('#username;password;email;status\n' + ''.join(';'.join(r) + ';OK\n' for r in records))
        (ROOT / 'links.log').write_text(''.join('ACTIVATION;dry-run;'+r[2]+';OK\n' for r in records))
        job = {'id': jid, 'container': None, 'state': 'completed', 'message': 'DRY_RUN completed; no external calls made'}
        return job
    cmd = ['docker', 'run', '--rm', '--name', name, '-v', '/runtime:/data',
           '-e', 'CAPTCHA_PROVIDER=' + provider, '-e', 'KC_CAPTCHA_VALUE=' + token,
           IMAGE, '-a', '/data/kinancity-batch.csv', '-o', '/data/result.csv', '-npc']
    def start():
        global job
        try:
            p = subprocess.run(cmd, capture_output=True, text=True)
            job = {'id': jid, 'container': name, 'state': 'completed' if p.returncode == 0 else 'failed', 'message': (p.stdout + p.stderr)[-4000:]}
        except Exception as exc:
            job = {'id': jid, 'container': name, 'state': 'failed', 'message': str(exc)}
    threading.Thread(target=start, daemon=True).start()
    return job

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, value):
        raw = json.dumps(value).encode(); self.send_response(code); self.send_header('Content-Type','application/json'); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path == '/api/status': self._json(200, job)
        elif self.path == '/api/health': self._json(200, {'ok': True, 'core_image': IMAGE})
        elif self.path == '/api/output':
            raw = completed_csv().encode(); self.send_response(200); self.send_header('Content-Type','text/csv'); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
        else: self._json(404, {'error':'not found'})
    def do_OPTIONS(self):
        self.send_response(204); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS'); self.send_header('Access-Control-Allow-Headers','Content-Type'); self.end_headers()
    def do_POST(self):
        if self.path != '/api/run': self._json(404, {'error':'not found'}); return
        try:
            n = int(self.headers.get('Content-Length','0')); payload = json.loads(self.rfile.read(n)); self._json(202, run_job(payload))
        except Exception as exc: self._json(400, {'error': str(exc)})
    def log_message(self, *_): pass

ThreadingHTTPServer(('0.0.0.0', 8090), Handler).serve_forever()
