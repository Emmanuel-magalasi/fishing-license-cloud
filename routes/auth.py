from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import User, db
from forms import RegistrationForm, LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            surname=form.surname.data,
            other_names=form.other_names.data,
            date_of_birth=form.date_of_birth.data,
            national_id=form.national_id.data,
            phone_number=form.phone_number.data,
            alt_phone_number=form.alt_phone_number.data,
            email=form.email.data,
            physical_address=form.physical_address.data,
            district=form.district.data,
            role='user'
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page if next_page else url_for('main.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))