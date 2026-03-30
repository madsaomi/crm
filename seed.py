"""
Скрипт генерации тестовых данных для CRM.
Генерирует реалистичные данные с казахскими/русскими именами.
"""
import os
import random
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import Manager, Teacher, Student, Group, Enrollment, Payment, Attendance

# ─── Реалистичные данные ────────────────────────────────────────

FIRST_NAMES_MALE = [
    'Alisher', 'Aziz', 'Bekzod', 'Doston', 'Eldor', 'Farhod', 'G\\\'ayrat', 'Hasan',
    'Islom', 'Javohir', 'Kamron', 'Laziz', 'Mansur', 'Nodir', 'Odil', 'Po\'lat',
    'Ravshan', 'Sardor', 'Timur', 'Umid', 'Vali', 'Xurshid', 'Yoqub', 'Zafar',
    'Akmal', 'Bobur', 'Dilshod', 'Erkin', 'Firdavs', 'G\\\'olib', 'Husan', 'Ilyos',
]

FIRST_NAMES_FEMALE = [
    'Asal', 'Barno', 'Charos', 'Dilnoza', 'E\\\'zoza', 'Feruza', 'Gulnoza', 'Hilola',
    'Iroda', 'Jamila', 'Kamola', 'Lola', 'Malika', 'Nargiza', 'Oydin', 'Parvina',
    'Ra\\\'no', 'Sevara', 'Shakhnoza', 'Umida', 'Vazira', 'Xolida', 'Yulduz', 'Zarina',
    'Aziza', 'Dildora', 'Fotima', 'Gulzoda', 'Husniya', 'Maftuna', 'Nigora',
]

LAST_NAMES = [
    'Abdullayev', 'Alimov', 'Axmedov', 'Botirov', 'Davlatov', 'Ergashev',
    'Fayziyev', 'G\\\'aniyev', 'Hoshimov', 'Ibragimov', 'Jalilov', 'Karimov',
    'Latipov', 'Mahmudov', 'Nazarov', 'Obidov', 'Po\\\'latov', 'Qodirov',
    'Rahimov', 'Salimov', 'Tohirov', 'Usmonov', 'Vahobov', 'Xalilov',
    'Yo\\\'ldoshev', 'Zokirov',
]

MANAGER_NAMES = [
    'Aziza Karimovna', 'Dilshod Aliyev', 'Nargiza Rustamova', 'Sardor Akmalov',
    'Zarina Shavkatovna'
]

TEACHER_NAMES = [
    'Alisher Usmonov', 'Kamila Rahmatova', 'Sanjar Qodirov', 'Madina Umarova',
    'Bekzod To\\\'rayev', 'Sevara Yo\\\'ldosheva', 'Otabek Nuriddinov', 'Dildora Zokirova'
]

SUBJECTS = [
    'Английский язык', 'Математика', 'Физика', 'Химия', 'Биология',
    'Казахский язык', 'Русский язык', 'История', 'География', 'Информатика',
    'Программирование', 'Робототехника', 'Рисование', 'Музыка', 'Шахматы',
    'IELTS Prep', 'SAT Prep', 'ЕНТ Подготовка', 'Олимпиадная математика',
    'Скорочтение', 'Ментальная арифметика', 'Логика', 'Каллиграфия',
]

LEVELS = ['Beginner', 'Elementary', 'Intermediate', 'Advanced', 'Pro',
          'A1', 'A2', 'B1', 'B2', 'C1', '1-уровень', '2-уровень', '3-уровень']

ROOMS = ['101', '102', '103', '201', '202', '203', '301', '302', '303',
         '401', '402', '105A', '105B', '210', '215', 'Lab-1', 'Lab-2', 'Online']

PHONES = [
    '+7 701', '+7 702', '+7 705', '+7 707', '+7 708', '+7 747', '+7 771', '+7 775', '+7 776', '+7 778',
]

