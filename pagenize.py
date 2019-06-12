import click
import glob
import os
import platform
import re
import shutil
import subprocess
import textwrap


@click.group(help='pagenize')
@click.pass_context
def pagenize(ctx):
    pass


@pagenize.command(help='Collect your .html and .md files into docs/ with index pages.')
@click.option('-y', '--no-ask', 'yes', is_flag=True, help='Answer "yes" automatically.')
@click.pass_context
def create_docs(ctx, yes):
    # Check if there is ".git" directory in current directory
    if os.listdir(path='.').count('.git') == 0:
        print('There is no ".git" directory in this directory.')
        return

    # Confirmation
    curdir = os.getcwd()
    if not yes:
        print(f'Current directory is: {curdir}')
        if input('Do you pagenize this directory? (y/N): ') != 'y':
            print('Pagenize aborted.')
            return
    else:
        print(f'The following directory will be pagenized: {curdir}')

    # Check OS (conditions for directory separator)
    s = '\\' if platform.system() == 'Windows' else '/'

    # Remove docs/
    if os.path.isdir('docs'):
        shutil.rmtree('docs')
    elif os.path.isfile('docs'):
        os.remove('docs')

    # Search *.html and *.md recursively, except README.md and pagenize/
    origin_paths = [p for p in glob.iglob('./**', recursive=True)
                    if re.search(r'^(?!.*pagenize)^(?!.*README).*(\.html|\.md)', p)]

    # Create file paths in docs
    docs_paths = [f'docs{s}' + p.split(s, 1)[1] for p in origin_paths]

    # Make dirs
    for path in docs_paths:
        dirname = path.rsplit(s, 1)[0]
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

    # Copy .md files into docs
    print("----- Files will be copied into docs -------------------------------------------------")
    for i, path in enumerate(origin_paths):
        print('{}. {}'.format(i, path))
        shutil.copy2(path, docs_paths[i])
    print("--------------------------------------------------------------------------------------")

    # Remove files other than .html and .md in docs/
    for f in [p for p in glob.glob('./docs/**', recursive=True) if
              re.search(r'^.*^(?!.*\.html|.*\.md)', p) and os.path.isfile(p)]:
        os.remove(f)

    # Remove empty dirs in docs/
    ctn = True
    while ctn:
        empty_dirs = [p for p in glob.glob('./docs/**', recursive=True)
                      if os.path.isdir(p) and not os.listdir(p)]
        if len(empty_dirs) == 0:
            ctn = False
        else:
            for d in empty_dirs:
                os.rmdir(d)

    # Make index.md in each dir
    print("Making index pages...")
    make_index_pages(f'.{s}docs', curdir, s)

    # complete
    print("Successfully completed pagenize.")


def make_index_pages(path, curdir, s):
    username = subprocess.check_output(['git', 'config', '--get', 'user.name'])
    remote = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'])

    username_str = str(username).split("'")[1].split('\\n')[0]
    remote_str = str(remote).split("'")[1].split('\\n')[0]

    github_user = ''
    github_repo = ''
    if remote_str.startswith('https://github.com'):
        repo = remote_str.rsplit('/')[-2:]
        github_user = repo[0]
        github_repo = repo[1]
    elif remote_str.startswith('git@github.com'):
        repo = remote_str.rsplit(':', 1)[1].split('/')
        github_user = repo[0]
        github_repo = repo[1]

    base_url = f'https://{github_user}.github.io/{github_repo}'

    inner_path = path.split(f'.{s}', 1)[1]
    inner_url_path = inner_path.replace(s, '/').split('docs', 1)[1]

    urls = {}
    for filename in os.listdir(path):
        filepath = f'{curdir}{s}{inner_path}{s}{filename}'

        if os.path.isdir(filepath):
            urls[filename] = f"{base_url}{inner_url_path}/{filename}/index"

            # make index pages recursively
            make_index_pages(f'{path}{s}{filename}', curdir, s)

        elif os.path.isfile(filepath):
            urls[filename] = f"{base_url}{inner_url_path}/{filename.rsplit('.', 1)[0]}"

    # Create index.md and write content
    with open(f'{path}{s}index.md', mode='w') as f:
        # link to the repository
        info = textwrap.dedent(f"""
            # Info

            Author: {username_str}

            - This index page is automatically generated with my Python script named [albatrosstoi/pagenize](https://github.com/albatrosstoi/pagenize)
            - Repository of this page: [GitHub \| {github_user}/{github_repo}](https://github.com/{github_user}/{github_repo}),
        """)

        # breadcrumb
        splt = path.split(f'.{s}docs', 1)[1].split(s)
        bc = textwrap.dedent("""
            # {}
        """).format(' / '.join([f"[{splt[i] or 'ROOT'}]({base_url}{'/'.join(splt[0:i+1] + ['index'])})" for i in range(0, len(splt))]))

        # list of the links to children
        children = textwrap.dedent("""
            # Child Files

        """)
        children += "".join(
            [f'- [{filename}]({url})\n' for filename, url in urls.items()])

        # write contents
        f.write(info + bc + children)


if __name__ == '__main__':
    pagenize()
