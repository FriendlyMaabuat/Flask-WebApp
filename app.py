from datetime import datetime

from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

db = SQLAlchemy(app)

mail = Mail(app)


class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(90))
    last_name = db.Column(db.String(90))
    email = db.Column(db.String(90))
    date = db.Column(db.Date)
    occupation = db.Column(db.String(90))


@app.route("/", methods=["GET", "POST"])
def index():
    print(request.method)
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        date = request.form["date"]
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        occupation = request.form["occupation"]

        form = Form(
            first_name=first_name,
            last_name=last_name,
            email=email,
            date=date_obj,
            occupation=occupation,
        )
        db.session.add(form)
        db.session.commit()

        message_body = (
            f"Thank you for your submission, {first_name}. \n"
            f"Here are your data that has been submitted \n"
            f"First Name: {first_name}\n"
            f"Last Name: {last_name}\n"
            f"Available start date: {date}\n"
            f"Occupation: {occupation.capitalize()}\n"
            f"We will contact you soon!"
        )
        message = Message(
            subject="New form submission",
            sender=app.config["MAIL_USERNAME"],
            recipients=[email],
            body=message_body,
        )

        mail.send(message)

        flash(f"{first_name}, your form was submitted succesfully!", "success")

        session["submitted"] = True

        return redirect(url_for("index"))

    submitted = session.pop("submitted", None)
    return render_template("index.html", submitted=submitted)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True, port=5001)
