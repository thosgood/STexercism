import sublime
import sublime_plugin
import subprocess
import re

class StexercismSubmitCurrentFileCommand(sublime_plugin.TextCommand):
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
    def run(self, edit):
        match = re.search(
            r'exercism/\w*/([-\w]*)/',
            self.view.file_name())
        if match:
            open_cli = subprocess.check_output([
                "exercism",
                "open",
                match.group(1)])

#TODO: add options for flags -x and -ff, prolly off a listinput
class StexercismTestCurrentFilePythonCommand(sublime_plugin.TextCommand):
    def run(self, edit):
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
            print(submit_cli.decode('UTF-8').strip())
        
        except subprocess.CalledProcessError as err:
            
            if err.returncode == 1: #This is an exception only made if there are failed tasks, works fine otherwise
                print(err.output.decode('UTF-8').strip())
                pass
            else:
                raise RuntimeError(
                    "command '{}' returned with error (code {}): {}.".format(
                        err.cmd,
                        err.returncode,
                        err.output.decode('UTF-8').strip())
                    + "\n\nMaybe you are checking the wrong file?")

#TODO: Add more tracks, possibly make it a list on Sublime to not fill command list.

def convert(text): 
    """Converts the name of the exercise into usable names for cmd"""
    s = ''.join(ch for ch in text if ch.isalnum() or ch == " ")
    str_list = s.strip().split()
    return "-".join(str_list).lower()

class StexercismExerciseNameInputHandler(sublime_plugin.TextInputHandler):
    def name(self):
        return "exername"

    def placeholder(self):
        return "Exercise Name"

    def next_input(self, args):
        if 'trackname' not in args:
            return StexercismTrackNameInputHandler()

class StexercismTrackNameInputHandler(sublime_plugin.ListInputHandler):
    def list_items(self):
        return track_list

    def placeholder(self):
        return "Track Name"

#TODO: Have a settings option for if you want pytest.ini to auto create?
#Can also include option for auto opening the file that you downloaded
class StexercismDownloadFileCommand(sublime_plugin.TextCommand):
    def run(self, edit, exername, stexercism_track_name): 
        try:
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
            #this next part is a placeholder to help add a pytest.ini file to whatever folder you made
            if stexercism_track_name == 'python':
                directory_name = submit_cli.decode('UTF-8').strip().split("\n")[-1]
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

#TODO: Figure out how to make track_list a different file
#or even possibly a way to auto-update from the website?
track_list = [
    ('Bash', 'bash'),
    ('C', 'c'),
    ('C#', 'csharp'),
    ('C++', 'cpp'),
    ('CFML', 'cfml'),
    ('Clojure', 'clojure'),
    ('ClojureScript', 'clojurescript'),
    ('CoffeeScript', 'coffeescript'),
    ('Common Lisp', 'common-lisp'),
    ('Crystal', 'crystal'),
    ('D', 'd'),
    ('Dart', 'dart'),
    ('Delphi Pascal', 'delphi'),
    ('Elixir', 'elixir'),
    ('Elm', 'elm'),
    ('Emacs Lisp', 'emacs-lisp'),
    ('Erlang', 'erlang'),
    ('F#', 'fsharp'),
    ('Fortran', 'fortran'),
    ('Go', 'go'),
    ('Groovy', 'groovy'),
    ('Haskell', 'haskell'),
    ('Java', 'java'),
    ('Javascript', 'javascript'),
    ('Julia', 'julia'),
    ('Kotlin', 'kotlin'),
    ('LFE', 'lfe'),
    ('Lua', 'lua'),
    ('MIPS Assembly', 'mips'),
    ('Nim', 'nim'),
    ('Objective-C', 'objctive-c'),
    ('OCaml', ' ocaml'),
    ('Perl 5', 'perl5'),
    ('Pharo', 'pharo-smalltalk'),
    ('PHP', 'php'),
    ('PL/SQL', 'plsql'),
    ('Prolog', 'prolog'),
    ('PureScript', 'purescript'),
    ('Python', 'python'),
    ('R', 'r'),
    ('Racket', 'racket'),
    ('Raku', 'raku'),
    ('ReasonML', 'reasonml'),
    ('Ruby', 'ruby'),
    ('Rust', 'rust'),
    ('Scala', 'scala'),
    ('Scheme', 'scheme'),
    ('Standard ML', ' sml'),
    ('Swift', 'swift'),
    ('Tcl', 'tcl'),
    ('Typescript', 'typescript'),
    ('VB.NET', 'vbnet'),
    ('Vim script', 'vimscript'),
    ('Wren', 'wren'),
    ('x86-64 Assembly', 'x86-64-assembly')]

#TODO: Add command to create pytest.ini in file's directory to prevent warnings if the track is python
#if possible make it work with Download (Can get last 
