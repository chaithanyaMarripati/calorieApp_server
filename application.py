from datetime import datetime

import bcrypt
import smtplib

# from apps import App
from flask import json
# from utilities import Utilities
from flask import render_template, session, url_for, flash, redirect, request, Flask
from flask_mail import Mail
from flask_pymongo import PyMongo
from tabulate import tabulate
from forms import HistoryForm, RegistrationForm, LoginForm, CalorieForm, UserProfileForm, EnrollForm
from apps import Mongo


app = Flask(__name__)
app.secret_key = 'secret'
# mongo contains test database details
mongo = Mongo().mongoClient

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "bogusdummy123@gmail.com"
app.config['MAIL_PASSWORD'] = "helloworld123!"
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
    if session.get('email'):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    """"
    login() function displays the Login form (login.html) template
    route "/login" will redirect to login() function.
    LoginForm() called and if the form is submitted then various values are fetched and verified from the database entries
    Input: Email, Password, Login Type
    Output: Account Authentication and redirecting to Dashboard
    """
    if not session.get('email'):
        form = LoginForm()
        if form.validate_on_submit():
            email = session.get('email')
            temp = mongo.user.find_one({'email': form.email.data}, {
                'email', 'pwd','name'})
            print("temp value is here", temp)
            if temp is not None and temp['email'] == form.email.data and (
                bcrypt.checkpw(
                    form.password.data.encode("utf-8"),
                    temp['pwd']) ):
                flash('You have been logged in!', 'success')
                session['email'] = temp['email']
                session['name'] = temp['name']
                #session['login_type'] = form.type.data
                data = mongo.profile.find_one({'email': temp['email']}, {'weight', 'height', 'target_weight'})
                if data:
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('user_profile')) #render_template('user_profile.html', title = "Details")
            else:
                flash(
                    'Login Unsuccessful. Please check username and password',
                    'danger')
    else:
        return redirect(url_for('home'))
    return render_template(
        'login.html',
        title='Login',
        form=form)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    """
    logout() function just clears out the session and returns success
    route "/logout" will redirect to logout() function.
    Output: session clear
    """
    session.clear()
    return "success"

@app.route("/display_profile", methods=['GET', 'POST'])
def display_profile():
    """
    user_profile() function displays the UserProfileForm (user_profile.html) template
    route "/user_profile" will redirect to user_profile() function.
    user_profile() called and if the form is submitted then various values are fetched and updated into the database entries
    Input: Email, height, weight, goal, Target weight
    Output: Value update in database and redirected to home login page
    """
    if session.get('email'):
        email = session.get('email')
        data = mongo.profile.find_one({'email': email}, {'weight', 'height', 'target_weight'})
        return render_template('display_profile.html', title = 'Profile', data=data, status=True)


