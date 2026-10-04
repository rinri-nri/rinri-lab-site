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
動画に必須 = ["番号", "題", "流れ"]

FONTS = ("https://fonts.googleapis.com/css2?family=LINE+Seed+JP:wght@400;800"
         "&family=Shippori+Mincho+B1:wght@800&family=Montserrat:ital,wght@1,800&display=swap")

# 帯に流す英語。帯の中で2回くり返し、半分ずらすと継ぎ目なく回る
帯の言葉 = ["WHY?", "LOOK IT UP", "NEXT QUESTION", "AND THEN?", "CHECK THE SOURCE"]


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
        if not v["流れ"] or any("疑問" not in 段 for 段 in v["流れ"]):
            sys.exit(f"{パス.name} の 流れ に、疑問 の無い段があります")
        動画たち.append(v)
    return sorted(動画たち, key=lambda v: v["番号"], reverse=True)  # 新しい順


def 段落(文):
    return "".join(f"<p>{escape(p.strip())}</p>" for p in 文.strip().split("\n\n") if p.strip())


def ページ番号(v):
    return f"{v['番号']:03d}"


def きっかけ(v):
    """流れの最初の疑問が、その動画のきっかけ（カードにもここから出す）。"""
    return v["流れ"][0]["疑問"]


# --- 飾りの部品 ------------------------------------------------

# 疑問の記号のステッカー。明朝体の記号を、縁の無い色の形にのせる（2026-10-04 本人: 疑問の記号で統一）。
# 大きいものほど手前にあるとみなし、スクロールで速く動かす（速さは style.css ではなくここの 大きさの段 で決まる）
大きさの段 = {"L": "0.32", "M": "0.18", "S": "0.07"}  # data-speed。動き.js が「区切りの中心からのずれ × 速さ」だけ動かす

# 置き方: (記号, 形, 色, 大きさ, 縦の位置, 横の位置, スマホでも出すか)。位置は区切りの中での %
# 形は maru（丸）か fuda（札）、色は 1〜3（札の3色）・w（白）・k（黒）
置き方 = {
    "hero": [("？", "maru", "w", "L", "10%", "left:4%", True), ("！", "fuda", "1", "M", "16%", "right:8%", True),
             ("…", "maru", "3", "S", "8%", "left:38%", False), ("※", "fuda", "2", "M", "76%", "left:5%", False),
             ("？", "maru", "k", "S", "44%", "right:3%", False), ("〃", "maru", "1", "S", "78%", "left:30%", False),
             ("？", "fuda", "3", "L", "66%", "right:12%", True), ("！", "maru", "2", "S", "24%", "left:54%", False)],
    "how": [("？", "maru", "1", "M", "6%", "right:4%", True), ("…", "fuda", "w", "S", "70%", "left:3%", False),
            ("！", "maru", "k", "S", "88%", "right:3%", False)],
    "videos": [("※", "maru", "3", "M", "10%", "right:6%", False), ("？", "fuda", "2", "L", "62%", "right:2%", True),
               ("〃", "maru", "w", "S", "86%", "left:4%", False)],
    "about": [("！", "fuda", "1", "M", "14%", "right:5%", True), ("？", "maru", "3", "S", "56%", "left:3%", False),
              ("…", "maru", "w", "L", "74%", "right:10%", False)],
    "vhero": [("？", "maru", "w", "L", "10%", "right:6%", True), ("！", "fuda", "1", "S", "18%", "left:3%", False),
              ("※", "maru", "3", "M", "70%", "right:16%", False), ("〃", "fuda", "2", "S", "60%", "left:40%", False)],
}


def ステッカー(場所):
    return '<div class="stickers" aria-hidden="true">' + "".join(
        f'<span class="st {大} {形} c{色}{"" if スマホ else " pc-only"}" style="top:{縦};{横}" '
        f'data-speed="{大きさの段[大]}"><b class="mincho">{記号}</b></span>'
        for 記号, 形, 色, 大, 縦, 横, スマホ in 置き方[場所]) + "</div>"


