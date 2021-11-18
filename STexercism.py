import sublime
import sublime_plugin
import subprocess
import re
from sys import platform
import os
import webbrowser

settings_filename = "STexercism.sublime-settings"

def convert(text): 
    """Converts the name of the exercise into usable names for cmd"""
    s = ''.join(ch for ch in text if ch.isalnum() or ch == " ")
    str_list = s.strip().split()
    return "-".join(str_list).lower()

def toggleSomething(toggle):
    """Toggles whatever the file needed is"""
    exer_settings = sublime.load_settings(settings_filename)
    try:
        exer_settings.set(toggle, not exer_settings.get(toggle))
        sublime.save_settings(settings_filename)
        print("Current '" + toggle + "' setting: {}".format(exer_settings.get(toggle)))
    except:
        exer_settings.set(toggle, False)
        sublime.save_settings(settings_filename)
        print("Failed to change settings.\nCurrent '" + toggle + "' setting: {}".format(exer_settings.get(toggle)))

def cmdType(commands, flag = False):
    """:param commands: list of all strings to be added in"""
    submit_cli = subprocess.check_output(commands, stderr = subprocess.STDOUT)
    sublime.active_window().run_command(
                "show_panel",
                {"panel": "console", "toggle": True})
    print(submit_cli.decode('latin-1').strip())
    if flag:
        return submit_cli

def checkOS(path):
    if platform == "win32":
        os.startfile(path)
    elif platform == "darwin":
        subprocess.Popen([
            "open",
            path])
    else:
        subprocess.Popen([
            "xdg-open",
            path])

def errorMsg(err):
    return "command '{}' returned with error (code {}): {}.".format(
        err.cmd,
        err.returncode,
        err.output.decode('UTF-8').strip())

#GENERAL USE COMMANDS
class StexercismSubmitCurrentFileCommand(sublime_plugin.TextCommand):
    """submits the current file open on Sublime Text"""
    def run(self, edit):
        try:
            submit_cli = cmdType(["exercism", "submit", self.view.file_name()], True)
            exer_settings = sublime.load_settings(settings_filename)
            #Opens site if toggle is on
            if exer_settings.get("toggle_open_site_submit"):
                webbrowser.open_new(submit_cli.decode('UTF-8').strip().split("\n")[-1].strip())
        except subprocess.CalledProcessError as err:
            raise RuntimeError(errorMsg(err)
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
            raise RuntimeError(errorMsg(err)
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
            cmdType(print_list)
        except TypeError as err:
            raise RuntimeError(errorMsg(err)
                + "\n\nFlag list doesn't exist or is missing. Please check sublime-settings.")

        except subprocess.CalledProcessError as err:
            if err.returncode == 1: #This is an exception only made if there are failed tasks, works fine otherwise
                print(err.output.decode('latin-1').strip())
            else:
                try:
                    cmdtype(["python", "-m", "pytest", self.view.file_name()[:-3]+"_test.py"])
                    print("WARNING: Invalid flags. Please check sublime-settings.\nTest has been run with no flags.")
                except:
                    raise RuntimeError(errorMsg(err)
                        + "\n\nMaybe you are checking the wrong file?")

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
            submit_cli = cmdType(["exercism",
                    "download",
                    "--exercise=" + convert(exername),
                    "--track=" + stexercism_track_name], True)
            #This next part adds a pytest.ini file if you toggled the flag to be true in sublime-settings or through the command
            if stexercism_track_name == 'python' and exer_settings.get("pytest_ini_toggle"):
                directory_name = submit_cli.decode('UTF-8').strip().split("\n")[-1] + "\\pytest.ini"
                file = open(directory_name, "w")
                file.write("[pytest]\nmarkers =\n    task: A concept exercise task.")
                file.close()
                print("\npytest.ini file created at directory: " + directory_name)
            #This next part opens the directory to downloaded exercise
            if exer_settings.get("toggle_open_path_download"):
                path = submit_cli.decode('UTF-8').strip().split("\n")[-1]
                checkOS(path)
        except subprocess.CalledProcessError as err:
            raise RuntimeError(errorMsg(err))

    def input(self, args):
        if 'exername' not in args:
            return StexercismExerciseNameInputHandler()
        elif 'stexercism_track_name' not in args:
            return StexercismTrackNameInputHandler()

#MAINTENANCE PROGRAMS
class StexercismMaintListInputHandler(sublime_plugin.ListInputHandler):
    def list_items(self):
        return sublime.load_settings(settings_filename).get("maint_command_list")

class StexercismMaintenanceListCommand(sublime_plugin.TextCommand):
    def run(self, edit, stexercism_maint_list):
        try:
            self.view.run_command(stexercism_maint_list)
        except subprocess.CalledProcessError as err:
            raise RuntimeError(errorMsg(err))
    def input(self, args):
        if 'stexercism_maint_list' not in args:
            return StexercismMaintListInputHandler()

class StexercismVersionCheckCommand(sublime_plugin.TextCommand):
    """Checks version of CLI"""
    def run(self, edit):
        cmdType(["exercism", "version"])

class StexercismUpdateCommand(sublime_plugin.TextCommand):
    """Updates CLI"""
    def run(self, edit):
        cmdType(["exercism", "upgrade"])

class StexercismWorkspaceCommand(sublime_plugin.TextCommand):
    """Finds the directory to exercism and opens file on file browser of OS (if toggled)"""
    def run(self, edit):
        try:
            submit_cli = cmdType(["exercism", "workspace"], True)
            if sublime.load_settings(settings_filename).get("toggle_open_path_workspace"):
                #Checks what OS will work
                path = submit_cli.decode('UTF-8').strip().split("\n")[-1]
                checkOS(path)
        except subprocess.CalledProcessError as err:
            raise RuntimeError(errorMsg(err))

#TOGGLES
class StexercismTogglesListInputHandler(sublime_plugin.ListInputHandler):
    def list_items(self):
        return sublime.load_settings(settings_filename).get("toggle_command_list")

class StexercismTogglesListCommand(sublime_plugin.TextCommand):
    """Lists all toggle commands and runs them"""
    def run(self, edit, stexercism_toggles_list):
        try:
            self.view.run_command(stexercism_toggles_list)
        except subprocess.CalledProcessError as err:
            raise RuntimeError(errorMsg(err))
    def input(self, args):
        if 'toggle_command' not in args:
            return StexercismTogglesListInputHandler()


class StexercismTogglePytestIniCommand(sublime_plugin.TextCommand):
    """Toggles the option to auto-create a pytest.ini file when downloading a python file"""
    def run(self, edit):
        toggleSomething("pytest_ini_toggle")

class StexercismToggleOpenWindowWorkspaceCommand(sublime_plugin.TextCommand):
    """Toggles the option to open path to exercism/ when running workspace command"""
    def run(self, edit):
        toggleSomething("toggle_open_path_workspace")
#NOTE: I haven't tested this on Mac or linux b/c I don't have those OSes

class StexercismToggleOpenWindowDownloadCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        toggleSomething("toggle_open_path_download")
#NOTE: I haven't tested this on Mac or linux b/c I don't have those OSes

class StexercismToggleOpenSiteSubmitCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        toggleSomething("toggle_open_site_submit")


#TODO: Make the toggles for download and workspace open on Sublime as part of project
#instead of opening finder
#TODO: Chunk out certain repeated code into diff methods e.g.:
#Print out console command
#Error code
#TODO: Add "Download-Multiple"
