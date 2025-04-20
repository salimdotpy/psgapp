from flask import Flask, render_template, request, flash, session, redirect, url_for, send_file
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import io, re

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config["DEBUG"] = True
app.config["threaded"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="psgapp",
    password="Credential",
    hostname="psgapp.mysql.pythonanywhere-services.com",
    databasename="psgapp$psgdb",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.secret_key = "psgapp secret key"

class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.BigInteger(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(40, collation='utf8mb4_unicode_ci'), nullable=False)
    email = db.Column(db.String(40, collation='utf8mb4_unicode_ci'), nullable=False, unique=True)
    mobile = db.Column(db.String(40, collation='utf8mb4_unicode_ci'), default=None, nullable=True)
    password = db.Column(db.String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return { 'id': self.id, 'name': self.name, 'email': self.email, 'mobile': self.mobile, 'password': self.password,
        'created_at': str(self.created_at), 'updated_at': str(self.updated_at) }

class Student(db.Model):

    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80, collation='utf8mb4_unicode_ci'), default=None, nullable=True)
    matricno = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), default=None, nullable=True)
    pwriteup = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), default=0, nullable=True)
    pdefence = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), default=0, nullable=True)
    ptotal = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), default=0, nullable=True)
    swriteup = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), default=0, nullable=True)
    sdefence = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), default=0, nullable=True)
    stotal = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), default=0, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return { 'id': self.id, 'name': self.name, 'matricno': self.matricno, 'pwriteup': self.pwriteup, 'pdefence': self.pdefence, 'ptotal': self.ptotal,
        'swriteup': self.swriteup, 'sdefence': self.sdefence, 'stotal': self.stotal, 'created_at': str(self.created_at), 'updated_at': str(self.updated_at) }

class Lecturer(db.Model):

    __tablename__ = "lecturers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80, collation='utf8mb4_unicode_ci'), default=None, nullable=True)
    username = db.Column(db.String(40, collation='utf8mb4_unicode_ci'), default=None, nullable=True)
    password = db.Column(db.String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return { 'id':self.id, 'name': self.name, 'password': self.password, 'created_at': str(self.created_at), 'updated_at': str(self.updated_at) }

class Allocate(db.Model):
    __tablename__ = "allocates"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sid = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    lid = db.Column(db.Integer, db.ForeignKey('lecturers.id'), nullable=True)
    type = db.Column(db.String(40, collation='utf8mb4_unicode_ci'), default=None, nullable=True)
    status = db.Column(db.String(40, collation='utf8mb4_unicode_ci'), default=None, nullable=True)
    student = db.relationship('Student', foreign_keys=sid)
    lecturer = db.relationship('Lecturer', foreign_keys=lid)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now)

    def to_dict(self):
        return { 'id': self.id, 'sid': self.sid, 'lid': self.lid, 'type': self.type, 'status': self.status, 'student': self.student,
        'lecturer': self.lecturer, 'created_at': str(self.created_at), 'updated_at': str(self.updated_at) }

# Create the database
# with app.app_context():
#     db.create_all()

