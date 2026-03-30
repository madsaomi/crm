from datetime import datetime
from extensions import db


class Manager(db.Model):
    __tablename__ = 'managers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    students = db.relationship('Student', backref='manager', lazy=True)

    def __repr__(self):
        return f'<Manager {self.name}>'


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    groups = db.relationship('Group', backref='teacher', lazy=True)

    def __repr__(self):
        return f'<Teacher {self.name}>'


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=True)

    enrollments = db.relationship('Enrollment', backref='student', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='student', lazy=True, cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Student {self.name}>'


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    schedule_type = db.Column(db.String(10), default='even')  # even / odd
    room = db.Column(db.String(50), nullable=True)
    start_time = db.Column(db.String(5), default='18:00')  # format HH:MM
    monthly_fee = db.Column(db.Float, default=0.0)  # expected monthly payment per student

    enrollments = db.relationship('Enrollment', backref='group', lazy=True, cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='group', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Group {self.name}>'


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Enrollment student={self.student_id} group={self.group_id}>'


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Payment {self.amount} for student={self.student_id}>'


class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(10), default='present')  # present / absent
    comment = db.Column(db.String(500), nullable=True)  # reason for absence

    def __repr__(self):
        return f'<Attendance student={self.student_id} status={self.status}>'
