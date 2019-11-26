from configparser import ConfigParser
from glob import glob, iglob
from shutil import rmtree, copy2
from termcolor import colored
from textwrap import dedent
import click
import copy
import os
import platform
import re
import string
import subprocess as sp
import sys
from logger import Logger

PAGENIZE_TEMPLATE_FILENAME = 'pagenize.tmpl.md'


@click.group(help='pagenize')
@click.pass_context
def pagenize(ctx):
    pass


@pagenize.command(help='Collect your .html and .md files into docs/ with index pages.')
@click.option('-y', '--no-ask', 'yes', is_flag=True, help='Answer "yes" automatically.')
@click.pass_context
def make(ctx, yes):
    if not is_git_repo():
        Logger.fatal('Here is not a git repository.')

    # Confirmation
    cwd = os.getcwd()
    if not yes and input(f'--> Do you pagenize "{cwd}" ? (y/N): ') != 'y':
        Logger.fatal('Pagenize aborted.')

    # TODO Git Status の結果を取得して変更分だけを docs/ に適用する実装にしたい
    # TODO HTML / MD ファイルが docs/ と元のディレクトリに重複して存在してる問題も解決したい
    # TODO docs/ から削除する時は直接消すようにして、元のソースで消しても消えないようにする → そうするとファイル名変更時にややこしくなるからそこは要検討
    # o = sp.check_output(['git', 'status', '-s'])
    # print(o)
    # l = list(filter(lambda x: x != '', str(o).split('\'')[1].split('\\n')))
    # l2 = list(map(lambda x: x.split('  '), l))
    # print(l2)

    # Remove all docs/
    if os.path.isdir('docs'):
        rmtree('docs')
    elif os.path.isfile('docs'):
        os.remove('docs')

    # Search files
    sre = get_search_regex()
    delim = get_delim()
    paths = [
        (v, f'docs{delim}{v.split(delim, 1)[1]}') for v in iglob('./**', recursive=True) if re.search(sre, v)
    ]
    if not paths:
        Logger.fatal('No target files in your project. Pagenize aborted.')

    # Make dirs
    _, paths_dest = list(zip(*paths))
    for p in paths_dest:
        dirname = p.rsplit(delim, 1)[0]
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

    # Copy files into docs
    copy_to_docs(paths)

    # Make index.md for each dir in docs/
    Logger.info("Making index pages...")

    [Logger.primary(v) for v in make_index(['.', 'docs'], delim)]

    Logger.info("Completed.")


def is_git_repo() -> bool:
    """
    Check if current directory is a git repository or not.
    """

    return os.listdir(path='.').count('.git') == 1


def get_delim() -> str:
    """
    Return file path separator for each operation systems.
    """

    return '\\' if platform.system() == 'Windows' else '/'


def get_search_regex():
    """
    Return regex for searching files.
    """

    return r'^(?!.*(README|pagenize)).*(\.html|\.md|\.jpg|\.png)$'


def copy_to_docs(paths: list):
    [(Logger.primary(f'{f} -> {t}'), copy2(f, t)) for f, t in paths]


def make_index(path_list: list, delim: str, index_list: list = []):
    """
    Make files for index pages.
    """

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
            make_index(child, delim, index_list=index_list)

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

    output = sp.check_output('git config --get remote.origin.url'.split(' '))
    remote = str(output).split("'")[1].split('\\n')[0]
    if remote.startswith('https://'):
        repo = remote.rsplit('/')[-2:]
    elif remote.startswith('git@'):
        repo = remote.rsplit(':', 1)[1].split('/')
    else:
        Logger.fatal('Unexpected remote repository url')

    return repo[0], repo[1]
