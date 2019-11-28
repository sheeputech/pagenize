from configparser import ConfigParser
from glob import glob, iglob
from logger import Logger
from termcolor import colored
from textwrap import dedent
import click
import copy
import os
import platform
import re
import shutil
import string
import subprocess
import sys

PAGENIZE_TEMPLATE_FILENAME = 'pagenize.tmpl.md'
WATCH_FILE_EXTENSION_LIST = ['html', 'md', 'png', 'jpg']

"""
TODO 改善余地

- index.md が docs/ の状態に依存している
"""


@click.group(help='pagenize')
@click.pass_context
def pagenize(ctx):
    pass


@pagenize.command(help='Collect your .html and .md files into docs/ with index pages.')
@click.option('-y', '--no-ask', 'yes', is_flag=True, help='Answer "yes" automatically.')
@click.pass_context
def make(ctx, yes):
    if not is_git_dir():
        Logger.fatal('Here is not root directory of git repository.')

    # Confirmation
    cwd = os.getcwd()
    if not yes and input(f'--> Do you pagenize "{cwd}" ? (y/N): ') != 'y':
        Logger.fatal('Pagenize aborted.')

    # Get list of changed files from git
    changed_files = list_changed_files()

    apply_changes_to_docs(changed_files)

    # Make index.md for each dir in docs/
    Logger.info("Making index pages...")

    [Logger.primary(v) for v in make_index(['.', 'docs'])]

    Logger.info("Completed.")


def list_changed_files() -> list:
    """
    TODO Git の仕様変更に弱そう
    """
    # Run "git status -s" to detect file changes
    git_status_out = subprocess.check_output(['git', 'status', '-s'])

    # Convert output object to string and trim
    git_status_str = str(git_status_out).split('\'')[1]

    # Convert output string to list and organize (x[0]: staged status, x[1]: unstaged status)
    change_list = list(
        map(lambda x: [x[0], x[3:].split(' -> '), x[3:].rsplit('.', 1)[1]],
            git_status_str.split('\\n')[:-1])
    )

    # status[0]: git status (ex: CREATE, MOD, DELETE)
    # status[1]: list contains path of changed file; status[1][0]: file path, status[1][1]: renamed file path (if status[0] == 'R')
    # status[2]: file extension
    return [status for status in filter(is_target, change_list)]


def is_target(status):
    """
    status[0]: git status (ex: CREATE, MOD, DELETE)
    status[1]: list contains path of changed file; status[1][0]: file path, status[1][1]: renamed file path (if status[0] == 'R')
    status[2]: file extension

    is_target() extracts only staged files, exclude files in docs/ and at last filter by file extension.
    """
    return status[0] != ' ' and not status[1][0].startswith('docs/') and status[2] in WATCH_FILE_EXTENSION_LIST


def apply_changes_to_docs(changed_files: list):
    for changed_file in changed_files:
        status = changed_file[0]
        if status == 'R':  # Rename
            path_new = changed_file[1][1]
            [path_docs, path_new_docs] = concat_docs(*changed_file[1])

            prefix = Logger.color_str('RENAME', 'blue')
            Logger.info(f'{prefix}: {path_docs}\n     -> {path_new_docs}')

            # Move file
            shutil.copy2(path_new, path_new_docs)

        elif status == 'A':  # Add
            path = changed_file[1][0]
            [path_docs] = concat_docs(path)

            prefix = Logger.color_str('CREATE', 'magenta')
            Logger.info(f'{prefix}: {path_docs}')

            # Create parent dirs if not exist when move new file into docs/
            dir_docs = os.path.dirname(path_docs)
            if not os.path.exists(dir_docs):
                os.makedirs(dir_docs)

            shutil.copy2(path, path_docs)

        elif status == 'M':  # Modify
            path = changed_file[1][0]
            [path_docs] = concat_docs(path)

            prefix = Logger.color_str('MODIFY', 'green')
            Logger.info(f'{prefix}: {path_docs}')

            shutil.copy2(path, path_docs)

        elif status == 'D':  # Delete
            # ソース内の HTML などは ADD や MODIFY の時に move されてしまうから DELETE が検知されることはない
            # → 今のところ DELETE は処理しない
            pass