# Allowed file types
ALLOWED_EXTENSIONS = ['xls', 'xlsx']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    pageTitle = "Index Page"
    return render_template('index.html', pageTitle=pageTitle)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Create variables for easy access
        name = request.form['name']
        password = request.form['password']
        # Validation checks
        lecturer = Lecturer.query.filter_by(username=name).first()
        if lecturer is None or not lecturer.check_password(password):
            flash('Invalid Credential', ('error'))
            return redirect(request.referrer)
        session['lecturer'] = lecturer.to_dict()
        flash('You\'ve successfully logged in!', ('success'))
        return redirect(url_for('dashboard'))

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    pageTitle = "Lecturer Dashboard"
    widget = {}
    if 'lecturer' in session:
        lecturer = Lecturer.query.get(session['lecturer']['id'])
        # widget['projects'] = Allocate.query.filter_by(type='project', lid=lecturer.id).all()
        # widget['seminars'] = Allocate.query.filter_by(type='seminar', lid=lecturer.id).all()
        widget['dprojects'] = Allocate.query.filter_by(type='project', status='defence', lid=lecturer.id).all()
        widget['wprojects'] = Allocate.query.filter_by(type='project', status='writeup', lid=lecturer.id).all()
        widget['dseminars'] = Allocate.query.filter_by(type='seminar', status='defence', lid=lecturer.id).all()
        widget['wseminars'] = Allocate.query.filter_by(type='seminar', status='writeup', lid=lecturer.id).all()
        if request.method == 'POST':
            # Create variables for easy access
            opass = request.form['opass']
            npass = request.form['npass']
            cpass = request.form['cpass']
            if not opass or not npass or not cpass:
                msg = ['Please fill out the form!', 'error']
            elif npass != cpass:
                msg = ['Two password does not match!', 'error']
            elif not lecturer.check_password(opass):
                msg = ['Old password does not match!', 'error']
            else:
                password = generate_password_hash(npass)
                lecturer.password = password
                try:
                    db.session.commit()
                    msg = ['Password updated successfully!', 'success']
                except:
                    db.session.rollback()
                    msg = ['Unable to update password, please try again later!', 'error']
                session['lecturer'] = lecturer.to_dict()
            flash(msg[0], (msg[1]))
            return redirect(request.referrer)
        return render_template('dashboard.html', pageTitle=pageTitle, lecturer=lecturer, widget=widget)
    flash('Please login first!', ('warning'))
    return redirect(url_for('index'))

@app.route("/project", methods=['GET', 'POST'])
def project():
    pageTitle = "Project Mark"
    widget = {}
    if 'lecturer' in session:
        lecturer = Lecturer.query.get(session['lecturer']['id'])
        widget['dprojects'] = Allocate.query.filter_by(type='project', status='defence', lid=lecturer.id).all()
        widget['wprojects'] = Allocate.query.filter_by(type='project', status='writeup', lid=lecturer.id).all()

        if request.method == 'POST':
            mode = request.form['mode']
            ids = request.form.getlist('data_ids[]')
            scores = request.form.getlist('data_scores[]')
            try:
                if mode == 'writeup':
                    for i in range(len(ids)):
                        student = Student.query.filter_by(id=ids[i]).first()
                        student.pwriteup = scores[i]
                else:
                    for i in range(len(ids)):
                        student = Student.query.filter_by(id=ids[i]).first()
                        student.pdefence = scores[i]
                db.session.commit()
                flash('Students scores uploaded successfully', ('success'))
            except Exception as e:
                flash(f'Error processing file: {e}', ('error'))
                db.session.rollback()
            return redirect(request.referrer)
        return render_template('project.html', pageTitle=pageTitle, lecturer=lecturer, widget=widget)
    flash('Please login first!', ('warning'))
    return redirect(url_for('index'))

@app.route("/seminar", methods=['GET', 'POST'])
def seminar():
    pageTitle = "Seminar Mark"
    widget = {}
    if 'lecturer' in session:
        lecturer = Lecturer.query.get(session['lecturer']['id'])
        widget['dseminars'] = Allocate.query.filter_by(type='seminar', status='defence', lid=lecturer.id).all()
        widget['wseminars'] = Allocate.query.filter_by(type='seminar', status='writeup', lid=lecturer.id).all()

        if request.method == 'POST':
            mode = request.form['mode']
            ids = request.form.getlist('data_ids[]')
            scores = request.form.getlist('data_scores[]')
            try:
                if mode == 'writeup':
                    for i in range(len(ids)):
                        student = Student.query.filter_by(id=ids[i]).first()
                        student.swriteup = scores[i]
                else:
                    for i in range(len(ids)):
                        student = Student.query.filter_by(id=ids[i]).first()
                        student.sdefence = scores[i]
                db.session.commit()
                flash('Students scores uploaded successfully', ('success'))
            except Exception as e:
                flash(f'Error processing file: {e}', ('error'))
                db.session.rollback()
            return redirect(request.referrer)
        return render_template('seminar.html', pageTitle=pageTitle, lecturer=lecturer, widget=widget)
    flash('Please login first!', ('warning'))
    return redirect(url_for('index'))

