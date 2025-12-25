AI Prompt Builder

Simple web UI for composing, testing and managing prompt templates for AI models.

Features
- Builder with structured fields: Role, Context, Task, Example
- Model selector (Claude supported; placeholders for future models)
- Send prompts to Claude and display responses (responses are shown in UI only, not saved)
- Save / Load / Update / Delete prompt templates
- Responsive three-column UI: Saved prompts (left), Builder (center), Response (right)

Requirements
- Python 3.10+
- PostgreSQL (or any `DATABASE_URL` compatible DB)
- CLAUDE_API_KEY (Anthropic)

Install Python deps:

```
pip install -r requirements.txt
```

Setup
1. Copy environment variables into `.env` in project root (example):

```
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
CLAUDE_API_KEY=sk-xxxx
```

2. Initialize database schema (example using `psql`):

```
psql $DATABASE_URL -f schema.sql
```

3. Run the app locally:

```
python app.py
```

The app listens on `0.0.0.0:8080` by default.

Usage
- Open your browser at `http://localhost:8080/`.
- Left column: saved prompt templates (title + date). Load a template to edit.
- Center: Builder — select model, edit Role/Context/Task/Example. `Send` will call the model and show response in the right column. `Save` creates a new template. If a template is loaded, `Update` will overwrite it.
- Right column: large response area where model output appears (responses are not stored in the DB).

Notes
- Titles are limited to 25 characters (client- and server-side truncation).
- The app currently integrates with Anthropic's Claude SDK via the `anthropic` package. GPT-5/other providers are not yet integrated.
- Environment variables from `.env` are loaded at runtime; when running in containers use your orchestrator to pass secrets.

Docker
A `Dockerfile` exists; build and run with your usual Docker workflow. Ensure environment variables are provided to the container.

Contributing
PRs and issues welcome. For new model integrations, add server-side client logic and extend the model dropdown in the UI.

License
Specify a license for your project (MIT recommended if unsure).
