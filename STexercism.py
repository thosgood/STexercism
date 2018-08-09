import sublime
import sublime_plugin
import subprocess
import re


class SubmitCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        submit_cli = subprocess.check_output(["exercism", "submit", self.view.file_name()])
        print(submit_cli)

# TODO: make sure you get the right file? use directory name...

class OpenCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        match = re.search(r'exercism/\w*/([-\w]*)/', self.view.file_name())
        if match:
            open_cli = subprocess.check_output(["exercism", "open", match.group(1)])