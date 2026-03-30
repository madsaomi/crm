from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Student, Manager, Enrollment, Group

students_bp = Blueprint('students', __name__)


@students_bp.route('/students')
def list_students():
    students = Student.query.order_by(Student.name).all()
    return render_template('students/list.html', students=students)


@students_bp.route('/students/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        manager_id = request.form.get('manager_id')

        if not name:
            flash('Имя студента обязательно', 'danger')
            return redirect(url_for('students.create_student'))

        student = Student(
            name=name,
            phone=phone,
            manager_id=int(manager_id) if manager_id else None
        )
        db.session.add(student)
        db.session.commit()
        flash('Студент добавлен', 'success')
        return redirect(url_for('students.list_students'))

    managers = Manager.query.order_by(Manager.name).all()
    return render_template('students/form.html', student=None, managers=managers)


@students_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.name = request.form.get('name', '').strip()
        student.phone = request.form.get('phone', '').strip()
        manager_id = request.form.get('manager_id')
        student.manager_id = int(manager_id) if manager_id else None

        if not student.name:
            flash('Имя студента обязательно', 'danger')
            return redirect(url_for('students.edit_student', student_id=student_id))

        db.session.commit()
        flash('Студент обновлён', 'success')
        return redirect(url_for('students.list_students'))

    managers = Manager.query.order_by(Manager.name).all()
    return render_template('students/form.html', student=student, managers=managers)


@students_bp.route('/students/<int:student_id>/delete', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Студент удалён', 'success')
    return redirect(url_for('students.list_students'))


@students_bp.route('/students/<int:student_id>')
def view_student(student_id):
    student = Student.query.get_or_404(student_id)
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    total_paid = sum(p.amount for p in student.payments)

    # Calculate expected payment based on enrolled groups
    active_enrollments = [e for e in enrollments if e.active]
    expected = sum(e.group.monthly_fee for e in active_enrollments if e.group)
    debt = expected - total_paid

    return render_template('students/view.html',
                           student=student,
                           enrollments=enrollments,
                           total_paid=total_paid,
                           expected=expected,
                           debt=debt)
