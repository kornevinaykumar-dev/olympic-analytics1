requireAuth(); mountNav("dashboard.html");
Chart.defaults.color = "#cbd5e1"; Chart.defaults.borderColor = "rgba(255,255,255,.08)";

(async()=>{
  try{
    const d = await api("/dashboard");
    document.getElementById("c-countries").textContent = d.cards.total_countries;
    document.getElementById("c-sports").textContent = d.cards.total_sports;
    document.getElementById("c-medals").textContent = d.cards.total_medals.toLocaleString();
    document.getElementById("c-years").textContent = d.cards.total_years;

    new Chart(document.getElementById("pie"),{type:"doughnut",
      data:{labels:["Gold","Silver","Bronze"],datasets:[{
        data:[d.distribution.gold,d.distribution.silver,d.distribution.bronze],
        backgroundColor:["#facc15","#cbd5e1","#d97706"],borderWidth:0}]},
      options:{plugins:{legend:{position:"bottom"}}}});

    new Chart(document.getElementById("bar"),{type:"bar",
      data:{labels:d.top_countries.map(r=>r.country),
        datasets:[{label:"Total medals",data:d.top_countries.map(r=>r.total),backgroundColor:"#3b82f6"}]},
      options:{plugins:{legend:{display:false}}}});

    new Chart(document.getElementById("line"),{type:"line",
      data:{labels:d.trend.map(r=>r.year),
        datasets:[{label:"Medals awarded",data:d.trend.map(r=>r.total),
          borderColor:"#22d3ee",backgroundColor:"rgba(34,211,238,.2)",tension:.35,fill:true}]}});

    new Chart(document.getElementById("sportBar"),{type:"bar",
      data:{labels:d.sports.map(r=>r.sport),
        datasets:[{label:"Medals",data:d.sports.map(r=>r.total),backgroundColor:"#10b981"}]},
      options:{indexAxis:"y",plugins:{legend:{display:false}}}});
  }catch(e){ toast(e.message,"error"); }
})();
