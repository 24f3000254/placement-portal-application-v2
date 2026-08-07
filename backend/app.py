from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from models import Company, JobPosition, Application
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "abc123"
from extensions import db, jwt
db.init_app(app)
jwt.init_app(app)





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

from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt

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

    user_id = int (get_jwt_identity())

    user = User.query.get(user_id)

    if user.role != "student":
        return jsonify({"message":"Access denied"}),403

    jobs = JobPosition.query.filter_by(status="Active").all()

    data = []

    student = Student.query.filter_by(user_id=user.id).first()

    for job in jobs:
        company = Company.query.get(job.company_id)
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
            "company":company.company_name,
            "salary":job.salary,
            "experience":job.experience,
            "skills_required":job.skills_required,
            "deadline":job.deadline,
            "applied":applied,
            "status":status
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
        return jsonify({"message":"Access denied"}),403

    student = Student.query.filter_by(user_id=user.id).first()
    applications = Application.query.filter_by(student_id=student.id).all()
    data = []

    for application in applications:
        job = JobPosition.query.get(application.job_id)
        company = Company.query.get(job.company_id)

        data.append({
            "id":application.id,
            "job":job.title,
            "company":company.company_name,
            "status":application.status,
            "application_date":application.application_date,
            "interview_date":application.interview_date
        })
    return jsonify(data)

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
        status="Active"
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

    applications = Application.query.filter_by(job_id=job.id).all()
    data = []

    for application in applications:
        student = Student.query.get(application.student_id)
        student_user = User.query.get(student.user_id)

        item = {
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
            "status": application.status
        }
        data.append(item)

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
    application.status = data["status"]
    db.session.commit()

    return jsonify({
        "message": "Application status updated"
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

@app.route("/admin/approve-company/<int:user_id>",methods=["PUT"])
@check_role("admin")
def approve_company(user_id):
    user = User.query.get(user_id)
    if user == None:
        return jsonify({"message":"User Not Found"}),404

    user.approved = True
    db.session.commit()

    return jsonify({
        "message":"Company Approved"
    })

@app.route("/admin/reject-company/<int:user_id>",methods=["PUT"])
@check_role("admin")
def reject_company(user_id):
    user = User.query.get(user_id)

    if user == None:
        return jsonify({"message":"User Not Found"}),404

    user.active = False
    db.session.commit()

    return jsonify({
        "message":"Company Rejected"
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



if __name__ == "__main__":
    print("Placement Portal API Started")
    app.run(debug=True)