class MarkdownWriter:
    """
    MarkdownWriter:
        Python スクリプト上で Markdown ファイルを書くためのクラス
    
    Example:
        file = './index.md'
        md_writer = MarkdownWriter(file)
        md_writer.put
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.contents = []

    def write(self):
        """
        contents に格納されたファイルの内容を一気に file_path に該当するファイルに書き込む
        """
        pass

    def put_header(self, content: str, br: bool = True) -> self:
        pass

    def put_line(self, content: str, br: bool = True) -> self:
        pass

    def put_list(self, contentList: list, isNum: bool = False, br: bool = True) -> self:
        pass

    def put_list_item(self, content: str, isNum: bool = False, br: bool = False) -> self:
        pass

    def put_link(self, content: str, br: bool = True) -> self:
        pass

    def put_border(self) -> self:
        pass
