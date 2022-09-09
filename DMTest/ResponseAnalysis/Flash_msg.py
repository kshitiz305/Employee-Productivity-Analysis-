from flask import Flask, flash, render_template
import webbrowser
from Compare_response import compare_var_resp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stiler'
# APP_ROOT = os.path.dirname(os.path.abspath(__file__))

global emails_num

@app.route("/")
def home():

    emails_num = compare_var_resp()
    num_emp = str(emails_num)
    flash("You are going to send email to " + num_emp + " Practitioners.")
    return render_template("report.html")

webbrowser.open("http://localhost:5000/")

if __name__ == '__main__':
    app.secret_key = "stiler"
    app.run(debug=False)