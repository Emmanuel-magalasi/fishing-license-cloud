from app import db, app
from models import User

def seed_admin():
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(email='emmanuelmagalasi004@gmail.com').first()
        if not admin:
            admin = User(
                email='emmanuelmagalasi004@gmail.com',
                username='admin',
                role='admin'
            )
            admin.set_password('Giresi004@j')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully!')
        else:
            print('Admin user already exists!')

if __name__ == '__main__':
    seed_admin()