def 大きな英字(文字, 種類="bigword", 動き='data-speed="-0.35"'):
    return f'<div class="{種類} en" {動き} aria-hidden="true">{escape(文字)}</div>'


def 帯():
    半分 = "".join(f"<span>{w}</span><b>✱</b>" for w in 帯の言葉 * 2)
    return f"""<div class="bands" aria-hidden="true">
<div class="band band-a"><div class="track en">{半分}{半分}</div></div>
<div class="band band-b"><div class="track en">{半分}{半分}</div></div></div>"""


def 見出し(日本語, 英語):
    return f'<div class="sec-head reveal"><h2>{escape(日本語)}</h2><span class="en">{escape(英語)}</span></div>'


# --- ページの外側 ----------------------------------------------

def 枠(題, 中身, サイト, 上へ):
    """全ページ共通の外側。上へ はトップへの相対パス（"" か "../"）。"""
    足の帯 = "".join(f"<span>{escape(サイト['英語名'])}</span><b>✱</b><span>{escape(サイト['チャンネル名'])}</span><b>✱</b>" for _ in range(4))
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(題)}</title>
<script>document.documentElement.classList.add("js")</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{上へ}assets/style.css">
<script src="{上へ}assets/色を選ぶ.js"></script>
<script src="{上へ}assets/動き.js" defer></script>
</head><body>
<div class="progress" aria-hidden="true"></div>
<nav class="box topnav"><a class="logo" href="{上へ}index.html">{escape(サイト['チャンネル名'])}</a>
<div class="links"><a href="{上へ}index.html#videos">動画</a><a href="{上へ}index.html#about">このチャンネルについて</a><a href="{escape(サイト['youtube'])}">YouTube ↗</a></div></nav>
{中身}
<footer><div class="footband" aria-hidden="true"><div class="track en">{足の帯}{足の帯}</div></div>
<p class="en">© {escape(サイト['英語名'])}</p></footer>
</body></html>
"""


def サムネ(v, 上へ):
    名前 = v.get("サムネ", "")
    if 名前 and (ここ / "画像" / 名前).exists():
        return f'<img class="thumb" src="{上へ}img/{escape(名前)}" alt="" loading="lazy">'
    return '<div class="thumb"></div>'


# --- トップ ----------------------------------------------------

def カード(v, 順):
    return f"""<a class="box card reveal" style="--d:{順}" href="v/{ページ番号(v)}.html"><div class="thumb-wrap">{サムネ(v, "")}</div><div class="in">
<span class="num en">No.{ページ番号(v)}</span><b>{escape(v['題'])}</b>
<p>きっかけ：<span class="mincho">{escape(きっかけ(v))}</span></p></div></a>"""


def トップ(サイト, 動画たち):
    手順 = "".join(f'<li class="box reveal" style="--d:{i}"><i class="en">{i:02d}</i><span>{escape(s)}</span></li>'
                 for i, s in enumerate(サイト["決め方"], 1))
    ボタン = f'<a class="btn main" href="{escape(サイト["youtube"])}">YouTube で見る ↗</a>'
    if サイト.get("問い合わせ"):
        ボタン += f'<a class="btn" href="{escape(サイト["問い合わせ"])}">お問い合わせ</a>'
    中身 = f"""<header class="hero">
{大きな英字("why.")}
{ステッカー("hero")}
<div class="hero-in">
<p class="kicker en">{escape(サイト['英語名'])} — A ROOM FOR QUESTIONS</p>
<h1 class="top-title split" aria-label="「{escape(サイト['見出し'])}」{escape(サイト['見出しの続き'])}">「<span class="mincho fuda">{escape(サイト['見出し'])}</span>」<br>{escape(サイト['見出しの続き'])}</h1>
<a class="cue en" href="#how">SCROLL ↓</a>
</div></header>
{帯()}
<main>
<section class="sec" id="how">{大きな英字("how.", "secword", "data-drift")}{ステッカー("how")}<div class="wrap">
{見出し("テーマの決め方", "HOW WE PICK A THEME")}
<ol class="steps">{手順}</ol></div></section>
<section class="sec" id="videos">{大きな英字("videos.", "secword", "data-drift")}{ステッカー("videos")}<div class="wrap">
{見出し("押したい動画", "FEATURED")}
<div class="cards">{"".join(カード(v, i) for i, v in enumerate(動画たち))}</div></div></section>
<section class="sec" id="about">{大きな英字("about.", "secword", "data-drift")}{ステッカー("about")}<div class="wrap">
{見出し("このチャンネルについて", "ABOUT")}
<p class="quote mincho reveal">{escape(サイト['結びの一言'])}</p>
<div class="box about reveal">{段落(サイト['作り手'])}<div class="buttons">{ボタン}</div></div></div></section>
</main>"""
    return 枠(サイト["チャンネル名"], 中身, サイト, "")


# --- 動画ページ ------------------------------------------------

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


def 疑問の鎖(v):
    段たち = "".join(
        f"""<div class="node {'l' if i % 2 else 'r'} reveal"><span class="node-no en">Q{i}</span>
