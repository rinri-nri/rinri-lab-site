// まとめ画像の送り: 左右のボタンで1枚ずつ送り、いま何枚目かを出す。指のスワイプは、ブラウザの横スクロールにまかせる
const 送りは静か = matchMedia("(prefers-reduced-motion: reduce)").matches;

for (const 箱 of document.querySelectorAll(".slides-box")) {
  const 列 = 箱.querySelector(".slides");
  const 枚たち = [...列.children];
  const 前 = 箱.querySelector(".prev"), 次 = 箱.querySelector(".next"), 数え = 箱.querySelector(".slide-count");

  // 左端にいちばん近い1枚を「いま」とみなす
  const いま = () => {
    let 近い = 0;
    枚たち.forEach((枚, i) => { if (Math.abs(枚.offsetLeft - 列.scrollLeft) < Math.abs(枚たち[近い].offsetLeft - 列.scrollLeft)) 近い = i; });
    return 近い;
  };
  const 見せる = () => {
    const i = いま();
    数え.textContent = `${i + 1} / ${枚たち.length}`;
    前.disabled = i === 0;
    次.disabled = i === 枚たち.length - 1;
  };
  const 送る = 向き => {
    const i = Math.min(枚たち.length - 1, Math.max(0, いま() + 向き));
    列.scrollTo({ left: 枚たち[i].offsetLeft, behavior: 送りは静か ? "auto" : "smooth" });
  };
  前.addEventListener("click", () => 送る(-1));
  次.addEventListener("click", () => 送る(1));
  let 予約 = false;
  列.addEventListener("scroll", () => { if (!予約) { 予約 = true; requestAnimationFrame(() => { 予約 = false; 見せる(); }); } }, { passive: true });
  見せる();
}
