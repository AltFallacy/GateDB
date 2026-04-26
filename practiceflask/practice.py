from flask import Flask,render_template,url_for
from markupsafe import escape
from connectors.mysql_conns import mysql_conns
from users.User import User
from flask import request, redirect, abort
from flask_login import login_user,LoginManager,current_user,logout_user,login_required
from werkzeug.security import check_password_hash
from Auth.create_authdb import insert_user, get_user_by_id, create_authdb
from Auth.check_authdb import authenticate
from Auth.pending_req import PendingReq
from Auth.user_settings import UserSettings
from Auth.user_notes import UserNotes
from connectors.postgres_conns import postgres_conns
from connectors.sql_lite_conns import sq3_conns as sqlite_conns
from datetime import datetime
import sys
import os

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

app.config['SECRET_KEY']='development-key-1234'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
create_authdb()
pending_req = PendingReq()
pending_req.create_table()
user_settings = UserSettings()
user_settings.create_table()
user_notes = UserNotes()
user_notes.create_table()

@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)
    if user_data:
        return User(user_data[0], user_data[1], user_data[2],user_data[3])
    return None


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about', methods=['GET', 'POST'])
@login_required
def about():            
    if request.method == 'POST':
        user_notes.save_note(current_user.id, request.form.get("user_notes"))
        return redirect(url_for("about"))
        
    saved_note = user_notes.get_note(current_user.id)
    return render_template('about.html', saved_note=saved_note)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        env_type = request.form.get("env_type")
        db_type = request.form.get("db_type")
        host = request.form.get("host")
        username = request.form.get("username")
        password = request.form.get("password")
        database_name = request.form.get("database_name")
        
        user_settings.save_setting(current_user.id, env_type, db_type, host, username, password, database_name)
        return redirect(url_for("settings"))
        
    saved_configs = user_settings.get_all_settings(current_user.id)
    return render_template('settings.html', saved_configs=saved_configs)

