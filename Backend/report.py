from fastapi import APIRouter, Depends, Response
import csv
import io
import sqlite3
from database import get_db

router = APIRouter()


@router.get("/report/fall", response_class=Response)
def generate_fall_report(db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute(
        (
            "SELECT id, type, description, status, created_at, clip_path "
            "FROM incidents WHERE type=? ORDER BY created_at DESC"
        ),
        ("fall",),
    )
    rows = c.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["ID", "Type", "Description", "Status", "Created At", "Clip Path"]
    )
    for row in rows:
        writer.writerow(row)
    csv_content = output.getvalue()
    output.close()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=fall_report.csv"
        },
    )
