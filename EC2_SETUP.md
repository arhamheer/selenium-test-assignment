# EC2 Setup (minimal)

Use these non-conflicting ports:

- Backend API: 9000 (public)
- Frontend UI: 5173 (public)
- Jenkins UI: 9090 (public)
- PostgreSQL: 5432 (internal only — do NOT expose publicly)

If you are already inside `backend`, do not run `cd backend`.

Minimal commands:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip nodejs npm
```

1. Postgres:

```bash
docker run -d --name taskflow-postgres \
  -e POSTGRES_PASSWORD=pajay6205 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=taskflow_db \
  -p 5432:5432 postgres:16
```

2. Backend:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000
```

3. Frontend:

```bash
cd ../frontend
npm install --silent
npm run dev -- --host 0.0.0.0 --port 5173
```

Quick checks:

```bash
curl -s http://localhost:9000/ | head -n 1
curl -s http://localhost:5173/ | head -n 1
```
