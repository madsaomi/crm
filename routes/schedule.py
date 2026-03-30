import calendar
from datetime import datetime
from flask import Blueprint, render_template, request
from models import Group

schedule_bp = Blueprint('schedule', __name__)


@schedule_bp.route('/schedule')
def schedule_calendar():
    today = datetime.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    # Clamp month
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Get all groups
    groups = Group.query.order_by(Group.name).all()
    
    def get_time_range(start_str):
        if not start_str:
            start_str = '18:00'
        try:
            h, m = map(int, start_str.split(':'))
            end_m = m + 30
            end_h = h + 1 + (end_m // 60)
            end_m = end_m % 60
            return f"{h:02d}:{m:02d} - {end_h:02d}:{end_m:02d}"
        except:
            return "18:00 - 19:30"

    for g in groups:
        g.time_range = get_time_range(g.start_time)

    even_groups = [g for g in groups if g.schedule_type == 'even']
    odd_groups = [g for g in groups if g.schedule_type == 'odd']

    # Build calendar data
    cal = calendar.Calendar(firstweekday=0)  # Monday first
    month_days = cal.monthdayscalendar(year, month)

    month_name = [
        '', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ][month]

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    # Prev/next month
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

    return render_template('schedule/calendar.html',
                           year=year,
                           month=month,
                           month_name=month_name,
                           weekdays=weekdays,
                           month_days=month_days,
                           even_groups=even_groups,
                           odd_groups=odd_groups,
                           today=today,
                           prev_month=prev_month,
                           prev_year=prev_year,
                           next_month=next_month,
                           next_year=next_year)
