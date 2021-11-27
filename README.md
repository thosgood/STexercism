# STexercism

This is a Sublime Text 3 package that allows access to some of the `exercism.io` CLI commands (and so it requires that you already have the `exercism.io` CLI installed).

Currently supported (accessed through the command palette):
- `STexercism: Submit current exercise file`. Must be run when focused on the file to be submitted.
- `STexercism: Open current exercise on the website`. Should work on any file in the exercism directory.
- `STexercism: Test current Python exercise file`. Only works with the Python track currently. (requires Pytest). Can be edited in sublime-settings to include extra flags.
- `STexercism: Download an exercise file`. Copy and paste the title from the exercism website for exercise name. (If python, can be toggled to autocreate pytest.ini.)
- `STexercism: List of toggles`. Includes toggles that are binary. (i.e. turn on or off setting)
- `STexercism: List of maintenance commands`. Lists the commands below:
  + `STexercism: Check current version`.
  + `STexercism: Update CLI`.
  + `STexercism: Check workspace`. Can be toggled to open the directory.


### Toggles

This installation includes different toggles that you can customize to fit your preferences.
These include:
- `STexercism: Toggle auto-create for pytest.ini (Python)`.
- `STexercism: Toggle opening directory on workspace command`.
- `STexercism: Toggle opening directory on download command`.

*Please note that changing flags for the pytest command does not have a native command.
If you wish to change it, change it in the `User/STexercism.sublime-settings` file directly.
If any of the flags are invalid, then it'll automatically run the test with no flags and give a warning.*

**Changing any of the other toggles through STexercism.sublime-settings also works. The commands are there just for convenience.**

## Installation

Via package control.
