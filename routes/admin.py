from flask import Blueprint, render_template, flash, redirect, url_for, send_file, current_app, request
from flask_login import login_required, current_user
from datetime import datetime
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from models import License, User, db
import os

admin = Blueprint('admin', __name__)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    pending_licenses = License.query.filter_by(status='pending').order_by(License.created_at.desc()).all()
    approved_licenses = License.query.filter_by(status='approved').order_by(License.approved_at.desc()).limit(5).all()
    total_users = User.query.filter_by(role='user').count()
    
    return render_template('admin/dashboard.html',
                         title='Admin Dashboard',
                         pending_licenses=pending_licenses,
                         approved_licenses=approved_licenses,
                         total_users=total_users)

@admin.route('/admin/licenses')
@login_required
@admin_required
def manage_licenses():
    licenses = License.query.order_by(License.created_at.desc()).all()
    return render_template('admin/licenses.html', title='Manage Licenses', licenses=licenses)

@admin.route('/admin/license/<int:license_id>/<action>', methods=['GET', 'POST'])
@login_required
@admin_required
def process_license(license_id, action):
    license = License.query.get_or_404(license_id)
    
    if action == 'view':
        return render_template('admin/view_license.html', title='View License', license=license)
    
    if action == 'approve' and license.status == 'pending':
        license.status = 'approved'
        license.approved_at = datetime.utcnow()
        license.approved_by = current_user.id
        license.start_date = datetime.utcnow()
        
        # Calculate payment amount based on duration
        base_fee = 5000  # Base fee in Malawian Kwacha
        license.payment_amount = base_fee * license.duration
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f'License ID: {license.id}\nName: {license.full_name}\nZone: {license.fishing_zone}')
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Create directories if they don't exist
        qr_path = os.path.join(current_app.root_path, 'static', 'licenses', str(license.id))
        os.makedirs(qr_path, exist_ok=True)
        
        # Save QR code
        qr_file = os.path.join(qr_path, 'qr.png')
        qr_image.save(qr_file)
        
        # Generate PDF
        pdf_file = os.path.join(qr_path, 'license.pdf')
        c = canvas.Canvas(pdf_file, pagesize=letter)
        c.drawString(100, 750, f"Fishing License - {license.full_name}")
        c.drawString(100, 700, f"License ID: {license.id}")
        c.drawString(100, 650, f"Fishing Zone: {license.fishing_zone}")
        c.drawString(100, 600, f"Valid From: {license.start_date.strftime('%Y-%m-%d')}")
        c.drawString(100, 550, f"Duration: {license.duration} months")
        c.drawImage(qr_file, 100, 200, width=200, height=200)
        c.save()
        
        license.pdf_path = f'licenses/{license.id}/license.pdf'
        db.session.commit()
        flash('License approved! Proceeding to payment initiation.', 'success')
        return redirect(url_for('admin.initiate_payment', license_id=license.id))
        
    elif action == 'reject' and license.status == 'pending':
        license.status = 'rejected'
        license.approved_at = datetime.utcnow()
        license.approved_by = current_user.id
        db.session.commit()
        flash('License application rejected.', 'info')
        return redirect(url_for('admin.manage_licenses'))
    
    elif action == 'cancel' and license.status == 'pending':
        license.status = 'cancelled'
        db.session.commit()
        flash('License application cancelled.', 'info')
        return redirect(url_for('admin.manage_licenses'))
    
    return redirect(url_for('admin.manage_licenses'))

@admin.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.filter_by(role='user').order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', title='Manage Users', users=users)

@admin.route('/admin/payment/initiate/<int:license_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def initiate_payment(license_id):
    license = License.query.get_or_404(license_id)
    if request.method == 'POST':
        license.payment_method = request.form.get('payment_method')
        if license.payment_method == 'bank_deposit':
            license.bank_name = request.form.get('bank_name')
        
        # Send notification to user (placeholder for email/SMS integration)
        # TODO: Implement actual notification system
        
        flash('Payment initiation successful. Awaiting payment confirmation.', 'success')
        return redirect(url_for('admin.manage_licenses'))
    
    return render_template('admin/initiate_payment.html', title='Initiate Payment', license=license)

@admin.route('/admin/payment/confirm/<int:license_id>', methods=['POST'])
@login_required
@admin_required
def confirm_payment(license_id):
    license = License.query.get_or_404(license_id)
    license.payment_status = 'completed'
    license.payment_reference = request.form.get('payment_reference')
    license.payment_date = datetime.utcnow()
    
    # Generate QR code and PDF after payment confirmation
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f'License ID: {license.id}\nName: {license.full_name}\nZone: {license.fishing_zone}')
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    qr_path = os.path.join(current_app.root_path, 'static', 'licenses', str(license.id))
    os.makedirs(qr_path, exist_ok=True)
    
    qr_file = os.path.join(qr_path, 'qr.png')
    qr_image.save(qr_file)
    
    pdf_file = os.path.join(qr_path, 'license.pdf')
    c = canvas.Canvas(pdf_file, pagesize=letter)
    c.drawString(100, 750, f"Fishing License - {license.full_name}")
    c.drawString(100, 700, f"License ID: {license.id}")
    c.drawString(100, 650, f"Fishing Zone: {license.fishing_zone}")
    c.drawString(100, 600, f"Valid From: {license.start_date.strftime('%Y-%m-%d')}")
    c.drawString(100, 550, f"Duration: {license.duration} months")
    c.drawString(100, 500, f"Payment Method: {license.payment_method}")
    c.drawString(100, 450, f"Payment Reference: {license.payment_reference}")
    c.drawImage(qr_file, 100, 200, width=200, height=200)
    c.save()
    
    license.pdf_path = f'licenses/{license.id}/license.pdf'
    db.session.commit()
    
    flash('Payment confirmed and license PDF generated successfully!', 'success')
    return redirect(url_for('admin.manage_licenses'))

@admin.route('/admin/download/<int:license_id>')
@login_required
@admin_required
def download_license(license_id):
    license = License.query.get_or_404(license_id)
    if license.pdf_path:
        return send_file(os.path.join(current_app.root_path, 'static', license.pdf_path),
                        as_attachment=True,
                        download_name=f'license_{license.id}.pdf')
    flash('PDF not found for this license.', 'error')
    return redirect(url_for('admin.manage_licenses'))