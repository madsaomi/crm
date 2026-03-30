from flask import Blueprint, session, redirect, request, flash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/set_role/<role>')
def set_role(role):
    if role in ['admin', 'manager', 'teacher']:
        session['role'] = role
        flash(f'Роль успешно изменена на {role}', 'info')
    else:
        flash('Недопустимая роль', 'danger')
    return redirect(request.referrer or '/')

@auth_bp.before_app_request
def set_default_role():
    if 'role' not in session:
        session['role'] = 'admin'
