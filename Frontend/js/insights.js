requireAuth(); mountNav("insights.html");

async function spin(btn, fn){
  const orig = btn.textContent; btn.disabled=true; btn.innerHTML='<span class="spinner"></span> Generating…';
  try{ await fn(); } catch(e){ toast(e.message,"error"); }
  finally{ btn.disabled=false; btn.textContent=orig; }
}

(async()=>{
  const [cs, ss] = await Promise.all([api("/countries"), api("/sports")]);
  const c = document.getElementById("cSel"); cs.forEach(x=>c.insertAdjacentHTML("beforeend",`<option>${x.name}</option>`));
  const s = document.getElementById("sSel"); ss.forEach(x=>s.insertAdjacentHTML("beforeend",`<option>${x.name}</option>`));
})();

document.getElementById("cBtn").onclick = ()=> spin(document.getElementById("cBtn"), async ()=>{
  const country = document.getElementById("cSel").value;
  const stats = await api(`/analytics/country/${encodeURIComponent(country)}`);
  const r = await api("/generate-insights",{method:"POST",body:JSON.stringify({
    type:"country", country, stats:{total:stats.total_medals,best_year:stats.best_year,gold_pct:stats.gold_percentage,trend:stats.trend}
  })});
  document.getElementById("cOut").textContent = r.text;
});

document.getElementById("sBtn").onclick = ()=> spin(document.getElementById("sBtn"), async ()=>{
  const sport = document.getElementById("sSel").value;
  const data = await api(`/analytics/sport/${encodeURIComponent(sport)}`);
  const r = await api("/generate-insights",{method:"POST",body:JSON.stringify({
    type:"sport", sport, leaderboard:data.top_countries
  })});
  document.getElementById("sOut").textContent = r.text;
});

document.getElementById("tBtn").onclick = ()=> spin(document.getElementById("tBtn"), async ()=>{
  const d = await api("/dashboard");
  const r = await api("/generate-insights",{method:"POST",body:JSON.stringify({
    type:"trend", payload:{trend:d.trend, top_countries:d.top_countries, top_sports:d.sports}
  })});
  document.getElementById("tOut").textContent = r.text;
});
