// 読み込むたびに、背景色をフォーマル版の差し色（強の段）5色から1つ選ぶ。
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
document.documentElement.style.setProperty("--bg", 今の背景色);

// 次のページの色を、今と違う色から選んで預ける
function 次の背景色() {
  const 色 = どれか(背景の色たち.filter(c => c !== 今の背景色));
  try { sessionStorage.setItem(預け先, 色); } catch {}
  return 色;
}
