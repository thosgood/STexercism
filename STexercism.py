import sublime
import sublime_plugin
import subprocess
import re
from sys import platform
import os

settings_filename = "STexercism.sublime-settings"

def convert(text): 
    """Converts the name of the exercise into usable names for cmd"""
    s = ''.join(ch for ch in text if ch.isalnum() or ch == " ")
    str_list = s.strip().split()
    return "-".join(str_list).lower()

#GENERAL USE COMMANDS
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
        except TypeError as err:
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
                try:
                    submit_cli = subprocess.check_output(
                        ["python",
                        "-m",
                        "pytest",
                        self.view.file_name()[:-3]+"_test.py"],
                        stderr=subprocess.STDOUT)
                    sublime.active_window().run_command(
                        "show_panel",
                        {"panel": "console", "toggle": True})
                    print(submit_cli.decode('UTF-8').strip()
                    + "\nWARNING: Invalid flags. Please check sublime-settings.\nTest has been run with no flags.")
                except:
                    raise RuntimeError(
                        "command '{}' returned with error (code {}): {}.".format(
                            err.cmd,
                            err.returncode,
                            err.output.decode('UTF-8').strip())
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
            #This next part opens the directory to downloaded exercise
            if exer_settings.get("toggle_open_path_download"):
                path = submit_cli.decode('UTF-8').strip().split("\n")[-1]
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

#MAINTENANCE PROGRAMS
class StexercismMaintListInputHandler(sublime_plugin.ListInputHandler):
    def list_items(self):
        return sublime.load_settings(settings_filename).get("maint_command_list")

class StexercismMaintenanceListCommand(sublime_plugin.TextCommand):
    def run(self, edit, stexercism_maint_list):
        try:
            self.view.run_command(stexercism_maint_list)
        except subprocess.CalledProcessError as err:
            raise RuntimeError(
                "command '{}' returned with error (code {}): {}.".format(
                    err.cmd,
                    err.returncode,
                    err.output.decode('UTF-8').strip()))
    def input(self, args):
        if 'stexercism_maint_list' not in args:
            return StexercismMaintListInputHandler()

class StexercismVersionCheckCommand(sublime_plugin.TextCommand):
    """Checks version of CLI"""
    def run(self, edit):
        submit_cli = subprocess.check_output(
            ["exercism",
            "version"],
            stderr=subprocess.STDOUT)
        sublime.active_window().run_command(
            "show_panel",
            {"panel": "console", "toggle": True})
        print(submit_cli.decode('UTF-8').strip())

class StexercismUpdateCommand(sublime_plugin.TextCommand):
    """Updates CLI"""
    def run(self, edit):
        submit_cli = subprocess.check_output(
            ["exercism",
            "upgrade"],
            stderr=subprocess.STDOUT)
        sublime.active_window().run_command(
            "show_panel",
            {"panel": "console", "toggle": True})
        print(submit_cli.decode('UTF-8').strip())

class StexercismWorkspaceCommand(sublime_plugin.TextCommand):
    """Finds the directory to exercism and opens in File Explorer if on Windows"""
    def run(self, edit):
        try:
            submit_cli = subprocess.check_output(
                ["exercism",
                "workspace"],
                stderr=subprocess.STDOUT)
            sublime.active_window().run_command(
                "show_panel",
                {"panel": "console", "toggle": True})
            print(submit_cli.decode('UTF-8').strip())
            path = submit_cli.decode('UTF-8').strip().split("\n")[-1]
            
            if sublime.load_settings(settings_filename).get("toggle_open_path_workspace"):
                #Checks what OS will work
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
        except subprocess.CalledProcessError as err:
            raise RuntimeError(
                "command '{}' returned with error (code {}): {}.".format(
                    err.cmd,
                    err.returncode,
                    err.output.decode('UTF-8').strip()))

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
            raise RuntimeError(
                "command '{}' returned with error (code {}): {}.".format(
                    err.cmd,
                    err.returncode,
                    err.output.decode('UTF-8').strip()))
    def input(self, args):
        if 'toggle_command' not in args:
            return StexercismTogglesListInputHandler()


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

class StexercismToggleOpenWindowWorkspaceCommand(sublime_plugin.TextCommand):
    """Toggles the option to open path to exercism/ when running workspace command"""
    def run(self, edit):
        exer_settings = sublime.load_settings(settings_filename)
        try:
            exer_settings.set(
                "toggle_open_path_workspace", 
                not exer_settings.get("toggle_open_path_workspace"))
            sublime.save_settings(settings_filename)
            print("Current 'open path to directory (workshop)' setting: " + str(exer_settings.get("toggle_open_path_workspace")))
        except:
            exer_settings.set("toggle_open_path_workspace", True)
            sublime.save_settings(settings_filename)
            print("Current 'open path to directory (workshop)' setting: " + str(exer_settings.get("toggle_open_path_workspace")))
#NOTE: I haven't tested this on Mac or linux b/c I don't have those OSes

class StexercismToggleOpenWindowDownloadCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        exer_settings = sublime.load_settings(settings_filename)
        try:
            exer_settings.set(
                "toggle_open_path_download", 
                not exer_settings.get("toggle_open_path_download"))
            sublime.save_settings(settings_filename)
            print("Current 'open path to directory (download)' setting: " + str(exer_settings.get("toggle_open_path_download")))
        except:
            exer_settings.set("toggle_open_path_download", True)
            sublime.save_settings(settings_filename)
            print("Current 'open path to directory (download)' setting: " + str(exer_settings.get("toggle_open_path_download")))
