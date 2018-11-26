import traceback
import requests
import json
import os
from git import Repo
from tempfile import mkdtemp
from getpass import getpass

BASE_URL = 'https://algorithmia.com'
SESSION_KEY = 'ALGO_SESSION'
XSRF_KEY = 'XSRF-TOKEN'

# Set True for verbose output
verbose_output = False

class AlgorithmPublisher:

	@staticmethod
	def interactice_login():
		username = input('Username: ')
		passwd = getpass('Password for {}: '.format(username))
		return login(username=username, password=passwd)

	@staticmethod
	def login(username=None, password=None):
		if not username:
			username = os.environ['ALGORITHMIA_USERNAME']
		if not password:
			password = os.environ['ALGORITHMIA_PASSWORD']
		apub = AlgorithmPublisher(username, password)
		apub.create_session()
		return apub


	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.session = None

	def create_session(self):
		self.session = self.__get_session_and_cookies()
		if self.session is None:
			raise Exception('Unable to create a session. This maybe due to an incorrect username/password.')

	def close_session(self):
		self.session = None

	def create_algorithm(self, algo_name, algo_config=None):
		'''
		Description: Tries to create an algorithm on the Algorithmia platform.
			Fails if algorithm exists.
		Parameters: Username, password and algorithm name
		Returns: True if algorithm is created successfully, False if not
		'''
		self.__fail_on_no_session()

		algo_exists = self.algorithm_exists(algo_name)

		if not algo_exists:
			self.__create_algorithm_namespace(algo_name, algo_config)
			return True
		else:
			self.__debug_print("Algorithm already exists...")
			return False

	def git_clone(self, algo_name, local_repo_location=None):
		'''
		Description: Clones an Algorithmia algorithm repository locally.
			If no local location is given, will use temp location instead.
		Parameters: Username, password, algorithm name, (optional) local repo location.
		Returns: Cloned repo object
		'''
		self.__fail_on_no_session()

		git_url = self.__get_git_url(algo_name)

		if isinstance(local_repo_location, type(None)):
			local_repo_location = mkdtemp()+'/'+algo_name

		cloned_repo = Repo.clone_from(git_url, local_repo_location)
		return cloned_repo

	def git_push(self, cloned_repo, changed_files, commit_message=None):
		'''
		Description: Adds changed files, commits the changes.
			If no commit message is provided, default templating message is applied.
		Parameters: Cloned repo object, changed file list and (optional) commit message
		Returns: True if git push is successful, if not False
		'''
		self.__fail_on_no_session()

		if isinstance(commit_message, type(None)):
			commit_message = 'Applied algorithm template.'
	
		successful_git_action = self.__git_add_commit_push(cloned_repo, changed_files, commit_message)

		if successful_git_action:
			self.__debug_print('Successfully added files to git, commited them, and pushed them back to algorithmia.')
			return True
		else:
			self.__debug_print('Failed to perform git actions...')
			return False

	def publish_algorithm(self, algo_name, publish_config=None):
		'''
		Description: Publishes a given algorithm on the Algorithmia platform
		Parameters: Username, password, algorithm name, (optional) publishing config
		Returns: The API endpoint for the published algorithm
		'''
		self.__fail_on_no_session()

		algo_api_loc = self.__create_api_endpoint(algo_name, publish_config)
	
		return algo_api_loc

	def algorithm_exists(self, algo_name):
		'''
		Parameters: Algorithm name
		Returns: If the given algorithm exists (bool)
		'''
		self.__fail_on_no_session()
		algorithm_list = self.__list_algorithms()
		__algorithm_exists = len([x for x in algorithm_list if x['algoname'] == algo_name]) != 0
		return __algorithm_exists

	def __fail_on_no_session(self):
		if self.session is None:
			raise Exception('There is no session present. Start one before attempting to perform algorithm operation.')

	def __get_session_and_cookies(self):
		'''
		Parameters: Algorithmia username & password
		Returns: Session with keys needed to enact all webapi actions
			If it can't get keys, it'll return a None
		'''
		signin_url = BASE_URL+'/webapi/signin'

		login_payload = {'username': self.username, 'password': self.password}
		login_headers = {'Content-Type': 'application/json'}

		session = requests.Session()

		# Let's get the session key
		r = session.post(signin_url, data=json.dumps(login_payload), headers=login_headers)
		if not SESSION_KEY in r.cookies:
			self.__debug_print('Failed to get ' + SESSION_KEY)
			return None

		# Let's get the cross token key
		r2 = session.get(BASE_URL)
		if not XSRF_KEY in r2.cookies:
			self.__debug_print('Failed to get ' + XSRF_KEY)
			return None

		return session



	def __debug_print(self, message):
		if verbose_output:
			print(message)

	def __get_git_url(self, algo_name):
		'''
		Description: Returns the git url of an given algorithm & username
		Parameters: Username, password, algorithm name
		Returns: Git url of the algorithm
		'''
		git_url = 'https://'+self.username+':'+self.password+'@git.algorithmia.com/git/'+self.username+'/'+algo_name+'.git'
		return git_url


	def __list_algorithms(self):
		'''
		Parameters: Algorithm sessin & xsrf_token
		Returns: A list of algorithm names
		'''
		algo_list_url = BASE_URL+'/users/'+self.username+'/algorithms'

		algo_list_headers = {
			XSRF_KEY: self.session.cookies[XSRF_KEY],
			'Accept': 'application/json'
		}

		# Let's a list of algorithms that were created
		r3 = self.session.get(algo_list_url, headers=algo_list_headers)

		algorithm_list = json.loads(r3.text)

		return algorithm_list

	def __create_algorithm_namespace(self, algo_name, algo_config=None):
		'''
		Parameters: Algorithm session, username, algorithm name and algorithm settings
		Returns: True for successful creation, and False if not
		'''
		create_algo_url = BASE_URL+'/algorithms'

		# If not algo config is provided, we're going to use the default below
		if isinstance(algo_config, type(None)):
			algo_create_payload = {
				'username': self.username,
				'algolabel': algo_name,
				'algoname': algo_name,
				'language': 'python3-1',
				'packageset': None,
				'source_world': True,
				'license': 'apl',
				'has_internet': True,
				'can_recurse': True,
				'gpu_advanced': False
			}
		else:
			algo_create_payload = algo_config

		algo_create_headers = {
			XSRF_KEY: self.session.cookies[XSRF_KEY],
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		}
		# Let's create an algorithm from scratch
		r4 = self.session.post(create_algo_url, headers=algo_create_headers, data=json.dumps(algo_create_payload))
		if r4.status_code==200:
			self.__debug_print('Algorithm has been created!')
		else:
			self.__debug_print('Algorithm couldn\'t be created...')

	def __git_add_commit_push(self, cloned_repo, changed_files, commit_message):
		'''
		Parameters: Repo object, a list of files to add, and the commit message
		Returns: True if all git actions were successful, False if not
		'''
		try:
			cloned_repo.index.add(changed_files)
			cloned_repo.index.commit(commit_message)
			cloned_repo.remotes.origin.push()
			return True
		except Exception as err:
			traceback.print_exc()
			return False

	def __create_api_endpoint(self, algo_name, publish_config=None):
		'''
		Parameters: Algorithm session, username and algorithm name
		Returns: If successful, return algorithm api endpoint
		'''
		algo_publish_url = 'https://algorithmia.com/algorithms/'+self.username+'/'+algo_name+'/publish'

		algo_publish_headers = {
			XSRF_KEY: self.session.cookies[XSRF_KEY],
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		}

		# Use default config if it's not provided
		if isinstance(publish_config, type(None)):
			algo_publish_payload = {
				'bump_type': 'minor', # minor, major, revision
				'callable_world': False,
				'can_recurse': True,
				'credits_per_call': 0,
				'gpu_advanced': None,
				'has_internet': True,
				'release_notes': 'release notes go here',
				'sample_input': '\'sample input\'',
				'sample_output': 'hello sample input',
			}
		else:
			algo_publish_payload = publish_config

		# Let's publish the algorithm, and get an api endpoint
		r5 = self.session.post(algo_publish_url, headers=algo_publish_headers, data=json.dumps(algo_publish_payload))

		algo_version = json.loads(r5.text)['version']

		algorithm_api_location = 'algo://'+self.username+'/'+algo_name+'/'+algo_version
		self.__debug_print('Algorithm published here: ' + algorithm_api_location)
		return algorithm_api_location
