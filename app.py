import json
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, Response, session, redirect, url_for
import psycopg2
from anthropic import Anthropic

load_dotenv(override=True)

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret')

# API 키 확인 (디버깅용)
api_key = os.environ.get('CLAUDE_API_KEY')
if not api_key:
    print("⚠️  WARNING: CLAUDE_API_KEY not found!")
else:
    print("✓ CLAUDE_API_KEY loaded")

def get_db():
    return psycopg2.connect(os.environ['DATABASE_URL'])

# Simple HTTP Basic Auth credentials (can be overridden with env vars)
AUTH_USER = os.environ.get('AUTH_USER', 'admin')
AUTH_PASS = os.environ.get('AUTH_PASS', 'password')

# Max tokens default and optional limit (can be overridden with env vars)
MAX_TOKENS_DEFAULT = int(os.environ.get('MAX_TOKENS_DEFAULT', '1024'))
MAX_TOKENS_LIMIT = int(os.environ.get('MAX_TOKENS_LIMIT')) if os.environ.get('MAX_TOKENS_LIMIT') else None


@app.before_request
def require_login():
    # Allow static assets and login routes without auth
    if request.path.startswith('/static') or request.path in ('/favicon.ico', '/login'):
        return
    # Allow the login POST and GET
    if request.path == '/login' and request.method in ('GET', 'POST'):
        return
    # Check session
    if not session.get('user'):
        # For API requests return 401 JSON, for browser redirect to login
        if request.path.startswith('/api'):
            return jsonify({'error': 'authentication required'}), 401
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return send_from_directory('static', 'login.html')
    # POST: authenticate
    username = request.form.get('username')
    password = request.form.get('password')
    if username == AUTH_USER and password == AUTH_PASS:
        session['user'] = username
        return redirect(url_for('index'))
    # auth failed -> show login with error
    return redirect(url_for('login') + '?error=1')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

def _row_to_prompt(row):
    prompt_id, title, content_raw, response, model, created_at = row
    role = context = task = example = ''
    content_text = ''
    try:
        data = json.loads(content_raw or '{}')
        role = data.get('role', '') or ''
        context = data.get('context', '') or ''
        task = data.get('task', '') or ''
        example = data.get('example', '') or ''
        content_text = data.get('rendered', '') or ''
    except (TypeError, json.JSONDecodeError):
        content_text = content_raw or ''
        task = content_text
    return {
        'id': prompt_id,
        'title': title,
        'role': role,
        'context': context,
        'task': task,
        'example': example,
        'content': content_text,
        'model': model,
        'created_at': str(created_at),
        'response': None  # responses are no longer stored
    }


@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, title, content, response, model, created_at FROM prompts ORDER BY created_at DESC LIMIT 50')
    prompts = [_row_to_prompt(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(prompts)

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    role = data.get('role', '') or ''
    context = data.get('context', '') or ''
    task = data.get('task', '') or ''
    example = data.get('example', '') or ''
    model = data.get('model') or 'claude-sonnet-4-20250514'

    rendered = build_prompt_text(role, context, task, example)
    content_json = json.dumps({
        'role': role,
        'context': context,
        'task': task,
        'example': example,
        'rendered': rendered,
    })

    title = (data.get('title') or 'Untitled')[:25]
    cur.execute(
        'INSERT INTO prompts (title, content, model) VALUES (%s, %s, %s) RETURNING id',
        (title, content_json, model)
    )
    prompt_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'id': prompt_id})


@app.route('/api/prompts/<int:prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    data = request.json
    conn = get_db()
    cur = conn.cursor()

    role = data.get('role', '') or ''
    context = data.get('context', '') or ''
    task = data.get('task', '') or ''
    example = data.get('example', '') or ''
    model = data.get('model') or 'claude-sonnet-4-20250514'
    title = (data.get('title') or 'Untitled')[:25]

    rendered = build_prompt_text(role, context, task, example)
    content_json = json.dumps({
        'role': role,
        'context': context,
        'task': task,
        'example': example,
        'rendered': rendered,
    })

    cur.execute(
        'UPDATE prompts SET title = %s, content = %s, model = %s WHERE id = %s',
        (title, content_json, model, prompt_id)
    )
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if updated:
        return jsonify({'updated': True, 'id': prompt_id})
    return jsonify({'updated': False}), 404


@app.route('/api/prompts/<int:prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM prompts WHERE id = %s', (prompt_id,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if deleted:
        return jsonify({'deleted': True})
    else:
        return jsonify({'deleted': False}), 404

def build_prompt_text(role: str, context: str, task: str, example: str) -> str:
    sections = []
    if role:
        sections.append(f"Role:\n{role}")
    if context:
        sections.append(f"Context:\n{context}")
    if task:
        sections.append(f"Task:\n{task}")
    if example:
        sections.append(f"Example:\n{example}")
    return "\n\n".join(sections)


@app.route('/api/claude', methods=['POST'])
def call_claude():
    data = request.json
    if not api_key:
        return jsonify({'error': 'CLAUDE_API_KEY not set on server'}), 500

    model = data.get('model') or 'claude-sonnet-4-20250514'
    if not model.startswith('claude'):
        return jsonify({'error': f"Model '{model}' not supported yet"}), 400

    role = data.get('role', '') or ''
    context = data.get('context', '') or ''
    task = data.get('task', '') or ''
    example = data.get('example', '') or ''

    prompt_text = build_prompt_text(role, context, task, example)

    client = Anthropic(api_key=api_key)
    # determine max tokens: request -> env default -> apply optional limit
    try:
        requested = data.get('max_tokens')
        if requested is None:
            max_tokens = MAX_TOKENS_DEFAULT
        else:
            max_tokens = int(requested)
    except (TypeError, ValueError):
        max_tokens = MAX_TOKENS_DEFAULT
    if MAX_TOKENS_LIMIT:
        max_tokens = min(max_tokens, MAX_TOKENS_LIMIT)
    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt_text}]
        )
        response_text = message.content[0].text
        return jsonify({'response': response_text})
    except Exception as e:
        # catch network/timeouts/SDK errors and return a 504-like response
        print('ERROR calling Anthropic:', str(e))
        return jsonify({'error': 'Model request failed or timed out'}), 504

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)