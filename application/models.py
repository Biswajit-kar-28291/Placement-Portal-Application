from .database import db
# from datetime import date

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    role = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    student = db.relationship("Student", backref="user", uselist=False)
    company = db.relationship("Company", backref="user",uselist=False)


class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    department = db.Column(db.String(),nullable=False)
    resume = db.Column(db.String(), nullable=True)
    approval_status = db.Column(db.String(), nullable=False, default="approve")
    applications = db.relationship("Application", backref="student")

class Company(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    hr_contact = db.Column(db.String(), nullable=False)
    approval_status = db.Column(db.String(), nullable=False, default="pending")
    website = db.Column(db.String())
    drives = db.relationship("Drive", backref="company")
    applications = db.relationship("Application", backref="company")


class Drive(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    name=db.Column(db.String(), nullable=False)
    job_title = db.Column(db.String(), nullable=False)
    job_description = db.Column(db.Text,nullable=False)
    eligible_criteria = db.Column(db.Text,nullable=False)
    application_deadline = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False, default="ongoing")
    salary = db.Column(db.String(),nullable=False)
    location = db.Column(db.String(), nullable=False)
    applications = db.relationship("Application", backref="drive")


class Application(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("drive.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    application_date = db.Column(db.Date)
    status = db.Column(db.String(), nullable=False, default="Applied")