@app.route('/settings/delete', methods=['POST'])
@login_required
def delete_setting():
    env_type = request.form.get("env_type")
    db_type = request.form.get("db_type")
    user_settings.delete_setting(current_user.id, env_type, db_type)
    return redirect(url_for("settings"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_data = authenticate(username, password)
        if user_data:
            user = User(user_data[0], user_data[1], user_data[2], user_data[3])
            login_user(user)
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid Username or Password")
    return render_template("login.html")

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        insert_user(username, password, role)
        return redirect(url_for("login"))
    return render_template('signup.html')

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/querybox')
@login_required
def querybox():
    if current_user.role != 'admin':
        abort(403)
    req_list = pending_req.get_all_req()
    return render_template("querybox.html",req_list=req_list)

@app.route('/my-requests')
@login_required
def my_requests():
    req_list = pending_req.get_user_reqs(current_user.id)
    return render_template("my_requests.html", req_list=req_list)

@app.route('/my-requests/delete/<request_id>', methods=['POST'])
@login_required
def delete_my_request(request_id):
    req = pending_req.get_req(request_id)
    # Ensure the user deleting the record actually owns it
    if req and str(req[1]) == str(current_user.id):
        pending_req.delete_req(request_id)
    return redirect(url_for('my_requests'))

@app.route('/my-requests/batch-delete', methods=['POST'])
@login_required
def batch_delete_requests():
    request_ids = request.form.getlist("request_ids")
    if not request_ids:
        return redirect(url_for('my_requests'))
        
    for rid in request_ids:
        req = pending_req.get_req(rid)
        if req and str(req[1]) == str(current_user.id):
            pending_req.delete_req(rid)
            
    return redirect(url_for('my_requests'))


def _handle_approve(request_id):
    req = pending_req.get_req(request_id)
    if not req:
        return
    sql_query = req[2]
    db_type_full = req[7]
    
    # Parse engine
    db_engine = "MySQL"
    if " (" in db_type_full:
        db_engine = db_type_full.split(" (")[1].replace(")", "")
    
    # Fetch Admin's Central DB credentials from their settings
    creds = user_settings.get_setting(current_user.id, "Admin Central", db_engine)
    if not creds:
        # If admin hasn't configured it, reject immediately
        pending_req.mark_rejected(request_id, current_user.id)
        from sqlite3 import connect
        conn = connect(pending_req.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE pending_requests SET result = ? WHERE id = ?", (f"System Error: Admin has not configured Admin Central ({db_engine}) credentials.", request_id))
        conn.commit()
        conn.close()
        return

    try:
        # Dynamically instantiate the correct engine based on Admin settings
        if db_engine == "MySQL":
            engine = mysql_conns(creds["host"], creds["username"], creds["password"], creds["database_name"])
        elif db_engine == "PostgreSQL":
            engine = postgres_conns(creds["host"], creds["username"], creds["password"], creds["database_name"])
        elif db_engine == "SQLite":
            engine = sqlite_conns(creds["database_name"])
        else:
            raise Exception(f"Unsupported database engine: {db_engine}")
            
        result = engine.execute(sql_query)
        pending_req.mark_approved(request_id, current_user.id, str(result))
    except Exception as e:
        # If the query fails (syntax error, etc.), reject it and save the error message
        pending_req.mark_rejected(request_id, current_user.id)
        # update the result column even for rejections so the user sees WHY it failed
        from sqlite3 import connect
        conn = connect(pending_req.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE pending_requests SET result = ? WHERE id = ?", (f"SQL Error: {str(e)}", request_id))
        conn.commit()
        conn.close()

def _handle_reject(request_id):
    pending_req.mark_rejected(request_id, current_user.id)

@app.route('/admin/approve/<request_id>')
@login_required
def approve_request(request_id):
    if current_user.role != 'admin':
        abort(403)
    _handle_approve(request_id)
    return redirect(url_for("querybox"))

@app.route('/admin/reject/<request_id>')
@login_required
def reject_request(request_id):
    if current_user.role != 'admin':
        abort(403)
    _handle_reject(request_id)
    return redirect(url_for("querybox"))

@app.route('/admin/batch-action', methods=['POST'])
@login_required
def batch_process():
    if current_user.role != 'admin':
        abort(403)
    
    action = request.form.get("action")
    request_ids = request.form.getlist("request_ids")
    
    if not request_ids:
        return redirect(url_for("querybox"))

    for rid in request_ids:
        if action == "approve":
            _handle_approve(rid)
        elif action == "reject":
            _handle_reject(rid)
            
    return redirect(url_for("querybox"))
    
@app.route("/submit-request", methods=["POST"])
@login_required
def submit_request():
    sql_query = request.form.get("sql_query")
    db_type_full = request.form.get("db_type")
    
    if not sql_query or not sql_query.strip():
        return "Query cannot be empty", 400

    # Parse full type: e.g. "My Personal (MySQL)"
    target_env = "Admin Central"
    db_engine = db_type_full
    if " (" in db_type_full:
        target_env = db_type_full.split(" (")[0]
        db_engine = db_type_full.split(" (")[1].replace(")", "")

    # Enforce single query policy
    statements = [q.strip() for q in sql_query.split(';') if q.strip()]
    if len(statements) > 1:
        return "Error: Please submit only ONE query at a time.", 400
    
    clean_query = statements[0] + ";" if statements else ""

    # ---- VISION B: LOCAL BYPASSING ----
    if target_env == "My Personal":
        # Look for credentials
        creds = user_settings.get_setting(current_user.id, "My Personal", db_engine)
        if not creds:
            return f"Error: No credentials saved for My Personal ({db_engine}). Please add them in Settings.", 400
        
        # Execute immediately
        result = None
        try:
            if db_engine == "MySQL":
                engine = mysql_conns(creds["host"], creds["username"], creds["password"], creds["database_name"])
                result = engine.execute(clean_query)
            elif db_engine == "PostgreSQL":
                engine = postgres_conns(creds["host"], creds["username"], creds["password"], creds["database_name"])
                result = engine.execute(clean_query)
            elif db_engine == "SQLite":
                engine = sqlite_conns(creds["database_name"])
                result = engine.execute(clean_query)
                
            # Log as automatically approved/bypassed
            pending_req.insert_req(
                user_id=current_user.id,
                sql_query=clean_query,
                db_type=db_type_full,
                status="approved",  # Bypass the queue
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                processed_by=current_user.id, # Self-approved
                processed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            # Fetch the ID we just inserted to append the result
            reqs = pending_req.get_user_reqs(current_user.id)
            latest_id = reqs[0][0]
            pending_req.mark_approved(latest_id, current_user.id, str(result))
            
            return f"Bypassed Approval: Query executed successfully! View results in My Requests."
            
        except Exception as e:
            return f"Execution Error: {str(e)}", 500

    # ---- STANDARD ROUTE: ADMIN CENTRAL QUEUE ----
    pending_req.insert_req(
        user_id=current_user.id,
        sql_query=clean_query,
        db_type=db_type_full,
        status="pending",
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        processed_by=None,
        processed_at=None
    )

    return "Request submitted for Admin Approval"

if __name__ == "__main__":
    from waitress import serve
    print("Starting GateDB Production Server with Waitress on port 5000...")
    serve(app, host='0.0.0.0', port=5000, threads=6)
