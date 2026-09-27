from flask import Flask, render_template, request, redirect
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import date
app = Flask(__name__)

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

# ==========================
# DASHBOARD
# ==========================


@app.route("/")
def home():

    cursor = db.cursor()

    cursor.execute("SELECT * FROM Medicines")
    medicines = cursor.fetchall()

    total_medicines = len(medicines)

    low_stock_count = 0
    expired_count = 0

    today = date.today()

    updated_medicines = []

    for medicine in medicines:

        medicine_id = medicine[0]
        name = medicine[1]
        quantity = medicine[2]
        price = medicine[3]
        expiry = medicine[4]

        low_stock = quantity < 20

        expired = False

        if expiry:
            expired = expiry < today

        if low_stock:
            low_stock_count += 1

        if expired:
            expired_count += 1

        updated_medicines.append({
            "id": medicine_id,
            "name": name,
            "quantity": quantity,
            "price": price,
            "expiry": expiry,
            "low_stock": low_stock,
            "expired": expired
        })

    return render_template(
        "index.html",
        medicines=updated_medicines,
        total_medicines=total_medicines,
        low_stock_count=low_stock_count,
        expired_count=expired_count
    )

# ==========================
# ADD MEDICINE
# ==========================


@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        name = request.form["name"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        expiry = request.form["expiry"]

        cursor = db.cursor()

        query = """
        INSERT INTO Medicines
        (MedicineName, Quantity, Price, ExpiryDate)
        VALUES (%s,%s,%s,%s)
        """

        cursor.execute(
            query,
            (name, quantity, price, expiry)
        )

        db.commit()

        return redirect("/")

    return render_template("add.html")

# ==========================
# EDIT MEDICINE
# ==========================


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    cursor = db.cursor()

    if request.method == "POST":

        name = request.form["name"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        expiry = request.form["expiry"]

        query = """
        UPDATE Medicines
        SET MedicineName=%s,
            Quantity=%s,
            Price=%s,
            ExpiryDate=%s
        WHERE MedicineID=%s
        """

        cursor.execute(
            query,
            (name, quantity, price, expiry, id)
        )

        db.commit()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM Medicines WHERE MedicineID=%s",
        (id,)
    )

    medicine = cursor.fetchone()

    return render_template(
        "edit.html",
        medicine=medicine
    )

# ==========================
# DELETE MEDICINE
# ==========================


@app.route("/delete/<int:id>")
def delete(id):

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM Medicines WHERE MedicineID=%s",
        (id,)
    )

    db.commit()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
