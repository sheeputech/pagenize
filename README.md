# pagenize
Collect HTML and Markdown file from a project and make a source tree.

## What this command does.

1. Remove existing `docs/`.
2. Search `*.html` and `*.md` in the project recursively, except `README.md`, `docs/`, `pagenize/`. &rarr; `origin_paths`
3. Create paths of files will be placed in `docs` from `origin_paths`. &rarr; `docs_paths`
4. Create directory tree in docs
5. Move all files in `origin_paths` to `docs_paths`.
6. Make `index.md` in each directory.

## Reference

- [【Python入門】for文を使った繰り返し文の書き方 - Qiita](https://qiita.com/Morio/items/e8aed85346c0055beea7)
- [Negation in regular expressions](https://uxmilk.jp/50674)
- [Python | Check if file or dir exists | os.path](https://www.gesource.jp/programming/python/code/0008.html)
- [Python | Get list of files and dirs by a path | os.listdir()](https://note.nkmk.me/python-listdir-isfile-isdir/)
- [Python | Get paths by a condition | glob](https://note.nkmk.me/python-glob-usage/)
- [Python | Get stdin | input()](https://python.civic-apps.com/stdin/)
- [Python | Move a file/dir to another directory | shutil.move()](https://note.nkmk.me/python-shutil-move/)
- [Python | Regular expressions | re](https://qiita.com/hiroyuki_mrp/items/29e87bf5fe46de62983c)
- [Python | Remove dir(s) | shutil.rmtree()](https://note.nkmk.me/python-os-remove-rmdir-removedirs-shutil-rmtree/)
- [Python3.6 から追加された文法機能 - Qiita](https://qiita.com/shirakiya/items/2767b30fd4f9c05d930b)
- [Pythonにおける % と str.format() 。どっちを使うの？ - Qiita](https://qiita.com/amedama/items/8635aff8729a248bad16)
- [Pythonのf文字列（フォーマット済み文字列リテラル）の使い方 | note.nkmk.me](https://note.nkmk.me/python-f-strings/)
- [Pythonパッケージ: 便利なコマンドラインパーサClickを使ってみる - いろいろ試してみる](http://imamachi-n.hatenablog.com/entry/2017/03/10/235156)
- [R言語で区切り文字による文字列の分割](http://webbeginner.hatenablog.com/entry/2016/03/19/154026)
- [ベクトル要素の文字列結合 in R](http://d.hatena.ne.jp/kanosuke/20120621/1340290302)