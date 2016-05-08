# flasktaskr/views.py

###########
# imports #
###########

from forms import AddTaskForm, RegisterForm, LoginForm
from functools import wraps
from flask import Flask, flash, redirect, render_template, \
 request, session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
import datetime


##########
# config #
##########
app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

# import models (dd tables)
from models import Task, User

####################
# helper functions #
####################

def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs) 
		else:
			flash('You need to login first.')
			return redirect(url_for('login')) 
	return wrap



###################
# routes handlers #
###################

# Logout route
@app.route('/logout/')
def logout(): 
	session.pop('logged_in', None)
	session.pop('user_id', None) 
	flash('Goodbye!')
	return redirect(url_for('login'))


# Login route
@app.route('/', methods=['GET', 'POST']) 
def login():
	error = None
	form = LoginForm(request.form) 
	if request.method == 'POST':
		if form.validate_on_submit(): 
			user = User.query.filter_by(name=request.form['name']).first()
			if user is not None and user.password == request.form['password']: 
			 	session['logged_in'] = True
			 	session['user_id'] = user.id 
			 	flash('Welcome!')
				return redirect(url_for('tasks'))
			else:
				error = 'Invalid username or password.'
		else:
			error = 'Both fields are required.'
	return render_template('login.html', form=form, error=error)



#Register route
@app.route('/register/', methods=['GET', 'POST']) 
def register():
	error = None
	form = RegisterForm(request.form) 
	if request.method == 'POST':
		if form.validate_on_submit(): 
			new_user = User(form.name.data, form.email.data, form.password.data,)
			db.session.add(new_user)
			db.session.commit()
			flash('Thanks for registering. Please login.') 
			return redirect(url_for('login'))
		else:
			error = 'Incorrect data input. Please try again!'

	return render_template('register.html', form=form, error=error)




# Query tasks from the database and passing them to tasks.html
@app.route('/tasks/') 
@login_required
def tasks():
	open_tasks = db.session.query(Task) .filter_by(status='1') \
	.order_by(Task.due_date.asc())

	closed_tasks = db.session.query(Task) .filter_by(status='0') \
	.order_by(Task.due_date.asc())

	return render_template(
		'tasks.html', 
		form=AddTaskForm(request.form), 
		open_tasks=open_tasks, 
		closed_tasks=closed_tasks
	)


# Add new tasks 
@app.route('/add/', methods=['POST']) 
@login_required
def new_task():
	
	form = AddTaskForm(request.form)

	if request.method == 'POST':
		if form.validate_on_submit():
			new_task = Task(
				form.name.data,
				form.due_date.data,
				form.priority.data,
				datetime.datetime.utcnow(),
				'1',
				session['user_id']
			)
			# Add and commit to the db
			db.session.add(new_task)
			db.session.commit()

			# flash message and redirect to tasks.html
			flash('New entry was successfully posted. Thanks.') 

		else:
			error = 'Incorrect data input. Please try again!'
	
	return redirect(url_for('tasks'))


# Mark tasks as complete
@app.route('/complete/<int:task_id>/') 
@login_required
def complete(task_id):
	
	# set a new var
	new_id = task_id 
	
	# Query and update the database
	db.session.query(Task) .filter_by(task_id=new_id) .update({"status": "0"})
	
	# commit changes an close db
	db.session.commit()
	
	# flash message and redirect to tasks.html
	flash('The task is complete!') 
	return redirect(url_for('tasks'))


# Delete Tasks
@app.route('/delete/<int:task_id>/') 
@login_required
def delete_entry(task_id):

	# set a new var
	new_id = task_id 
	
	# Query and delete the entry
	db.session.query(Task) .filter_by(task_id=new_id) .delete()
	
	# commit changes an close db
	db.session.commit()
	
	# flash message and redirect to tasks.html
	
	flash('The task was deleted.')
	return redirect(url_for('tasks'))








