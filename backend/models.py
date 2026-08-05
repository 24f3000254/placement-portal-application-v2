from extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    student = db.relationship("Student", backref="user", uselist=False)
    company = db.relationship("Company", backref="user", uselist=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    education = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    year = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    resume = db.Column(db.String(200))
    applications = db.relationship("Application", backref="student")


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    company_name = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    website = db.Column(db.String(100))
    hr_contact = db.Column(db.String(100))
    jobs = db.relationship("JobPosition", backref="company")



class JobPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    salary = db.Column(db.Integer)
    experience = db.Column(db.String(100))
    skills_required = db.Column(db.String(200))
    deadline = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Pending")
    applications = db.relationship("Application", backref="job")


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    job_id = db.Column(db.Integer, db.ForeignKey("job_position.id"))
    status = db.Column(db.String(30), default="Applied")
    application_date = db.Column(db.String(50))


class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    job_id = db.Column(db.Integer, db.ForeignKey("job_position.id"))
    salary = db.Column(db.Integer)
    joining_date = db.Column(db.String(50))