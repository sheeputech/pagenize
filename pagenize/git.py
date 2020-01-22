import subprocess


class Git:
    """
    Git リポジトリを管理するクラス
    """

    def __init__(self, git_root_path):
        # Git リポジトリのルートディレクトリのパス
        self.git_root_path = git_root_path

    def add(self, *opts):
        cmd_out = self._run_cmd('add', opts)

    def status(self, *opts):
        cmd_out = self._run_cmd('status', opts)

    def _run_cmd(self, cmd: str, opts: list):
        cmd_series = ['git', cmd, *opts]

        return subprocess.check_output(cmd_series).decode('utf-8')


class status:
    """
    ファイルごとの変更ステータスを持つクラス
    """

    def __init__(self, path, status):
        self.path = path
        self.status = status
