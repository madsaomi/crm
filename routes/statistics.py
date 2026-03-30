from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
from models import Manager, Teacher, Student, Payment, Attendance, Enrollment, Group
from sqlalchemy import func

statistics_bp = Blueprint('statistics', __name__)


def get_attendance_stats(start_date, end_date):
    """Get attendance statistics for a date range."""
    total = Attendance.query.filter(
        Attendance.date >= start_date,
        Attendance.date < end_date
    ).count()

    present = Attendance.query.filter(
        Attendance.date >= start_date,
        Attendance.date < end_date,
        Attendance.status == 'present'
    ).count()

    absent = total - present
    rate = round(present / total * 100, 1) if total > 0 else 0

    return {
        'total': total,
        'present': present,
        'absent': absent,
        'rate': rate
    }


def get_payment_stats(start_date, end_date):
    """Get payment statistics for a date range."""
    payments = Payment.query.filter(
        Payment.date >= start_date,
        Payment.date < end_date
    ).all()

    total_amount = sum(p.amount for p in payments)
    count = len(payments)
    avg = round(total_amount / count, 0) if count > 0 else 0

    return {
        'total_amount': total_amount,
        'count': count,
        'average': avg
    }


@statistics_bp.route('/statistics')
def dashboard():
    today = datetime.today()
    selected_year = request.args.get('year', today.year, type=int)

    # ─── Period boundaries ───
    # Week (Monday to Sunday)
    week_start = today - timedelta(days=today.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)

    # Month
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        month_end = today.replace(month=today.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # Quarter
    quarter = (today.month - 1) // 3
    quarter_start_month = quarter * 3 + 1
    quarter_start = today.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
    quarter_end_month = quarter_start_month + 3
    if quarter_end_month > 12:
        quarter_end = today.replace(year=today.year + 1, month=quarter_end_month - 12, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        quarter_end = today.replace(month=quarter_end_month, day=1, hour=0, minute=0, second=0, microsecond=0)

    # Year
    year_start = datetime(selected_year, 1, 1)
    year_end = datetime(selected_year + 1, 1, 1)

    # ─── Attendance stats ───
    att_week = get_attendance_stats(week_start, week_end)
    att_month = get_attendance_stats(month_start, month_end)
    att_quarter = get_attendance_stats(quarter_start, quarter_end)
    att_year = get_attendance_stats(year_start, year_end)

    # ─── Payment stats ───
    pay_week = get_payment_stats(week_start, week_end)
    pay_month = get_payment_stats(month_start, month_end)
    pay_quarter = get_payment_stats(quarter_start, quarter_end)
    pay_year = get_payment_stats(year_start, year_end)

    # ─── Overall metrics ───
    total_students = Student.query.count()
    total_groups = Group.query.count()
    total_teachers = Teacher.query.count()
    total_managers = Manager.query.count()

    total_revenue = Payment.query.with_entities(func.sum(Payment.amount)).scalar() or 0

    # Total debt
    total_debt = 0
    active_enrollments = Enrollment.query.filter_by(active=True).all()
    student_payments_cache = {}
    for enrollment in active_enrollments:
        if enrollment.student_id not in student_payments_cache:
            student_payments_cache[enrollment.student_id] = sum(
                p.amount for p in Payment.query.filter_by(student_id=enrollment.student_id).all()
            )
        expected = enrollment.group.monthly_fee if enrollment.group else 0
        paid = student_payments_cache[enrollment.student_id]
        debt = expected - paid
        if debt > 0:
            total_debt += debt

    # ─── Manager KPI ───
    managers = Manager.query.all()
    manager_kpi = []
    for manager in managers:
        students = manager.students
        total_s = len(students)
        if total_s == 0:
            manager_kpi.append({
                'name': manager.name,
                'students': 0,
                'revenue': 0,
                'conversion': 0,
                'debt': 0
            })
            continue

        revenue = 0
        paid = 0
        debt = 0
        for s in students:
            sp = sum(p.amount for p in s.payments)
            revenue += sp
            if sp > 0:
                paid += 1
            active_e = [e for e in s.enrollments if e.active]
            expected = sum(e.group.monthly_fee for e in active_e if e.group)
            d = expected - sp
            if d > 0:
                debt += d

        conversion = round(paid / total_s * 100, 1) if total_s > 0 else 0
        manager_kpi.append({
            'name': manager.name,
            'students': total_s,
            'revenue': revenue,
            'conversion': conversion,
            'debt': debt
        })
    manager_kpi.sort(key=lambda x: x['revenue'], reverse=True)

    # ─── Teacher KPI ───
    teachers = Teacher.query.all()
    teacher_kpi = []
    for teacher in teachers:
        groups = teacher.groups
        if not groups:
            teacher_kpi.append({
                'name': teacher.name,
                'groups': 0,
                'students': 0,
                'attendance_rate': 0,
                'retention_rate': 0
            })
            continue

        total_s = 0
        active_s = 0
        total_att = 0
        present_att = 0
        for g in groups:
            enrollments = Enrollment.query.filter_by(group_id=g.id).all()
            total_s += len(enrollments)
            active_s += len([e for e in enrollments if e.active])
            att = Attendance.query.filter_by(group_id=g.id).all()
            total_att += len(att)
            present_att += sum(1 for a in att if a.status == 'present')

        att_rate = round(present_att / total_att * 100, 1) if total_att > 0 else 0
        ret_rate = round(active_s / total_s * 100, 1) if total_s > 0 else 0

        teacher_kpi.append({
            'name': teacher.name,
            'groups': len(groups),
            'students': active_s,
            'attendance_rate': att_rate,
            'retention_rate': ret_rate
        })
    teacher_kpi.sort(key=lambda x: x['attendance_rate'], reverse=True)

    # ─── Top Students ───
    # Top by payments
    students_all = Student.query.all()
    student_payments_list = []
    for s in students_all:
        total_paid = sum(p.amount for p in s.payments)
        if total_paid > 0:
            student_payments_list.append({
                'name': s.name,
                'amount': total_paid
            })
    student_payments_list.sort(key=lambda x: x['amount'], reverse=True)
    top_payers = student_payments_list[:10]

    # Top by attendance
    student_att_list = []
    for s in students_all:
        total_a = len(s.attendances)
        if total_a > 0:
            present_a = sum(1 for a in s.attendances if a.status == 'present')
            rate = round(present_a / total_a * 100, 1)
            student_att_list.append({
                'name': s.name,
                'rate': rate,
                'total': total_a,
                'present': present_a
            })
    student_att_list.sort(key=lambda x: x['rate'], reverse=True)
    top_attendees = student_att_list[:10]

    # Debtors
    debtors = []
    for s in students_all:
        total_paid = sum(p.amount for p in s.payments)
        active_e = [e for e in s.enrollments if e.active]
        expected = sum(e.group.monthly_fee for e in active_e if e.group)
        debt = expected - total_paid
        if debt > 0:
            debtors.append({
                'name': s.name,
                'debt': debt,
                'paid': total_paid,
                'expected': expected
            })
    debtors.sort(key=lambda x: x['debt'], reverse=True)
    top_debtors = debtors[:10]

    # Available years
    years = list(range(today.year - 3, today.year + 1))

    return render_template('statistics/dashboard.html',
                           today=today,
                           selected_year=selected_year,
                           years=years,
                           total_students=total_students,
                           total_groups=total_groups,
                           total_teachers=total_teachers,
                           total_managers=total_managers,
                           total_revenue=total_revenue,
                           total_debt=total_debt,
                           att_week=att_week,
                           att_month=att_month,
                           att_quarter=att_quarter,
                           att_year=att_year,
                           pay_week=pay_week,
                           pay_month=pay_month,
                           pay_quarter=pay_quarter,
                           pay_year=pay_year,
                           manager_kpi=manager_kpi,
                           teacher_kpi=teacher_kpi,
                           top_payers=top_payers,
                           top_attendees=top_attendees,
                           top_debtors=top_debtors)
