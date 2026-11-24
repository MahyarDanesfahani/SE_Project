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

API چارت درسی:

- `POST /api/v1/curricula`
- `GET /api/v1/curricula/{curriculum_id}`
- `POST /api/v1/curricula/{curriculum_id}/courses`
- `POST /api/v1/curricula/{curriculum_id}/import/preview` — فایل CSV/XLSX، بدون ثبت نهایی
- `POST /api/v1/curricula/{curriculum_id}/import/confirm` — تأیید ردیف‌های اصلاح‌شده و ثبت تراکنشی
- `POST /api/v1/curricula/{curriculum_id}/courses/{course_id}/prerequisites` — ثبت پیش‌نیاز/هم‌نیاز
- `GET /api/v1/curricula/{curriculum_id}/courses/{course_id}/prerequisites` — مشاهده روابط
- `POST /api/v1/offerings/terms` — ایجاد نیمسال
- `POST /api/v1/offerings` — ایجاد گروه درسی
- `POST /api/v1/offerings/{offering_id}/sessions` — افزودن جلسه زمانی
- `POST /api/v1/offerings/schedule/generate` — تولید سناریوهای بدون تداخل زمانی
- `POST /api/v1/academic-records` — ثبت سابقه درس
- `GET /api/v1/academic-records` — مشاهده سوابق خود دانشجو
- `POST /api/v1/grades` — ثبت نمره
- `GET /api/v1/grades` — مشاهده نمره‌ها
- `GET /api/v1/grades/gpa` — محاسبه معدل وزنی تأییدشده
- `POST /api/v1/exams` و `GET /api/v1/exams` — مدیریت امتحانات
- `POST /api/v1/tasks` و `GET /api/v1/tasks` — مدیریت وظایف
- `GET /api/v1/calendar` — تقویم یکپارچه امتحانات و وظایف
- `POST /api/v1/announcements` — ثبت اطلاعیه با منبع
- `GET /api/v1/announcements?search=...&category=...` — جست‌وجو و فیلتر اطلاعیه‌ها

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
