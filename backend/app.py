from flask import Flask, send_file, send_from_directory
import os
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import Company, JobPosition, Application
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "placement_portal_secret_key_2026_harsh_123456"
from extensions import db, jwt
db.init_app(app)
jwt.init_app(app)

from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_access_token



@jwt.invalid_token_loader
def invalid_token_callback(error):
    print("INVALID TOKEN:", error)
    return jsonify({"message": error}), 422


@jwt.unauthorized_loader
def missing_token_callback(error):
    print("MISSING TOKEN:", error)
    return jsonify({"message": error}), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print("TOKEN EXPIRED")
    return jsonify({"message": "Token expired"}), 401

CORS(app)

from models import *
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import request
from flask import jsonify
from datetime import timedelta

def check_role(role_name):
    def inside(fn):
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims["role"] != role_name:
                return jsonify({"message":"Access Denied"}),403
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return inside

@app.route("/")
def home():
    return "Placement Portal API Running"


@app.route("/student/register", methods=["POST"])
def student_register():

    data = request.json

    user = User.query.filter_by(email=data["email"]).first()

    if user:
        return jsonify({"message":"Email already exists"}),400

    new_user = User(
        name=data["name"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role="student",
        approved=True,
        active=True
    )

    db.session.add(new_user)
    db.session.flush()

    student = Student(
        user_id=new_user.id
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({"message":"Student Registered Successfully"})

@app.route("/student/jobs", methods=["GET"])
@jwt_required()
def student_jobs():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != "student":
        return jsonify({"message":"Access denied"}),403
    student = Student.query.filter_by(user_id=user.id).first()
    search = request.args.get("search","")
    jobs = JobPosition.query.filter_by(status="Active").all()
    data = []

    for job in jobs:
        company = Company.query.get(job.company_id)
        text = (
            job.title + " " +
            job.skills_required + " " +
            company.company_name
        ).lower()

        if search.lower() not in text:
            continue

        application = Application.query.filter_by(
            student_id=student.id,
            job_id=job.id
        ).first()
        applied = False
        status = ""

        if application:
            applied = True
            status = application.status

        data.append({
            "id":job.id,
            "title":job.title,
            "description":job.description,
            "company":company.company_name,
            "salary":job.salary,
            "experience":job.experience,
            "skills_required":job.skills_required,
            "benefits":job.benefits,
            "deadline":job.deadline,
            "status":job.status,
            "applied":applied,
            "application_status":status
        })
    return jsonify(data)

@app.route("/student/apply/<int:job_id>", methods=["POST"])
@jwt_required()
def apply_job(job_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != "student":
        return jsonify({"message":"Access denied"}),403

    student = Student.query.filter_by(user_id=user.id).first()
    job = JobPosition.query.get(job_id)
    if job is None:
        return jsonify({"message":"Job not found"}),404

    if job.status != "Active":
        return jsonify({
            "message": "This job is not approved or active"
        }), 400

    check = Application.query.filter_by(
        student_id=student.id,
        job_id=job.id
    ).first()

    if check:
        return jsonify({"message":"Already Applied"}),400

    application = Application(
        student_id=student.id,
        job_id=job.id,
        status="Applied",
        application_date=datetime.now().strftime("%d-%m-%Y")
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({
        "message":"Application Submitted"
    }),201

@app.route("/student/applications", methods=["GET"])
@jwt_required()
def my_applications():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "student":
        return jsonify({"message": "Access denied"}), 403

    student = Student.query.filter_by(user_id=user.id).first()
    applications = Application.query.filter_by(
        student_id=student.id
    ).all()

    data = []

    for application in applications:
        job = JobPosition.query.get(application.job_id)
        if job is None:
            continue

        company = Company.query.get(job.company_id)
        data.append({
            "id": application.id,
            "job_id": job.id,
            "job": job.title,
            "company": company.company_name,
            "salary": job.salary,
            "status": application.status,
            "application_date": application.application_date,
            "interview_date": application.interview_date,
            "feedback": application.feedback
        })

    return jsonify(data)


@app.route("/student/export-applications", methods=["POST"])
@jwt_required()
def export_student_applications():

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "student":
        return jsonify({"message": "Access denied"}), 403

    student = Student.query.filter_by(
        user_id=user.id
    ).first()

    from celery_app import celery

    task = celery.send_task(
        "tasks.export_student_csv",
        args=[student.id]
    )

    return jsonify({
        "message": "CSV export started",
        "task_id": task.id
    })

@app.route("/student/placements", methods=["GET"])
@jwt_required()
def student_placements():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "student":
        return jsonify({"message": "Access denied"}), 403

    student = Student.query.filter_by(user_id=user.id).first()
    placements = Placement.query.filter_by(
        student_id=student.id
    ).all()
    data = []
    for placement in placements:
        company = Company.query.get(placement.company_id)
        job = JobPosition.query.get(placement.job_id)
        data.append({
            "id": placement.id,
            "company": company.company_name,
            "job": job.title,
            "salary": placement.salary,
            "joining_date": placement.joining_date,
            "status": "Placed"
        })
    return jsonify(data)

@app.route("/student/placement/<int:placement_id>/download", methods=["GET"])
@jwt_required()
def download_placement(placement_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "student":
        return jsonify({"message":"Access denied"}),403

    student = Student.query.filter_by(user_id=user.id).first()
    placement = Placement.query.filter_by(
        id=placement_id,
        student_id=student.id
    ).first()

    if placement is None:
        return jsonify({
            "message":"Placement not found"
        }),404

    company = Company.query.get(placement.company_id)
    job = JobPosition.query.get(placement.job_id)

    text = "PLACEMENT CONFIRMATION\n\n"
    text += "Student Name: " + user.name + "\n"
    text += "Student Email: " + user.email + "\n"
    text += "Company: " + company.company_name + "\n"
    text += "Job Position: " + job.title + "\n"
    text += "Salary Package: " + str(placement.salary) + "\n"
    text += "Joining Date: " + str(placement.joining_date) + "\n"
    text += "Status: Placed\n"

    file_data = BytesIO(text.encode("utf-8"))

    return send_file(
        file_data,
        as_attachment=True,
        download_name="placement_confirmation.txt",
        mimetype="text/plain"
    )

@app.route("/student/profile", methods=["GET"])
@jwt_required()
def student_profile():

    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)

    if user.role != "student":
        return jsonify({"message":"Access denied"}),403

    student = Student.query.filter_by(user_id=user.id).first()

    return jsonify({
        "name":user.name,
        "email":user.email,
        "education":student.education,
        "branch":student.branch,
        "year":student.year,
        "cgpa":student.cgpa,
        "skills":student.skills,
        "experience":student.experience,
        "resume":student.resume
    })


@app.route("/student/profile", methods=["PUT"])
@jwt_required()
def update_student_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role != "student":
        return jsonify({"message":"Access denied"}),403

    student = Student.query.filter_by(user_id=user.id).first()
    data = request.get_json()
    user.name = data.get("name",user.name)

    student.education = data.get(
        "education",
        student.education
    )

    student.branch = data.get(
        "branch",
        student.branch
    )

    student.year = data.get(
        "year",
        student.year
    )

    student.cgpa = data.get(
        "cgpa",
        student.cgpa
    )

    student.skills = data.get(
        "skills",
        student.skills
    )

    student.experience = data.get(
        "experience",
        student.experience
    )
    db.session.commit()
    return jsonify({
        "message":"Profile Updated"
    })


@app.route("/student/resume", methods=["POST"])
@jwt_required()
def upload_resume():

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "student":
        return jsonify({
            "message":"Access denied"
        }),403

    student = Student.query.filter_by(
        user_id=user.id
    ).first()

    if "resume" not in request.files:
        return jsonify({
            "message":"Resume file is required"
        }),400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({
            "message":"Select a resume"
        }),400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "message":"Only PDF files are allowed"
        }),400

    filename = "student_" + str(student.id) + ".pdf"

    file.save("resumes/" + filename)

    student.resume = filename

    db.session.commit()

    return jsonify({
        "message":"Resume uploaded successfully",
        "resume":filename
    })

@app.route("/student/resume/<filename>", methods=["GET"])
@jwt_required()
def view_resume(filename):

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "student":
        return jsonify({
            "message":"Access denied"
        }),403

    student = Student.query.filter_by(
        user_id=user.id
    ).first()

    if student.resume != filename:
        return jsonify({
            "message":"Resume not found"
        }),404

    return send_from_directory(
        "resumes",
        filename
    )


@app.route("/company/resume/<filename>", methods=["GET"])
@jwt_required()
def company_view_resume(filename):

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "company":
        return jsonify({
            "message":"Access denied"
        }),403

    company = Company.query.filter_by(
        user_id=user.id
    ).first()

    applications = Application.query.all()

    allowed = False

    for application in applications:

        student = Student.query.get(application.student_id)

        job = JobPosition.query.get(application.job_id)

        if student and job:
            if student.resume == filename and job.company_id == company.id:
                allowed = True
                break

    if not allowed:
        return jsonify({
            "message":"Resume not found"
        }),404

    return send_from_directory(
        "resumes",
        filename
    )




@app.route("/company/register",methods=["POST"])
def company_register():
    data=request.json
    user=User.query.filter_by(email=data["email"]).first()
    if user:
        return jsonify({"message":"Email already exists"})


    new_user=User(
        name=data["company_name"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role="company",
        approved=False,

        active=True
    )

    db.session.add(new_user)
    db.session.commit()


    company=Company(
        user_id=new_user.id,
        company_name=data["company_name"],

        industry=data["industry"],
        location=data["location"],
        website=data["website"],
        hr_contact=data["hr_contact"]
    )

    db.session.add(company)
    db.session.commit()
    return jsonify({"message":"Company Registered. Wait For Approval"})

@app.route("/company/jobs", methods=["GET"])
@jwt_required()
def company_jobs():

    identity = int (get_jwt_identity())

    user = User.query.get(identity)

    if user.role != "company":
        return jsonify({"message": "Access denied"}), 403

    company = Company.query.filter_by(user_id=user.id).first()

    if company is None:
        return jsonify({"message": "Company not found"}), 404

    jobs = JobPosition.query.filter_by(company_id=company.id).all()

    data = []

    for job in jobs:
        total = Application.query.filter_by(job_id=job.id).count()
        item = {
            "id": job.id,
            "title": job.title,
            "salary": job.salary,
            "experience": job.experience,
            "skills_required": job.skills_required,
            "deadline": job.deadline,
            "status": job.status,
            "applications": total
        }
        data.append(item)

    return jsonify(data)

@app.route("/company/jobs", methods=["POST"])
@jwt_required()
def create_company_job():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "company":
        return jsonify({"message": "Access denied"}), 403

    company = Company.query.filter_by(user_id=user.id).first()

    if user.approved == False:
        return jsonify({
            "message":"Company is not approved by admin"
        }),403

    if company is None:
        return jsonify({"message": "Company not found"}), 404
    data = request.get_json()
    job = JobPosition(
        company_id=company.id,
        title=data["title"],
        description=data["description"],
        salary=data["salary"],
        experience=data["experience"],
        skills_required=data["skills_required"],
        benefits=data["benefits"],
        deadline=data["deadline"],
        status="Pending"
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({
        "message": "Job created successfully"
    }), 201

@app.route("/company/jobs/<int:job_id>/applications", methods=["GET"])
@jwt_required()
def company_job_applications(job_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "company":
        return jsonify({"message": "Access denied"}), 403

    company = Company.query.filter_by(user_id=user.id).first()
    job = JobPosition.query.filter_by(
        id=job_id,
        company_id=company.id
    ).first()

    if job is None:
        return jsonify({"message": "Job not found"}), 404

    applications = Application.query.filter_by(
        job_id=job.id
    ).all()

    data = []

    for application in applications:
        student = Student.query.get(application.student_id)
        student_user = User.query.get(student.user_id)
        data.append({
            "application_id": application.id,
            "student_id": student.id,
            "name": student_user.name,
            "email": student_user.email,
            "education": student.education,
            "branch": student.branch,
            "year": student.year,
            "cgpa": student.cgpa,
            "skills": student.skills,
            "experience": student.experience,
            "resume": student.resume,
            "status": application.status,
            "application_date": application.application_date,
            "interview_date": application.interview_date,
            "feedback": application.feedback
        })
    return jsonify(data)

@app.route("/company/application/<int:application_id>", methods=["PUT"])
@jwt_required()
def update_application_status(application_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "company":
        return jsonify({"message": "Access denied"}), 403

    company = Company.query.filter_by(user_id=user.id).first()
    application = Application.query.get(application_id)

    if application is None:
        return jsonify({"message": "Application not found"}), 404

    job = JobPosition.query.get(application.job_id)
    if job.company_id != company.id:
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json()
    status = data.get("status")
    feedback = data.get("feedback", "")
    allowed_status = [
    "Applied",
    "Shortlisted",
    "Interview",
    "Offer",
    "Rejected",
    "Selected",
    "Placed"
    ]

    if status not in allowed_status:
        return jsonify({
            "message": "Invalid application status"
        }), 400

    application.status = status
    application.feedback = feedback
    db.session.commit()

    return jsonify({
        "message": "Application status updated",
        "status": application.status,
        "feedback": application.feedback
    })

@app.route("/company/application/<int:application_id>/place", methods=["POST"])
@jwt_required()
def place_student(application_id):

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "company":
        return jsonify({"message": "Access denied"}), 403

    company = Company.query.filter_by(user_id=user.id).first()

    application = Application.query.get(application_id)

    if application is None:
        return jsonify({"message": "Application not found"}), 404

    job = JobPosition.query.get(application.job_id)

    if job.company_id != company.id:
        return jsonify({"message": "Access denied"}), 403

    if application.status != "Selected":
        return jsonify({
            "message": "Only selected students can be placed"
        }), 400

    old_placement = Placement.query.filter_by(
        student_id=application.student_id,
        job_id=application.job_id
    ).first()

    if old_placement:
        return jsonify({
            "message": "Student is already placed"
        }), 400

    data = request.get_json()

    placement = Placement(
        student_id=application.student_id,
        company_id=company.id,
        job_id=job.id,
        salary=data["salary"],
        joining_date=data["joining_date"]
    )

    db.session.add(placement)

    application.status = "Placed"

    db.session.commit()

    return jsonify({
        "message": "Student placed successfully"
    })

@app.route("/company/job/<int:job_id>/status", methods=["PUT"])
@jwt_required()
def update_job_status(job_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "company":
        return jsonify({"message": "Access denied"}), 403

    company = Company.query.filter_by(user_id=user.id).first()
    job = JobPosition.query.filter_by(
        id=job_id,
        company_id=company.id
    ).first()

    if job is None:
        return jsonify({"message": "Job not found"}), 404

    data = request.get_json()
    job.status = data["status"]
    db.session.commit()

    return jsonify({
        "message": "Job status updated"
    })

@app.route("/company/application/<int:application_id>/interview", methods=["PUT"])
@jwt_required()
def schedule_interview(application_id):
    user_id =int (get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "company":
        return jsonify({"message": "Access denied"}), 403

    company = Company.query.filter_by(user_id=user.id).first()
    application = Application.query.get(application_id)

    if application is None:
        return jsonify({"message": "Application not found"}), 404

    job = JobPosition.query.get(application.job_id)

    if job.company_id != company.id:
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json()
    application.interview_date = data["interview_date"]
    application.status = "Interview"
    db.session.commit()

    return jsonify({
        "message": "Interview scheduled successfully"
    })


@app.route("/company/export-applications", methods=["POST"])
@jwt_required()
def export_company_applications():

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "company":
        return jsonify({"message": "Access denied"}), 403

    company = Company.query.filter_by(
        user_id=user.id
    ).first()

    if company is None:
        return jsonify({"message": "Company not found"}), 404

    from celery_app import celery

    task = celery.send_task(
        "tasks.export_company_csv",
        args=[company.id]
    )

    return jsonify({
        "message": "CSV export started",
        "task_id": task.id
    })

@app.route("/company/dashboard", methods=["GET"])
@jwt_required()
def company_dashboard():
    user_id = int(get_jwt_identity())


    user = User.query.get(user_id)

    if user.role != "company":
        return jsonify({"message": "Access denied"}), 403

    company = Company.query.filter_by(user_id=user.id).first()

    if company is None:
        return jsonify({"message": "Company not found"}), 404

    jobs = JobPosition.query.filter_by(company_id=company.id).all()
    total_jobs = len(jobs)
    total_applications = 0
    shortlisted = 0
    selected = 0

    for job in jobs:
        applications = Application.query.filter_by(job_id=job.id).all()
        total_applications += len(applications)

        for application in applications:

            if application.status == "Shortlisted":
                shortlisted += 1

            if application.status == "Selected":
                selected += 1

    data = {
        "company_name": company.company_name,
        "industry": company.industry,
        "location": company.location,
        "website": company.website,
        "hr_contact": company.hr_contact,
        "total_jobs": total_jobs,
        
        "total_applications": total_applications,
        "shortlisted": shortlisted,
        "selected": selected
    }
    return jsonify(data)


@app.route("/login",methods=["POST"])
def login():
    data=request.json

    user=User.query.filter_by(email=data["email"]).first()
    if user==None:
        return jsonify({"message":"Email not found"})


    if check_password_hash(user.password,data["password"])==False:
        return jsonify({"message":"Wrong Password"})


    if user.active==False:
        return jsonify({"message":"Account Disabled"})


    if user.role=="company":
        if user.approved==False:

            return jsonify({"message":"Company Not Approved"})


    token = create_access_token(
    identity=str(user.id),
    additional_claims={"role":user.role},
    expires_delta=timedelta(days=1)
    )

    return jsonify({

    "message":"Login Successful",

    "token":token,

    "id":user.id,

    "role":user.role,

    "name":user.name
    })

@app.route("/admin/dashboard")
@check_role("admin")
def admin_dashboard():   
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_jobs = JobPosition.query.count()
    total_applications = Application.query.count()

    return {
        "students":total_students,
        "companies":total_companies,
        "jobs":total_jobs,
        "applications":total_applications
    }

@app.route("/admin/companies")
@check_role("admin")
def admin_companies():
    companies = Company.query.all()
    data = []
    for company in companies:
        user = User.query.get(company.user_id)
        data.append({
            "id":company.id,
            "user_id":user.id,
            "company_name":company.company_name,
            "industry":company.industry,
            "location":company.location,
            "approved":user.approved
        })

    return jsonify(data)

@app.route("/admin/students")
@check_role("admin")
def admin_students():
    students = Student.query.all()
    data = []
    for student in students:
        user = User.query.get(student.user_id)

        data.append({
            "id": student.id,
            "name": user.name,
            "email": user.email,
            "education": student.education,
            "branch": student.branch,
            "year": student.year,
            "cgpa": student.cgpa
        })
    return jsonify(data)

@app.route("/admin/jobs")
@check_role("admin")
def admin_jobs():
    jobs = JobPosition.query.all()
    data = []
    for job in jobs:
        company = Company.query.get(job.company_id)
        data.append({
            "id": job.id,
            "title": job.title,
            "experience": job.experience,
            "salary": job.salary,
            "status": job.status,
            "company": company.company_name
        })
    return jsonify(data)

@app.route("/admin/applications")
@check_role("admin")
def admin_applications():
    applications = Application.query.all()
    data = []

    for application in applications:
        student = Student.query.get(application.student_id)
        user = User.query.get(student.user_id)
        job = JobPosition.query.get(application.job_id)
        company = Company.query.get(job.company_id)
        data.append({
            "id": application.id,
            "student": user.name,
            "company": company.company_name,
            "job": job.title,
            "status": application.status
        })
    return jsonify(data)

@app.route("/admin/placements")
@check_role("admin")
def admin_placements():
    placements = Placement.query.all()
    data = []

    for placement in placements:
        student = Student.query.get(placement.student_id)
        user = User.query.get(student.user_id)
        company = Company.query.get(placement.company_id)
        job = JobPosition.query.get(placement.job_id)

        data.append({
            "id": placement.id,
            "student": user.name,
            "email": user.email,
            "company": company.company_name,
            "job": job.title,
            "salary": placement.salary,
            "joining_date": placement.joining_date
        })

    return jsonify(data)


@app.route("/admin/approve-company/<int:user_id>", methods=["PUT"])
@jwt_required()
def approve_company(user_id):
    user_id2 = int(get_jwt_identity())
    admin = User.query.get(user_id2)
    if admin.role != "admin":
        return jsonify({"message":"Access denied"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message":"Company not found"}), 404
    
    user.approved = True
    user.active = True
    db.session.commit()
    return jsonify({"message":"Company approved"})

@app.route("/admin/reject-company/<int:user_id>", methods=["PUT"])
@jwt_required()
def reject_company(user_id):
    user_id2 = int(get_jwt_identity())
    admin = User.query.get(user_id2)
    if admin.role != "admin":
        return jsonify({"message":"Access denied"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message":"Company not found"}), 404

    user.approved = False
    user.active = False
    db.session.commit()
    return jsonify({"message":"Company rejected"})

@app.route("/admin/approve-job/<int:job_id>", methods=["PUT"])
@jwt_required()
def approve_job(job_id):

    user_id = int(get_jwt_identity())

    admin = User.query.get(user_id)

    if admin.role != "admin":
        return jsonify({
            "message":"Access denied"
        }),403

    job = JobPosition.query.get(job_id)

    if job is None:
        return jsonify({
            "message":"Job not found"
        }),404

    company = Company.query.get(job.company_id)
    company_user = User.query.get(company.user_id)

    if company_user.approved == False:
        return jsonify({
            "message":"Company is not approved"
        }),400

    job.status = "Active"

    db.session.commit()

    return jsonify({
        "message":"Job approved"
    })


@app.route("/admin/reject-job/<int:job_id>", methods=["PUT"])
@jwt_required()
def reject_job(job_id):
    user_id = int(get_jwt_identity())
    admin = User.query.get(user_id)

    if admin.role != "admin":
        return jsonify({
            "message":"Access denied"
        }),403

    job = JobPosition.query.get(job_id)

    if job is None:
        return jsonify({
            "message":"Job not found"
        }),404

    job.status = "Rejected"
    db.session.commit()

    return jsonify({
        "message":"Job rejected"
    })


@app.route("/student/dashboard")
@check_role("student")
def student_dashboard():
    user_id=int(get_jwt_identity())
    return {
        "message":"Welcome Student",
        "user_id":user_id
    }


@app.route("/profile")
@jwt_required()
def profile():

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user == None:
        return jsonify({"message":"User Not Found"}),404

    return jsonify({
        "id":user.id,
        "name":user.name,
        "email":user.email,
        "role":user.role
    })   

@app.route("/logout",methods=["POST"])
@jwt_required()
def logout():
    return jsonify({
        "message":"Logout Successful"
    })

@app.route("/export-status/<task_id>", methods=["GET"])
@jwt_required()
def export_status(task_id):

    from celery_app import celery

    task = celery.AsyncResult(task_id)

    if task.state == "SUCCESS":

        return jsonify({
            "status": "SUCCESS",
            "message": "CSV export completed"
        })

    if task.state == "FAILURE":

        return jsonify({
            "status": "FAILURE",
            "message": "CSV export failed"
        })

    return jsonify({
        "status": "PENDING",
        "message": "CSV export is still running"
    })


@app.route("/export-download/<task_id>", methods=["GET"])
@jwt_required()
def download_export(task_id):

    from celery_app import celery

    task = celery.AsyncResult(task_id)

    if task.state != "SUCCESS":
        return jsonify({
            "message": "Export is not ready yet"
        }), 400

    file_name = task.result

    if not os.path.exists(file_name):
        return jsonify({
            "message": "Export file not found"
        }), 404

    return send_file(
        file_name,
        as_attachment=True,
        download_name="placement_export.csv",
        mimetype="text/csv"
    )


if __name__ == "__main__":
    print("Placement Portal API Started")
    app.run(debug=True)