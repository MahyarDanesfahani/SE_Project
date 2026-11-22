from app.modules.curriculum.importer import parse_course_file


def test_csv_preview_parses_valid_and_invalid_rows() -> None:
    content = "code,title,credits,semester\nCS101,Algorithms,3,1\n,Missing code,3,1\n".encode()
    rows = parse_course_file("curriculum.csv", content)
    assert rows[0].code == "cs101"
    assert rows[0].errors == []
    assert "کد درس الزامی است" in rows[1].errors
