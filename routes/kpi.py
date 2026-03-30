from flask import Blueprint, render_template
from models import Manager, Teacher, Student, Payment, Attendance, Enrollment, Group

kpi_bp = Blueprint('kpi', __name__)


def calculate_manager_kpi():
    """Calculate KPI for each manager."""
    managers = Manager.query.all()
    results = []

    for manager in managers:
        students = manager.students
        total_students = len(students)

        if total_students == 0:
            results.append({
                'manager': manager,
                'total_students': 0,
                'total_revenue': 0,
                'paid_students': 0,
                'conversion_rate': 0,
                'total_debt': 0
            })
            continue

        total_revenue = 0
        paid_students = 0
        total_debt = 0

        for student in students:
            student_payments = sum(p.amount for p in student.payments)
            total_revenue += student_payments

            if student_payments > 0:
                paid_students += 1

            # Calculate expected payment from active enrollments
            active_enrollments = [e for e in student.enrollments if e.active]
            expected = sum(e.group.monthly_fee for e in active_enrollments if e.group)
            debt = expected - student_payments
            if debt > 0:
                total_debt += debt

        conversion_rate = (paid_students / total_students * 100) if total_students > 0 else 0

        results.append({
            'manager': manager,
            'total_students': total_students,
            'total_revenue': total_revenue,
            'paid_students': paid_students,
            'conversion_rate': round(conversion_rate, 1),
            'total_debt': total_debt
        })

    return results


def calculate_teacher_kpi():
    """Calculate KPI for each teacher."""
    teachers = Teacher.query.all()
    results = []

    for teacher in teachers:
        groups = teacher.groups

        if not groups:
            results.append({
                'teacher': teacher,
                'groups_count': 0,
                'total_students': 0,
                'active_students': 0,
                'attendance_rate': 0,
                'retention_rate': 0,
                'debt_percentage': 0
            })
            continue

        total_students = 0
        active_students = 0
        total_attendance = 0
        present_count = 0
        total_debt = 0
        total_expected = 0

        for group in groups:
            enrollments = Enrollment.query.filter_by(group_id=group.id).all()
            total_students += len(enrollments)
            active_in_group = [e for e in enrollments if e.active]
            active_students += len(active_in_group)

            # Attendance
            att_records = Attendance.query.filter_by(group_id=group.id).all()
            total_attendance += len(att_records)
            present_count += sum(1 for a in att_records if a.status == 'present')

            # Debt
            for enrollment in active_in_group:
                student = enrollment.student
                student_payments = sum(p.amount for p in student.payments)
                expected = group.monthly_fee
                total_expected += expected
                debt = expected - student_payments
                if debt > 0:
                    total_debt += debt

        attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0
        retention_rate = (active_students / total_students * 100) if total_students > 0 else 0
        debt_percentage = (total_debt / total_expected * 100) if total_expected > 0 else 0

        results.append({
            'teacher': teacher,
            'groups_count': len(groups),
            'total_students': total_students,
            'active_students': active_students,
            'attendance_rate': round(attendance_rate, 1),
            'retention_rate': round(retention_rate, 1),
            'debt_percentage': round(debt_percentage, 1)
        })

    return results


@kpi_bp.route('/kpi/managers')
def manager_kpi():
    data = calculate_manager_kpi()
    return render_template('kpi/managers.html', data=data)


@kpi_bp.route('/kpi/teachers')
def teacher_kpi():
    data = calculate_teacher_kpi()
    return render_template('kpi/teachers.html', data=data)
