from flask import Flask, render_template
from config import Config
from extensions import db
from models import Student, Group, Teacher, Manager, Payment


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = 'super_secret_for_simulation'

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from routes.students import students_bp
    from routes.groups import groups_bp
    from routes.teachers import teachers_bp
    from routes.managers import managers_bp
    from routes.payments import payments_bp
    from routes.attendance import attendance_bp
    from routes.kpi import kpi_bp
    from routes.schedule import schedule_bp
    from routes.statistics import statistics_bp
    from routes.auth import auth_bp

    app.register_blueprint(students_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(managers_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(kpi_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(auth_bp)

    # Dashboard route
    @app.route('/')
    def index():
        from flask import session
        import datetime
        from routes.kpi import calculate_manager_kpi

        role = session.get('role', 'admin')
        context = {'role': role}

        if role == 'manager':
            today = datetime.datetime.now().date()
            today_revenue = sum(p.amount for p in Payment.query.all() if p.date.date() == today)
            all_kpi = calculate_manager_kpi()
            context['today_revenue'] = today_revenue
            context['my_kpi'] = all_kpi[0] if all_kpi else None
        
        elif role == 'teacher':
            context['teacher'] = Teacher.query.first()

        else:
            context['students_count'] = Student.query.count()
            context['groups_count'] = Group.query.count()
            context['teachers_count'] = Teacher.query.count()
            context['managers_count'] = Manager.query.count()
            context['recent_payments'] = Payment.query.order_by(Payment.date.desc()).limit(5).all()

        return render_template('index.html', **context)

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
