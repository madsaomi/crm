from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from extensions import db
from models import Payment, Student

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/payments')
def list_payments():
    student_id = request.args.get('student_id', type=int)
    if student_id:
        payments = Payment.query.filter_by(student_id=student_id).order_by(Payment.date.desc()).all()
        student = Student.query.get(student_id)
    else:
        payments = Payment.query.order_by(Payment.date.desc()).all()
        student = None
    return render_template('payments/list.html', payments=payments, student=student)


@payments_bp.route('/payments/create', methods=['GET', 'POST'])
def create_payment():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        amount = request.form.get('amount', '0')
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '')

        if not student_id or not amount:
            flash('Студент и сумма обязательны', 'danger')
            return redirect(url_for('payments.create_payment'))

        try:
            payment_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
        except ValueError:
            payment_date = datetime.utcnow()

        payment = Payment(
            student_id=int(student_id),
            amount=float(amount),
            date=payment_date,
            description=description
        )
        db.session.add(payment)
        db.session.commit()
        flash('Оплата добавлена', 'success')
        return redirect(url_for('payments.list_payments'))

    students = Student.query.order_by(Student.name).all()
    preselected = request.args.get('student_id', type=int)
    return render_template('payments/form.html', students=students, preselected=preselected)


@payments_bp.route('/payments/<int:payment_id>/delete', methods=['POST'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()
    flash('Оплата удалена', 'success')
    return redirect(url_for('payments.list_payments'))
