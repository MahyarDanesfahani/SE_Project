from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import University


def seed() -> None:
    with SessionLocal() as db:
        university = db.scalar(select(University).where(University.code == "ZNU"))
        if university is None:
            db.add(University(name="دانشگاه زنجان", code="ZNU"))
            db.commit()
            print("Seeded University of Zanjan")
        else:
            print("University of Zanjan already exists")


if __name__ == "__main__":
    seed()
