requireAuth(); mountNav("prediction.html");
Chart.defaults.color = "#cbd5e1"; Chart.defaults.borderColor="rgba(255,255,255,.08)";
let chart;

(async()=>{
  const [cs, ss] = await Promise.all([api("/countries"), api("/sports")]);
  const c = document.getElementById("country"); cs.forEach(x=>c.insertAdjacentHTML("beforeend",`<option>${x.name}</option>`));
  const s = document.getElementById("sport"); ss.forEach(x=>s.insertAdjacentHTML("beforeend",`<option>${x.name}</option>`));
})();

document.getElementById("predForm").addEventListener("submit", async (e)=>{
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target).entries());
  ["athletes","participation_count","prev_gold","prev_silver","prev_bronze"].forEach(k=>fd[k]=Number(fd[k]));
  const btn = document.getElementById("predBtn");
  btn.disabled=true; btn.innerHTML='<span class="spinner"></span> Predicting…';
  try{
    const r = await api("/predict",{method:"POST",body:JSON.stringify(fd)});
    const color = {Gold:"#facc15",Silver:"#cbd5e1",Bronze:"#d97706",None:"#64748b"}[r.predicted_medal] || "#3b82f6";
    document.getElementById("result").innerHTML = `
      <div class="d-flex align-items-center gap-3">
        <div style="font-size:3rem">${ {Gold:"🥇",Silver:"🥈",Bronze:"🥉",None:"🚫"}[r.predicted_medal] || "🏅" }</div>
        <div><div class="muted small">Predicted category</div>
        <div style="font-size:1.8rem;font-weight:700;color:${color}">${r.predicted_medal}</div>
        <div class="muted">Confidence: <b>${r.confidence}%</b></div></div></div>`;
    const labels = Object.keys(r.all_probabilities);
    const data = labels.map(l=>(r.all_probabilities[l]*100).toFixed(2));
    if(chart) chart.destroy();
    chart = new Chart(document.getElementById("probChart"),{type:"bar",
      data:{labels,datasets:[{label:"Probability (%)",data,backgroundColor:["#facc15","#cbd5e1","#d97706","#64748b"]}]},
      options:{plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,max:100}}}});
  }catch(err){ toast(err.message,"error"); }
  finally{ btn.disabled=false; btn.textContent="Predict"; }
});