def concat_docs(*paths):
    return map(lambda path: 'docs/' + path, paths)


def is_git_dir() -> bool:
    """
    Check if current directory is a git repository or not.
    """
    return os.listdir(path='.').count('.git') == 1


def get_delim() -> str:
    """
    Return file path separator for each operation systems.
    """
    return '\\' if platform.system() == 'Windows' else '/'


def make_index(path_list: list, index_list: list = []):
    """
    Make files for index pages.
    """
    delim = get_delim()
    git_user, git_repo = get_repo_info()
    p_base = f'https://{git_user}.github.io/{git_repo}'
    p_inner = path_list[2:] if len(path_list) > 2 else []

    index_path = delim.join([*path_list, 'index.md'])
    index_list.append(index_path)

    links = {}
    for file in sorted(os.listdir(delim.join(path_list))):
        child = copy.copy(path_list)
        child.append(file)

        # Remove file extension: Prevent browsers from displaying raw source codes of Markdown
        splf = file.rsplit('.', 1)
        file_name = splf[0]
        file_ext = ""
        if len(splf) == 1:
            file_name += "/index"
        else:
            file_ext = splf[1]

        file_name = file if file_ext in ["jpg", "png"] else file_name

        links[file] = '/'.join([p_base, *p_inner, file_name])

        if os.path.isdir(delim.join(child)):
            make_index(child, index_list=index_list)

    write_index(index_path, p_inner, links, git_user, git_repo, p_base)

    return index_list


def write_index(index_path: str, inner_paths: list, urls: list, git_user: str, git_repo: str, base: str):
    """
    Write index file.
    """
    # Set default template string
    tmpl_str = dedent("""
        ## $breadcrumb

        $indices

        ***

        ### Page Information

        - Source of this page is in this repository: $repo
        - This index page is automatically generated with [sheeputech/pagenize](https://github.com/sheeputech/pagenize)
    """)

    # Read template file
    if os.path.isfile(PAGENIZE_TEMPLATE_FILENAME):
        with open(PAGENIZE_TEMPLATE_FILENAME, 'r') as f:
            tmpl_str = f.read()

    # Generate string template and substitute
    tmpl = string.Template(tmpl_str)
    try:
        content = tmpl.substitute({
            'breadcrumb': make_index_breadcrumb(base, inner_paths),
            'indices': make_index_items(urls),
            'repo': make_index_repo(git_user, git_repo)
        })
    except KeyError as e:
        Logger.fatal(f'The template value {e} is not defined.')

    # Write
    with open(index_path, 'w') as f:
        f.write(content)


def make_index_breadcrumb(base, inner_list):
    """
    Make breadcrumb component for index page.
    """
    # Make link title list
    labs = ['root', *inner_list]

    # Make link list
    links = [
        '[{}]({})'.format(f, '{base}/{inner}'.format(base=base, inner='/'.join(labs[1:i+1]))) for i, f in enumerate(labs)
    ]

    # Return slash-joined links
    return ' / '.join(links)


def make_index_items(file_links):
    """
    Make link items component for index page.
    """
    items = "".join([f'- [{f}]({l})\n' for f, l in file_links.items()])

    # Remove the last line feed
    return items.rstrip()


def make_index_repo(user, repo):
    """
    Make repository info component for index page.
    """
    return f'[{user}/{repo}](https://github.com/{user}/{repo})'


def get_repo_info():
    """
    Get repository username and repository name
    """
    cmd = 'git config --get remote.origin.url'
    output = subprocess.check_output(cmd.split(' '))
    remote = str(output).split('\'')[1].split('\\n')[0]
    if remote.startswith('https://'):
        repo = remote.rsplit('/')[-2:]
    elif remote.startswith('git@'):
        repo = remote.rsplit(':', 1)[1].split('/')
    else:
        Logger.fatal('Unexpected remote repository url')

    return repo[0], repo[1]
