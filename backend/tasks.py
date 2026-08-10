from celery_app import celery
from app import app
from models import User, Student, Company, JobPosition, Application, Placement
from datetime import datetime, timedelta
import os
import csv


@celery.task
def interview_reminder():

    with app.app_context():

        applications = Application.query.filter(
            Application.interview_date.isnot(None)
        ).all()

        for application in applications:

            if application.interview_date == "":
                continue

            try:
                interview_time = datetime.strptime(
                    application.interview_date,
                    "%Y-%m-%d"
                )
            except:
                try:
                    interview_time = datetime.strptime(
                        application.interview_date,
                        "%Y-%m-%dT%H:%M"
                    )
                except:
                    try:
                        interview_time = datetime.strptime(
                            application.interview_date,
                            "%Y-%m-%d %H:%M"
                        )
                    except:
                        continue

            now = datetime.now()

            if now.date() <= interview_time.date() <= (now + timedelta(hours=24)).date():

                student = Student.query.get(application.student_id)

                if student:
                    user = User.query.get(student.user_id)

                    print(
                        "INTERVIEW REMINDER:",
                        user.name,
                        user.email,
                        application.interview_date
                    )

    return "Interview reminder task completed"


@celery.task
def monthly_placement_report():

    with app.app_context():

        students = Student.query.count()
        companies = Company.query.count()
        jobs = JobPosition.query.count()
        applications = Application.query.count()
        interviews = Application.query.filter_by(
            status="Interview"
        ).count()
        placements = Placement.query.count()

        report = """
        <html>
        <head>
            <title>Monthly Placement Report</title>
        </head>

        <body>

        <h1>Monthly Placement Report</h1>

        <h2>Summary</h2>

        <p>Total Students: {}</p>
        <p>Total Companies: {}</p>
        <p>Total Jobs: {}</p>
        <p>Total Applications: {}</p>
        <p>Total Interviews: {}</p>
        <p>Total Placements: {}</p>

        <h2>Placement Details</h2>

        <table border="1" cellpadding="8">

        <tr>
            <th>Student</th>
            <th>Company</th>
            <th>Job</th>
            <th>Salary</th>
            <th>Joining Date</th>
        </tr>

        """.format(
            students,
            companies,
            jobs,
            applications,
            interviews,
            placements
        )

        all_placements = Placement.query.all()

        for placement in all_placements:

            student = Student.query.get(placement.student_id)
            user = User.query.get(student.user_id)

            company = Company.query.get(
                placement.company_id
            )

            job = JobPosition.query.get(
                placement.job_id
            )

            report += """
            <tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>
            """.format(
                user.name,
                company.company_name,
                job.title,
                placement.salary,
                placement.joining_date
            )

        report += """
        </table>

        </body>
        </html>
        """

        if not os.path.exists("reports"):
            os.makedirs("reports")

        file_name = "reports/monthly_placement_report.html"

        with open(file_name, "w", encoding="utf-8") as file:
            file.write(report)

        print("Monthly placement report generated")

        return "Monthly placement report generated"


@celery.task
def export_student_csv(student_id):

    with app.app_context():

        student = Student.query.get(student_id)

        if student is None:
            return "Student not found"

        if not os.path.exists("exports"):
            os.makedirs("exports")

        file_name = "exports/student_" + str(student_id) + "_applications.csv"

        applications = Application.query.filter_by(
            student_id=student_id
        ).all()

        with open(file_name, "w", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Company",
                "Job",
                "Salary",
                "Status",
                "Application Date",
                "Interview Date"
            ])

            for application in applications:

                job = JobPosition.query.get(application.job_id)
                company = Company.query.get(job.company_id)

                writer.writerow([
                    company.company_name,
                    job.title,
                    job.salary,
                    application.status,
                    application.application_date,
                    application.interview_date
                ])

        print("Student CSV export completed")

        return file_name


@celery.task
def export_company_csv(company_id):

    with app.app_context():

        company = Company.query.get(company_id)

        if company is None:
            return "Company not found"

        if not os.path.exists("exports"):
            os.makedirs("exports")

        file_name = "exports/company_" + str(company_id) + "_applications.csv"

        jobs = JobPosition.query.filter_by(
            company_id=company_id
        ).all()

        with open(file_name, "w", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Student",
                "Email",
                "Job",
                "Status",
                "Application Date",
                "Interview Date",
                "Feedback"
            ])

            for job in jobs:

                applications = Application.query.filter_by(
                    job_id=job.id
                ).all()

                for application in applications:

                    student = Student.query.get(
                        application.student_id
                    )

                    user = User.query.get(
                        student.user_id
                    )

                    writer.writerow([
                        user.name,
                        user.email,
                        job.title,
                        application.status,
                        application.application_date,
                        application.interview_date,
                        application.feedback
                    ])

        print("Company CSV export completed")

        return file_name