# ZU Assistant

سامانه یکپارچه دستیار هوشمند دانشجویان دانشگاه زنجان.

## اسناد

- [SRS پروژه](SRS_README.md)
- [وضعیت پیاده‌سازی](docs/IMPLEMENTATION_STATUS.md)

## ساختار

- `backend/` — FastAPI، SQLAlchemy و Alembic
- `frontend/` — Next.js و TypeScript
- `infra/` — سرویس‌های زیرساختی توسعه
- `docs/` — وضعیت و تصمیم‌های فنی

## اجرای اولیه

```powershell
docker compose -f infra/docker-compose.yml up -d db
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

سپس `http://localhost:8000/api/v1/health` را باز کنید.

برای اجرای migration و seed اولیه:

```powershell
cd backend
alembic upgrade head
python scripts/seed.py
```

## وضعیت

این پروژه در فاز صفر توسعه است. قابلیت‌ها نباید تا زمان پیاده‌سازی واقعی، تست و ثبت در [IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) تکمیل‌شده تلقی شوند.
