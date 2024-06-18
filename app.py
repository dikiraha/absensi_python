from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
import mysql.connector
from datetime import datetime
from functools import wraps
import bcrypt
import pprint

app = Flask(__name__)
app.secret_key = 'password'

# Configure MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="absensi"
)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'nik' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nik = request.form['nik']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE nik = %s", (nik,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['id'] = user['id']
            session['name'] = user['name']
            session['nik'] = user['nik']
            session['role_id'] = user['role_id']
            return redirect(url_for('index'))
        else:
            flash('Invalid nik or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('nik', None)
    return redirect(url_for('login'))

@app.route('/hadir', methods=['GET', 'POST'])
@login_required
def hadir():
    cursor = db.cursor(dictionary=True)
    user_id = session.get('id')  # Ambil user_id dari session atau di mana pun Anda menyimpan informasi pengguna yang sedang login

    # Query untuk mengambil data kehadiran user yang sedang login pada tanggal yang berbeda
    cursor.execute("""
        SELECT 
            a.id AS user_id, 
            a.name, 
            a.nik, 
            d.name AS department,
            DATE(h.time) AS date,
            MIN(CASE WHEN h.type = 'MASUK' THEN h.time END) AS time_in,
            MAX(CASE WHEN h.type = 'PULANG' THEN h.time END) AS time_out
        FROM 
            log_absens h 
            JOIN users a ON h.user_id = a.id 
            JOIN departments d ON a.department_id = d.id
        WHERE 
            h.user_id = %s
        GROUP BY 
            a.id, 
            a.name, 
            a.nik, 
            d.name,
            DATE(h.time)
        ORDER BY 
            DATE(h.time) DESC
    """, (user_id,))
    attendance_records = cursor.fetchall()
    
    return render_template('hadir/index.html', attendance_records=attendance_records)

@app.route('/')
def index():
    cursor = db.cursor(dictionary=True)
    today = datetime.today().strftime('%Y-%m-%d')

    # Query to fetch today's attendance records with time_in and time_out
    cursor.execute("""
        SELECT u.id, u.name, u.nik, 
        (SELECT time FROM log_absens WHERE user_id = u.id AND type = 'MASUK' AND DATE(time) = %s ORDER BY time LIMIT 1) AS time_in,
        (SELECT time FROM log_absens WHERE user_id = u.id AND type = 'PULANG' AND DATE(time) = %s ORDER BY time DESC LIMIT 1) AS time_out,
        d.name AS department
        FROM users u 
        JOIN departments d ON u.department_id = d.id
        WHERE EXISTS (SELECT 1 FROM log_absens WHERE user_id = u.id AND DATE(time) = %s)
        ORDER BY time_out DESC
    """, (today, today, today,))
    attendance_records = cursor.fetchall()
    
    return render_template('absen/index.html', attendance_records=attendance_records)

@app.route('/create_karyawan', methods=['GET', 'POST'])
@login_required
def create_karyawan():
    if request.method == 'POST':
        id_card = request.form['id_card']
        nik = request.form['nik']
        name = request.form['name']
        jabatan_id = request.form['jabatan_id']
        department_id = request.form['department_id']
        role_id = request.form['role_id']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        cursor = db.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (id_card, nik, name, jabatan_id, department_id, role_id, password) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (id_card, nik, name, jabatan_id, department_id, role_id, hashed_password)
            )
            db.commit()
            flash("Karyawan berhasil ditambahkan", "success")
        except mysql.connector.Error as err:
            db.rollback()
            flash(f"Error: {err.msg}", "danger")
            return redirect(url_for('create_karyawan'))

    cursor = db.cursor()

    # Query to fetch today's attendance records
    cursor.execute("""
        SELECT u.id_card, u.name AS user_name, j.name AS jabatan_name, d.name AS department_name, r.name AS role_name
        FROM users u
        JOIN jabatans j ON u.jabatan_id = j.id
        JOIN departments d ON u.department_id = d.id
        JOIN roles r ON u.role_id = r.id
        ORDER BY u.name DESC
    """)
    
    attendance_records = cursor.fetchall()

    # Query to fetch jabatans
    cursor.execute("SELECT id, name FROM jabatans")
    jabatans = cursor.fetchall()
    
    cursor.execute("SELECT id, name FROM departments")
    departments = cursor.fetchall()
    
    cursor.execute("SELECT id, name FROM roles")
    roles = cursor.fetchall()
    cursor.close()

    return render_template('karyawan/create.html', attendance_records=attendance_records, jabatans=jabatans, departments=departments, roles=roles, success=request.args.get('success'), error=request.args.get('error'), enumerate=enumerate)

@app.route('/delete_karyawan', methods=['POST'])
@login_required
def delete_karyawan():
    if request.method == 'POST':
        id_delete = request.form.get('id')
        try:
            # Execute a raw SQL DELETE query
            db.engine.execute(f"DELETE FROM users WHERE nik = '{id_delete}'")
            return "Karyawan berhasil dihapus"
        except Exception as e:
            return f"Error: {str(e)}"
    return redirect(url_for('index'))

@app.route('/scan', methods=['POST'])
def scan():
    id_card = request.form.get('id_card')
    type_ = request.form.get('type')

    cursor = db.cursor(dictionary=True)

    # Check if the id_card exists in users table
    cursor.execute("SELECT id FROM users WHERE id_card = %s", (id_card,))
    user_record = cursor.fetchone()

    if user_record:
        user_id = user_record['id']

        try:
            cursor.execute("INSERT INTO log_absens (user_id, type) VALUES (%s, %s)", (user_id, type_))
            db.commit()
            return jsonify(success=True, type=type_)
        except Exception as e:
            db.rollback()
            return jsonify(success=False, error=str(e))
    else:
        return jsonify(success=False, error="Nomor tidak ditemukan")

if __name__ == '__main__':
    app.run(debug=True)