PAYMENT_DESCRIPTIONS = [
    'Оплата за январь', 'Оплата за февраль', 'Оплата за март',
    'Оплата за апрель', 'Оплата за май', 'Оплата за июнь',
    'Оплата за июль', 'Оплата за август', 'Оплата за сентябрь',
    'Оплата за октябрь', 'Оплата за ноябрь', 'Оплата за декабрь',
    'Частичная оплата', 'Доплата', 'Предоплата', 'Перерасчёт',
]

ABSENCE_COMMENTS = [
    'Болел', 'Болела', 'Простуда', 'Температура', 'ОРВИ',
    'Семейные обстоятельства', 'Уважительная причина', 'По семейным обстоятельствам',
    'Опоздал', 'Опоздала', 'Ушёл раньше', 'Ушла раньше',
    'На олимпиаде', 'На соревнованиях', 'На экзамене',
    'Уехал из города', 'Уехала из города', 'В отъезде',
    'Записка от родителей', 'Справка от врача',
    'Не предупредил', 'Не предупредила', 'Без причины',
    'Проблемы с транспортом', 'Погодные условия',
    None, None, None, None, None,  # some without comment
]


def random_phone():
    prefix = random.choice(PHONES)
    return f'{prefix} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}'


def random_name():
    if random.random() < 0.5:
        first = random.choice(FIRST_NAMES_MALE)
    else:
        first = random.choice(FIRST_NAMES_FEMALE)
    last = random.choice(LAST_NAMES)
    return f'{last} {first}'


