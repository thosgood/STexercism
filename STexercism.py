import sublime
import sublime_plugin
import subprocess


class SubmitCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        submit_cli = subprocess.check_output(["exercism", "submit", self.view.file_name()])
        print(submit_cli)

# TODO: make sure you get the right file? use directory name...
