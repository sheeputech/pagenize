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
import subprocess
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
        log(f'Current directory is: {cwd}', 'primary', False)
        if input('--> Do you pagenize this directory? (y/N): ') != 'y':
            log('Pagenize aborted.')
            sys.exit()

    # Remove docs/
    if os.path.isdir('docs'):
        rmtree('docs')
    elif os.path.isfile('docs'):
        os.remove('docs')

    # Search files
    search_re = get_search_regex()
    sep = get_path_sep()
    paths = [
        (v, f'docs{sep}{v.split(sep, 1)[1]}') for v in iglob('./**', recursive=True) if re.search(search_re, v)
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
    if os.path.isfile('pagenize.ini'):
        conf = ConfigParser()
        conf.read('pagenize.ini')
        if conf.has_section(PAGENIZE_CONFIG_SECTION) and conf.has_option(PAGENIZE_CONFIG_SECTION, PAGENIZE_CONFIG_OPTION_SEARCH_INDEX):
            r = conf[PAGENIZE_CONFIG_SECTION][PAGENIZE_CONFIG_OPTION_SEARCH_INDEX]
            return r

    return r'^(?!.*(README|pagenize)).*(html|md)$'


def make_index(path: list, sep: str, index_list: list = []):
    git_user, git_repo = get_repo_info()
    base = f'https://{git_user}.github.io/{git_repo}'
    dirdepth = len(path) - 2
    inner = path[2:] if dirdepth > 2 else[]

    index_path = sep.join([*path, 'index.md'])
    index_list.append(index_path)

    urls = {}
    for file in sorted(os.listdir(sep.join(path))):
        nextpath = copy.copy(path)
        nextpath.append(file)
        if os.path.isdir(sep.join(nextpath)):
            urls[file] = '/'.join([base, *inner, file, 'index'])
            make_index(nextpath, sep, index_list=index_list)
        elif os.path.isfile(sep.join(nextpath)):
            urls[file] = '/'.join([base, *inner, file])

    write_index_page(index_path, inner, urls, git_user, git_repo, base)

    return index_list


def write_index_page(index_path: str, inner_paths: list, urls: list, git_user: str, git_repo: str, base: str):
    # Breadcrumb
    labs = ['root', *inner_paths]
    links = ['[{}]({})'.format(f, '{base}/{path}'.format(base=base, path='/'.join(labs[1:i+1])))
             for i, f in enumerate(labs)]
    breadcrumb = ' / '.join(links)

    # Index items
    items = "".join([f'- [{f}]({url})\n' for f, url in urls.items()])

    # Source repository URL
    repo = f'[{git_user}/{git_repo}](https://github.com/{git_user}/{git_repo})'

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

    tmpl = string.Template(tmpl_str)
    try:
        content = tmpl.substitute({
            'breadcrumb': breadcrumb,
            'indices': items,
            'repo': repo
        })
        with open(index_path, 'w') as f:
            f.write(content)
    except KeyError as e:
        log(f'The template value {e} is not defined.',  'error')
        sys.exit()


def get_repo_info():
    o = subprocess.check_output(
        ['git', 'config', '--get', 'remote.origin.url'])
    remote = str(o).split("'")[1].split('\\n')[0]
    if remote.startswith('https://'):
        repo = remote.rsplit('/')[-2:]
    elif remote.startswith('git@'):
        repo = remote.rsplit(':', 1)[1].split('/')
    else:
        log('Unexpected remote repository url', 'error')
        sys.exit()

    return repo[0], repo[1]


def log(mes: str, logtype: str = None, brankline: bool = True):
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
        print('\n', mes, '\n', flush=True) if brankline else print(mes, flush=True)
        return

    mes = colored(f'{prefix}{mes}', color)
    print('\n', mes, '\n', flush=True) if brankline else print(mes, flush=True)
    return


if __name__ == '__main__':
    pagenize()
