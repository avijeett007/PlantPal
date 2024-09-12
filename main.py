import os
import base64
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from urllib.parse import urlparse
from utils.openai_vision import analyze_plant_image
from models import db, User, SearchHistory
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///plant_tracker.db'
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    if current_user.credits <= 0:
        return jsonify({'error': 'No credits available. Please subscribe to continue using the service.'}), 403

    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    try:
        result = analyze_plant_image(image)
        current_user.credits -= 1
        image_data = base64.b64encode(image.read()).decode('utf-8')
        search_history = SearchHistory(
            user_id=current_user.id,
            plant_name=result['name'],
            image_data=image_data,
            locations=result['locations'],
            benefits=result['benefits'],
            care_tips=result['care_tips']
        )
        db.session.add(search_history)
        db.session.commit()
        print("Structured result:", result)
        return jsonify(result)
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash('Please use a different username.')
            return redirect(url_for('register'))
        user = User.query.filter_by(email=email).first()
        if user is not None:
            flash('Please use a different email address.')
            return redirect(url_for('register'))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=request.form.get('remember_me'))
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/search_history')
@login_required
def search_history():
    searches = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.timestamp.desc()).all()
    return render_template('search_history.html', searches=searches)

@app.route('/get_credits')
@login_required
def get_credits():
    return jsonify({'credits': current_user.credits})

@app.route('/search_detail/<int:search_id>')
@login_required
def search_detail(search_id):
    search = SearchHistory.query.get_or_404(search_id)
    if search.user_id != current_user.id:
        abort(403)
    return render_template('search_detail.html', search=search)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
