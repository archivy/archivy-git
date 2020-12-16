import os.path

import click
import git as gitpython

from archivy.helpers import get_db
from archivy import app
from archivy.data import get_items, create_dir
from archivy.models import DataObj

def get_repo():
    with app.app_context():
        return gitpython.Repo(app.config["USER_DIR"])

@click.group()
def git():
    pass

@git.command()
def setup():
    with app.app_context():
        click.echo(f"Creating new git repo in {app.config['USER_DIR']}...")
        repo = gitpython.Repo.init(app.config["USER_DIR"])
        branch = click.prompt("Main branch", type=str, default="main")
        repo.index.add("data/")
        repo.index.add("hooks.py")
        repo.index.commit("Initial commit")
        repo.active_branch.rename(branch)
        
        while True:
            remote_url = click.prompt("Enter the url of the remote you'd like to sync to. Ex: https://github.com/archivy/archivy", type=str)
            origin = repo.create_remote("origin", remote_url)
            if origin.exists():
                break
            click.echo("Remote does not exist.")
        origin.push(branch)
        origin.fetch()
        repo.active_branch.set_tracking_branch(getattr(origin.refs, branch))


@git.command()
@click.argument("paths", type=click.Path(exists=True), nargs=-1, required=True)
def sync(paths):
    repo = get_repo()
    with app.app_context():
        prefixed_paths = [os.path.join(app.config["USER_DIR"], "data", path) for path in paths]
    repo.index.add(prefixed_paths)
    repo.index.commit("Sync from git repo.")
    repo.remotes.origin.push()


def sync_dataobj(dataobj):
    repo = get_repo()
    origin = repo.remotes.origin

    repo.index.add([dataobj.fullpath])
    repo.index.commit(f"Changes to {dataobj.title}.")
    origin.push()
