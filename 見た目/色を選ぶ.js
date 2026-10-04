// サイトの色を決める: 差し色（読み込むたびに5色から1つ）と、ライト／ダークのモード。
// ページが描かれる前に決めたいので、<head> で読み込む。色の値そのものは style.css が持つ

// --- 差し色 ---
// 値の出どころは VideoProject の style.py の 差し色の段。水色だけは彩度を 97% から 75% に下げてある（本人: 彩度が高すぎる）
const 背景の色たち = ["#3EC3E3", "#FF827B", "#D7FA00", "#FF9900", "#D29CFF"];

// ページを移るとき、切り替えの幕（動き.js）で見せた色を次のページでも使う。ここに預けておく
const 預け先 = "次の背景色";
function 預かった色() {
  try {
    const 色 = sessionStorage.getItem(預け先);
    sessionStorage.removeItem(預け先);
    return 背景の色たち.includes(色) ? 色 : null;
  } catch { return null; }
}
function どれか(色たち) { return 色たち[Math.floor(Math.random() * 色たち.length)]; }

const 今の背景色 = 預かった色() || どれか(背景の色たち);
document.documentElement.style.setProperty("--accent", 今の背景色);

// 次のページの色を、今と違う色から選んで預ける
function 次の背景色() {
  const 色 = どれか(背景の色たち.filter(c => c !== 今の背景色));
  try { sessionStorage.setItem(預け先, 色); } catch {}
  return 色;
}

// --- ライト／ダーク ---
// 本人がボタンで選んだもの（この端末に覚える）を優先し、選んでいなければ OS の設定に合わせる
const モードの預け先 = "見た目のモード";
const OSはダーク = matchMedia("(prefers-color-scheme: dark)");

function 選んだモード() {
  try {
    const m = localStorage.getItem(モードの預け先);
    return m === "light" || m === "dark" ? m : null;
  } catch { return null; }
}
function モードを当てる(m) { document.documentElement.dataset.theme = m; }

モードを当てる(選んだモード() || (OSはダーク.matches ? "dark" : "light"));
OSはダーク.addEventListener("change", e => { if (!選んだモード()) モードを当てる(e.matches ? "dark" : "light"); });

// ボタンを押すと、押したところから丸く塗り替える（対応していないブラウザと、動きを減らす設定の人には、すぐ切り替える）
document.addEventListener("click", e => {
  const ボタン = e.target.closest(".theme-btn");
  if (!ボタン) return;
  const 次 = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  const 切り替える = () => {
    モードを当てる(次);
    try { localStorage.setItem(モードの預け先, 次); } catch {}
  };
  const 静か = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!document.startViewTransition || 静か) { 切り替える(); return; }
  const 枠 = ボタン.getBoundingClientRect();
  const x = 枠.left + 枠.width / 2, y = 枠.top + 枠.height / 2;
  // いちばん遠い角までの距離の1.2倍まで広げる。ちょうどの距離だと、終わり際の減速で遠い角が最後まで塗り残り、
  // 円が途中で止まったように見えた（本人）。少し大きく広げて、減速に入る前に画面を覆い切る
  const 半径 = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y)) * 1.2;
  document.startViewTransition(切り替える).ready.then(() => {
    document.documentElement.animate(
      { clipPath: [`circle(0 at ${x}px ${y}px)`, `circle(${半径}px at ${x}px ${y}px)`] },
      { duration: 650, easing: "cubic-bezier(.65, 0, .35, 1)", pseudoElement: "::view-transition-new(root)" });
  });
});
