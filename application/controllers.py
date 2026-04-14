from flask import Flask,render_template,request,redirect
from datetime import date
import os
from werkzeug.utils import secure_filename
from flask import current_app as app
from .models import *
from flask import send_from_directory

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get ("username")
        password= request.form.get("password")
        this_user=User.query.filter_by(username=username).first()
        if this_user:
            if password==this_user.password:
                if this_user.role=="admin":
                    return redirect("/admin")
                elif this_user.role=="company":
                    if this_user.company and this_user.company.approval_status == "approve":
                        return redirect(f"/company/{this_user.id}")
                    else:
                        return render_template("wait_company.html", user=this_user.company)
                else:
                    if this_user.student and this_user.student.approval_status == "approve":
                        return redirect(f"/student/{this_user.id}")
                    else:
                        return render_template("wait_student.html", user=this_user.student)
            else:
                return render_template("p_incorrect.html")
        else:
            return render_template("u_does_not_exist.html")
    return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        role = request.form.get("role")

        user_name = User.query.filter_by(username=username).first()
        user_email = User.query.filter_by(email=email).first()

        if user_name or user_email:
            return render_template("u_exist.html")

        if role == "student":
            dep = request.form.get("department")
            file = request.files.get("resume")

            if not dep:
                return "<h1>Department name is required</h1>"

            if not file or file.filename == "":
                return "<h1>Resume PDF is required</h1>"

            if not file.filename.endswith(".pdf"):
                return "<h1>Only PDF allowed</h1>"

            filename = secure_filename(file.filename)
            filename = username + "_" + filename
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            new_user = User(
                username=username,
                email=email,
                role=role,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()

            new_student = Student(
                user_id=new_user.id,
                name=username,
                email=email,
                department=dep,
                resume=filename
            )
            db.session.add(new_student)
            db.session.commit()

            return redirect("/login")

        else:
            hr = request.form.get("hr")
            web = request.form.get("website")

            if not hr or not web:
                return "<h1>HR and Website required</h1>"

            new_user = User(
                username=username,
                email=email,
                role=role,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()

            new_company = Company(
                user_id=new_user.id,
                name=username,
                email=email,
                hr_contact=hr,
                website=web
            )
            db.session.add(new_company)
            db.session.commit()

            return redirect("/login")

    return render_template("registration.html")

@app.route("/admin")
def admin():
    this_user=User.query.filter_by(username="Admin").first()
    student=Student.query.all()
    company=Company.query.all()
    drive=Drive.query.all()
    application=Application.query.all()
    return render_template("admin_dash.html",user=this_user,student=student,company=company,drive=drive,application=application)

@app.route("/search")
def search():
    key= request.args.get("key")
    keyword= request.args.get("keyword")
    if key=="student_n":
        result=Student.query.filter_by(name=keyword).first()
    elif key=="student_e":
        result=Student.query.filter_by(email=keyword).first()
        print(keyword,key,result.name)
    elif key=="student_i":
        result=Student.query.filter_by(id=keyword).first()
    elif key=="company_n":
        result=Company.query.filter_by(name=keyword).first()
    elif key=="company_e":
        result=Company.query.filter_by(email=keyword).first()
    elif key=="company_i":
        result=Company.query.filter_by(id=keyword).first()
    elif key=="drive":
        result=Drive.query.filter_by(name=keyword).first()
    else:
        result=None

    print(key, result)
    return render_template("search.html",result=result,key=key)


@app.route("/admin_drive_view_details/<int:id>")
def admin_drive_view_details(id):
    drive=Drive.query.filter_by(id=id).first()
    # if application.student.approval_status=="blacklist":
    #     return render_template("wait_student.html", user=application.student)
    if drive.company.approval_status=="blacklist":
        return render_template("wait_company.html", user=drive.company)

    return render_template("admin_drive_view_details.html",drive=drive)

@app.route("/complete_a/<int:id>")
def complete_a(id):
    drive=Drive.query.filter_by(id=id).first()
    if drive.company.approval_status=="blacklist":
        return render_template("wait_company.html", user=drive.company)
    drive.status="complete"
    for application in drive.applications:
        application.status="Drive Closed"
    db.session.commit()
    return redirect("/admin")


@app.route("/blacklist_copany/<int:id>")
def c_blacklist(id):
    this_user=Company.query.filter_by(id=id).first()
    this_user.approval_status="blacklist"
    for application in this_user.applications:
        application.status="c_blacklist"
    db.session.commit()
    return redirect("/admin")

@app.route("/resume/<filename>")
def view_resume(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/blacklist_student/<int:id>")
def s_blacklist(id):
    this_user=Student.query.filter_by(id=id).first()
    this_user.approval_status="blacklist"
    for application in this_user.applications:
        application.status="s_blacklist"
    db.session.commit()
    return redirect("/admin")
@app.route("/approve/<int:id>")
def approve(id):
    this_user=Company.query.filter_by(id=id).first()
    this_user.approval_status="approve"
    for application in this_user.applications:
        application.status="Applied"
    db.session.commit()
    return redirect("/admin")
@app.route("/s_approve/<int:id>")
def s_approve(id):
    this_user=Student.query.filter_by(id=id).first()
    this_user.approval_status="approve"
    for application in this_user.applications:
        application.status="Applied"
    db.session.commit()
    return redirect("/admin")


@app.route("/student_reveiw_application/<int:id>")
def student_reveiw_application(id):
    drive=Drive.query.filter_by(id=id).first()
    return render_template("student_review_application.html",drive=drive)

@app.route("/admin_view/<int:id>")
def admin_view(id):
    application=Application.query.filter_by(id=id).first()
    
    if application.student.approval_status=="blacklist":
        return render_template("wait_student.html", user=application.student)
    if application.company.approval_status=="blacklist":
        return render_template("wait_company.html", user=application.company)
    if application.student.approval_status=="pending" or application.company.approval_status=="pending":
        return render_template("u_does_not_exist.html")#dummy
    return render_template("admin_view.html",application=application)









# student only



@app.route("/student/<int:user_id>")
def student(user_id):
    this_user=Student.query.filter_by(user_id=user_id).first()
    company=Company.query.filter_by(approval_status="approve").all()
    application=Application.query.filter_by(student_id=this_user.id).all()
    if this_user.approval_status=="blacklist":
        return render_template("wait_student.html", user=this_user)
    return render_template("student_dash.html",this_user=this_user, company=company,application=application)

@app.route("/edit_profile/<int:id>", methods=["GET", "POST"])
def edit_profile(id):
    this_user = Student.query.filter_by(id=id).first()
    
    if this_user.approval_status=="blacklist":
        return render_template("wait_student.html", user=this_user)

    if request.method == "POST":
        department = request.form.get("department")
        file = request.files.get("resume")

        if department:
            this_user.department = department

        if file and file.filename != "":
            if file.filename.endswith(".pdf"):
                filename = secure_filename(file.filename)
                filename = this_user.name + "_" + filename
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)
                this_user.resume = filename
            else:
                return "<h1>Only PDF allowed</h1>"

        db.session.commit()
        return redirect(f"/student/{this_user.user_id}")

    return render_template("edit_profile.html", this_user=this_user)

@app.route("/student/history/<int:id>")
def s_history(id):
    this_user=Student.query.filter_by(id=id).first()
    
    if this_user.approval_status=="blacklist":
        return render_template("wait_student.html", user=this_user)
    return render_template("student_application_history.html",this_user=this_user)

@app.route("/view_details/<int:s_id>/<int:c_id>")
def s_view_details(s_id,c_id):
    company=Company.query.filter_by(id=c_id).first()
    student=Student.query.filter_by(id=s_id).first()
    if student.approval_status=="blacklist":
        return render_template("wait_student.html", user=student)
    if company.approval_status=="blacklist":
        return render_template("wait_company.html", user=company)
    return render_template("student_view_details.html",company=company,student=student)

@app.route("/drive_details/<int:s_id>/<int:d_id>")
def drive_details(s_id,d_id):
    drive=Drive.query.filter_by(id=d_id).first()
    student=Student.query.filter_by(id=s_id).first()
    if student.approval_status=="blacklist":
        return render_template("wait_student.html", user=student)
    if drive.company.approval_status=="blacklist":
        return render_template("wait_company.html", user=drive.company)
    return render_template("drive_details.html", drive=drive,student=student)


@app.route("/apply/<int:s_id>/<int:d_id>")
def apply(s_id,d_id):
    drive=Drive.query.filter_by(id=d_id).first()
    student=Student.query.filter_by(id=s_id).first()
    if student.approval_status=="blacklist":
        return render_template("wait_student.html", user=student)
    if drive.company.approval_status=="blacklist":
        return render_template("wait_company.html", user=drive.company)
    dt=date.today()
    app=Application.query.filter_by(student_id=s_id, drive_id=d_id).first()
    if app :
        return redirect(f"/student/application/status/{app.id}")
    application=Application(student_id=s_id,drive_id=d_id,company_id=drive.company_id,application_date=dt)
    db.session.add(application)
    db.session.commit()
    return redirect(f"/student/application/status/{application.id}")

@app.route("/student/application/status/<int:id>")
def s_application_status(id):
    application=Application.query.filter_by(id=id).first()
    if application.student.approval_status=="blacklist":
        return render_template("wait_student.html", user=application.student)
    if application.company.approval_status=="blacklist":
        return render_template("wait_company.html", user=application.company)
    return render_template("application_status.html",application=application)













# for company only


@app.route("/company/<int:user_id>")
def company(user_id):
    this_user=Company.query.filter_by(user_id=user_id).first()
    drive=Drive.query.filter_by(company_id=this_user.id).all()
    if this_user.approval_status=="blacklist":
        return render_template("wait_company.html", user=this_user)
    return render_template("company_dash.html",this_user=this_user,drive=drive)
@app.route("/company_view_details/<int:id>")
def c_view_details(id):
    application=Application.query.filter_by(drive_id=id).all()
    drive=Drive.query.filter_by(id=id).first()
    if drive.company.approval_status=="blacklist":
        return render_template("wait_company.html", user=drive.company)
    if len(application)==0:
        application=None
    return render_template("company_view_details.html",application=application, drive=drive)

@app.route("/create_drive/<int:id>",methods=["GET","POST"])
def create_drive(id):
    this_user=Company.query.filter_by(id=id).first()
    if this_user.approval_status=="blacklist":
        return render_template("wait_company.html", user=this_user)
    else:
        if request.method=="POST":
            dname=request.form.get("name")
            jt=request.form.get("jt")
            jd=request.form.get("jd")
            ec=request.form.get("ec")
            salary=request.form.get("salary")
            location=request.form.get("location")
            ad=request.form.get("ad")
            new_drive=Drive(company_id=this_user.id,name=dname,job_title=jt,job_description =jd,eligible_criteria=ec,application_deadline=ad,salary=salary,location =location )
            db.session.add(new_drive)
            db.session.commit()
            return redirect(f"/company/{this_user.user_id}")
        return render_template("create_drive.html",this_user=this_user)

# @app.route("/update_drive_d/<int:id>",methods=["GET","POST"])
# def update_drive_d(id):
#     this_drive=Drive.query.filter_by(id=id).first()
#     if this_drive.company.approval_status=="pending":
#         return render_template("u_does_not_exist.html")
#     if request.method=="POST":
#         this_drive.job_title =request.form.get("jt")
#         this_drive.job_description=request.form.get("jd")
#         this_drive.eligible_criteria=request.form.get("ec")
#         this_drive.salary=request.form.get("salary")
#         this_drive.location=request.form.get("location")
#         this_drive.application_deadline=request.form.get("ad")
#         this_drive.status="ongoing"
#         for application in this_drive.applications:
#              db.session.delete(application)
#         # new_drive=Drive(company_id=this_user.id,name=dname,job_title=jt,job_description =jd,eligible_criteria=ec,application_deadline=ad,salary=salary,location =location )
#         db.session.add(this_drive)
#         db.session.commit()
#         return redirect("/admin")
#     return render_template("update_a.html",this_drive=this_drive)
@app.route("/update_drive_c/<int:id>",methods=["GET","POST"])
def update_drive_c(id):
    this_drive=Drive.query.filter_by(id=id).first()
    if this_drive.company.approval_status=="blacklist":
        return render_template("wait_company.html", user=this_drive.company)
    if request.method=="POST":
        this_drive.job_title =request.form.get("jt")
        this_drive.job_description=request.form.get("jd")
        this_drive.eligible_criteria=request.form.get("ec")
        this_drive.salary=request.form.get("salary")
        this_drive.location=request.form.get("location")
        this_drive.application_deadline=request.form.get("ad")
        this_drive.status="ongoing"
        for application in this_drive.applications:
             db.session.delete(application)
        # new_drive=Drive(company_id=this_user.id,name=dname,job_title=jt,job_description =jd,eligible_criteria=ec,application_deadline=ad,salary=salary,location =location )
        db.session.add(this_drive)
        db.session.commit()
        return redirect(f"/company/{this_drive.company.user_id}")
    return render_template("update_c.html",this_drive=this_drive)


@app.route("/complete/<int:id>")
def complete(id):
    drive=Drive.query.filter_by(id=id).first()
    if drive.company.approval_status=="blacklist":
        return render_template("wait_company.html", user=drive.company)
    drive.status="complete"
    for application in drive.applications:
        application.status="Drive Closed"
    db.session.commit()
    return redirect(f"/company/{drive.company.user_id}")

@app.route("/action/<int:id>",methods=["GET","POSt"])
def action(id):
    application=Application.query.filter_by(id=id).first()
    if application.student.approval_status=="blacklist":
        return render_template("wait_student.html", user=application.student)
    if application.company.approval_status=="blacklist":
        return render_template("wait_company.html", user=application.company)
    if request.method=="POST":
        status=request.form.get("status")
        application.status=status
        db.session.add(application)
        db.session.commit()
        return redirect(f"/company_view_details/{application.drive.id}")
    return render_template("review_application.html",application=application)