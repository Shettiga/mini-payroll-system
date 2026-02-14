from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
app.secret_key = "secretkey"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="payroll_system"
)

cursor = db.cursor(dictionary=True)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            session["admin"] = username
            return redirect("/dashboard")
        else:
            flash("Invalid Username or Password!", "error")
            return redirect("/")

    return render_template("login.html")

# 🏠 Dashboard
@app.route("/dashboard")
def dashboard():
    if "admin" in session:
        return render_template("dashboard.html")
    return redirect("/")

# ➕ Add Employee
@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        name = request.form["name"]
        designation = request.form["designation"]
        department = request.form["department"]
        basic_salary = request.form["basic_salary"]

        cursor.execute("INSERT INTO employee (name, designation, department, basic_salary) VALUES (%s,%s,%s,%s)",
                       (name, designation, department, basic_salary))
        db.commit()
        return "Employee Added Successfully"

    return render_template("add_employee.html")

# 💰 Process Salary
@app.route("/salary", methods=["GET", "POST"])
def salary():
    cursor.execute("SELECT * FROM employee")
    employees = cursor.fetchall()

    if request.method == "POST":
        emp_id = request.form["emp_id"]
        hra = float(request.form["hra"])
        da = float(request.form["da"])
        overtime = float(request.form["overtime"])
        tax = float(request.form["tax"])
        pf = float(request.form["pf"])

        cursor.execute("SELECT basic_salary FROM employee WHERE emp_id=%s", (emp_id,))
        basic = cursor.fetchone()["basic_salary"]

        gross = basic + hra + da + overtime
        deductions = tax + pf
        net_salary = gross - deductions

        cursor.execute("INSERT INTO salary (emp_id, hra, da, overtime, tax, pf, net_salary) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                       (emp_id, hra, da, overtime, tax, pf, net_salary))
        db.commit()

        return f"Salary Processed! Net Salary: {net_salary}"

    return render_template("salary.html", employees=employees)

# 🧾 View Payslip
@app.route("/payslip")
def payslip():
    cursor.execute("""SELECT e.name, s.* FROM salary s 
                      JOIN employee e ON e.emp_id = s.emp_id""")
    data = cursor.fetchall()
    return render_template("payslip.html", data=data)


# 📥 Download Payslip PDF
@app.route("/download_payslip/<int:salary_id>")
def download_payslip(salary_id):
    cursor.execute("""
        SELECT e.name, e.designation, e.department, s.*
        FROM salary s
        JOIN employee e ON e.emp_id = s.emp_id
        WHERE s.salary_id = %s
    """, (salary_id,))
    
    row = cursor.fetchone()
    if not row:
        return "Payslip not found"

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.drawString(200, 750, "Employee Payslip")
    pdf.drawString(50, 720, f"Employee Name: {row['name']}")
    pdf.drawString(50, 700, f"Designation: {row['designation']}")
    pdf.drawString(50, 680, f"Department: {row['department']}")
    pdf.drawString(50, 650, f"HRA: {row['hra']}")
    pdf.drawString(50, 630, f"DA: {row['da']}")
    pdf.drawString(50, 610, f"Overtime: {row['overtime']}")
    pdf.drawString(50, 590, f"Tax: {row['tax']}")
    pdf.drawString(50, 570, f"PF: {row['pf']}")
    pdf.drawString(50, 540, f"Net Salary: {row['net_salary']}")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name="payslip.pdf",
                     mimetype="application/pdf")


# 🚪 Logout
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)