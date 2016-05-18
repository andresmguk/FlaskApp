# flasktaskr/views.py

###########
# imports #
###########

from forms import AddTaskForm, RegisterForm, LoginForm
from functools import wraps
from flask import Flask, flash, redirect, render_template, \
 request, session, url_for
from sqlalchemy.exc import IntegrityError
from flask.ext.sqlalchemy import SQLAlchemy
import datetime


##########
# config #
##########
app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 10

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


def flash_errors(form):
	for field, errors in form.errors.items():
		for error in errors:
			flash(u"Error in the %s field - %s" % (getattr(form, field).label.text, error), 'error')



def open_tasks(): 
	return db.session.query(Task) .filter_by(status='1') \
	.order_by(Task.due_date.asc())


def closed_tasks(): 
	return db.session.query(Task) .filter_by(status='0') \
	.order_by(Task.due_date.asc())





###################
# routes handlers #
###################

# Logout route
@app.route('/logout/')
@login_required
def logout(): 
	session.pop('logged_in', None)
	session.pop('user_id', None)
	session.pop('role', None)
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
			 	session['role'] = user.role 
			 	flash('Welcome!')
				return redirect(url_for('tasks'))
			else:
				error = 'Invalid username or password.'
	return render_template('login.html', form=form, error=error)



#Register route
@app.route('/register/', methods=['GET', 'POST']) 
def register():
	error = None
	form = RegisterForm(request.form) 
	if request.method == 'POST':
		if form.validate_on_submit(): 
			new_user = User(form.name.data, form.email.data, form.password.data,)
			
			try:
				db.session.add(new_user)
				db.session.commit()
				flash('Thanks for registering. Please login.') 
				return redirect(url_for('login'))

			except IntegrityError: # DB integrity error check
				error = 'That username and/or email already exist.'
				return render_template('register.html', form=form, error=error)

	return render_template('register.html', form=form, error=error)



# Query tasks from the database and passing them to tasks.html
@app.route('/tasks/') 
@login_required
def tasks():
	return render_template(
		'tasks.html', 
		form=AddTaskForm(request.form), 
		open_tasks=open_tasks(), 
		closed_tasks=closed_tasks()
	)


# Add new tasks 
@app.route('/add/', methods=['POST']) 
@login_required
def new_task():
	error = None
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
			return redirect(url_for('tasks')) 

	return render_template('tasks.html', form=form, error=error,
		open_tasks=open_tasks(), closed_tasks=closed_tasks())
	
	


# Mark tasks as complete
@app.route('/complete/<int:task_id>/') 
@login_required
def complete(task_id):
	
	# set a new var
	new_id = task_id 
	
	# Query the db an assign to a var
	task = db.session.query(Task) .filter_by(task_id=new_id) 
	
	# check if the tasks belong to the user
	if session['user_id'] == task.first().user_id or session['role'] == 'admin': 

		# upadate status
		task. update({"status": "0"})
		# commit changes an close db
		db.session.commit()
		
		# flash message and redirect to tasks.html
		flash('The task is complete!') 
		return redirect(url_for('tasks'))

	else:
		flash('You can only update tasks that belong to you')
		return redirect(url_for('tasks'))




# Delete Tasks
@app.route('/delete/<int:task_id>/') 
@login_required
def delete_entry(task_id):

	# set a new var
	new_id = task_id 
	
	# Query and delete the entry
	task = db.session.query(Task) .filter_by(task_id=new_id)

	if session['user_id'] == task.first().user_id or session['role'] == 'admin': 

		task.delete()
	
		# commit changes an close db
		db.session.commit()
		
		# flash message and redirect to tasks.html
		flash('The task was deleted.')
		return redirect(url_for('tasks'))

	else:
		flash('You can only delete tasks that belong to you')
		return redirect(url_for('tasks'))







