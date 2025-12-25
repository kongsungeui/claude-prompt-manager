AI 프롬프트 빌더

간단한 웹 UI로 AI 모델용 프롬프트 템플릿을 작성, 테스트, 관리할 수 있습니다.

기능
- 구조화된 빌더 필드: Role, Context, Task, Example
- 모델 선택(현재 Claude 지원, 향후 다른 모델 확장 가능)
- 모델에 요청을 보내 응답을 UI에 표시(응답은 DB에 저장되지 않음)
- 프롬프트 템플릿 저장/불러오기/수정(Update)/삭제
- 반응형 3단 레이아웃: 왼쪽(저장된 템플릿), 가운데(빌더), 오른쪽(응답)

요구사항
- Python 3.10+
- PostgreSQL 또는 `DATABASE_URL`을 지원하는 DB
- CLAUDE_API_KEY (Anthropic)

의존성 설치

```bash
pip install -r requirements.txt
```

설정
1. 프로젝트 루트에 `.env` 파일을 만들고 환경 변수를 추가하세요:

```
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
CLAUDE_API_KEY=sk-xxxx
```

2. 데이터베이스 스키마 초기화(예: `psql` 사용):

```bash
psql $DATABASE_URL -f schema.sql
```

실행

```bash
python app.py
```

기본적으로 `0.0.0.0:8080`에서 대기합니다.

사용법
- 브라우저에서 `http://localhost:8080/` 열기
- 왼쪽: 저장된 프롬프트 목록(제목 + 날짜). 불러와 편집 가능
- 가운데: 빌더 — 모델 선택, Role/Context/Task/Example 작성. `Send`는 모델에 요청하여 오른쪽 응답 패널에 표시합니다. `Save`는 새 템플릿 생성. 불러온 상태에서 `Update`는 기존 항목을 덮어씁니다.
- 오른쪽: 모델 응답이 크게 표시됩니다(응답은 DB에 저장되지 않음)

주의사항
- 제목은 25자까지 허용합니다(클라이언트 및 서버 측에서 제한 적용).
- 현재 Anthropic의 `anthropic` SDK(Claude)를 사용합니다. GPT-5 등 다른 제공자는 미통합 상태입니다.
- 민감한 값(`.env` 등)은 레포에 커밋하지 마세요. 배포 환경에서 적절히 시크릿을 설정하세요.

Docker
- 레포에 `Dockerfile`이 포함되어 있으면 컨테이너로 빌드/배포할 수 있습니다. DigitalOcean App Platform이나 Droplet에서 컨테이너 실행을 권장합니다.

기여
- PR 및 이슈 환영합니다. 다른 모델을 통합하려면 서버 측 클라이언트 로직과 UI의 모델 드롭다운을 확장하세요.

라이선스
- 프로젝트에 적용할 라이선스를 선택하세요(미정이면 MIT 권장).
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
