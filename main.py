from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import shutil
import uuid

# -----------------------------------
# Load Environment Variables
# -----------------------------------

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ Supabase credentials missing")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------------
# FastAPI App
# -----------------------------------

app = FastAPI(title="Hostel Management API")

# Serve uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# -----------------------------------
# Models
# -----------------------------------

class Student(BaseModel):
    name: str
    email: EmailStr
    room_no: int


class Complaint(BaseModel):
    student_id: int
    message: str


class UpdateFees(BaseModel):
    student_id: int
    fees_status: str


# -----------------------------------
# Root API
# -----------------------------------

@app.get("/")
def home():
    return {"message": "🏠 Hostel Backend Running Successfully"}


# -----------------------------------
# Add Student (without image)
# -----------------------------------

@app.post("/add-student")
def add_student(student: Student):
    try:
        data = {
            "name": student.name,
            "email": student.email,
            "room_no": student.room_no,
            "fees_status": "Pending"
        }

        response = supabase.table("students").insert(data).execute()

        return {"status": "success", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------
# Add Student WITH Image
# -----------------------------------

@app.post("/add-student-with-image")
def add_student_with_image(
    name: str = Form(...),
    email: str = Form(...),
    room_no: int = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Unique filename
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = f"uploads/{filename}"

        # Save image
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Save to database
        data = {
            "name": name,
            "email": email,
            "room_no": room_no,
            "fees_status": "Pending",
            "image": file_path
        }

        response = supabase.table("students").insert(data).execute()

        return {
            "status": "success",
            "image_url": f"http://127.0.0.1:8000/{file_path}",
            "data": response.data
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------
# Get All Students
# -----------------------------------

@app.get("/get-students")
def get_students():
    try:
        response = supabase.table("students").select("*").execute()
        return {"status": "success", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------
# Get Students by Room
# -----------------------------------

@app.get("/students-by-room/{room_no}")
def students_by_room(room_no: int):
    try:
        response = (
            supabase.table("students")
            .select("*")
            .eq("room_no", room_no)
            .execute()
        )

        return {"status": "success", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------
# Update Fees Status
# -----------------------------------

@app.put("/update-fees")
def update_fees(data: UpdateFees):
    try:
        response = (
            supabase.table("students")
            .update({"fees_status": data.fees_status})
            .eq("id", data.student_id)
            .execute()
        )

        return {"status": "updated", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------
# Delete Student
# -----------------------------------

@app.delete("/delete-student/{student_id}")
def delete_student(student_id: int):
    try:
        response = (
            supabase.table("students")
            .delete()
            .eq("id", student_id)
            .execute()
        )

        return {"status": "deleted", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------
# Add Complaint
# -----------------------------------

@app.post("/add-complaint")
def add_complaint(complaint: Complaint):
    try:
        data = {
            "student_id": complaint.student_id,
            "message": complaint.message,
            "status": "Open"
        }

        response = supabase.table("complaints").insert(data).execute()

        return {"status": "success", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------
# Get All Complaints
# -----------------------------------

@app.get("/get-complaints")
def get_complaints():
    try:
        response = supabase.table("complaints").select("*").execute()
        return {"status": "success", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------
# Update Complaint Status
# -----------------------------------

@app.put("/update-complaint/{complaint_id}")
def update_complaint(complaint_id: int, status: str):
    try:
        response = (
            supabase.table("complaints")
            .update({"status": status})
            .eq("id", complaint_id)
            .execute()
        )

        return {"status": "updated", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))