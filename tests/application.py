from datetime import datetime

import bcrypt

# from apps import App
from flask import json

# from utilities import Utilities
from flask import render_template, session, url_for, flash, redirect, request, Flask
from flask_mail import Mail
from flask_pymongo import PyMongo

from forms import RegistrationForm, LoginForm, UserProfileForm

app = Flask(__name__)
app.secret_key = "secret"
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/test"
app.config["MONGO_CONNECT"] = False
mongo = PyMongo(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "bogusdummy123@gmail.com"
app.config["MAIL_PASSWORD"] = "helloworld123!"
mail = Mail(app)


@app.route("/")
@app.route("/home")
def home():
    """
    home() function displays the homepage of our website.
    route "/home" will redirect to home() function.
    input: The function takes session as the input
    Output: Out function will redirect to the login page
    """
    if session.get("email"):
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """ "
    login() function displays the Login form (login.html) template
    route "/login" will redirect to login() function.
    LoginForm() called and if the form is submitted then various values are fetched and verified from the database entries
    Input: Email, Password, Login Type
    Output: Account Authentication and redirecting to Dashboard
    """
    if not session.get("email"):
        form = LoginForm()
        if form.validate_on_submit():
            temp = mongo.db.user.find_one({"email": form.email.data}, {"email", "pwd"})
            if (
                temp is not None
                and temp["email"] == form.email.data
                and (
                    bcrypt.checkpw(form.password.data.encode("utf-8"), temp["pwd"])
                    or temp["temp"] == form.password.data
                )
            ):
                flash("You have been logged in!", "success")
                session["email"] = temp["email"]
                # session['login_type'] = form.type.data
                return redirect(url_for("dashboard"))
            else:
                flash(
                    "Login Unsuccessful. Please check username and password", "danger"
                )
    else:
        return redirect(url_for("home"))
    return render_template("login.html", title="Login", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """
    logout() function just clears out the session and returns success
    route "/logout" will redirect to logout() function.
    Output: session clear
    """
    session.clear()
    return "success"


@app.route("/register", methods=["GET", "POST"])
def register():
    # ############################
    # register() function displays the Registration portal (register.html) template
    # route "/register" will redirect to register() function.
    # RegistrationForm() called and if the form is submitted then various values are fetched and updated into database
    # Input: Username, Email, Password, Confirm Password
    # Output: Value update in database and redirected to home login page
    # ##########################
    if not session.get("email"):
        form = RegistrationForm()
        if form.validate_on_submit():
            if request.method == "POST":
                username = request.form.get("username")
                email = request.form.get("email")
                password = request.form.get("password")
                mongo.db.user.insert(
                    {
                        "name": username,
                        "email": email,
                        "pwd": bcrypt.hashpw(
                            password.encode("utf-8"), bcrypt.gensalt()
                        ),
                    }
                )
            flash(f"Account created for {form.username.data}!", "success")
            return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


"""
@app.route("/calories", methods=['GET', 'POST'])
def calories():
    # ############################
    # calorie() function displays the Calorieform (calories.html) template
    # route "/calories" will redirect to calories() function.
    # CalorieForm() called and if the form is submitted then various values are fetched and updated into the database entries
    # Input: Email, date, food, burnout
    # Output: Value update in database and redirected to home page
    # ##########################
    now = datetime.now()
    now = now.strftime('%Y-%m-%d')

    get_session = session.get('email')
    if get_session is not None:
        form = CalorieForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                email = session.get('email')
                food = request.form.get('food')
                cals = food.split(" ")
                cals = int(cals[1][1:len(cals[1]) - 1])
                burn = request.form.get('burnout')

                temp = mongo.db.calories.find_one({'email': email}, {
                    'email', 'calories', 'burnout'})
                if temp is not None:
                    mongo.db.calories.update({'email': email}, {'$set': {
                                             'calories': temp['calories'] + cals, 'burnout': temp['burnout'] + int(burn)}})
                else:
                    mongo.db.calories.insert(
                        {'date': now, 'email': email, 'calories': cals, 'burnout': int(burn)})
                flash(f'Successfully updated the data', 'success')
                return redirect(url_for('calories'))
    else:
        return redirect(url_for('home'))
    return render_template('calories.html', form=form, time=now)
"""


@app.route("/user_profile", methods=["GET", "POST"])
def user_profile():
    # ############################
    # user_profile() function displays the UserProfileForm (user_profile.html) template
    # route "/user_profile" will redirect to user_profile() function.
    # user_profile() called and if the form is submitted then various values are fetched and updated into the database entries
    # Input: Email, height, weight, goal, Target weight
    # Output: Value update in database and redirected to home login page
    # ##########################
    if session.get("email"):
        form = UserProfileForm()
        if form.validate_on_submit():
            if request.method == "POST":
                email = session.get("email")
                weight = request.form.get("weight")
                height = request.form.get("height")
                goal = request.form.get("goal")
                target_weight = request.form.get("target_weight")
                temp = mongo.db.profile.find_one(
                    {"email": email}, {"height", "weight", "goal", "target_weight"}
                )
                if temp is not None:
                    mongo.db.profile.update(
                        {"email": email},
                        {
                            "$set": {
                                "weight": temp["weight"],
                                "height": temp["height"],
                                "goal": temp["goal"],
                                "target_weight": temp["target_weight"],
                            }
                        },
                    )
                else:
                    mongo.db.profile.insert(
                        {
                            "email": email,
                            "height": height,
                            "weight": weight,
                            "goal": goal,
                            "target_weight": target_weight,
                        }
                    )

            flash(f"User Profile Updated", "success")
            return render_template("display_profile.html", status=True, form=form)
    else:
        return redirect(url_for("login"))
    return render_template("user_profile.html", status=True, form=form)


"""
@app.route("/history", methods=['GET'])
def history():
    # ############################
    # history() function displays the Historyform (history.html) template
    # route "/history" will redirect to history() function.
    # HistoryForm() called and if the form is submitted then various values are fetched and update into the database entries
    # Input: Email, date
    # Output: Value fetched and displayed
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = HistoryForm()
    return render_template('history.html', form=form)


@app.route("/ajaxhistory", methods=['POST'])
def ajaxhistory():
    # ############################
    # ajaxhistory() is a POST function displays the fetches the various information from database
    # route "/ajaxhistory" will redirect to ajaxhistory() function.
    # Details corresponding to given email address are fetched from the database entries
    # Input: Email, date
    # Output: date, email, calories, burnout
    # ##########################
    email = get_session = session.get('email')
    print(email)
    if get_session is not None:
        if request.method == "POST":
            date = request.form.get('date')
            res = mongo.db.calories.find_one({'email': email, 'date': date}, {
                                             'date', 'email', 'calories', 'burnout'})
            if res:
                return json.dumps({'date': res['date'], 'email': res['email'], 'burnout': res['burnout'], 'calories': res['calories']}), 200, {
                    'ContentType': 'application/json'}
            else:
                return json.dumps({'date': "", 'email': "", 'burnout': "", 'calories': ""}), 200, {
                    'ContentType': 'application/json'}
"""


@app.route("/friends", methods=["GET"])
def friends():
    # ############################
    # friends() function displays the list of friends corrsponding to given email
    # route "/friends" will redirect to friends() function which redirects to friends.html page.
    # friends() function will show a list of "My friends", "Add Friends" functionality, "send Request" and Pending Approvals" functionality
    # Details corresponding to given email address are fetched from the database entries
    # Input: Email
    # Output: My friends, Pending Approvals, Sent Requests and Add new friends
    # ##########################
    email = session.get("email")

    myFriends = list(
        mongo.db.friends.find(
            {"sender": email, "accept": True}, {"sender", "receiver", "accept"}
        )
    )
    myFriendsList = list()

    for f in myFriends:
        myFriendsList.append(f["receiver"])

    print(myFriends)
    allUsers = list(mongo.db.user.find({}, {"name", "email"}))

    pendingRequests = list(
        mongo.db.friends.find(
            {"sender": email, "accept": False}, {"sender", "receiver", "accept"}
        )
    )
    pendingReceivers = list()
    for p in pendingRequests:
        pendingReceivers.append(p["receiver"])

    pendingApproves = list()
    pendingApprovals = list(
        mongo.db.friends.find(
            {"receiver": email, "accept": False}, {"sender", "receiver", "accept"}
        )
    )
    for p in pendingApprovals:
        pendingApproves.append(p["sender"])

    print(pendingApproves)

    # print(pendingRequests)
    return render_template(
        "friends.html",
        allUsers=allUsers,
        pendingRequests=pendingRequests,
        active=email,
        pendingReceivers=pendingReceivers,
        pendingApproves=pendingApproves,
        myFriends=myFriends,
        myFriendsList=myFriendsList,
    )


@app.route("/ajaxsendrequest", methods=["POST"])
def ajaxsendrequest():
    # ############################
    # ajaxsendrequest() is a function that updates friend request information into database
    # route "/ajaxsendrequest" will redirect to ajaxsendrequest() function.
    # Details corresponding to given email address are fetched from the database entries and send request details updated
    # Input: Email, receiver
    # Output: DB entry of receiver info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        receiver = request.form.get("receiver")
        res = mongo.db.friends.insert_one(
            {"sender": email, "receiver": receiver, "accept": False}
        )
        if res:
            return (
                json.dumps({"status": True}),
                200,
                {"ContentType": "application/json"},
            )
    return json.dumps({"status": False}), 500, {"ContentType:": "application/json"}


@app.route("/ajaxcancelrequest", methods=["POST"])
def ajaxcancelrequest():
    # ############################
    # ajaxcancelrequest() is a function that updates friend request information into database
    # route "/ajaxcancelrequest" will redirect to ajaxcancelrequest() function.
    # Details corresponding to given email address are fetched from the database entries and cancel request details updated
    # Input: Email, receiver
    # Output: DB deletion of receiver info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        receiver = request.form.get("receiver")
        res = mongo.db.friends.delete_one({"sender": email, "receiver": receiver})
        if res:
            return (
                json.dumps({"status": True}),
                200,
                {"ContentType": "application/json"},
            )
    return json.dumps({"status": False}), 500, {"ContentType:": "application/json"}


@app.route("/ajaxapproverequest", methods=["POST"])
def ajaxapproverequest():
    # ############################
    # ajaxapproverequest() is a function that updates friend request information into database
    # route "/ajaxapproverequest" will redirect to ajaxapproverequest() function.
    # Details corresponding to given email address are fetched from the database entries and approve request details updated
    # Input: Email, receiver
    # Output: DB updation of accept as TRUE info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        receiver = request.form.get("receiver")
        print(email, receiver)
        res = mongo.db.friends.update_one(
            {"sender": receiver, "receiver": email},
            {"$set": {"sender": receiver, "receiver": email, "accept": True}},
        )
        mongo.db.friends.insert_one(
            {"sender": email, "receiver": receiver, "accept": True}
        )
        if res:
            return (
                json.dumps({"status": True}),
                200,
                {"ContentType": "application/json"},
            )
    return json.dumps({"status": False}), 500, {"ContentType:": "application/json"}


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # ############################
    # dashboard() function displays the dashboard.html template
    # route "/dashboard" will redirect to dashboard() function.
    # dashboard() called and displays the list of activities
    # Output: redirected to dashboard.html
    # ##########################
    return render_template("dashboard.html", title="Dashboard")


if __name__ == "__main__":
    app.run(debug=True)
