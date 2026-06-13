requireAuth(); mountNav("analytics.html");
Chart.defaults.color = "#cbd5e1"; Chart.defaults.borderColor = "rgba(255,255,255,.08)";
let cChart, sChart, rChart;

(async()=>{
  const [cs, ss] = await Promise.all([api("/countries"), api("/sports")]);
  const cSel = document.getElementById("countrySel");
  cs.forEach(c=>cSel.insertAdjacentHTML("beforeend",`<option>${c.name}</option>`));
  const sSel = document.getElementById("sportSel");
  ss.forEach(s=>sSel.insertAdjacentHTML("beforeend",`<option>${s.name}</option>`));

  document.getElementById("loadCountry").onclick = async ()=>{
    const name = cSel.value;
    try{
      const d = await api(`/analytics/country/${encodeURIComponent(name)}`);
      document.getElementById("countryResult").innerHTML = `
        <div class="col-md-4"><div class="stat-card"><div class="label">Total Medals</div><div class="value">${d.total_medals}</div></div></div>
        <div class="col-md-4"><div class="stat-card"><div class="label">Best Year</div><div class="value">${d.best_year ?? "—"}</div></div></div>
        <div class="col-md-4"><div class="stat-card"><div class="label">Gold %</div><div class="value">${d.gold_percentage}%</div></div></div>
        <div class="col-12"><div class="card p-3"><div class="card-header">${d.country} — Medal Trend</div><div class="chart-box"><canvas id="cChart"></canvas></div></div></div>`;
      if(cChart) cChart.destroy();
      cChart = new Chart(document.getElementById("cChart"),{type:"line",
        data:{labels:d.trend.map(r=>r.year),datasets:[
          {label:"Gold",data:d.trend.map(r=>r.gold),borderColor:"#facc15",backgroundColor:"rgba(250,204,21,.2)",tension:.3},
          {label:"Silver",data:d.trend.map(r=>r.silver),borderColor:"#cbd5e1",tension:.3},
          {label:"Bronze",data:d.trend.map(r=>r.bronze),borderColor:"#d97706",tension:.3},
          {label:"Total",data:d.trend.map(r=>r.total),borderColor:"#3b82f6",borderDash:[6,4],tension:.3},
        ]}});
    }catch(e){ toast(e.message,"error"); }
  };

  document.getElementById("loadSport").onclick = async ()=>{
    const name = sSel.value;
    try{
      const d = await api(`/analytics/sport/${encodeURIComponent(name)}`);
      document.getElementById("sportResult").innerHTML = `
        <div class="col-lg-6"><div class="card p-3"><div class="card-header">${d.sport} — Top Countries (Radar)</div><div class="chart-box"><canvas id="rChart"></canvas></div></div></div>
        <div class="col-lg-6"><div class="card p-3"><div class="card-header">${d.sport} — Year Trend</div><div class="chart-box"><canvas id="sChart"></canvas></div></div></div>`;
      if(rChart) rChart.destroy(); if(sChart) sChart.destroy();
      rChart = new Chart(document.getElementById("rChart"),{type:"radar",
        data:{labels:d.top_countries.map(r=>r.country),
          datasets:[{label:"Total Medals",data:d.top_countries.map(r=>r.total),
            borderColor:"#22d3ee",backgroundColor:"rgba(34,211,238,.3)"}]}});
      sChart = new Chart(document.getElementById("sChart"),{type:"bar",
        data:{labels:d.trend.map(r=>r.year),datasets:[{label:"Medals",
          data:d.trend.map(r=>r.total),backgroundColor:"#3b82f6"}]},
        options:{plugins:{legend:{display:false}}}});
    }catch(e){ toast(e.message,"error"); }
  };
})();
