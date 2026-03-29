"""
routers/students.py
-------------------
Student management CRUD endpoints.

GET    /students/by-class/{class_id}        → list students in a class
PUT    /students/{student_id}               → update student info
POST   /students/                           → add new student
DELETE /students/{student_id}               → deactivate student
POST   /students/{student_id}/move          → move student to another class
POST   /students/{student_id}/reactivate    → reactivate a deactivated student
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import Student, Class

router = APIRouter(prefix="/students", tags=["students"])


# ── Pydantic Schemas ────────────────────────────────────────────────────────

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    nis: Optional[str] = None
    nisn: Optional[str] = None
    gender: Optional[str] = None

class StudentCreate(BaseModel):
    name: str
    nis: str
    nisn: Optional[str] = None
    gender: Optional[str] = None
    class_id: int

class StudentMove(BaseModel):
    new_class_id: int


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/by-class/{class_id}")
def list_students_in_class(
    class_id: int,
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
):
    """List all students in a class, ordered by name."""
    kelas = db.query(Class).filter(Class.id == class_id).first()
    if not kelas:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")

    query = db.query(Student).filter(Student.class_id == class_id)
    if not include_inactive:
        query = query.filter(Student.is_active == True)

    students = query.order_by(Student.name).all()

    return {
        "class_id": kelas.id,
        "class_name": kelas.name,
        "grade_level": kelas.grade_level,
        "total": len(students),
        "students": [
            {
                "id": s.id,
                "nis": s.nis,
                "nisn": s.nisn,
                "name": s.name,
                "gender": s.gender,
                "is_active": s.is_active,
            }
            for s in students
        ],
    }


@router.put("/{student_id}")
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
):
    """Update student name, NIS, NISN, or gender."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    if data.name is not None:
        student.name = data.name.strip()
    if data.nis is not None:
        # Check uniqueness within the same class
        existing = (
            db.query(Student)
            .filter(
                Student.nis == data.nis,
                Student.class_id == student.class_id,
                Student.id != student.id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"NIS {data.nis} sudah digunakan di kelas ini",
            )
        student.nis = data.nis.strip()
    if data.nisn is not None:
        student.nisn = data.nisn.strip() or None
    if data.gender is not None:
        if data.gender not in ("L", "P", ""):
            raise HTTPException(status_code=400, detail="Gender harus L atau P")
        student.gender = data.gender or None

    db.commit()
    db.refresh(student)

    return {
        "status": "updated",
        "student": {
            "id": student.id,
            "nis": student.nis,
            "nisn": student.nisn,
            "name": student.name,
            "gender": student.gender,
            "class_id": student.class_id,
            "is_active": student.is_active,
        },
    }


@router.post("/")
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
):
    """Add a new student to a class."""
    kelas = db.query(Class).filter(Class.id == data.class_id).first()
    if not kelas:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")

    # Check NIS uniqueness within class
    existing = (
        db.query(Student)
        .filter(Student.nis == data.nis, Student.class_id == data.class_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"NIS {data.nis} sudah ada di kelas {kelas.name}",
        )

    if data.gender and data.gender not in ("L", "P"):
        raise HTTPException(status_code=400, detail="Gender harus L atau P")

    student = Student(
        name=data.name.strip(),
        nis=data.nis.strip(),
        nisn=data.nisn.strip() if data.nisn else None,
        gender=data.gender or None,
        class_id=data.class_id,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return {
        "status": "created",
        "student": {
            "id": student.id,
            "nis": student.nis,
            "nisn": student.nisn,
            "name": student.name,
            "gender": student.gender,
            "class_id": student.class_id,
            "is_active": student.is_active,
        },
    }


@router.delete("/{student_id}")
def deactivate_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    """Soft-delete: set is_active = False."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    student.is_active = False
    db.commit()

    return {"status": "deactivated", "student_id": student_id, "name": student.name}


@router.post("/{student_id}/reactivate")
def reactivate_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    """Re-enable a deactivated student."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    student.is_active = True
    db.commit()

    return {"status": "reactivated", "student_id": student_id, "name": student.name}


@router.post("/{student_id}/move")
def move_student(
    student_id: int,
    data: StudentMove,
    db: Session = Depends(get_db),
):
    """Move a student to a different class."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    new_class = db.query(Class).filter(Class.id == data.new_class_id).first()
    if not new_class:
        raise HTTPException(status_code=404, detail="Kelas tujuan tidak ditemukan")

    if student.class_id == data.new_class_id:
        raise HTTPException(status_code=400, detail="Siswa sudah di kelas ini")

    # Check NIS uniqueness in new class
    existing = (
        db.query(Student)
        .filter(
            Student.nis == student.nis,
            Student.class_id == data.new_class_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"NIS {student.nis} sudah ada di kelas {new_class.name}",
        )

    old_class_name = student.kelas.name
    student.class_id = data.new_class_id
    db.commit()

    return {
        "status": "moved",
        "student_id": student_id,
        "name": student.name,
        "from_class": old_class_name,
        "to_class": new_class.name,
    }