@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    register() function displays the Registration portal (register.html) template
    route "/register" will redirect to register() function.
    RegistrationForm() called and if the form is submitted then various values are fetched and updated into database
    Input: Username, Email, Password, Confirm Password
    Output: Value update in database and redirected to home login page
    """
    if not session.get('email'):
        form = RegistrationForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
                mongo.user.insert_one({'name': username, 'email': email, 'pwd': bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt())})
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/calories", methods=['GET', 'POST'])
def calories():
    """
    calorie() function displays the Calorieform (calories.html) template
    route "/calories" will redirect to calories() function.
    CalorieForm() called and if the form is submitted then various values are fetched and updated into the database entries
    Input: Email, date, food, burnout
    Output: Value update in database and redirected to home page
    """
    now = datetime.now()
    now = now.strftime('%Y-%m-%d')
    form = CalorieForm()
    get_session = session.get('email')
    if get_session is not None:
        
        if form.validate_on_submit():
            print(form,"this is the form")
            print(request,"this is the request ")
            if request.method == 'POST':
                email = session.get('email')
                date = request.form.get('date')
                food = request.form.get('food')
                # print(food)
                cals = food.split(" ")
                # print(cals)
                # flash(cals)
                # print(cals[-1][1:-1:],type(cals[1]))
                cals = int(cals[-1][1:-1:])
                burn = request.form.get('burnout')

                # temp = mongo.calories.find_one({'email': email}, {
                #     'email', 'calories', 'burnout'})
                # if temp is not None:
                #     mongo.calories.update({'email': email}, {'$set': {
                #                              'calories': temp['calories'] + cals, 'burnout': temp['burnout'] + int(burn)}})
                # else:
                mongo.calories.insert( {'date': date, 'email': email, 'calories': cals, 'burnout': int(burn)})
                flash(f'Successfully updated the data', 'success')
                return redirect(url_for('calories'))
    else:
        return redirect(url_for('home'))
    return render_template('calories.html', title = 'Calories', form=form, time=now)


@app.route("/user_profile", methods=['GET', 'POST'])
def user_profile():
    """
    user_profile() function displays the UserProfileForm (user_profile.html) template
    route "/user_profile" will redirect to user_profile() function.
    user_profile() called and if the form is submitted then various values are fetched and updated into the database entries
    Input: Email, height, weight, goal, Target weight
    Output: Value update in database and redirected to home login page
    """
    if session.get('email'):
        form = UserProfileForm()
        if form.validate_on_submit():
            email = session.get('email')
            if request.method == 'POST':
                weight = request.form.get('weight')
                height = request.form.get('height')
                goal = request.form.get('goal')
                target_weight = request.form.get('target_weight')
                temp = mongo.profile.find_one({'email': email}, {
                    'height', 'weight', 'goal', 'target_weight'})
                if temp is not None:
                    mongo.profile.update_one({'email': email},
                                            {"$set": {'weight': weight,
                                                      'height': height,
                                                      'goal': goal,
                                                      'target_weight': target_weight}})
                else:
                    mongo.profile.insert_one({'email': email,
                                             'height': height,
                                             'weight': weight,
                                             'goal': goal,
                                             'target_weight': target_weight})
            data = mongo.profile.find_one({'email': email}, {'weight', 'height', 'target_weight'})
            flash(f'User Profile Updated', 'success')
            return render_template('display_profile.html',data=data, status=True, form=form)
    else:
        return redirect(url_for('login'))
    return render_template('user_profile.html', status=True, form=form)


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
            res = mongo.calories.find_one({'email': email, 'date': date}, {
                                             'date', 'email', 'calories', 'burnout'})
            if res:
                return json.dumps({'date': res['date'], 'email': res['email'], 'burnout': res['burnout'], 'calories': res['calories']}), 200, {
                    'ContentType': 'application/json'}
            else:
                return json.dumps({'date': "", 'email': "", 'burnout': "", 'calories': ""}), 200, {
                    'ContentType': 'application/json'}


@app.route("/friends", methods=['GET', 'POST'])
def friends():
    # ############################
    # friends() function displays the list of friends corrsponding to given email
    # route "/friends" will redirect to friends() function which redirects to friends.html page.
    # friends() function will show a list of "My friends", "Add Friends" functionality, "send Request" and Pending Approvals" functionality
    # Details corresponding to given email address are fetched from the database entries
    # Input: Email
    # Output: My friends, Pending Approvals, Sent Requests and Add new friends
    # ##########################

    # Render a template with the search results
    email = session.get('email')

    myFriends = list(mongo.friends.find(
        {'sender': email, 'accept': True}, {'sender', 'receiver', 'accept'}))
    myFriendsList = list()

    for f in myFriends:
        myFriendsList.append(f['receiver'])

    # allUsers = list(mongo.user.find({}, {'name', 'email'}))

    sendingemail = request.form.get('email')
    sendingRequest = ""


    pendingRequests = list(mongo.friends.find(
        {'sender': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    pendingReceivers = list()
    for p in pendingRequests:
        pendingReceivers.append(p['receiver'])

    pendingApproves = list()
    pendingApprovals = list(mongo.friends.find(
        {'receiver': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    for p in pendingApprovals:
        pendingApproves.append(p['sender'])

    if sendingemail and sendingemail not in pendingReceivers and sendingemail not in pendingApproves and sendingemail not in myFriendsList:
        sendingRequest = mongo.user.find_one({'email': sendingemail},{'name','email'})

    if( type(sendingRequest) is  str and len(sendingRequest) ==0 ):
        sendingRequest = None
    return render_template('friends.html', title = 'Friends', sendingRequest = sendingRequest, pendingRequests=pendingRequests, active=email,
                           pendingReceivers=pendingReceivers, pendingApproves=pendingApproves, myFriends=myFriends, myFriendsList=myFriendsList)


@app.route("/send_email", methods=['GET','POST'])
def send_email():
    # ############################
    # send_email() function shares Calorie History with friend's email
    # route "/send_email" will redirect to send_email() function which redirects to friends.html page.
    # Input: Email
    # Output: Calorie History Received on specified email
    # ##########################
    email = session.get('email')
    data = list(mongo.calories.find({'email': email}, {'date','email','calories','burnout'}))
    table = [['Date','Email ID','Calories','Burnout']]
    for a in data:
        tmp = [a['date'],a['email'],a['calories'],a['burnout']] 
        table.append(tmp) 
    
    friend_email = str(request.form.get('share')).strip()
    friend_email = str(friend_email).split(',')
    server = smtplib.SMTP_SSL("smtp.gmail.com",465)
    #Storing sender's email address and password
    sender_email = "calorie.app.server@gmail.com"
    sender_password = "upmicpgobxxuqapp"
    
    #Logging in with sender details
    server.login(sender_email,sender_password)
    message = 'Subject: Calorie History\n\n Your Friend wants to share their calorie history with you!\n {}'.format(tabulate(table))
    for e in friend_email:
        server.sendmail(sender_email,e,message)
        
    server.quit()
    
    myFriends = list(mongo.friends.find(
        {'sender': email, 'accept': True}, {'sender', 'receiver', 'accept'}))
    myFriendsList = list()
    
    for f in myFriends:
        myFriendsList.append(f['receiver'])

    allUsers = list(mongo.user.find({}, {'name', 'email'}))
    
    pendingRequests = list(mongo.friends.find(
        {'sender': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    pendingReceivers = list()
    for p in pendingRequests:
        pendingReceivers.append(p['receiver'])

    pendingApproves = list()
    pendingApprovals = list(mongo.friends.find(
        {'receiver': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    for p in pendingApprovals:
        pendingApproves.append(p['sender'])
        
    return render_template('friends.html', allUsers=allUsers, pendingRequests=pendingRequests, active=email,
                           pendingReceivers=pendingReceivers, pendingApproves=pendingApproves, myFriends=myFriends, myFriendsList=myFriendsList)



@app.route("/ajaxsendrequest", methods=['POST'])
def ajaxsendrequest():
    # ############################
    # ajaxsendrequest() is a function that updates friend request information into database
    # route "/ajaxsendrequest" will redirect to ajaxsendrequest() function.
    # Details corresponding to given email address are fetched from the database entries and send request details updated
    # Input: Email, receiver
    # Output: DB entry of receiver info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        res = mongo.friends.insert_one(
            {'sender': email, 'receiver': receiver, 'accept': False})
        if res:
            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'}
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'}


@app.route("/ajaxcancelrequest", methods=['POST'])
def ajaxcancelrequest():
    # ############################
    # ajaxcancelrequest() is a function that updates friend request information into database
    # route "/ajaxcancelrequest" will redirect to ajaxcancelrequest() function.
    # Details corresponding to given email address are fetched from the database entries and cancel request details updated
    # Input: Email, receiver
    # Output: DB deletion of receiver info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        res = mongo.friends.delete_one(
            {'sender': email, 'receiver': receiver})
        if res:
            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'}
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'}


@app.route("/ajaxapproverequest", methods=['POST'])
def ajaxapproverequest():
    # ############################
    # ajaxapproverequest() is a function that updates friend request information into database
    # route "/ajaxapproverequest" will redirect to ajaxapproverequest() function.
    # Details corresponding to given email address are fetched from the database entries and approve request details updated
    # Input: Email, receiver
    # Output: DB updation of accept as TRUE info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        print(email, receiver)
        res = mongo.friends.update_one({'sender': receiver, 'receiver': email}, {
                                          "$set": {'sender': receiver, 'receiver': email, 'accept': True}})
        mongo.friends.insert_one(
            {'sender': email, 'receiver': receiver, 'accept': True})
        if res:
            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'}
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'}


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    # ############################
    # dashboard() function displays the dashboard.html template
    # route "/dashboard" will redirect to dashboard() function.
    # dashboard() called and displays the list of activities
    # Output: redirected to dashboard.html
    # ##########################
    return render_template('dashboard.html', title='Dashboard')
def fetch():
    email = session.get('email')
    return list(mongo.user.find({'Email': email},{'Status'}))

@app.route("/yoga", methods=['GET', 'POST'])
def yoga():
    # ############################
    # yoga() function displays the yoga.html template
    # route "/yoga" will redirect to yoga() function.
    # A page showing details about yoga is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "yoga"
                status = mongo.user.find_one({'Email': email, 'Status': enroll},{'Email','Status'})
                print(status)
                if status:
                    flash(
                        f'You have already enrolled in our {enroll} plan!','warning')
                else:
                    mongo.user.insert({'Email': email, 'Status': enroll})
                    flash(
                        f' You have succesfully enrolled in our {enroll} plan!',
                        'success')
            data = fetch()
            return render_template('new_dashboard.html', data = data, form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('yoga.html', title='Yoga', form=form)


@app.route("/swim", methods=['GET', 'POST'])
def swim():
    # ############################
    # swim() function displays the swim.html template
    # route "/swim" will redirect to swim() function.
    # A page showing details about swimming is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "swimming"
                status = mongo.user.find_one({'Email': email, 'Status': enroll},{'Email','Status'})
                if status:
                    flash(
                        f'You have already enrolled in our {enroll} plan!','warning')
                else:
                    mongo.user.insert({'Email': email, 'Status': enroll})
                    flash(
                        f' You have succesfully enrolled in our {enroll} plan!',
                        'success')
            data = fetch()
            return render_template('new_dashboard.html', data = data, form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('swim.html', title='Swim', form=form)


@app.route("/abbs", methods=['GET', 'POST'])
def abbs():
    # ############################
    # abbs() function displays the abbs.html template
    # route "/abbs" will redirect to abbs() function.
    # A page showing details about abbs workout is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "abbs"
                status = mongo.user.find_one({'Email': email, 'Status': enroll},{'Email','Status'})
                if status:
                    flash(
                        f'You have already enrolled in our {enroll} plan!','warning')
                else:
                    mongo.user.insert({'Email': email, 'Status': enroll})
                    flash(
                        f' You have succesfully enrolled in our {enroll} plan!',
                        'success')
            data = fetch()
            return render_template('new_dashboard.html', data = data, form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('abbs.html', title='Abbs Smash!', form=form)


@app.route("/belly", methods=['GET', 'POST'])
def belly():
    # ############################
    # belly() function displays the belly.html template
    # route "/belly" will redirect to belly() function.
    # A page showing details about belly workout is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "belly"
                status = mongo.user.find_one({'Email': email, 'Status': enroll},{'Email','Status'})
                if status:
                    flash(
                        f'You have already enrolled in our {enroll} plan!','warning')
                else:
                    mongo.user.insert({'Email': email, 'Status': enroll})
                    flash(
                        f' You have succesfully enrolled in our {enroll} plan!',
                        'success')
            data = fetch()
            return render_template('new_dashboard.html', data = data, form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('belly.html', title='Belly Burner', form=form)


@app.route("/core", methods=['GET', 'POST'])
def core():
    # ############################
    # core() function displays the belly.html template
    # route "/core" will redirect to core() function.
    # A page showing details about core workout is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "core"
                status = mongo.user.find_one({'Email': email, 'Status': enroll},{'Email','Status'})
                if status:
                    flash(
                        f'You have already enrolled in our {enroll} plan!','warning')
                else:
                    mongo.user.insert({'Email': email, 'Status': enroll})
                    flash(
                        f' You have succesfully enrolled in our {enroll} plan!',
                        'success')
            data = fetch()
            return render_template('new_dashboard.html', data = data, form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('core.html', title='Core Conditioning', form=form)


@app.route("/gym", methods=['GET', 'POST'])
def gym():
    # ############################
    # gym() function displays the gym.html template
    # route "/gym" will redirect to gym() function.
    # A page showing details about gym plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "gym"
                status = mongo.user.find_one({'Email': email, 'Status': enroll},{'Email','Status'})
                if status:
                    flash(
                        f'You have already enrolled in our {enroll} plan!','warning')
                else:
                    mongo.user.insert({'Email': email, 'Status': enroll})
                    flash(
                        f' You have succesfully enrolled in our {enroll} plan!',
                        'success')
            data = fetch()
            return render_template('new_dashboard.html', data = data, form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('gym.html', title='Gym', form=form)

@app.route("/walk", methods=['GET', 'POST'])
def walk():
    # ############################
    # walk() function displays the walk.html template
    # route "/walk" will redirect to walk() function.
    # A page showing details about walk plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "walk"
                status = mongo.user.find_one({'Email': email, 'Status': enroll},{'Email','Status'})
                if status:
                    flash(
                        f'You have already enrolled in our {enroll} plan!','warning')
                else:
                    mongo.user.insert({'Email': email, 'Status': enroll})
                    flash(
                        f' You have succesfully enrolled in our {enroll} plan!',
                        'success')
            data = fetch()
            return render_template('new_dashboard.html', data = data, form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('walk.html', title='Walk', form=form)

@app.route("/dance", methods=['GET', 'POST'])
def dance():
    # ############################
    # dance() function displays the dance.html template
    # route "/dance" will redirect to dance() function.
    # A page showing details about dance plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "dance"
                status = mongo.user.find_one({'Email': email, 'Status': enroll},{'Email','Status'})
                if status:
                    flash(
                        f'You have already enrolled in our {enroll} plan!','warning')
                else:
                    mongo.user.insert({'Email': email, 'Status': enroll})
                    flash(
                        f' You have succesfully enrolled in our {enroll} plan!',
                        'success')
            data = fetch()
            return render_template('new_dashboard.html', data = data, form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('dance.html', title='Dance', form=form)

@app.route("/hrx", methods=['GET', 'POST'])
def hrx():
    # ############################
    # hrx() function displays the hrx.html template
    # route "/hrx" will redirect to hrx() function.
    # A page showing details about hrx plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "hrx"
                status = mongo.user.find_one({'Email': email, 'Status': enroll},{'Email','Status'})
                if status:
                    flash(
                        f'You have already enrolled in our {enroll} plan!','warning')
                else:
                    mongo.user.insert({'Email': email, 'Status': enroll})
                    flash(
                        f' You have succesfully enrolled in our {enroll} plan!',
                        'success')
            data = fetch()
            return render_template('new_dashboard.html', data = data, form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('hrx.html', title='HRX', form=form)

# @app.route("/ajaxdashboard", methods=['POST'])
# def ajaxdashboard():
#     # ############################
#     # login() function displays the Login form (login.html) template
#     # route "/login" will redirect to login() function.
#     # LoginForm() called and if the form is submitted then various values are fetched and verified from the database entries
#     # Input: Email, Password, Login Type
#     # Output: Account Authentication and redirecting to Dashboard
#     # ##########################
#     email = get_session = session.get('email')
#     print(email)
#     if get_session is not None:
#         if request.method == "POST":
#             result = mongo.db.user.find_one(
#                 {'email': email}, {'email', 'Status'})
#             if result:
#                 return json.dumps({'email': result['email'], 'Status': result['result']}), 200, {
#                     'ContentType': 'application/json'}
#             else:
#                 return json.dumps({'email': "", 'Status': ""}), 200, {
#                     'ContentType': 'application/json'}

# Define a route for BMI calculation and workout suggestions
@app.route('/workout_suggestions', methods=['GET','POST'])
def workout_suggestions():
    email = session.get('email')

    # Assuming you have already created a MongoClient and connected to the database
    # client = MongoClient("mongodb://localhost:27017")
    # db = client["your_database_name"]

    # Define the collection you want to query

    # Query data based on a specific condition
    result = mongo.profile.find_one({'email': email},{'height', 'weight', 'target_weight'})

    height_m = int(result['height']) / 100.0
    weight_kg = int(result['weight'])
    if height_m <= 0:
        raise ValueError("Height must be a positive value.")
    
    if weight_kg <= 0:
        raise ValueError("Weight must be a positive value.")
    
    bmi =  weight_kg / (height_m ** 2)
    email = session.get('email')
    suggestions = []

    # Determine the BMI category
    suggestions.append("Your BMI is "+str(int(bmi))+".")
    if bmi < 18.5:
        # Suggest workouts for Underweight category
        suggestions.append("So, this indiactes you are in the Underweight category.")
        suggestions.append("To gain weight: Focus on strength training and calorie surplus.")
        # Include specific workout plans for Underweight
        
        # Strength Training
        suggestions.append("Week 1-8 (3-4 days a week): Strength Training")
        suggestions.append("Exercise 1: Bench Press - 3 sets of 8-10 reps")
        suggestions.append("Exercise 2: Deadlift - 3 sets of 6-8 reps")
        suggestions.append("Exercise 3: Squats - 3 sets of 8-10 reps")
        suggestions.append("Exercise 4: Pull-Ups - 3 sets of 6-8 reps (if available)")
        # Suggested diet: Maintain a calorie surplus (e.g., increase calorie intake by 300-500 calories/day).

    elif 18.5 <= bmi < 25.0:
        # Suggest workouts for Normal weight category
        suggestions.append("So, this indiactes you are in the Normal weight category.")
        suggestions.append("To maintain weight: Maintain a balanced workout routine and calorie intake.")
        # Include specific workout plans for Normal weight
        
        # Balanced Workout
        suggestions.append("Week 1-8 (3-4 days a week): Balanced Workout")
        suggestions.append("Exercise 1: Squats - 3 sets of 12 reps")
        suggestions.append("Exercise 2: Push-Ups - 3 sets of 10 reps")
        suggestions.append("Exercise 3: Planks - 3 sets of 30 seconds")
        suggestions.append("Exercise 4: Dumbbell Rows - 3 sets of 10 reps (if available)")
        # Suggested diet: Maintain a balanced diet with enough calories to maintain weight.

    elif 25.0 <= bmi :
        # Suggest workouts for Overweight category
        suggestions.append("So, this indiactes you are in the Overweight category.")
        suggestions.append("To lose weight: Focus on cardio and maintain a calorie deficit.")
        # Include specific workout plans for Overweight
        
        # High-Intensity Interval Training (HIIT)
        suggestions.append("Week 1-2 (3 days a week): High-Intensity Interval Training (HIIT)")
        suggestions.append("Exercise 1: Jumping Jacks - 45 seconds, Rest 15 seconds")
        suggestions.append("Exercise 2: Burpees - 45 seconds, Rest 15 seconds")
        suggestions.append("Exercise 3: Mountain Climbers - 45 seconds, Rest 15 seconds")
        suggestions.append("Repeat 3 exercises for 4 sets")
        # Suggested diet: Maintain a calorie deficit (e.g., reduce calorie intake by 500 calories/day).

        # Cardio Workout
        suggestions.append("Week 3-4 (3 days a week): Cardio Workout")
        suggestions.append("Exercise 1: Running - 30 minutes")
        suggestions.append("Exercise 2: Cycling - 30 minutes")
        suggestions.append("Exercise 3: Jump Rope - 30 minutes")
        # Suggested diet: Continue maintaining a calorie deficit.

    suggestions.append("You must maintain the workout to achive your taget")

    return render_template('suggestion.html', title='Suggestion',status=True, data = suggestions)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0",port=3000)