@app.route("/admin/login", methods=['GET', 'POST'])
def adminLogin():
    if request.method == 'POST':# Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Validation checks
        admin = Admin.query.filter_by(name=username).first()
        if admin is None or not admin.check_password(password):
            flash('Invalid Credential', ('error'))
            return redirect(request.referrer)
        session['admin'] = admin.to_dict()
        flash('You\'ve successfully logged in!', ('success'))
        return redirect(url_for('adminDashboard'))

@app.route("/admin/dashboard", methods=['GET', 'POST'])
def adminDashboard():
    pageTitle = "Admin Dashboard"
    widget = {}
    if 'admin' in session:
        widget['lecturer'] = Lecturer.query.all()
        widget['student'] = Student.query.all()
        admin = Admin.query.get(session['admin']['id'])
        if request.method == 'POST' and 'editProfile' in request.form:
            # Create variables for easy access
            name = request.form['name']
            email = request.form['email']
            contact = request.form['contact']
            if not name or not contact or not email:
                msg = ['Please fill out the form!', 'error']
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) or len(email) > 30:
                msg = ['Invalid email address!', 'error']
            elif not contact or len(contact) != 11:
                msg = ['Invalid phone number!', 'error']
            else:
                admin.name = name
                admin.email = email
                admin.mobile = contact
                try:
                    db.session.commit()
                    msg = ['Profile updated successfully!', 'success']
                except:
                    db.session.rollback()
                    msg = ['Unable to update profile, please try again later!', 'error']
                session['admin'] = admin.to_dict()
            flash(msg[0], (msg[1]))
            return redirect(request.referrer)
        if request.method == 'POST' and 'editPassword' in request.form:
            # Create variables for easy access
            opass = request.form['opass']
            npass = request.form['npass']
            cpass = request.form['cpass']
            if not opass or not npass or not cpass:
                msg = ['Please fill out the form!', 'error']
            elif npass != cpass:
                msg = ['Two password does not match!', 'error']
            elif not admin.check_password(opass):
                msg = ['Old password does not match!', 'error']
            else:
                password = generate_password_hash(npass)
                admin.password = password
                try:
                    db.session.commit()
                    msg = ['Password updated successfully!', 'success']
                except:
                    db.session.rollback()
                    msg = ['Unable to update password, please try again later!', 'error']
                session['admin'] = admin.to_dict()
            flash(msg[0], (msg[1]))
            return redirect(request.referrer)
        return render_template('admin/dashboard.html', pageTitle=pageTitle, admin=admin, widget=widget)
    flash('Please login first!', ('warning'))
    return redirect(url_for('index'))

