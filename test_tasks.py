# flasktaskr4/test_tasks.py 


###########
# imports #
###########

import os
import unittest 

from views import app, db
from _config import basedir
from models import User

TEST_DB = 'test.db'


################
# Unit Testing #
################

class AllTests(unittest.TestCase):

	#### Setup and teardown ###
	###########################

	# executed prior each test
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, TEST_DB)
		self.app = app.test_client()
		db.create_all()

	# executed after each test
	def tearDown(self):
		db.session.remove()
		db.drop_all()


	###############
	#### Tests ####
	###############


	# Check if we can add a user to the db - sort of a unity and integrity test
	#def test_user_setup(self):
	#	new_user = User("michael", "michael@aol.com", "1234567")
	#	db.session.add(new_user)
	#	db.session.commit()
	#	test = db.session.query(User).all()
	#	for t in test:
	#		t.name 
	#	assert t.name == "michael"


	######################
	### helper methods ###
	######################

	# login helper method 
	def login(self, name, password):
		return self.app.post('/', data=dict(name=name, password=password), follow_redirects=True)

	# register helper method
	def register(self, name, email, password, confirm):
		return self.app.post('register/', data=dict(name=name, email=email, \
			password=password, confirm=confirm), follow_redirects=True)

	# logout helper method
	def logout(self):
		return self.app.get('logout/', follow_redirects=True)

	# create a user directly in the db
	def create_user(self, name, email, password):
		new_user = User(name=name, email=email, password=password)
		db.session.add(new_user)
		db.session.commit()

	# create a task (not in the db)
	def create_task(self):
		return self.app.post('add/', data=dict(
			name='Go to the bank',
			due_date='01/12/2017',
			priority='5',
			posted_date='05/01/2016',
			status='1'), follow_redirects=True)





	#############################################
	#### Tasks related function unit tests ######
	#############################################

	# Two helper methods added: i. create_user ii. create_task (see above) 

	# 10
	def test_users_can_add_tasks(self):
		self.create_user('Andre', 'andre@lolo.pt', '123456')
		self.login('Andre', '123456')
		self.app.get('tasks/', follow_redirects=True)
		response = self.create_task()
		self.assertIn(b'New entry was successfully posted. Thanks.', response.data)

	# 11
	def test_cannot_add_tasks_when_error_on_data(self):
		self.create_user('Andre', 'andre@lolo.pt', '123456')
		self.login('Andre', '123456')
		self.app.get('tasks/', follow_redirects=True)
		response = self.app.post('add/', data=dict(
			name='Go to the bank',
			due_date='',
			priority='5',
			posted_date='05/01/2016',
			status='1'), follow_redirects=True)
		self.assertIn(b'This field is required.', response.data)

	# 12
	def test_users_can_complete_tasks(self):
		self.create_user('Andre', 'andre@lolo.pt', '123456')
		self.login('Andre', '123456')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		response = self.app.get('complete/1/', follow_redirects=True)
		self.assertIn(b'The task is complete!', response.data)


	# 13
	def test_users_can_delete_tasks(self):
		self.create_user('Andre', 'andre@lolo.pt', '123456')
		self.login('Andre', '123456')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		response = self.app.get('delete/1/', follow_redirects=True)
		self.assertIn(b'The task was deleted.', response.data)

	# 14 
	def test_user_cannot_complete_tasks_they_did_not_create(self):
		self.create_user('Andre', 'andre@lolo.pt', '123456')
		self.login('Andre', '123456')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.create_user('filipe', 'filipe@lolo.pt', '123456')
		self.login('filipe', '123456')
		self.app.get('tasks/', follow_redirects=True)
		response = self.app.get('complete/1/', follow_redirects=True)
		self.assertIn(b'You can only update tasks that belong to you', response.data)


	# 15
	def test_user_cannot_delete_tasks_they_did_not_create(self):
		self.create_user('Andre', 'andre@lolo.pt', '123456')
		self.login('Andre', '123456')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.create_user('filipe', 'filipe@lolo.pt', '123456')
		self.login('filipe', '123456')
		self.app.get('tasks/', follow_redirects=True)
		response = self.app.get('delete/1/', follow_redirects=True)
		self.assertIn(b'You can only delete tasks that belong to you', response.data)




### to run the file ####

if __name__ == "__main__":
	unittest.main()









