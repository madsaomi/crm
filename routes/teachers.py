from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Teacher

teachers_bp = Blueprint('teachers', __name__)


@teachers_bp.route('/teachers')
def list_teachers():
    teachers = Teacher.query.order_by(Teacher.name).all()
    return render_template('teachers/list.html', teachers=teachers)


@teachers_bp.route('/teachers/<int:teacher_id>')
def view_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    return render_template('teachers/view.html', teacher=teacher)


@teachers_bp.route('/teachers/create', methods=['GET', 'POST'])
def create_teacher():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Имя преподавателя обязательно', 'danger')
            return redirect(url_for('teachers.create_teacher'))

        teacher = Teacher(name=name)
        db.session.add(teacher)
        db.session.commit()
        flash('Преподаватель добавлен', 'success')
        return redirect(url_for('teachers.list_teachers'))

    return render_template('teachers/form.html', teacher=None)


@teachers_bp.route('/teachers/<int:teacher_id>/edit', methods=['GET', 'POST'])
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)

    if request.method == 'POST':
        teacher.name = request.form.get('name', '').strip()
        if not teacher.name:
            flash('Имя преподавателя обязательно', 'danger')
            return redirect(url_for('teachers.edit_teacher', teacher_id=teacher_id))

        db.session.commit()
        flash('Преподаватель обновлён', 'success')
        return redirect(url_for('teachers.list_teachers'))

    return render_template('teachers/form.html', teacher=teacher)


@teachers_bp.route('/teachers/<int:teacher_id>/delete', methods=['POST'])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Преподаватель удалён', 'success')
    return redirect(url_for('teachers.list_teachers'))
