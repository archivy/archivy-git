import os.path

import click
import git as gitpython

from archivy import app
from archivy.models import DataObj

# https://gitpython.readthedocs.io/en/stable/reference.html#git.remote.PushInfo
ERROR_CODES = [1024, 8, 32, 16]


def check_errored(flags):
    # gitpython returns flags to be checked by doing an AND with specified codes
    return any([flags & error_code for error_code in ERROR_CODES])


def get_repo():
    with app.app_context():
        return gitpython.Repo(app.config["USER_DIR"])


@click.group()
def git():
    pass


@git.command()
def setup():
    """Creates and sets up git repository."""
    with app.app_context():
        click.echo(f"Creating new git repo in {app.config['USER_DIR']}...")
        repo = gitpython.Repo.init(app.config["USER_DIR"])
        branch = click.prompt("Main branch", type=str, default="main")
        repo.index.add("data/")
        repo.index.commit("Initial commit")
        repo.active_branch.rename(branch)

        while True:
            remote_url = click.prompt(
                "Enter the url of the remote you'd like to sync to. "
                "Ex: https://github.com/archivy/archivy",
                type=str,
            )
            username = click.prompt("Enter your username", type=str)
            password = click.prompt(
                "Enter your personal access token", type=str, hide_input=True
            )
            remote_url = remote_url.replace(
                "https://", f"https://{username}:{password}@"
            )
            origin = repo.create_remote("origin", remote_url)
            if origin.exists():
                break
            click.echo("Remote does not exist.")
        origin.push(branch)
        origin.fetch()
        repo.active_branch.set_tracking_branch(getattr(origin.refs, branch))
        click.echo("Successfully setup repository.")


@git.command()
@click.argument("paths", type=click.Path(), nargs=-1)
def push(paths):
    """Pushes local changes to the remote."""
    repo = get_repo()
    if not paths or "." in paths:
        repo.git.add(all=True)
    else:
        with app.app_context():
            prefixed_paths = [
                os.path.join(app.config["USER_DIR"], path) for path in paths
            ]
        repo.index.add(prefixed_paths)
    repo.index.commit("Sync local changes to remote git repo.")
    push_event = repo.remotes.origin.push()[0]
    if check_errored(push_event.flags):
        click.echo(push_event.summary)
    else:
        click.echo("Successfully pushed changes to remote!")


@git.command()
def pull():
    """Pulls changes from remote to local repository."""
    repo = get_repo()
    pull_event = repo.remotes.origin.pull()[0]
    if check_errored(pull_event.flags):
        click.echo(f"Error during pull. {pull_event.note}")
    else:
        click.echo("Sucessfully pulled changes from remote!")


def sync_dataobj(dataobj: DataObj):
    """Helper method that adds and pushes changes to a single data object."""
    repo = get_repo()
    origin = repo.remotes.origin

    repo.index.add([dataobj.fullpath])
    repo.index.commit(f"Changes to {dataobj.title}.")
    origin.push()