def seed_data():
    """Generate full set of test data."""
    app = create_app()
    with app.app_context():
        print('[*] Cleaning database...')
        db.drop_all()
        db.create_all()

        # --- Managers ---
        print('[+] Creating managers...')
        managers = []
        for name in MANAGER_NAMES:
            m = Manager(name=name)
            db.session.add(m)
            managers.append(m)
        db.session.flush()
        print(f'    OK: {len(managers)} managers')

        # --- Teachers ---
        print('[+] Creating teachers...')
        teachers = []
        for name in TEACHER_NAMES:
            t = Teacher(name=name)
            db.session.add(t)
            teachers.append(t)
        db.session.flush()
        print(f'    OK: {len(teachers)} teachers')

        # --- Groups ---
        print('[+] Creating groups...')
        groups = []
        group_id = 0
        for subject in SUBJECTS:
            num_groups = random.randint(2, 5)
            for i in range(num_groups):
                level = random.choice(LEVELS)
                group_name = f'{subject} ({level}) #{group_id + 1}'
                fee = random.choice([15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 60000])
                g = Group(
                    name=group_name,
                    teacher_id=random.choice(teachers).id,
                    schedule_type=random.choice(['even', 'odd']),
                    room=random.choice(ROOMS),
                    start_time=f'{random.randint(9, 20):02d}:00',
                    monthly_fee=fee,
                )
                db.session.add(g)
                groups.append(g)
                group_id += 1
        db.session.flush()
        print(f'    OK: {len(groups)} groups')

        # --- Students ---
        NUM_STUDENTS = 2000
        print(f'[+] Creating {NUM_STUDENTS} students...')
        students = []
        used_names = set()
        for i in range(NUM_STUDENTS):
            while True:
                name = random_name()
                if name not in used_names:
                    used_names.add(name)
                    break

            s = Student(
                name=name,
                phone=random_phone(),
                manager_id=random.choice(managers).id,
            )
            db.session.add(s)
            students.append(s)

            if (i + 1) % 500 == 0:
                print(f'    ... {i + 1}/{NUM_STUDENTS}')

        db.session.flush()
        print(f'    OK: {len(students)} students')

        # --- Enrollments ---
        print('[+] Creating enrollments...')
        enrollments = []
        enrollment_map = {}
        for student in students:
            num_groups = random.choices([1, 2, 3, 4], weights=[30, 40, 20, 10])[0]
            selected_groups = random.sample(groups, min(num_groups, len(groups)))

            enrollment_map[student.id] = []
            for group in selected_groups:
                active = random.random() < 0.85
                days_ago = random.randint(30, 365)
                e = Enrollment(
                    student_id=student.id,
                    group_id=group.id,
                    enrolled_at=datetime.utcnow() - timedelta(days=days_ago),
                    active=active,
                )
                db.session.add(e)
                enrollments.append(e)
                enrollment_map[student.id].append((group.id, active))

        db.session.flush()
        print(f'    OK: {len(enrollments)} enrollments')

        # --- Payments ---
        print('[+] Creating payments...')
        payments = []
        batch = []
        for student in students:
            if random.random() < 0.70:
                num_payments = random.randint(1, 12)
                for j in range(num_payments):
                    days_ago = random.randint(1, 365)
                    amount = random.choice([
                        15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000,
                        10000, 12000, 60000, 75000, 100000,
                    ])
                    p = Payment(
                        student_id=student.id,
                        amount=amount,
                        date=datetime.utcnow() - timedelta(days=days_ago),
                        description=random.choice(PAYMENT_DESCRIPTIONS),
                    )
                    batch.append(p)

                    if len(batch) >= 1000:
                        db.session.add_all(batch)
                        db.session.flush()
                        payments.extend(batch)
                        batch = []

        if batch:
            db.session.add_all(batch)
            db.session.flush()
            payments.extend(batch)
        print(f'    OK: {len(payments)} payments')

        # --- Attendance ---
        print('[+] Creating attendance records...')
        attendance_records = []
        batch = []

        for group in groups:
            group_students = [
                s for s in students
                if group.id in [gid for gid, active in enrollment_map.get(s.id, []) if active]
            ]

            if not group_students:
                continue

            num_lessons = random.randint(20, 36)
            for lesson_num in range(num_lessons):
                days_ago = random.randint(1, 90)
                lesson_date = datetime.utcnow() - timedelta(days=days_ago)

                for student in group_students:
                    status = 'present' if random.random() < 0.78 else 'absent'
                    # Add comment for absent students (and sometimes for present)
                    comment = None
                    if status == 'absent':
                        comment = random.choice(ABSENCE_COMMENTS)
                    elif random.random() < 0.05:
                        comment = random.choice(['Опоздал на 10 мин', 'Ушёл раньше', 'Пришёл с опозданием', None])

                    a = Attendance(
                        student_id=student.id,
                        group_id=group.id,
                        date=lesson_date,
                        status=status,
                        comment=comment,
                    )
                    batch.append(a)

                    if len(batch) >= 5000:
                        db.session.add_all(batch)
                        db.session.flush()
                        attendance_records.extend(batch)
                        batch = []
                        if len(attendance_records) % 50000 == 0:
                            print(f'    ... {len(attendance_records)} records...')

        if batch:
            db.session.add_all(batch)
            db.session.flush()
            attendance_records.extend(batch)

        print(f'    OK: {len(attendance_records)} attendance records')

        # --- Commit ---
        print('\n[*] Saving to database...')
        db.session.commit()

        # --- Summary ---
        print('\n' + '=' * 50)
        print('TOTAL TEST DATA:')
        print(f'    Managers:      {len(managers)}')
        print(f'    Teachers:      {len(teachers)}')
        print(f'    Groups:        {len(groups)}')
        print(f'    Students:      {len(students)}')
        print(f'    Enrollments:   {len(enrollments)}')
        print(f'    Payments:      {len(payments)}')
        print(f'    Attendance:    {len(attendance_records)}')
        total = (len(managers) + len(teachers) + len(groups) + len(students) +
                 len(enrollments) + len(payments) + len(attendance_records))
        print(f'    --------------------------')
        print(f'    TOTAL RECORDS: {total:,}')
        print('=' * 50)

        db_path = os.path.join(os.path.dirname(__file__), 'database.db')
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f'\nDB size: {size_mb:.1f} MB')
        print('DONE! Run: python app.py')


if __name__ == '__main__':
    seed_data()
