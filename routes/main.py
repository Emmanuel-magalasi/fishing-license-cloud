from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request
from flask_login import login_required, current_user
from datetime import datetime
from models import License, db
from forms import LicenseApplicationForm

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('main/home.html', title='Home')

@main.route('/dashboard')
@login_required
def dashboard():
    user_licenses = License.query.filter_by(user_id=current_user.id).order_by(License.created_at.desc()).all()
    return render_template('main/dashboard.html', title='Dashboard', licenses=user_licenses)

@main.route('/apply-license', methods=['GET', 'POST'])
@login_required
def apply_license():
    form = LicenseApplicationForm()
    if form.validate_on_submit():
        license = License(
            user_id=current_user.id,
            full_name=form.full_name.data,
            id_number=form.id_number.data,
            fishing_zone=form.fishing_zone.data,
            duration=form.duration.data,
            status='pending'
        )
        
        db.session.add(license)
        db.session.commit()
        
        flash('License application submitted successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/apply_license.html', title='Apply for License', form=form)

@main.route('/license/<int:license_id>')
@login_required
def view_license(license_id):
    license = License.query.get_or_404(license_id)
    if license.user_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to view this license.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/view_license.html', title='License Details', license=license)

@main.route('/make-payment/<int:license_id>', methods=['GET', 'POST'])
@login_required
def make_payment(license_id):
    license = License.query.get_or_404(license_id)
    if license.user_id != current_user.id:
        flash('You do not have permission to make payment for this license.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if license.payment_status == 'completed':
        flash('Payment has already been completed for this license.', 'info')
        return redirect(url_for('main.download_license', license_id=license_id))
    
    if not license.payment_method or not license.payment_amount:
        flash('Payment has not been initiated by admin yet.', 'warning')
        return redirect(url_for('main.view_license', license_id=license_id))
    
    if request.method == 'POST':
        # In a real application, you would integrate with actual payment gateway here
        # For demo purposes, we'll simulate a successful payment
        license.payment_status = 'completed'
        license.payment_date = datetime.utcnow()
        db.session.commit()
        
        flash('Payment processed successfully! You can now download your license.', 'success')
        return redirect(url_for('main.download_license', license_id=license_id))
    
    return render_template('main/make_payment.html', title='Make Payment', license=license)

@main.route('/license/<int:license_id>/download')
@login_required
def download_license(license_id):
    license = License.query.get_or_404(license_id)
    if license.user_id != current_user.id:
        flash('You do not have permission to access this license.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if license.payment_status != 'completed':
        flash('Payment must be completed before accessing the download page.', 'warning')
        return redirect(url_for('main.make_payment', license_id=license_id))
    
    return render_template('main/download_license.html', title='Download License', license=license)

@main.route('/license/<int:license_id>/cancel', methods=['POST'])
@login_required
def cancel_license(license_id):
    license = License.query.get_or_404(license_id)
    
    if license.user_id != current_user.id:
        flash('You do not have permission to cancel this license.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if license.status != 'pending':
        flash('Only pending licenses can be cancelled.', 'warning')
        return redirect(url_for('main.view_license', license_id=license.id))
    
    license.status = 'cancelled'
    db.session.commit()
    
    flash('Your license application has been cancelled successfully.', 'success')
    return redirect(url_for('main.dashboard'))