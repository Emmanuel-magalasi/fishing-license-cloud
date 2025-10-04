from flask import Blueprint, send_file
from flask_login import login_required, current_user
from models import License
from utils.license_pdf import generate_license_pdf
import os
from tempfile import mkstemp

license_bp = Blueprint('license', __name__)

@license_bp.route('/download-license/<int:license_id>')
@login_required
def download_license(license_id):
    # Get the license from database
    license = License.query.get_or_404(license_id)
    
    # Ensure the user has permission to access this license
    if license.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Prepare license data for PDF generation
    license_data = {
        'full_name': license.full_name,
        'id_number': license.id_number,
        'license_type': license.license_type,
        'fishing_method': license.fishing_method,
        'fishing_location': license.fishing_location,
        'license_number': f'MLW-{license.id:06d}'
    }
    
    # Create a temporary file for the PDF
    fd, temp_path = mkstemp(suffix='.pdf')
    os.close(fd)
    
    try:
        # Generate the PDF
        pdf_path = generate_license_pdf(license_data, temp_path)
        
        # Send the file to the user
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'fishing-license-{license.id}.pdf',
            mimetype='application/pdf'
        )
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_path)
        except:
            pass