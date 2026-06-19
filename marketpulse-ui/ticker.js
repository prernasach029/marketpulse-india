// ── Shared NSE index ticker strip ──
(function(){
  const idx = [
    ["NIFTY 50","24,318.40","+0.62%",1],["SENSEX","79,943.71","+0.55%",1],
    ["BANK NIFTY","51,602.05","-0.31%",0],["NIFTY IT","41,887.20","+1.24%",1],
    ["NIFTY AUTO","23,104.80","+0.88%",1],["NIFTY FMCG","57,210.15","-0.14%",0],
    ["INR/USD","83.42","+0.08%",1],["GOLD MCX","71,840","+0.43%",1],
    ["CRUDE MCX","6,284","-1.02%",0],["NIFTY PHARMA","21,455.60","+0.71%",1]
  ];
  const tick = a => `<span class="tick"><span class="sym">${a[0]}</span><span class="val">${a[1]}</span><span class="chg ${a[3]?'up':'down'}">${a[3]?'▲':'▼'} ${a[2].replace('-','')}</span></span>`;
  const el = document.getElementById('track');
  if (el) el.innerHTML = (idx.map(tick).join('')).repeat(2);
})();
