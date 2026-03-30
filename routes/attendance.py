from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from extensions import db
from models import Attendance, Group, Enrollment, Student

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/attendance')
def list_attendance():
    group_id = request.args.get('group_id', type=int)
    groups = Group.query.order_by(Group.name).all()

    records = []
    selected_group = None
    if group_id:
        selected_group = Group.query.get(group_id)
        records = Attendance.query.filter_by(group_id=group_id).order_by(Attendance.date.desc()).limit(100).all()

    return render_template('attendance/list.html',
                           groups=groups,
                           records=records,
                           selected_group=selected_group)


@attendance_bp.route('/attendance/mark/<int:group_id>', methods=['GET', 'POST'])
def mark_attendance(group_id):
    group = Group.query.get_or_404(group_id)
    enrollments = Enrollment.query.filter_by(group_id=group_id, active=True).all()
    students = [e.student for e in enrollments]

    if request.method == 'POST':
        date_str = request.form.get('date', '')
        try:
            att_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
        except ValueError:
            att_date = datetime.utcnow()

        for student in students:
            status = request.form.get(f'status_{student.id}', 'absent')
            comment = request.form.get(f'comment_{student.id}', '').strip()
            attendance = Attendance(
                student_id=student.id,
                group_id=group_id,
                date=att_date,
                status=status,
                comment=comment if comment else None
            )
            db.session.add(attendance)

        db.session.commit()
        flash('Посещаемость отмечена', 'success')
        return redirect(url_for('attendance.list_attendance', group_id=group_id))

    today = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('attendance/mark.html', group=group, students=students, today=today)


@attendance_bp.route('/attendance/monthly/<int:group_id>')
def monthly_attendance(group_id):
    """Monthly attendance journal for a group."""
    group = Group.query.get_or_404(group_id)
    today = datetime.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    # Clamp
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    import calendar
    num_days = calendar.monthrange(year, month)[1]
    
    # Filter days by schedule_type
    filtered_days = []
    for d in range(1, num_days + 1):
        weekday = calendar.weekday(year, month, d)  # 0=Mon, ..., 6=Sun
        if group.schedule_type == 'odd' and weekday in [0, 2, 4]:
            filtered_days.append(d)
        elif group.schedule_type == 'even' and weekday in [1, 3, 5]:
            filtered_days.append(d)
        # We skip Sundays and days that don't match the schedule_type

    days = filtered_days
    
    # Pre-calculate short weekday names for templates
    weekday_names = {0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс'}
    days_with_weekday = [(d, weekday_names[calendar.weekday(year, month, d)]) for d in days]

    # Get active students in group
    enrollments = Enrollment.query.filter_by(group_id=group_id, active=True).all()
    students = sorted([e.student for e in enrollments], key=lambda s: s.name)

    # Get attendance records for this month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    records = Attendance.query.filter(
        Attendance.group_id == group_id,
        Attendance.date >= start_date,
        Attendance.date < end_date
    ).all()

    # Build lookup: (student_id, day) -> record
    att_map = {}
    for r in records:
        day = r.date.day
        key = (r.student_id, day)
        att_map[key] = r

    # Calculate stats per student
    student_stats = {}
    for student in students:
        total = 0
        present = 0
        for day in days:
            key = (student.id, day)
            if key in att_map:
                total += 1
                if att_map[key].status == 'present':
                    present += 1
        rate = round(present / total * 100, 1) if total > 0 else 0
        student_stats[student.id] = {
            'total': total,
            'present': present,
            'absent': total - present,
            'rate': rate
        }

    month_names = [
        '', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]

    # Navigation
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    return render_template('attendance/monthly.html',
                           group=group,
                           year=year,
                           month=month,
                           month_name=month_names[month],
                           days=days_with_weekday,
                           students=students,
                           att_map=att_map,
                           student_stats=student_stats,
                           prev_month=prev_month,
                           prev_year=prev_year,
                           next_month=next_month,
                           next_year=next_year)


@attendance_bp.route('/attendance/update', methods=['POST'])
def update_attendance():
    """Update or create a single attendance record via AJAX."""
    student_id = request.form.get('student_id', type=int)
    group_id = request.form.get('group_id', type=int)
    day = request.form.get('day', type=int)
    month = request.form.get('month', type=int)
    year = request.form.get('year', type=int)
    status = request.form.get('status', 'present')
    comment = request.form.get('comment', '').strip()

    if not all([student_id, group_id, day, month, year]):
        flash('Ошибка: неполные данные', 'danger')
        return redirect(request.referrer or '/')

    att_date = datetime(year, month, day)

    # Find existing record
    record = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.group_id == group_id,
        Attendance.date >= att_date,
        Attendance.date < att_date + timedelta(days=1)
    ).first()

    if record:
        record.status = status
        record.comment = comment if comment else None
    else:
        record = Attendance(
            student_id=student_id,
            group_id=group_id,
            date=att_date,
            status=status,
            comment=comment if comment else None
        )
        db.session.add(record)

    db.session.commit()
    flash('Посещаемость обновлена', 'success')
    return redirect(url_for('attendance.monthly_attendance',
                            group_id=group_id, year=year, month=month))
