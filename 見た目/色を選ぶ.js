// 読み込むたびに、背景色をフォーマル版の差し色（強の段）5色から1つ選ぶ。
// 値の出どころは VideoProject の style.py の 差し色の段。水色だけは彩度を 97% から 75% に下げてある（本人: 彩度が高すぎる）
const 差し色 = ["#3EC3E3", "#FF827B", "#D7FA00", "#FF9900", "#D29CFF"];
document.documentElement.style.setProperty("--bg", 差し色[Math.floor(Math.random() * 差し色.length)]);
