`archivy-git` allows users to use version control with their [Archivy](https://archivy.github.io) instance.

It is an official extension developed by [archivy](https://github.com/archivy/)

## Install

You need to have `archivy` already installed.

Run `pip install archivy_git`.

## Usage

```bash
$ archivy git --help
Usage: archivy git [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  pull   Pulls changes from remote to local repository.
  push   Pushes local changes to the remote.
  setup  Creates and sets up git repository.
```

Use the `setup` command to create and configure a new, empty git repository. If you connect your repo to a private GitHub repository, keep in mind you can no longer login with your username / password and you need to create a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

You can also just clone an existing repository, in which case you don't need to run setup

Then you can periodically `pull/push` through the command line. **The plugin is not yet compatible with the web interface.** 

However, it can also be useful to automatically push changes when you make an edit or create a new note / bookmark. To do this, you'll need to configure a [Hook](https://archivy.github.io/reference/hooks).

These are events that Archivy exposes and that you can configure.

To do so, run `archivy hooks` to edit the file and create it if it doesn't exist.

We can use the `sync_dataobj` `archivy-git` method to sync changes when they are made.

Example:

```python
from archivy.config import BaseHooks
class Hooks(BaseHooks):
	
	def on_edit(self, dataobj):
		from archivy_git import sync_dataobj	
		sync_dataobj(dataobj) # syncs / pushes changes

	def on_dataobj_create(self, dataobj):
		# the same for creation
		from archivy_git import sync_dataobj	
		sync_dataobj(dataobj)
```
