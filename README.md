# HADIR System — Backend

**Hadirkan Administrasi Digital untuk Institusi dan Rekap**

School attendance recording system for SMAN 5 Garut.
3 admin staff record teacher + student attendance across 24-36 classes.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure PostgreSQL is running with database 'hadir'
#    User: hadir_user / Password: hadir123

# 3. Seed the database
python seed.py

# 4. Run the server
uvicorn main:app --reload
```

## Project Structure

```
hadir/
├── config.py              # Database URL, constants, statuses
├── database.py            # SQLAlchemy engine + session
├── main.py                # FastAPI entry point
├── seed.py                # Creates tables + loads seed data
├── requirements.txt
│
├── models/
│   ├── __init__.py        # Imports all models
│   ├── staff.py           # Admin staff (3 operators)
│   ├── teacher.py         # Teachers (67, from Kode Guru)
│   ├── school.py          # Class + Student
│   ├── schedule.py        # ScheduleSlot (795 weekly slots)
│   └── attendance.py      # QRToken, RecordingSession,
│                          # AttendanceSession, TeacherRecord,
│                          # StudentRecord
│
├── seed_data/
│   ├── teachers.json      # 67 teachers from parse_hadir_data.py
│   └── schedule.json      # 795 slots from parse_hadir_data.py
│
├── services/              # Business logic (next phase)
└── routers/               # API routes (next phase)
```

## Data Flow

```
Staff (admin) --[TOTP verify]--> RecordingSession
                                      |
                        AttendanceSession (per slot per date)
                           /                    \
              TeacherAttendanceRecord    StudentAttendanceRecord (x35)
                   (1 per session)         (1 per student)
```

## Seed Data Summary

| Entity         | Count | Source                    |
|----------------|-------|---------------------------|
| Staff          | 3     | Hardcoded (admin 1-3)     |
| Teachers       | 67    | teachers.json             |
| Classes        | 36    | Extracted from schedule   |
| Schedule Slots | 795   | schedule.json             |
| Students       | TBD   | Need roster file          |

## Next Steps

1. Student roster seed (from e-RAPOR or Excel)
2. TOTP token generation service
3. Recording session API routes
4. Attendance recording API (teacher + student)
5. Dashboard / reporting queries
