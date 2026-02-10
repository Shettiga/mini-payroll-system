from flask import Flask, render_template, request, redirect, session
import mysql.connector

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

# 🔐 Login
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
            return "Invalid Login"

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

# 🚪 Logout
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
