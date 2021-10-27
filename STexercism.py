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
            
            if err.returncode == 1: #This is an exception made for if there are failed tasks
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

def convert(text): #Converts the name of the exercise into usable names for cmd
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
    ('Python', 'python'),
    ('PureScript', 'purescript'),
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