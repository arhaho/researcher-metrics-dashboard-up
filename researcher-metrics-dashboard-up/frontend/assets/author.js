async function loadSnapshot(){
  const res = await fetch('data/snapshot.json?ts=' + Date.now(), {cache:'no-store'});
  return await res.json();
}
function getParam(name){
  const params = new URLSearchParams(location.search);
  return params.get(name);
}
function chart(elId, labels, values, label){
  const ctx = document.getElementById(elId).getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: { labels, datasets: [{ label, data: values }] },
    options: { responsive: true, maintainAspectRatio: false }
  });
}
loadSnapshot().then(snap=>{
  const aid = getParam('aid');
  const a = snap.authors.find(x=>x.openalex_key===aid);
  if(!a){ document.body.innerHTML = '<p>Author not found.</p>'; return; }
  document.getElementById('authorName').textContent = a.display_name || aid;
  document.getElementById('insts').textContent = (a.institutions||[]).join(', ');
  const div = document.getElementById('metrics');
  div.innerHTML = `
    <div class="metric"><b>Papers</b><div>${a.works_count??''}</div></div>
    <div class="metric"><b>Citations</b><div>${a.cited_by_count??''}</div></div>
    <div class="metric"><b>h-index</b><div>${a.h_index??''}</div></div>
    <div class="metric"><b>i10-index</b><div>${a.i10_index??''}</div></div>
    <div class="metric"><b>Updated</b><div>${a.updated_date??''}</div></div>
  `;
  const byYear = (a.counts_by_year||[]).slice().sort((x,y)=>x.year - y.year);
  const labels = byYear.map(r=>r.year);
  const works = byYear.map(r=>r.works_count);
  const cites = byYear.map(r=>r.cited_by_count);
  chart('worksChart', labels, works, 'Works');
  chart('citesChart', labels, cites, 'Citations');
});
