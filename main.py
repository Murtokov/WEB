# -*- coding: utf8 -*-

import sys
import os
import sqlite3
from flask import Flask, render_template, redirect, request, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.register import RegisterForm
from data.users import User
from data.login import LoginForm
from data.courseworks import Coursework
from data.directions import Direction
from flask_restful import abort
from data.add_coursework import AddCourseworkForm
from data.add_direction import AddDirectionForm
from werkzeug.utils import secure_filename
from data.add_logo import AddLogoForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api_key = "40d1649f-0493-4b70-98ba-98533de7710b"
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/kursovik.sqlite")
app.config['UPLOAD_FOLDER'] = r'F:\Users\User\PycharmProjects\HTML\static\img'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 10
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


@app.route("/")
@app.route("/base")
def base():
    db_sess = db_session.create_session()
    courseworks = db_sess.query(Coursework).all()
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    deadlines = {coursework.id: (str(coursework.deadline).split()[0]) for coursework in courseworks}
    imag = {coursework.id: f'''<img src="('static', filename='static\img\{coursework.id}.jpg')>"'''
            for coursework in courseworks}
    return render_template("main.html", courseworks=courseworks, names=names, deadlines=deadlines, imag=imag)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload/<int:id>', methods=['GET', 'POST'])
def upload_file(id):
    form = AddLogoForm()
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            formt = secure_filename(file.filename).split('.')[-1]
            filename = f'{id}_coursework.{formt}'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db_sess = db_session.create_session()
            courseworks = db_sess.query(Coursework).filter(Coursework.id == id,
                                                           (Coursework.leader == current_user.id) | (
                                                                   current_user.id == 1) | (
                                                                   current_user.is_teacher == 1)).first()
            # img = Image.open(f'static\img\{filename}')
            try:
                # fin = open(f'static\img\{filename}', "rb")
                # img = fin.read()
                # courseworks.file = sqlite3.Binary(img)
                courseworks.file = filename
                db_sess.commit()
            except BaseException:
                pass
    return render_template("upload.html")


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route("/directions")
def directions():
    db_sess = db_session.create_session()
    directions = db_sess.query(Direction).all()
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("directions.html", directions=directions, names=names)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неверный логин или пароль", form=form)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form,
                                   message="Такой пользователь уже существует")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            course=form.course.data,
            address=form.address.data,
            email=form.email.data,
            is_teacher=form.is_teacher.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/coursework_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def coursework_delete(id):
    db_sess = db_session.create_session()
    courseworks = db_sess.query(Coursework).filter(Coursework.id == id,
                                                   (Coursework.leader == current_user.id) | (
                                                           current_user.id == 1) | (
                                                           current_user.is_teacher == 1)).first()

    if courseworks:
        db_sess.delete(courseworks)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/add_coursework', methods=['GET', 'POST'])
def add_coursework():
    add_form = AddCourseworkForm()
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    ids = {name.id for name in users}
    ids = max(ids)
    dirs_ = db_sess.query(Direction).all()
    dirs = {name.id for name in dirs_}
    dirs = max(dirs)
    files = request.files.getlist('file')
    if files:
        print(files)
    if add_form.validate_on_submit():
        coursework = Coursework(
            title=add_form.title.data,
            leader=add_form.leader.data,
            coursework=add_form.coursework.data,
            coursework_sheets=add_form.coursework_sheets.data,
            students=add_form.students.data,
            deadline=add_form.deadline.data,
            direction=add_form.direction.data,
            is_finished=add_form.is_finished.data
        )
        db_sess.add(coursework)
        db_sess.commit()
        return redirect('/')
    return render_template('add_coursework.html', form=add_form, ids=ids, dirs=dirs)


@app.route('/coursework_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def coursework_edit(id):
    form = AddCourseworkForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        courseworks = db_sess.query(Coursework).filter(Coursework.id == id,
                                                       (Coursework.leader == current_user.id) | (
                                                               current_user.id == 1) | (
                                                               current_user.is_teacher == 1)).first()

        if courseworks:
            form.title.data = courseworks.title
            form.leader.data = courseworks.leader
            form.coursework.data = courseworks.coursework
            form.coursework_sheets.data = courseworks.coursework_sheets
            form.students.data = courseworks.students
            form.deadline.data = courseworks.deadline
            form.direction.data = courseworks.direction
            form.is_finished.data = courseworks.is_finished
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        courseworks = db_sess.query(Coursework).filter(Coursework.id == id,
                                                       (Coursework.leader == current_user.id) | (
                                                               current_user.id == 1) | (
                                                               current_user.is_teacher == 1)).first()
        if courseworks:
            courseworks.title = form.title.data
            courseworks.leader = form.leader.data
            courseworks.coursework = form.coursework.data
            courseworks.coursework_sheets = form.coursework_sheets.data
            courseworks.students = form.students.data
            courseworks.deadline = form.deadline.data
            courseworks.direction = form.direction.data
            courseworks.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_coursework.html', form=form)


@app.route('/add_direction', methods=['GET', 'POST'])
def add_direction():
    add_form = AddDirectionForm()
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    ids = {name.id for name in users}
    ids = max(ids)
    if add_form.validate_on_submit():
        direction = Direction(
            title=add_form.title.data,
            teacher=add_form.teacher.data,
            students=add_form.students.data,
            email=add_form.email.data
        )
        db_sess.add(direction)
        db_sess.commit()
        return redirect('/directions')
    return render_template('add_direction.html', form=add_form, ids=ids)


@app.route('/direction_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def direction_delete(id):
    db_sess = db_session.create_session()
    directions = db_sess.query(Direction).filter(Direction.id == id,
                                                 (current_user.id == 1) | (
                                                         current_user.is_teacher == 1)).first()

    if directions:
        db_sess.delete(directions)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/directions')


@app.route('/direction_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def direction_edit(id):
    form = AddDirectionForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        directions = db_sess.query(Direction).filter(Direction.id == id,
                                                     (current_user.id == 1) | (
                                                             current_user.is_teacher == 1)).first()

        if directions:
            form.title.data = directions.title
            form.teacher.data = directions.teacher
            form.students.data = directions.students
            form.email.data = directions.email
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        directions = db_sess.query(Direction).filter(Direction.id == id,
                                                     (current_user.id == 1) | (
                                                             current_user.is_teacher == 1)).first()
        if directions:
            directions.title = form.title.data
            directions.teacher = form.teacher.data
            directions.students = form.students.data
            directions.email = form.email.data
            db_sess.commit()
            return redirect('/directions')
        else:
            abort(404)
    return render_template('add_direction.html', form=form)


def main():
    db_session.global_init("db/kursovik.sqlite")
    app.run()


if __name__ == '__main__':
    main()
