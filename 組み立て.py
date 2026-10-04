"""サイト.toml と 動画/*.toml から、公開用の HTML を _site/ に組み立てる。

使い方: python 組み立て.py
標準ライブラリだけで動く（GitHub の上でも、追加の部品を入れずに動かすため）。
出力のパスは英数字だけにする（日本語のURLは、共有したときに長い記号の列に化けるため）。
"""

import shutil
import sys
import tomllib
from html import escape
from pathlib import Path

ここ = Path(__file__).parent
出力 = ここ / "_site"
動画に必須 = ["番号", "題", "きっかけ", "流れ"]

FONTS = ("https://fonts.googleapis.com/css2?family=LINE+Seed+JP:wght@400;800"
         "&family=Shippori+Mincho+B1:wght@800&family=Montserrat:ital,wght@1,800&display=swap")


def 読む(パス):
    with open(パス, "rb") as f:
        return tomllib.load(f)


def 動画を読む():
    動画たち = []
    for パス in sorted((ここ / "動画").glob("*.toml")):
        v = 読む(パス)
        足りない = [k for k in 動画に必須 if k not in v]
        if 足りない:
            sys.exit(f"{パス.name} に {'・'.join(足りない)} がありません")
        動画たち.append(v)
    return sorted(動画たち, key=lambda v: v["番号"], reverse=True)  # 新しい順


def 段落(文):
    return "".join(f"<p>{escape(p.strip())}</p>" for p in 文.strip().split("\n\n") if p.strip())


def ページ番号(v):
    return f"{v['番号']:03d}"


def 枠(題, 中身, サイト, 上へ):
    """全ページ共通の外側。上へ はトップへの相対パス（"" か "../"）。"""
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(題)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{上へ}assets/style.css">
<script src="{上へ}assets/色を選ぶ.js"></script>
</head><body><div class="wrap">
<nav class="box"><a class="logo" href="{上へ}index.html">{escape(サイト['チャンネル名'])}</a>
<div class="links"><a href="{上へ}index.html#videos">動画</a><a href="{上へ}index.html#about">このチャンネルについて</a><a href="{escape(サイト['youtube'])}">YouTube ↗</a></div></nav>
{中身}
<footer class="en">© {escape(サイト['英語名'])}</footer>
</div></body></html>
"""


def サムネ(v, 上へ):
    名前 = v.get("サムネ", "")
    if 名前 and (ここ / "画像" / 名前).exists():
        return f'<img class="thumb" src="{上へ}img/{escape(名前)}" alt="">'
    return '<div class="thumb"></div>'


def カード(v):
    return f"""<a class="box card" href="v/{ページ番号(v)}.html">{サムネ(v, "")}<div class="in">
<span class="num en">No.{ページ番号(v)}</span><b>{escape(v['題'])}</b>
<p>きっかけ：<span class="mincho">{escape(v['きっかけ'])}</span></p></div></a>"""


def トップ(サイト, 動画たち):
    手順 = "".join(f'<div class="step"><i>{i}</i>{escape(s)}</div>' for i, s in enumerate(サイト["決め方"], 1))
    ボタン = f'<a class="btn main" href="{escape(サイト["youtube"])}">YouTube で見る</a>'
    if サイト.get("問い合わせ"):
        ボタン += f'<a class="btn" href="{escape(サイト["問い合わせ"])}">お問い合わせ</a>'
    中身 = f"""<section class="hero">
<h1>「<span class="mincho fuda">{escape(サイト['見出し'])}</span>」<br>{escape(サイト['見出しの続き'])}</h1>
<div class="box how"><h3 class="en">HOW WE PICK A THEME</h3>{手順}</div>
</section>
<h2 id="videos">押したい動画</h2>
<div class="cards">{"".join(カード(v) for v in 動画たち)}</div>
<h2 id="about">このチャンネルについて</h2>
<div class="box about">{段落(サイト['作り手'])}<div class="buttons">{ボタン}</div></div>"""
    return 枠(サイト["チャンネル名"], 中身, サイト, "")


def 資料(r):
    題 = escape(r["題"])
    if r.get("url"):
        題 = f'<a href="{escape(r["url"])}">{題}</a>'
    中 = f'<div class="src-title">{題}</div>'
    if r.get("著者"):
        中 += f'<div class="src-by en">{escape(r["著者"])}</div>'
    if r.get("一言"):
        中 += f'<div class="src-note">{escape(r["一言"])}</div>'
    return 中


def 動画ページ(サイト, v):
    中身 = f"""<span class="num en">No.{ページ番号(v)}</span>
<h1 class="v-title">{escape(v['題'])}</h1>
<div class="v-q"><span class="mincho fuda"><small>きっかけの疑問</small>{escape(v['きっかけ'])}</span></div>
<h2>ここにたどり着くまで</h2>
<div class="box flow">{段落(v['流れ'])}</div>"""
    if v.get("youtube"):
        中身 += f'<div class="buttons"><a class="btn main" href="{escape(v["youtube"])}">この動画を YouTube で見る</a></div>'
    if v.get("出典"):
        行 = "".join(f'<tr><td class="ts en">{escape(r.get("時刻", ""))}</td><td>{資料(r)}</td></tr>' for r in v["出典"])
        中身 += f'<h2>動画で使った資料</h2><div class="box"><table><tr><th>時刻</th><th>資料</th></tr>{行}</table></div>'
    if v.get("参考"):
        中身 += f'<h2>調べるときに使った資料</h2><ul class="box refs">{"".join(f"<li>{資料(r)}</li>" for r in v["参考"])}</ul>'
    中身 += '<div class="back"><a class="btn" href="../index.html">← トップへ</a></div>'
    return 枠(f"{v['題']}｜{サイト['チャンネル名']}", 中身, サイト, "../")


def main():
    サイト = 読む(ここ / "サイト.toml")
    動画たち = 動画を読む()
    if 出力.exists():
        shutil.rmtree(出力)
    (出力 / "v").mkdir(parents=True)
    shutil.copytree(ここ / "見た目", 出力 / "assets")
    if (ここ / "画像").exists():
        shutil.copytree(ここ / "画像", 出力 / "img")
    (出力 / "index.html").write_text(トップ(サイト, 動画たち), encoding="utf-8")
    for v in 動画たち:
        (出力 / "v" / f"{ページ番号(v)}.html").write_text(動画ページ(サイト, v), encoding="utf-8")
    print(f"組み立てました: トップ1枚・動画{len(動画たち)}枚 → {出力}")


if __name__ == "__main__":
    main()
