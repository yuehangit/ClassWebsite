import sqlite3

from flask import Flask, render_template, request, g,session, redirect, url_for, escape


DATABASE = './assignment3.db'


def get_db():

    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

app = Flask(__name__)
app.secret_key=b'y'

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:

        db.close()

@app.route('/signup')
def signup():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/signupInfo',methods=['GET','POST'])
def signupInfo():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        sql = """
       	    SELECT *
    	    FROM users
       	    """
        results = query_db(sql, args=(), one=True)
        for result in results:
            if result[1] == request.form['username']:
                return render_template('signupfail.html')
        session['username'] = request.form['username']
        sqli = sqlite3.connect(DATABASE)
        cursor = sqli.cursor()
        usern = request.form.get('username')
        passw = request.form.get('password')
        nameuser = request.form.get('usern')
        if request.form.get('isinstruct'):
            session['user'] = "instructor"
            cursor.execute("INSERT INTO users(username, password, usertype) VALUES (?, ?, 'instructor') ",(usern, passw))
            for result in results:
                if result[1] == request.form['username']:
                    userid = request[0]
                    session['id'] = userid
            cursor.execute("INSERT INTO students(studentid, userid, studentname, course, instructor, assignment, mark) VALUES (1, ?, ?, 'b', 'bill', 'exam', 0 ) ",
                           (userid, nameuser))
            sqli.commit()
            cursor.close()
            return redirect(url_for('home'))
        else:
            session['user'] = "student"
            cursor.execute("INSERT INTO users(username, password, usertype) VALUES (?, ?, 'student') ", (usern, passw))
            for result in results:
                if result[1] == request.form['username']:
                    userid = request[0]
                    session['id'] = userid
            sqli.commit()
            cursor.close()
            return redirect(url_for('home'))
    else:
        return redirect('signup')
@app.route('/')
def home():
    if 'username' in session:
        if session['user'] == "student":
            return redirect(url_for('welcome_student'))
        else:
            return redirect(url_for('welcome'))
    return redirect('login')

@app.route('/home')
def homepage():
    return render_template('index.html')
@app.route('/login')
def login():
    if  'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')
@app.route('/assignments')
def assignments():
    if 'username' in session:
        return render_template('assignments.html')
    return redirect('login')
@app.route('/calendar')
def calendar():
    if 'username' in session:
        return render_template('calendar.html')
    return redirect('login')
@app.route('/labs')
def labs():
    if 'username' in session:
        return render_template('labs.html')
    return redirect('login')

@app.route('/lectures')
def lectures():
    if 'username' in session:
        return render_template('lectures.html')
    return redirect('login')

@app.route('/resources')
def resources():
    if 'username' in session:
        return render_template('resources.html')
    return redirect('login')

@app.route('/team')
def team():
    if 'username' in session:
        return render_template('team.html')
    return redirect('login')

@app.route('/tests')
def tests():
    if 'username' in session:
        return render_template('tests.html')
    return redirect('login')

@app.route('/loginme',methods=['GET','POST'])
def loginme():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        sql = """
    		SELECT *
    		FROM users
    		"""
        results = query_db(sql, args=(), one=False)

        for result in results:
            if result[1] == request.form['username']:
                if result[2] == request.form['password']:
                    session['username'] = request.form['username']
                    if result[3] == "instructor":
                        session['user'] = "instructor"
                    else:
                        session['user'] = "student"
                    session['id'] = result[0]
                    return redirect(url_for('home'))

        return render_template('loginfail.html')
    else:
        return redirect(url_for('home'))
@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
        session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/remark-requests')
def get_student():
    if session['user'] == "instructor":
        id = session['id']
        sql = """
               		SELECT *
               		FROM instructors
               		"""
        results = query_db(sql, args=(), one=False)

        for result in results:
            if result[0] == id:
                instructor = result[1]
        db = get_db()
        db.row_factory = make_dicts

        student = query_db('select * from remarks where instructor = ?', [instructor], one=False)
        db.close()
        return render_template('remark-requests.html', student=student)
    else:
        return redirect(url_for('home'))






@app.route('/instructor-home')
def welcome():
    if session['user'] == "instructor":
        return render_template('instructor-home.html')
    else:
        return redirect(url_for('home'))

@app.route('/student-grades')
def student_grades():
    if session['user'] == "instructor":
        sql = """
                    		SELECT *
                    		FROM instructors
                    		"""
        results = query_db(sql, args=(), one=False)

        for result in results:
            if result[0] == session['id']:
                instructor_name = result[1]
        db = get_db()
        db.row_factory = make_dicts
        students = query_db('select * from students where instructor=?', [instructor_name], one=False)
        db.close()
        return render_template('student-grades.html', student=students)
    else:
        return redirect(url_for('home'))


