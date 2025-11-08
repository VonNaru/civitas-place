from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, render_template_string, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
# small secret for session if later used (change for production)
app.secret_key = 'dev-secret'

# JSON file location for storing users
JSON_FILE = 'user.json'

def load_users_from_file(path=JSON_FILE):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except Exception as e:
        print(f"Failed to load users from {path}:", e)
    return {}

def save_users_to_file(users_dict, path=JSON_FILE):
    try:
        dirpath = os.path.dirname(path)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        tmp_path = path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(users_dict, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception as e:
        print(f"Failed to save users to {path}:", e)

# Load users at startup
users = load_users_from_file()

@app.route('/')
def index():
    return redirect('/Login.html')

@app.route('/register', methods=['POST'])
def register():
    form = request.form
    name = form.get('name','').strip()
    email = form.get('email','').strip()
    password = form.get('password','').strip()
    
    errors = []
    if not name:
        errors.append('Nama lengkap harus diisi.')
    if not email:
        errors.append('Email harus diisi.')
    if not password:
        errors.append('Password harus diisi.')

    if errors:
        # Save the submitted values so the form can be pre-filled after redirect
        session['register_form'] = {'name': name, 'email': email}
        # Flash errors and redirect back to the register page so user sees them in the form
        for e in errors:
            flash(e)
        return redirect(url_for('register_page'))

    username = email
    if username in users:
        # Preserve entered values so user doesn't need to retype
        session['register_form'] = {'name': name, 'email': email}
        flash('Username/email sudah terdaftar')
        return redirect(url_for('register_page'))

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    users[username] = {"username": username, "password_hash": hashed_password, "full_name": name}
    save_users_to_file(users)
    # After successful registration redirect user to login page
    return redirect('/Login.html')

@app.route('/login', methods=['POST'])
def login():
    form = request.form
    email = form.get('email','').strip()
    password = form.get('password','').strip()
    
    if not email or not password:
        # keep entered email to prefill after redirect
        session['login_form'] = {'email': email}
        flash('Email dan password harus diisi')
        return redirect(url_for('login_page'))
    
    user = users.get(email)
    if not user or not check_password_hash(user['password_hash'], password):
        session['login_form'] = {'email': email}
        flash('Username atau password salah')
        return redirect(url_for('login_page'))

    # Successful login -> redirect to home page
    return redirect('/Home_pages.html')

# Routes untuk halaman HTML
@app.route('/Login.html')
def login_page():
    form_data = session.pop('login_form', {})
    return render_template('Login.html', form_data=form_data)

@app.route('/Register.html')
def register_page():
    form_data = session.pop('register_form', {})
    return render_template('Register.html', form_data=form_data)

@app.route('/Home_pages.html')
def home_page():
    return render_template('Home_pages.html')

if __name__ == '__main__':
    app.run(debug=True)
