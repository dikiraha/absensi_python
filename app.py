from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'password'

# Configure MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="attendance_db"
)

@app.route('/absen_hadir', methods=['GET', 'POST'])
def absen_hadir():
    return jsonify({"message": "Nomor tidak ditemukan"}), 404

@app.route('/karyawan/create')
def karyawan_create():
    return render_template('karyawan/create.html')

@app.route('/')
def index():
    cursor = db.cursor(dictionary=True)
    today = datetime.today().strftime('%Y-%m-%d')

    # Query to fetch today's attendance records
    cursor.execute("""
        SELECT h.nomor, a.nama, h.timestamp 
        FROM hadir h 
        JOIN absensi a ON h.nomor = a.nomor 
        WHERE DATE(h.timestamp) = %s
        ORDER BY h.timestamp DESC
    """, (today,))

    attendance_records = cursor.fetchall()

    return render_template('absen/index.html', attendance_records=attendance_records)

@app.route('/create_karyawan', methods=['GET', 'POST'])
def create_karyawan():
    if request.method == 'POST':
        nomor = request.form['nomor']
        nama = request.form['nama']

        cursor = db.cursor()

        try:
            cursor.execute("INSERT INTO absensi (nomor, nama) VALUES (%s, %s)", (nomor, nama))
            db.commit()
            return redirect(url_for('create_karyawan'))
        except mysql.connector.Error as err:
            return redirect(url_for('create_karyawan', error=err.msg))

    cursor = db.cursor()
    
    # Query to fetch today's attendance records
    cursor.execute("""
        SELECT nomor, nama 
        FROM absensi
        ORDER BY nomor DESC
    """)

    attendance_records = cursor.fetchall()
    cursor.close()

    return render_template('karyawan/create.html', attendance_records=attendance_records, success=request.args.get('success'), error=request.args.get('error'), enumerate=enumerate)


@app.route('/scan', methods=['POST'])
def scan():
    nomor = request.form.get('nomor')

    cursor = db.cursor(dictionary=True)

    # Check if the nomor exists in absensi table
    cursor.execute("SELECT * FROM absensi WHERE nomor = %s", (nomor,))
    absensi_record = cursor.fetchone()

    if absensi_record:
        # Check if the nomor is already in hadir table today
        cursor.execute("SELECT * FROM hadir WHERE nomor = %s AND DATE(timestamp) = CURDATE()", (nomor,))
        hadir_record = cursor.fetchone()

        if hadir_record:
            flash("Anda sudah absen", "warning")
        else:
            # Insert into hadir table
            cursor.execute("INSERT INTO hadir (nomor) VALUES (%s)", (nomor,))
            db.commit()
            flash("Absen berhasil", "success")
    else:
        flash("Nomor tidak ditemukan", "danger")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