@app.route('/instructor-feedback')
def get_feedback():
    if session['user'] == "instructor":
        sql = """
               		SELECT *
               		FROM instructors
               		"""
        results = query_db(sql, args=(), one=False)

        for result in results:
            if result[0] == session['id']:
                instructor_name = result[1]
        db = get_db()
        db.row_factory = make_dicts
        student = query_db('select * from Feedback where instructor=?', [instructor_name], one=False)
        db.close()
        return render_template('instructor-Feedback.html', student=student)
    else:
        return redirect(url_for('home'))
@app.route('/insert-grades')
def insert_grades():
    if session['user'] == "instructor":
        return render_template('insert-grades.html')
    else:
        return redirect(url_for('home'))

@app.route('/insert-the-grades',methods=['GET','POST'])
def insert_the_grades():
    if session['user'] == "instructor":
        sql = """
                            		SELECT *
                            		FROM students
                            		"""
        results = query_db(sql, args=(), one=False)
        studentid = request.form.get('student ID')
        course = request.form.get('course code')
        stud_name = request.form.get('s_name')
        instructor = request.form.get('instructor name')
        mark = request.form.get('Grade')
        assignment = request.form.get('Assessment Type')
        id = session['id']
        sqli = sqlite3.connect(DATABASE)
        cursor = sqli.cursor()
        for result in results:
            if result[2] == session['id'] and result[6] == assignment and result[4] == course and result[
                5] == instructor:
                sqlu = ''' UPDATE students
                                  SET mark= ? 
                                  WHERE userid = ?'''
                cursor.execute(sqlu, mark, id)
                sqli.commit()
                cursor.close()
                return redirect(url_for('home'))
        cursor.execute(
            "INSERT INTO students(studentid, studentname,course, instructor, mark, assignment) VALUES (?, ?, ?, ?, ? , ?) ",
            (studentid, stud_name, course, instructor, mark, assignment))
        sqli.commit()
        cursor.close()
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

#*******STUDENT VIEW PAGES*****
@app.route('/student-home')
def welcome_student():
    if session['user'] == "student":
        return render_template('student-home.html')
    return redirect(url_for('home'))

@app.route('/my-grades')
def get_my_grades():
    if session['user'] == "student":
        db = get_db()
        db.row_factory = make_dicts
        student_id = session['id']    #OVER HERE WE NEED A WAY TO SET THE NAME ACCORDING TO THE PERSON LOGGED IN
        student = query_db('SELECT * FROM students where userid=?', [student_id], one=False)
        db.close()
        return render_template('my-grades.html', student=student)
    return redirect(url_for('home'))

@app.route('/student-remark-requests')
def student_remark():
    if session['user'] == "student":
        return render_template('student-remark-requests.html')
    return redirect(url_for('home'))


@app.route('/send-remark-requests',methods=['GET','POST'])
def send_remark_request():
    if session['user'] == "student":
        sql = """
                        		SELECT *
                        		FROM students
                        		"""
        results = query_db(sql, args=(), one=False)
        student_id = request.form.get('student ID')
        student_name = request.form.get('student name')
        course = request.form.get('Course code')
        assignment = request.form.get('assignment type')
        mark = request.form.get('student mark')
        instructor = request.form.get('Instructor Name')
        explaination = request.form.get('remark reason')
        id = session['id']

        sqli = sqlite3.connect(DATABASE)
        cursor = sqli.cursor()
        cursor.execute(
            "INSERT INTO remarks(studentid, userid, studentname, course, instructor, mark, assignment, explaination) VALUES (?, ?, ?, ?, ? , ?, ?, ?) ",
            (student_id, id, student_name, course, instructor, mark, assignment, explaination))
        sqli.commit()
        cursor.close()
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/student-feedback')
def student_feedback():
    if session['user'] == "student":
        db = get_db()
        db.row_factory = make_dicts
        student_id = session['id']
        instructors = query_db('SELECT * from instructors where name in (select instructor from students where userid = ?)', [student_id], one=False)
        db.close()
        return render_template('student-feedback.html', instructors = instructors)
    return redirect(url_for('home'))

@app.route('/send-student-feedback',methods=['GET','POST'])
def send_feedback():
    if session['user'] == "student":
        course = request.form.get('course')
        #instructor = request.form.get('instructor name')
        instructor = request.form.get('option_1')
        q1 = request.form.get('question 1')
        q2 = request.form.get('question 2')
        q3 = request.form.get('question 3')
        q4 = request.form.get('question 4')

        sqli = sqlite3.connect(DATABASE)
        cursor = sqli.cursor()
        cursor.execute("INSERT INTO feedback(course, instructor,  q1, q2, q3, q4) VALUES (?, ?, ?, ?, ? , ?) ",
                       (course, instructor, q1, q2, q3, q4))
        sqli.commit()
        cursor.close()
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

if __name__=="__main__":
	app.run(debug=True,host='0.0.0.0')