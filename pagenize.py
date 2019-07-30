from configparser import ConfigParser
from glob import glob, iglob
from shutil import rmtree, copy2
from termcolor import colored
from textwrap import dedent
import click
import copy
import os
# import pagenizer
import platform
import re
import string
import subprocess as sp
import sys

PAGENIZE_CONFIG_SECTION = 'pagenize'
PAGENIZE_CONFIG_OPTION_SEARCH_INDEX = 'search_regex'
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
        log('This is not a git repository.', 'error')
        sys.exit()

    # Confirmation
    cwd = os.getcwd()
    if not yes:
        if input(f'--> Do you pagenize "{cwd}" ? (y/N): ') != 'y':
            log('Pagenize aborted.')
            sys.exit()

    # Remove docs/
    if os.path.isdir('docs'):
        rmtree('docs')
    elif os.path.isfile('docs'):
        os.remove('docs')

    # Search files
    sre = get_search_regex()
    sep = get_path_sep()
    paths = [
        (v, f'docs{sep}{v.split(sep, 1)[1]}') for v in iglob('./**', recursive=True) if re.search(sre, v)
    ]
    _, paths_dest = list(zip(*paths))

    # Make dirs
    for p in paths_dest:
        dirname = p.rsplit(sep, 1)[0]
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

    # Copy files into docs
    [(log(f'{f} -> {t}', 'primary', False), copy2(f, t)) for f, t in paths]

    # Make index.md for each dir in docs/
    log("Making index pages...")

    [log(v, "primary", False) for v in make_index(['.', 'docs'], sep)]

    log("Completed.")


def is_git_repo() -> bool:
    """
    Check if current directory is a git repository or not.
    """

    return os.listdir(path='.').count('.git') == 1


def get_path_sep() -> str:
    """
    Return file path separator for each operation systems.
    """

    return '\\' if platform.system() == 'Windows' else '/'


def get_search_regex():
    """
    Return regex for searching files.
    """

    if os.path.isfile('pagenize.ini'):
        conf = ConfigParser()
        conf.read('pagenize.ini')
        if conf.has_section(PAGENIZE_CONFIG_SECTION) and conf.has_option(PAGENIZE_CONFIG_SECTION, PAGENIZE_CONFIG_OPTION_SEARCH_INDEX):
            r = conf[PAGENIZE_CONFIG_SECTION][PAGENIZE_CONFIG_OPTION_SEARCH_INDEX]
            return r

    return r'^(?!.*(README|pagenize)).*(html|md)$'


def make_index(path_list: list, sep: str, index_list: list = []):
    git_user, git_repo = get_repo_info()
    p_base = f'https://{git_user}.github.io/{git_repo}'
    p_inner = path_list[2:] if len(path_list) > 2 else []

    index_path = sep.join([*path_list, 'index.md'])
    index_list.append(index_path)

    links = {}
    for file in sorted(os.listdir(sep.join(path_list))):
        child = copy.copy(path_list)
        child.append(file)

        # Remove file extension: Prevent browsers from displaying raw source codes of Markdown
        file_name = file.rsplit('.', 1)[0]
        links[file] = '/'.join([p_base, *p_inner, file_name])
        if os.path.isdir(sep.join(child)):
            make_index(child, sep, index_list=index_list)

    write_index(index_path, p_inner, links, git_user, git_repo, p_base)

    return index_list


def write_index(index_path: str, inner_paths: list, urls: list, git_user: str, git_repo: str, base: str):
    # Set default template string
    tmpl_str = dedent("""
        ## $breadcrumb

        $indices

        ***

        ### Page Information

        - Source of this page is in this repository: $repo
        - This index page is automatically generated with [sheeputech/cli-pagenize](https://github.com/sheeputech/cli-pagenize)
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
        log(f'The template value {e} is not defined.',  'error')
        sys.exit()

    # Write
    with open(index_path, 'w') as f:
        f.write(content)


def make_index_breadcrumb(base, inner_list):
    # Make link title list
    labs = ['root', *inner_list]

    # Make link list
    links = [
        '[{}]({})'.format(f, '{base}/{inner}'.format(base=base, inner='/'.join(labs[1:i+1]))) for i, f in enumerate(labs)
    ]

    # Return slash-joined links
    return ' / '.join(links)


def make_index_items(file_links):
    items = "".join([f'- [{f}]({l})\n' for f, l in file_links.items()])

    # Remove the last line feed
    return items.rstrip()


def make_index_repo(user, repo):
    return f'[{user}/{repo}](https://github.com/{user}/{repo})'


def get_repo_info():
    output = sp.check_output('git config --get remote.origin.url'.split(' '))
    remote = str(output).split("'")[1].split('\\n')[0]
    if remote.startswith('https://'):
        repo = remote.rsplit('/')[-2:]
    elif remote.startswith('git@'):
        repo = remote.rsplit(':', 1)[1].split('/')
    else:
        log('Unexpected remote repository url', 'error')
        sys.exit()

    return repo[0], repo[1]


def log(mes: str, logtype: str = None, bl: bool = True):
    if logtype == 'primary':
        prefix = ''
        color = 'green'
    elif logtype == 'warn':
        prefix = 'Warn: '
        color = 'yellow'
    elif logtype == 'error':
        prefix = 'Error: '
        color = 'red'
    else:
        print('\n', mes, '\n', flush=True) if bl else print(mes, flush=True)
        return

    mes = colored(f'{prefix}{mes}', color)
    print('\n', mes, '\n', flush=True) if bl else print(mes, flush=True)


if __name__ == '__main__':
    pagenize()