<p class="node-q mincho fuda">{escape(段['疑問'])}</p>
{f'<div class="box node-a">{段落(段["分かったこと"])}</div>' if 段.get("分かったこと") else ""}</div>"""
        for i, 段 in enumerate(v["流れ"], 1))
    終わりの中 = f"""<div class="end-thumb">{サムネ(v, "../")}</div><div class="end-text">
<span class="en">AND THEN — IT BECAME A VIDEO</span><b>{escape(v['題'])}</b>
{'<span class="btn main">YouTube で見る ↗</span>' if v.get("youtube") else ""}</div>"""
    if v.get("youtube"):
        終わり = f'<a class="box end-card" href="{escape(v["youtube"])}">{終わりの中}</a>'
    else:
        終わり = f'<div class="box end-card">{終わりの中}</div>'
    return f"""<div class="chain"><div class="chain-line" aria-hidden="true"><i></i></div>{段たち}
<div class="node node-end reveal"><span class="node-no en">→</span>{終わり}</div></div>"""


def 動画ページ(サイト, v):
    中身 = f"""<header class="hero vhero">
{大きな英字(f"no.{ページ番号(v)}")}
{ステッカー("vhero")}
<div class="hero-in">
<span class="num en">No.{ページ番号(v)}</span>
<h1 class="v-title split" aria-label="{escape(v['題'])}">{escape(v['題'])}</h1>
<div class="v-q"><span class="mincho fuda"><small>きっかけの疑問</small>{escape(きっかけ(v))}</span></div>
</div></header>
{帯()}
<main>
<section class="sec">{大きな英字("route.", "secword", "data-drift")}<div class="wrap">
{見出し("ここにたどり着くまで", "THE ROUTE OF QUESTIONS")}
{疑問の鎖(v)}</div></section>"""
    if v.get("出典"):
        行 = "".join(f'<tr style="--d:{i}"><td class="ts en">{escape(r.get("時刻", ""))}</td><td>{資料(r)}</td></tr>'
                    for i, r in enumerate(v["出典"]))
        中身 += f"""<section class="sec">{大きな英字("sources.", "secword", "data-drift")}<div class="wrap">
{見出し("動画で使った資料", "SOURCES")}
<div class="box table-box reveal"><table><tr><th>時刻</th><th>資料</th></tr>{行}</table></div></div></section>"""
    if v.get("参考"):
        項目 = "".join(f"<li>{資料(r)}</li>" for r in v["参考"])
        中身 += f"""<section class="sec"><div class="wrap">
{見出し("調べるときに使った資料", "FURTHER READING")}
<ul class="box refs reveal">{項目}</ul></div></section>"""
    中身 += '<div class="wrap back"><a class="btn" href="../index.html">← トップへ</a></div></main>'
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