@app.route("/admin/manage-student", methods=['GET', 'POST'])
def adminStudent():
    pageTitle = "Manage Student"
    if 'admin' in session:
        students = Student.query.all()
        admin = Admin.query.get(session['admin']['id'])
        if request.method == 'POST':
            if 'file' in request.files:
                file = request.files['file']
                if file.filename == '':
                    flash('No selected file', ('error'))
                    return redirect(request.referrer)

                if file and allowed_file(file.filename):
                    # Process the Excel file and insert into DB
                    try:
                        db.session.execute('DROP TABLE allocates')
                        db.session.execute('DROP TABLE students')
                        db.session.commit()
                        db.create_all()
                        df = pd.read_excel(file)
                        for index, row in df.iterrows():
                            new_student = Student(matricno=row['Matric. No'], name=row['Names'])
                            db.session.add(new_student)
                        db.session.commit()
                        flash('Data successfully inserted into database', ('success'))
                    except Exception as e:
                        flash(f'Error processing file: {e}', ('error'))
                        db.session.rollback()

                    return redirect(request.referrer)

                else:
                    flash('Invalid file format', ('error'))
                    return redirect(request.url)
            if 'report' in request.form:
                type = request.form['type']
                if type == 'project':
                    try:
                        # Convert data into a pandas DataFrame
                        data = {
                            "Matric. No": [student.matricno for student in students],
                            "Names": [student.name for student in students],
                            "Writeup Score": [int(student.pwriteup) for student in students],
                            "Defence Score": [int(student.pdefence) for student in students],
                            "Total Score": [int(student.pwriteup) + int(student.pdefence) for student in students],
                        }

                        df = pd.DataFrame(data)

                        # Create an in-memory BytesIO object
                        output = io.BytesIO()

                        # Save the DataFrame to this in-memory buffer
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False)

                        output.seek(0)  # Reset the pointer to the beginning of the stream

                        # Send the file as a response without saving it on the server
                        return send_file(
                            output,
                            as_attachment=True,
                            download_name="Students_project_report.xlsx",
                            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    except Exception as e:
                        flash(f"Error generating Excel file: {e}")
                        return redirect(request.referrer)
                else:
                    try:
                        # Convert data into a pandas DataFrame
                        data = {
                            "Matric. No": [student.matricno for student in students],
                            "Name": [student.name for student in students],
                            "Writeup Score": [int(student.swriteup) for student in students],
                            "Defence Score": [int(student.sdefence) for student in students],
                            "Total Score": [int(student.swriteup) + int(student.sdefence) for student in students],
                        }

                        df = pd.DataFrame(data)

                        # Create an in-memory BytesIO object
                        output = io.BytesIO()

                        # Save the DataFrame to this in-memory buffer
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False)

                        output.seek(0)  # Reset the pointer to the beginning of the stream

                        # Send the file as a response without saving it on the server
                        return send_file(
                            output,
                            as_attachment=True,
                            download_name="Students_seminar_report.xlsx",
                            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    except Exception as e:
                        flash(f"Error generating Excel file: {e}")
                        return redirect(request.referrer)

        return render_template('admin/manage_student.html', pageTitle=pageTitle, admin=admin, students=students)
    flash('Please login first!', ('warning'))
    return redirect(url_for('index'))

@app.route("/admin/manage-lecturer", methods=['GET', 'POST'])
def adminLecturer():
    pageTitle = "Manage Lecturer"
    widget = {}
    if 'admin' in session:
        widget['lecturers'] = Lecturer.query.all()
        admin = Admin.query.get(session['admin']['id'])
        widget['dprojects'] = Allocate.query.filter_by(type='project', status='defence').group_by(Allocate.lid).all()
        # widget['dprojects'] = Allocate.query.filter_by(type='project', status='defence').all()
        widget['wprojects'] = Allocate.query.filter_by(type='project', status='writeup').group_by(Allocate.lid).all()
        widget['dseminars'] = Allocate.query.filter_by(type='seminar', status='defence').group_by(Allocate.lid).all()
        widget['wseminars'] = Allocate.query.filter_by(type='seminar', status='writeup').group_by(Allocate.lid).all()
        if request.method == 'POST':
            if 'file' in request.files:
                file = request.files['file']
                if file.filename == '':
                    flash('No selected file', ('error'))
                    return redirect(request.referrer)

                if file and allowed_file(file.filename):
                    # Process the Excel file and insert into DB
                    try:
                        db.session.execute('DROP TABLE allocates')
                        db.session.execute('DROP TABLE lecturers')
                        db.session.commit()
                        db.create_all()
                        df = pd.read_excel(file)
                        for index, row in df.iterrows():
                            password = generate_password_hash('password')
                            name = row['name']
                            username = name.split(' ')
                            new_lecturer = Lecturer(name=name, username=username[0], password=password)
                            db.session.add(new_lecturer)
                        db.session.commit()
                        flash('Data successfully inserted into database', ('success'))
                    except Exception as e:
                        flash(f'Error processing file: {e}', ('error'))
                        db.session.rollback()

                    return redirect(request.referrer)

                else:
                    flash('Invalid file format', ('error'))
                    return redirect(request.url)
        return render_template('admin/manage_lecturer.html', pageTitle=pageTitle, admin=admin, widget=widget)
    flash('Please login first!', ('warning'))
    return redirect(url_for('index'))

@app.route("/admin/allocate", methods=['GET', 'POST'])
def adminAllocate():
    pageTitle = "Create Allocation"
    if 'admin' in session:
        widget = {}
        widget['lecturers'] = Lecturer.query.all()
        widget['students'] = Student.query.all()
        widget['allocates'] = Allocate.query.all()
        widget['dprojects'] = Allocate.query.filter_by(type='project', status='defence').all()
        widget['wprojects'] = Allocate.query.filter_by(type='project', status='writeup').all()
        widget['dseminars'] = Allocate.query.filter_by(type='seminar', status='defence').all()
        widget['wseminars'] = Allocate.query.filter_by(type='seminar', status='writeup').all()

        admin = Admin.query.get(session['admin']['id'])
        if request.method == 'POST':
            if 'create' in request.form:
                type = request.form['type']
                status = request.form['mode']
                leid = request.form['lecturer'] if status == 'writeup' else request.form.getlist('lecturer')
                sids = request.form.getlist('students[]')
                if len(sids) > 0:
                    sids = list(filter(lambda x: x != 'false', sids))
                else:
                    flash('No student selected', ('error'))
                    return redirect(request.url)
                try:
                    oldCount = sa = lsa = newCount = 0
                    if status == 'defence':
                        for ids in leid:
                            oldCount = Allocate.query.filter_by(lid=ids, type=type, status=status).all()
                            for sid in sids:
                                checkLS = Allocate.query.filter_by(lid=ids, sid=sid, type=type).first()
                                # checkS = Allocate.query.filter_by(sid=sid, type=type, status=status).first()
                                if checkLS: sa += 1
                                # if checkS: lsa += 1
                                # if checkLS or checkS: continue
                                if checkLS: continue
                                new_ = Allocate(sid=sid, lid=ids, type=type, status=status)
                                db.session.add(new_)
                                newCount += 1
                    else:
                        oldCount = Allocate.query.filter_by(lid=leid, type=type, status=status).all()
                        for sid in sids:
                            checkLS = Allocate.query.filter_by(lid=leid, sid=sid, type=type).first()
                            checkS = Allocate.query.filter_by(sid=sid, type=type, status=status).first()
                            if checkLS: sa += 1
                            if checkS: lsa += 1
                            if checkLS or checkS: continue
                            new_ = Allocate(sid=sid, lid=leid, type=type, status=status)
                            db.session.add(new_)
                            newCount += 1
                    db.session.commit()
                    msg = f"You've newly allocated {newCount} student(s) to this lecturer, old allocation: ({len(oldCount)}), unable to allocate: ({sa+lsa})"
                    if newCount == 0:
                        flash(f"No new student allocated to this lecturer, old allocation: {len(oldCount)}", ('warning'))
                    else:
                        flash(msg, ('success'))
                except Exception as e:
                        flash(f'Something went wrong: {e}', ('error'))
                        db.session.rollback()
                return redirect(request.url)
            if 'delete' in request.form:
                by = request.form['by']
                id = request.form['id']
                if by == 'student':
                    try:
                        Allocate.query.filter_by(id=id).delete()
                        db.session.commit()
                        msg = 'Allocation Deleted sucessfully', 'success'
                    except Exception as e:
                        msg = e, 'error'
                    flash(str(msg[0]), msg[1])
                else:
                    try:
                        Allocate.query.filter_by(lid=id).delete()
                        db.session.commit()
                        msg = 'Allocation Deleted sucessfully', 'success'
                    except Exception as e:
                        msg = str(e), 'error'
                    flash(msg[0], msg[1])
                return redirect(request.referrer)
            if 'bulkdelete' in request.form:
                pids = request.form.getlist('projects[]')
                if len(pids) > 0:
                    pids = list(filter(lambda x: x != 'false', pids))
                else:
                    flash('No record selected', ('error'))
                    return redirect(request.url)
                try:
                    for ids in pids:
                        Allocate.query.filter_by(id=ids).delete()
                    db.session.commit()
                    msg = 'Allocation Deleted sucessfully', 'success'
                except Exception as e:
                    msg = e, 'error'
                flash(str(msg[0]), msg[1])
                return redirect(request.url)
        return render_template('admin/allocate.html', pageTitle=pageTitle, admin=admin, widget=widget)
    flash('Please login first!', ('warning'))
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.pop('lecturer', None)
    flash('You have successfully logged out!', ('success'))
    return redirect(url_for('index'))

@app.route("/admin/logout")
def adminLogout():
    session.pop('admin', None)
    flash('You have successfully logged out!', ('success'))
    return redirect(url_for('index'))