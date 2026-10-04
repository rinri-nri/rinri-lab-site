// サイトの動き: 見出しの文字の登場・スクロールで現れる・パララックス・疑問の鎖の線・ページの切り替え（アイリス）。
// 見た目の値は style.css、背景色は 色を選ぶ.js が持つ。ここは「いつ・どれだけ動かすか」だけ。
// 動きを減らす設定の人には、パララックスと切り替えの幕を出さない（文字の登場などは style.css 側で止める）
const 静か = matchMedia("(prefers-reduced-motion: reduce)").matches;

// --- 見出しを1文字ずつに分ける（style.css の .ch が順に跳ねて出る） ---
// 1文字ずつの箱にすると、ブラウザの禁則（「。」や「」」を行頭に置かない）が効かなくなる。
// そこで、閉じる記号は前の字に、開く記号は次の字にくっつけて1つの箱にする
const 行頭に置かない = "」』）、。，．？！ー…ぁぃぅぇぉっゃゅょ";
const 行末に置かない = "「『（";
function 禁則でまとめる(文) {
  const 塊 = [];
  let 持ち越し = "";
  for (const 字 of 文) {
    if (行末に置かない.includes(字)) { 持ち越し += 字; continue; }
    if (行頭に置かない.includes(字) && 塊.length && !持ち越し) { 塊[塊.length - 1] += 字; continue; }
    塊.push(持ち越し + 字);
    持ち越し = "";
  }
  if (持ち越し) 塊.push(持ち越し);
  return 塊;
}
function 文字に分ける(要素) {
  let 番号 = 0;
  const たどる = 親 => {
    for (const 子 of [...親.childNodes]) {
      if (子.nodeType === Node.TEXT_NODE) {
        const 束 = document.createDocumentFragment();
        for (const 字 of 禁則でまとめる(子.textContent)) {
          if (!字.trim()) { 束.append(字); continue; }
          const s = document.createElement("span");
          s.className = "ch";
          s.style.setProperty("--i", 番号++);
          s.textContent = 字;
          s.setAttribute("aria-hidden", "true");  // 読み上げは見出しの aria-label で
          束.append(s);
        }
        子.replaceWith(束);
      } else if (子.nodeType === Node.ELEMENT_NODE && 子.tagName !== "BR") {
        たどる(子);
      }
    }
  };
  たどる(要素);
}
document.querySelectorAll(".split").forEach(文字に分ける);

// --- スクロールで現れる ---
const 見張り = new IntersectionObserver(出来事 => {
  for (const e of 出来事) {
    if (e.isIntersecting) { e.target.classList.add("in"); 見張り.unobserve(e.target); }
  }
}, { threshold: 0.15, rootMargin: "0px 0px -8% 0px" });
document.querySelectorAll(".reveal").forEach(el => 見張り.observe(el));

// --- スクロールに合わせて動かす ---
// 浮くもの: 自分の区切りの中心が画面の中心からずれた分 × data-speed だけ縦に動かす。
// 速さが大きいほど速く流れ、手前にあるように見える（マウスには追従させない: 2026-10-04 本人）
const 浮くもの = [...document.querySelectorAll("[data-speed]")];
const 流れる字 = [...document.querySelectorAll("[data-drift]")];
const 鎖 = document.querySelector(".chain");
const 進み具合 = document.querySelector(".progress");
let 予約済み = false;

function 割合(値) { return Math.min(1, Math.max(0, 値)); }

function 描く() {
  予約済み = false;
  const y = scrollY, 高さ = innerHeight;
  if (!静か) {
    for (const el of 浮くもの) {
      const r = el.closest("header, section").getBoundingClientRect();
      el.style.transform = `translate3d(0, ${(r.top + r.height / 2 - 高さ / 2) * +el.dataset.speed}px, 0)`;
    }
    for (const el of 流れる字) {
      const r = el.parentElement.getBoundingClientRect();
      el.style.transform = `translateX(${(r.top + r.height / 2 - 高さ / 2) * -0.3}px)`;
    }
  }
  if (鎖) {
    const r = 鎖.getBoundingClientRect();
    鎖.style.setProperty("--p", 割合((高さ * 0.6 - r.top) / r.height));
  }
  if (進み具合) {
    進み具合.style.setProperty("--p", 割合(y / Math.max(1, document.documentElement.scrollHeight - 高さ)));
  }
}
function 頼む() { if (!予約済み) { 予約済み = true; requestAnimationFrame(描く); } }
addEventListener("scroll", 頼む, { passive: true });
addEventListener("resize", 頼む);
描く();

// --- ページの切り替え: 黒い丸が広がり、次のページの色の丸が追いかける（動画のアイリスと同じ形） ---
const 幕の時間 = 620;  // style.css の .iris の transition が終わるまで
document.addEventListener("click", e => {
  const a = e.target.closest("a");
  if (静か || !a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || a.target) return;
  const 行き先 = new URL(a.href, location.href);
  if (行き先.origin !== location.origin) return;
  if (行き先.pathname === location.pathname && 行き先.hash) return;  // 同じページの中の移動はそのまま
  e.preventDefault();
  const キーで押した = e.detail === 0;  // キーボードのときは画面の真ん中から
  const 幕 = document.createElement("div");
  幕.className = "iris";
  幕.setAttribute("aria-hidden", "true");
  幕.style.setProperty("--x", (キーで押した ? innerWidth / 2 : e.clientX) + "px");
  幕.style.setProperty("--y", (キーで押した ? innerHeight / 2 : e.clientY) + "px");
  幕.style.setProperty("--next", 次の背景色());
  幕.innerHTML = "<i></i><i></i>";
  document.body.append(幕);
  幕.getBoundingClientRect();  // 丸が0の状態を一度描かせてから広げる（これが無いと広がる動きが出ない）
  幕.classList.add("go");
  setTimeout(() => { location.href = 行き先.href; }, 幕の時間);
});
// 「戻る」でキャッシュから戻ったとき、閉じたままの幕を外す
addEventListener("pageshow", e => { if (e.persisted) document.querySelectorAll(".iris").forEach(x => x.remove()); });
