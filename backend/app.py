from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "abc123"
from extensions import db, jwt
db.init_app(app)
jwt.init_app(app)

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


@app.route("/student/register",methods=["POST"])
def student_register():
    data=request.json
    user=User.query.filter_by(email=data["email"]).first()
    if user:
        return jsonify({"message":"Email already exists"})

    new_user=User(
        name=data["name"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role="student",
        approved=True,
        active=True
    )

    db.session.add(new_user)
    db.session.commit()


    student=Student(
        user_id=new_user.id,
        education=data["education"],
        branch=data["branch"],
        year=data["year"],
        cgpa=data["cgpa"],
        skills=data["skills"]
    )

    db.session.add(student)
    db.session.commit()
    return jsonify({"message":"Student Registered Successfully"})

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


    token=create_access_token(
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

@app.route("/student/dashboard")
@check_role("student")
def student_dashboard():
    user_id=get_jwt_identity()
    return {
        "message":"Welcome Student",
        "user_id":user_id
    }

@app.route("/company/dashboard")
@check_role("company")
def company_dashboard():
    user_id=get_jwt_identity()

    return {
        "message":"Welcome Company",
        "user_id":user_id
    }


@app.route("/profile")
@jwt_required()
def profile():

    user_id = get_jwt_identity()
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