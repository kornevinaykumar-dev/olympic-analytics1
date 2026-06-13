// Shared frontend utilities
const API = "/api";
const TOKEN_KEY = "olympics_token";
const USER_KEY = "olympics_user";

function getToken(){ return localStorage.getItem(TOKEN_KEY); }
function setAuth(token, user){
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}
function getUser(){ try{return JSON.parse(localStorage.getItem(USER_KEY)||"null")}catch{return null} }
function logout(){ localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); window.location.href="login.html"; }

function requireAuth(){
  if(!getToken()){ window.location.href="login.html"; }
}

async function api(path, opts={}){
  const headers = { "Content-Type":"application/json", ...(opts.headers||{}) };
  const t = getToken();
  if(t) headers["Authorization"] = `Bearer ${t}`;
  const res = await fetch(API+path, { ...opts, headers });
  if(res.status === 401){ logout(); return; }
  const ct = res.headers.get("content-type")||"";
  if(ct.includes("application/json")){
    const data = await res.json();
    if(!res.ok) throw new Error(data.error || ("Request failed: "+res.status));
    return data;
  }
  if(!res.ok) throw new Error("Request failed: "+res.status);
  return res;
}

function renderNav(active){
  const user = getUser();
  const links = [
    ["dashboard.html","Dashboard"],
    ["standings.html","Standings"],
    ["analytics.html","Analytics"],
    ["prediction.html","Prediction"],
    ["insights.html","AI Insights"],
    ["profile.html","Profile"],
  ];
  return `
  <nav class="navbar navbar-expand-lg navbar-dark">
    <div class="container-fluid px-4">
      <a class="navbar-brand" href="dashboard.html">🏅 Olympic Analytics</a>
      <button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nv"><span class="navbar-toggler-icon"></span></button>
      <div class="collapse navbar-collapse" id="nv">
        <ul class="navbar-nav me-auto">
          ${links.map(([h,l])=>`<li class="nav-item"><a class="nav-link ${active===h?'active':''}" href="${h}">${l}</a></li>`).join("")}
        </ul>
        <span class="text-light me-3 d-none d-md-inline">👤 ${user?.name || "User"}</span>
        <button class="btn btn-sm btn-outline-light" onclick="logout()">Logout</button>
      </div>
    </div>
  </nav>`;
}

function mountNav(active){
  const el = document.getElementById("navbar");
  if(el) el.innerHTML = renderNav(active);
}

function toast(msg, type="info"){
  const div = document.createElement("div");
  div.className = `alert alert-${type==="error"?"danger":type==="success"?"success":"primary"} position-fixed`;
  div.style.cssText="top:1rem;right:1rem;z-index:9999;min-width:260px;box-shadow:0 8px 30px rgba(0,0,0,.4)";
  div.textContent = msg;
  document.body.appendChild(div);
  setTimeout(()=>div.remove(), 3500);
}
