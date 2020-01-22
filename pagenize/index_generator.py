import markdown_writer

class IndexGenerator:
    """
    IndexGenerator:
        ドキュメントディレクトリに再帰的に目次ファイル (index.md) を作成するクラス

    ドキュメントが格納されているディレクトリのルートパスで初期化する。
    generate でそのルートパス以下に index.md を再帰的に作成していく。

    各ディレクトリ内でやること
        - 全てのファイル・ディレクトリのパスのリストアップ
        - パンくず
        - index.md の生成

    IndexGenerator はディレクトリ毎にそれ自身をインスタンス化することであるディレクトリ以下に対して再帰的に index.md を作成していく。
    """

    def __init__(self, target_dir_path):
        self.target_dir = target_dir_path

    def generate(self):
        # set breadcrumb

        # list up files/dirs in target_dir_path
        # sort by file or dir
        # if a path is dir, initialize a sub IndexGenerator
        # write index.md
        pass

    def get_git_repo_info(self):
        pass

    def write_index_file():
        pass
