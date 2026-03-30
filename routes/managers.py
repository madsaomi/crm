from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Manager

managers_bp = Blueprint('managers', __name__)


@managers_bp.route('/managers')
def list_managers():
    managers = Manager.query.order_by(Manager.name).all()
    return render_template('managers/list.html', managers=managers)


@managers_bp.route('/managers/<int:manager_id>')
def view_manager(manager_id):
    manager = Manager.query.get_or_404(manager_id)
    return render_template('managers/view.html', manager=manager)


@managers_bp.route('/managers/create', methods=['GET', 'POST'])
def create_manager():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Имя менеджера обязательно', 'danger')
            return redirect(url_for('managers.create_manager'))

        manager = Manager(name=name)
        db.session.add(manager)
        db.session.commit()
        flash('Менеджер добавлен', 'success')
        return redirect(url_for('managers.list_managers'))

    return render_template('managers/form.html', manager=None)


@managers_bp.route('/managers/<int:manager_id>/edit', methods=['GET', 'POST'])
def edit_manager(manager_id):
    manager = Manager.query.get_or_404(manager_id)

    if request.method == 'POST':
        manager.name = request.form.get('name', '').strip()
        if not manager.name:
            flash('Имя менеджера обязательно', 'danger')
            return redirect(url_for('managers.edit_manager', manager_id=manager_id))

        db.session.commit()
        flash('Менеджер обновлён', 'success')
        return redirect(url_for('managers.list_managers'))

    return render_template('managers/form.html', manager=manager)


@managers_bp.route('/managers/<int:manager_id>/delete', methods=['POST'])
def delete_manager(manager_id):
    manager = Manager.query.get_or_404(manager_id)
    db.session.delete(manager)
    db.session.commit()
    flash('Менеджер удалён', 'success')
    return redirect(url_for('managers.list_managers'))
