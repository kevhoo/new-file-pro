import sublime
import sublime_plugin
from .NewFileBase import NewFileBase
from ..libs.SideBarAPI import SideBarItem, SideBarSelection, SideBarProject
from threading import Thread

#import traceback

DEFAULT_FILE_TYPE = 'txt'

class NewFilePro(NewFileBase):
	def __init__(self, window):
		super(NewFilePro, self).__init__(window)

	def run(self, paths = [], name = '', t = DEFAULT_FILE_TYPE ):
		code = ''
		if t != DEFAULT_FILE_TYPE:
			code = self.get_code(t)
		import functools
		self.window.run_command('hide_panel')
		self.window.show_input_panel("New " + t.upper() + " File: ", name, functools.partial(self.on_done, paths, False, t, code), None, None);

	def on_done(self, paths, relative_in_project, t, code, name):

		name = self.appendFileExtension(name, t)
		paths = SideBarSelection(paths).getSelectedDirectoriesOrDirnames()
		if not paths:
			paths = SideBarProject().getDirectories()
			if paths:
				paths = [SideBarItem(paths[0], False)]

		if not paths:
			sublime.active_window().new_file()		
		else:
			for item in paths:
				item = SideBarItem(item.join(name), False)
				if item.exists():
					sublime.error_message("Unable to create file, file or folder exists.")
					self.run(paths, name, t)
					return
				else:
					try:
						item.create()
						item.edit()
						t = Thread(target=self.set_code, args=(code,))
						t.start()
					except:
						#traceback.print_exc()
						sublime.error_message("Unable to create file:\n\n"+item.path())
						self.run(paths, name, t)
						return
			SideBarProject().refresh();	
			

	def set_code(self, code):
		sublime.active_window().active_view().run_command('insert_snippet', {'contents': code})



