# flasktaskr4/test_users.py 


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






	#### Login function unit tests ####
	###################################

	# 1
	def test_form_is_presented_on_login_page(self):
		response = self.app.get('/') 
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Please login to access your task list.', response.data)

	# 2
	def test_users_cannot_login_unless_registered(self):
		response = self.login('foo', 'bar') # login helper method
		self.assertIn(b'Invalid username or password.', response.data)

	# 3
	def test_users_can_loggin_when_registered(self):
		self.register('filipe', 'filipe@sapo.pt', '123456', '123456') # register helper methof
		response = self.login('filipe', '123456') # login helper method
		self.assertIn('Welcome!', response.data)

	# 4 - similar to # 2
	def test_invalid_form_data(self):
		self.register('filipe', 'filipe@sapo.pt', '123456', '123456') # register helper methof
		response = self.login('Joaquim', '123456') # login helper method)
		self.assertIn(b'Invalid username or password.', response.data)



    ######################################
	#### Register function unit tests ####
	######################################

	# 5
	def test_form_is_presented_on_register_page(self):
		response = self.app.get('register/') 
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Please register to access the task list.', response.data)

	# 6 - users registration (form validation)
	def test_user_registration(self):
		self.app.get('register/', follow_redirects=True)
		response = self.register('filipe', 'filipe@sapo.pt', '123456', '123456')
		self.assertIn(b'Thanks for registering. Please login.', response.data)

	# 7 - inccorret data on registration - similar to # 2 (avoid DRY) -> integrity test too!
	def test_user_registration_error(self):
		self.app.get('register/', follow_redirects=True)
		self.register('filipe', 'filipe@sapo.pt', '123456', '123456')
		self.app.get('register/', follow_redirects=True)
		response = self.register('filipe', 'filipe@sapo.pt', '123456', '123456')
		self.assertIn(b'That username and/or email already exist.', response.data)



	######################################
	#### Logout function unit tests ######
	######################################

	# 8
	def test_logged_in_users_can_logout(self):
		self.register('filipe', 'filipe@sapo.pt', '123456', '123456')
		self.login('filipe', '123456')
		response = self.logout()
		self.assertIn(b'Goodbye!', response.data)


	# 9
	def test_not_logged_in_users_can_logout(self):
		response = self.logout()
		self.assertNotIn(b'Goodbye!', response.data) # assertNotIn



	######################################
	#### Admin Permissions unit tests ######
	######################################

	# 8
	def test_default_user_role(self):
		db.session.add(
			User("johnny", "john@doe.com", "johnny"))

		db.session.commit()

		users = db.session.query(User).all()
		print users

		for user in users:
			self.assertEquals(user.role, 'user')





### to run the file ####

if __name__ == "__main__":
	unittest.main()









