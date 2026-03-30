from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Group, Teacher, Student, Enrollment

groups_bp = Blueprint('groups', __name__)


@groups_bp.route('/groups')
def list_groups():
    groups = Group.query.order_by(Group.name).all()
    return render_template('groups/list.html', groups=groups)


@groups_bp.route('/groups/create', methods=['GET', 'POST'])
def create_group():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        teacher_id = request.form.get('teacher_id')
        schedule_type = request.form.get('schedule_type', 'even')
        room = request.form.get('room', '').strip()
        start_time = request.form.get('start_time', '18:00')
        monthly_fee = request.form.get('monthly_fee', 0)

        if not name:
            flash('Название группы обязательно', 'danger')
            return redirect(url_for('groups.create_group'))

        group = Group(
            name=name,
            teacher_id=int(teacher_id) if teacher_id else None,
            schedule_type=schedule_type,
            room=room,
            start_time=start_time,
            monthly_fee=float(monthly_fee) if monthly_fee else 0.0
        )
        db.session.add(group)
        db.session.commit()
        flash('Группа создана', 'success')
        return redirect(url_for('groups.list_groups'))

    teachers = Teacher.query.order_by(Teacher.name).all()
    return render_template('groups/form.html', group=None, teachers=teachers)


@groups_bp.route('/groups/<int:group_id>/edit', methods=['GET', 'POST'])
def edit_group(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == 'POST':
        group.name = request.form.get('name', '').strip()
        teacher_id = request.form.get('teacher_id')
        group.teacher_id = int(teacher_id) if teacher_id else None
        group.schedule_type = request.form.get('schedule_type', 'even')
        group.room = request.form.get('room', '').strip()
        group.start_time = request.form.get('start_time', '18:00')
        monthly_fee = request.form.get('monthly_fee', 0)
        group.monthly_fee = float(monthly_fee) if monthly_fee else 0.0

        if not group.name:
            flash('Название группы обязательно', 'danger')
            return redirect(url_for('groups.edit_group', group_id=group_id))

        db.session.commit()
        flash('Группа обновлена', 'success')
        return redirect(url_for('groups.list_groups'))

    teachers = Teacher.query.order_by(Teacher.name).all()
    return render_template('groups/form.html', group=group, teachers=teachers)


@groups_bp.route('/groups/<int:group_id>/delete', methods=['POST'])
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash('Группа удалена', 'success')
    return redirect(url_for('groups.list_groups'))


@groups_bp.route('/groups/<int:group_id>')
def view_group(group_id):
    group = Group.query.get_or_404(group_id)
    enrollments = Enrollment.query.filter_by(group_id=group_id).all()
    all_students = Student.query.order_by(Student.name).all()
    enrolled_ids = {e.student_id for e in enrollments}
    available_students = [s for s in all_students if s.id not in enrolled_ids]
    return render_template('groups/view.html',
                           group=group,
                           enrollments=enrollments,
                           available_students=available_students)


@groups_bp.route('/groups/<int:group_id>/enroll', methods=['POST'])
def enroll_student(group_id):
    student_id = request.form.get('student_id')
    if not student_id:
        flash('Выберите студента', 'danger')
        return redirect(url_for('groups.view_group', group_id=group_id))

    existing = Enrollment.query.filter_by(student_id=int(student_id), group_id=group_id).first()
    if existing:
        if not existing.active:
            existing.active = True
            db.session.commit()
            flash('Студент повторно зачислен', 'success')
        else:
            flash('Студент уже в группе', 'warning')
    else:
        enrollment = Enrollment(student_id=int(student_id), group_id=group_id)
        db.session.add(enrollment)
        db.session.commit()
        flash('Студент зачислен в группу', 'success')

    return redirect(url_for('groups.view_group', group_id=group_id))


@groups_bp.route('/groups/<int:group_id>/unenroll/<int:enrollment_id>', methods=['POST'])
def unenroll_student(group_id, enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    enrollment.active = False
    db.session.commit()
    flash('Студент отчислен из группы', 'success')
    return redirect(url_for('groups.view_group', group_id=group_id))
