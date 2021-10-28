import sublime
import sublime_plugin
import subprocess
import re

settings_filename = "STexercism.sublime-settings"

class StexercismSubmitCurrentFileCommand(sublime_plugin.TextCommand):
    """submits the current file open on Sublime Text"""
    def run(self, edit):
        try:
            submit_cli = subprocess.check_output(
                ["exercism",
                "submit",
                self.view.file_name()],
                stderr=subprocess.STDOUT)
            sublime.active_window().run_command(
                "show_panel",
                {"panel": "console", "toggle": True})
            print(submit_cli.decode('UTF-8').strip())
        except subprocess.CalledProcessError as err:
            raise RuntimeError(
                "command '{}' returned with error (code {}): {}.".format(
                    err.cmd,
                    err.returncode,
                    err.output.decode('UTF-8').strip())
                + "\n\nMaybe you submitted the wrong file?")
# TODO: make sure you get the right file? this would be very language dependent

class StexercismOpenCurrentExerciseCommand(sublime_plugin.TextCommand):
    """Opens the current exercise's website page"""
    def run(self, edit):
        try: 
            match = re.search(
                r'exercism\\\w*\\([-\w]*)\\',
                self.view.file_name())
            if match:
                open_cli = subprocess.check_output([
                    "exercism",
                    "open",
                    self.view.file_name()[:self.view.file_name().rfind("\\")]])
            else:
                raise RuntimeError(
                    "This program isn't in the exercism folder." 
                    + "\nMake sure the directory ends with"
                    + "\n'exercism\\EXERISE_NAME\\FILE_NAME.TYPE'")
        except subprocess.CalledProcessError as err:
            raise RuntimeError(
                "command '{}' returned with error (code {}): {}.".format(
                    err.cmd,
                    err.returncode,
                    err.output.decode('UTF-8').strip())
                + "\n\nIs the directory correct?\n"
                + match.group(0)
                + self.view.file_name())

class StexercismTestCurrentFilePythonCommand(sublime_plugin.TextCommand):
    """(Python only) Tests the current file using pytest"""
    def run(self, edit):
        try:
            exer_settings = sublime.load_settings(settings_filename)
            print_list = ["python", "-m", "pytest"]
            print_list.extend(exer_settings.get("pytest_testing_flags"))
            print_list.append(self.view.file_name()[:-3]+"_test.py")
            submit_cli = subprocess.check_output(
                print_list,
                stderr=subprocess.STDOUT)
            sublime.active_window().run_command(
                "show_panel",
                {"panel": "console", "toggle": True})
            print(submit_cli.decode('UTF-8').strip())
        except TypeError:
            raise RuntimeError(
                "command '{}' returned with error (code {}): {}.".format(
                    err.cmd,
                    err.returncode,
                    err.output.decode('UTF-8').strip())
                + "\n\nFlag list doesn't exist or is missing. Please check sublime-settings.")

        except subprocess.CalledProcessError as err:
            if err.returncode == 1: #This is an exception only made if there are failed tasks, works fine otherwise
                print(err.output.decode('UTF-8').strip())
            else:
                raise RuntimeError(
                    "command '{}' returned with error (code {}): {}.".format(
                        err.cmd,
                        err.returncode,
                        err.output.decode('UTF-8').strip())
                    + "\n\nMaybe you are checking the wrong file? Also check your flags in sublime-settings")
#TODO_IDEA: Add more tracks, possibly make it a list on Sublime to not fill command list.


def convert(text): 
    """Converts the name of the exercise into usable names for cmd"""
    s = ''.join(ch for ch in text if ch.isalnum() or ch == " ")
    str_list = s.strip().split()
    return "-".join(str_list).lower()

class StexercismExerciseNameInputHandler(sublime_plugin.TextInputHandler):
    """Input for name of exercise. Not case/spacing/symbol-sensitive"""
    def name(self):
        return "exername"

    def placeholder(self):
        return "Exercise Name"

    def next_input(self, args):
        if 'trackname' not in args:
            return StexercismTrackNameInputHandler()

class StexercismTrackNameInputHandler(sublime_plugin.ListInputHandler):
    """Lists out all the tracks to pick"""
    def list_items(self):
        return sublime.load_settings(settings_filename).get("track_list")

    def placeholder(self):
        return "Track Name"


class StexercismDownloadFileCommand(sublime_plugin.TextCommand):
    """Uses gathered input to download an exercise file"""
    def run(self, edit, exername, stexercism_track_name): 
        try:
            exer_settings = sublime.load_settings(settings_filename)
            submit_cli = subprocess.check_output(
                ["exercism",
                "download",
                "--exercise=" + convert(exername),
                "--track=" + stexercism_track_name],
                stderr=subprocess.STDOUT)
            sublime.active_window().run_command(
                "show_panel",
                {"panel": "console", "toggle": True})
            print(submit_cli.decode('UTF-8').strip())
            #This next part adds a pytest.ini file if you toggled the flag to be true in sublime-settings or through the command
            if stexercism_track_name == 'python' and exer_settings.get("pytest_ini_toggle"):
                directory_name = submit_cli.decode('UTF-8').strip().split("\n")[-1] + "\\pytest.ini"
                f = open(directory_name, "w")
                f.write("[pytest]\nmarkers =\n    task: A concept exercise task.")
                f.close()
                print("\npytest.ini file created at directory: " + directory_name)
        except subprocess.CalledProcessError as err:
            raise RuntimeError(
                "command '{}' returned with error (code {}): {}.".format(
                    err.cmd,
                    err.returncode,
                    err.output.decode('UTF-8').strip()))

    def input(self, args):
        if 'exername' not in args:
            return StexercismExerciseNameInputHandler()
        elif 'stexercism_track_name' not in args:
            return StexercismTrackNameInputHandler()
#TODO_IDEA: Can also include option for auto opening the file that you downloaded?
#(Very track-specific and no consistent way to do so)
#Possibly for python: get dir > do ls on dir > find the file with the correct type (.py) and doesn't have "_test"

class StexercismTogglePytestIniCommand(sublime_plugin.TextCommand):
    """Toggles the option to auto-create a pytest.ini file when downloading a python file"""
    def run(self, edit):
        exer_settings = sublime.load_settings(settings_filename)
        try:
            exer_settings.set(
                "pytest_ini_toggle", 
                not exer_settings.get("pytest_ini_toggle"))
            sublime.save_settings(settings_filename)
            print("Current pytest.ini auto-create setting: " + str(exer_settings.get("pytest_ini_toggle")))
        except:
            exer_settings.set("pytest_ini_toggle", False)
            sublime.save_settings(settings_filename)
            print("Current pytest.ini auto-create setting: " + str(exer_settings.get("pytest_ini_toggle")))
