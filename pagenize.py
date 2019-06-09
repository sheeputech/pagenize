import click
import glob
import os
import re
import shutil
import subprocess
import textwrap


@click.group(help='pagenize')
@click.pass_context
def pagenize(ctx):
    pass


@pagenize.command(help='Configure pagenize.')
@click.pass_context
def init(ctx):
    print('init')


@pagenize.command(help='Collect your .html and .md files into docs/ with index pages.')
@click.option('-y', '--no-ask', 'yes', is_flag=True, help='Answer "yes" automatically.')
@click.pass_context
def create_docs(ctx, yes):
    # Confirmation
    curdir = os.getcwd()
    if not yes:
        print(f'Current directory is: {curdir}')
        if input('Do you pagenize this directory? (y/N): ') != 'y':
            print('Pagenize aborted.')
            return
    else:
        print(f'The following directory will be pagenized: {curdir}')

    # TODO Read config file

    # Remove docs/
    if os.path.isdir('docs'):
        shutil.rmtree('docs')
    elif os.path.isfile('docs'):
        os.remove('docs')

    # Search *.html and *.md recursively, except README.md and pagenize/
    origin_paths = [p for p in glob.iglob('./**', recursive=True)
                    if re.search(r'^(?!.*pagenize)^(?!.*README).*(\.md)', p)]

    # Create file paths in docs
    docs_paths = ['docs\\' + p.split('\\', 1)[1] for p in origin_paths]

    # Make dirs
    for path in docs_paths:
        dirname = path.rsplit('\\', 1)[0]
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
    make_index_pages('.\\docs')

    # complete
    print("Successfully completed pagenize.")


def make_index_pages(path):
    # TODO detect repository name automatically and set base_url
    github_user = 'sheeputech'
    github_repo = 'class'
    base_url = f'https://{github_user}.github.io/{github_repo}'

    curdir = os.getcwd()
    inner_path = path.split('.\\', 1)[1]
    inner_url_path = inner_path.replace('\\', '/').split('docs', 1)[1]

    urls = {}
    for filename in os.listdir(path):
        filepath = f'{curdir}\\{inner_path}\\{filename}'

        if os.path.isdir(filepath):
            urls[filename] = f"{base_url}{inner_url_path}/{filename}/index"

            # make index pages recursively
            make_index_pages(f'{path}\\{filename}')

        elif os.path.isfile(filepath):
            urls[filename] = f"{base_url}{inner_url_path}/{filename.rsplit('.', 1)[0]}"

    # Create index.md and write content
    with open(f'{path}\\index.md', mode='w') as f:
        # link to the repository
        info = textwrap.dedent(f"""
            # Info

            - This index page is automatically generated with my Python script named [pagenize](https://github.com/sheeputech/pagenize)
            - Repository of this page: [GitHub | {github_user}/{github_repo}](https://github.com/{github_user}/{github_repo}),
        """)

        # breadcrumb
        splt = path.split('.\\docs', 1)[1].split('\\')
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
