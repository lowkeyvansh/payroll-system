from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payroll.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    position = db.Column(db.String(150), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)

class WorkLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    hours_worked = db.Column(db.Float, nullable=False)

class EmployeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    position = StringField('Position', validators=[DataRequired(), Length(min=2, max=150)])
    hourly_rate = DecimalField('Hourly Rate', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Employee')

class WorkLogForm(FlaskForm):
    employee_id = IntegerField('Employee ID', validators=[DataRequired()])
    hours_worked = DecimalField('Hours Worked', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Log Hours')

db.create_all()

@app.route('/')
def home():
    employees = Employee.query.all()
    work_logs = WorkLog.query.all()
    return render_template('index.html', employees=employees, work_logs=work_logs)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        new_employee = Employee(name=form.name.data, position=form.position.data, hourly_rate=form.hourly_rate.data)
        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_employee.html', form=form)

@app.route('/log_hours', methods=['GET', 'POST'])
def log_hours():
    form = WorkLogForm()
    if form.validate_on_submit():
        new_work_log = WorkLog(employee_id=form.employee_id.data, hours_worked=form.hours_worked.data)
        db.session.add(new_work_log)
        db.session.commit()
        flash('Hours logged successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('log_hours.html', form=form)

@app.route('/payroll_report')
def payroll_report():
    employees = Employee.query.all()
    payroll = []
    for employee in employees:
        work_logs = WorkLog.query.filter_by(employee_id=employee.id).all()
        total_hours = sum(log.hours_worked for log in work_logs)
        total_pay = total_hours * employee.hourly_rate
        payroll.append({
            'name': employee.name,
            'position': employee.position,
            'total_hours': total_hours,
            'total_pay': total_pay
        })
    return render_template('payroll_report.html', payroll=payroll)

if __name__ == '__main__':
    app.run(debug=True)
