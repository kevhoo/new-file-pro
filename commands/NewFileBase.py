import sublime
import sublime_plugin
import re
import os
import datetime

TMLP_DIR = 'templates'
KEY_SYNTAX = 'syntax'
KEY_FILE_EXT = 'extension'
IS_GTE_ST3 = int(sublime.version()) >= 3000
PACKAGE_NAME = 'new-file-pro'
PACKAGES_PATH = sublime.packages_path()
BASE_PATH = os.path.abspath(os.path.dirname(__file__))


class NewFileBase(sublime_plugin.WindowCommand):
	def __init__(self, window):
		super(NewFileBase, self).__init__(window)

	def appendFileExtension(self, name, t):
		tmp = name.split('.')
		length = len(tmp)
		s_ext = tmp[length - 1]
		exts = {'css': 'css', 'html': 'html', 'js': 'js', 'json': 'json', 'php': 'php', 'php-class': 'php', 'php-interface': 'php', 'xml':'xml', 'python': 'python', 'ruby': 'ruby'}
		try:
			t_ext = exts[t]
			if (s_ext == t_ext and length == 1) or s_ext != t_ext:
				return name + '.' + t_ext
		except KeyError:
			pass
		return name;


	def appendPHPExtension(self, name):
		t = name.split('.')
		length = len(t)
		ext = t[length - 1]
		if ext != "php":
			return name + '.php'
		return name;

	def get_code(self, type='text' ):
		code = ''
		file_name = "%s.tmpl" % type
		isIOError = False

		if IS_GTE_ST3:
			tmpl_dir = 'Packages/' + PACKAGE_NAME + '/' + TMLP_DIR + '/'
			user_tmpl_dir = 'Packages/User/' + PACKAGE_NAME + '/' + TMLP_DIR + '/'
		else:
			tmpl_dir = os.path.join(PACKAGES_PATH, PACKAGE_NAME, TMLP_DIR)
			user_tmpl_dir = os.path.join(PACKAGES_PATH, 'User', PACKAGE_NAME, TMLP_DIR)

		self.user_tmpl_path = os.path.join(user_tmpl_dir, file_name)
		self.tmpl_path = os.path.join(tmpl_dir, file_name)

		if IS_GTE_ST3:
			try:
				code = sublime.load_resource(self.user_tmpl_path)
			except IOError:
				try:
					code = sublime.load_resource(self.tmpl_path)
				except IOError:
					isIOError = True
		else:
			if os.path.isfile(self.user_tmpl_path):
				code = self.open_file(self.user_tmpl_path)
			elif os.path.isfile(self.tmpl_path):
				code = self.open_file(self.tmpl_path)
			else:
				isIOError = True

		if isIOError:
			sublime.message_dialog('[Warning] No such file: ' + self.tmpl_path + ' or ' + self.user_tmpl_path)

		return self.format_tag(code)

	def format_tag(self, code):
		win = sublime.active_window()
			
		code = code.replace('\r', '') # replace \r\n -> \n
		# format
		settings = self.get_settings()
		format = settings.get('date_format', '%Y-%m-%d')
		date = datetime.datetime.now().strftime(format)
		if not IS_GTE_ST3:
			code = code.decode('utf8') # for st2 && Chinese characters
		code = code.replace('${date}', date)

		attr = settings.get('attr', {})
		for key in attr:
			code = code.replace('${%s}' % key, attr.get(key, ''))

		if settings.get('enable_project_variables', False) and hasattr(win, 'extract_variables'):
			variables = win.extract_variables()
			for key in ['project_base_name', 'project_path', 'platform']:
				code = code.replace('${%s}' % key, variables.get(key, ''))

		code = re.sub(r"(?<!\\)\${(?!\d)", '\${', code)
		return code

	def open_file(self, path, mode='r'):
		fp = open(path, mode)
		code = fp.read()
		fp.close()
		return code

	def get_settings(self, type=None):
		settings = sublime.load_settings(PACKAGE_NAME + '.sublime-settings')

		if not type:
			return settings

		opts = settings.get(type, [])
		return opts


