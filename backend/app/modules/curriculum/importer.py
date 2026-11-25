import csv
import io
from dataclasses import dataclass

from openpyxl import load_workbook


@dataclass
class ParsedCourse:
    row_number: int
    code: str
    title: str
    credits: int | None
    semester_number: int | None
    status: str
    errors: list[str]


HEADER_ALIASES = {
    "code": {"code", "course_code", "کد", "کد درس"},
    "title": {"title", "course_title", "نام", "نام درس", "عنوان"},
    "credits": {"credits", "unit", "واحد", "تعداد واحد"},
    "semester_number": {"semester", "semester_number", "ترم", "شماره ترم"},
    "status": {"status", "وضعیت"},
}


def _normalise(value: object) -> str:
    return str(value or "").strip().lower()


def _headers(values: list[object]) -> dict[str, int]:
    result: dict[str, int] = {}
    for index, value in enumerate(values):
        name = _normalise(value)
        for field, aliases in HEADER_ALIASES.items():
            if name in aliases:
                result[field] = index
                break
    return result


def _parse_rows(rows: list[tuple[object, ...]]) -> list[ParsedCourse]:
    if not rows:
        raise ValueError("فایل خالی است")
    header = _headers(list(rows[0]))
    missing = [field for field in ("code", "title") if field not in header]
    if missing:
        raise ValueError("ستون‌های الزامی کد و عنوان درس پیدا نشدند")
    parsed: list[ParsedCourse] = []
    for row_number, row in enumerate(rows[1:], start=2):
        value = lambda field: row[header[field]] if field in header and header[field] < len(row) else ""
        code, title = _normalise(value("code")), str(value("title") or "").strip()
        errors: list[str] = []
        try:
            credits = int(value("credits")) if "credits" in header and str(value("credits")).strip() else None
        except ValueError:
            credits, errors = None, ["تعداد واحد باید عدد باشد"]
        try:
            semester = int(value("semester_number")) if "semester_number" in header and str(value("semester_number")).strip() else None
        except ValueError:
            semester, errors = None, errors + ["شماره ترم باید عدد باشد"]
        if not code:
            errors.append("کد درس الزامی است")
        if not title:
            errors.append("عنوان درس الزامی است")
        parsed.append(ParsedCourse(row_number, code, title, credits, semester, _normalise(value("status")) or "required", errors))
    return parsed


def parse_course_file(filename: str, content: bytes) -> list[ParsedCourse]:
    extension = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if extension == "csv":
        text = content.decode("utf-8-sig")
        return _parse_rows([tuple(row) for row in csv.reader(io.StringIO(text))])
    if extension == "xlsx":
        workbook = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        rows = [tuple(row) for row in workbook.active.iter_rows(values_only=True)]
        return _parse_rows(rows)
    raise ValueError("فقط فایل‌های CSV و XLSX پشتیبانی می‌شوند")
