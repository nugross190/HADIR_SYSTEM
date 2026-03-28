@echo off
echo Mengorganisir struktur folder HADIR SYSTEM...

:: Membuat folder jika belum ada
if not exist models mkdir models
if not exist routers mkdir routers
if not exist services mkdir services
if not exist frontend mkdir frontend

:: Move model files
move staff.py models\
move teacher.py models\
move school.py models\
move schedule.py models\
move attendance.py models\
move __init__.py models\

:: Move router files
move auth.py routers\
move totp.py routers\

:: Copy special router file
copy "mnt\user-data\outputs\hadir\routers\attendance.py" routers\

:: Create empty __init__.py
type nul > routers\__init__.py
type nul > services\__init__.py

:: Move service files
move auth_service.py services\
move totp_service.py services\
move attendance_service.py services\

:: Move frontend files
move index.html frontend\
move display.html frontend\

:: Clean up junk
rd /s /q mnt
rd /s /q __pycache__
del Aplikasi_jadwal_upd.xlsx

echo Selesai! Struktur folder sudah rapi.
pause