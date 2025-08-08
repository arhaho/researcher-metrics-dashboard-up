async function loadData(){
  const res = await fetch('data/snapshot.json?ts=' + Date.now(), {cache: 'no-store'});
  if(!res.ok){ throw new Error('Failed to load snapshot.json'); }
  return await res.json();
}
function toCsv(rows){
  const esc = (v)=>(''+v).replaceAll('"','""');
  const header = ['Author','Institutions','Papers','Citations','h_index','i10_index','OpenAlex_ID'];
  const lines = [header.join(',')];
  rows.forEach(r=>{
    lines.push([`"${esc(r.display_name)}"`,`"${esc((r.institutions||[]).join('; '))}"`,r.works_count,r.cited_by_count,r.h_index??'',r.i10_index??'',r.openalex_key].join(','));
  });
  return lines.join('\n');
}
function renderTable(snapshot){
  const tbody = document.querySelector('#authorsTable tbody');
  tbody.innerHTML = '';
  const rows = snapshot.authors.filter(a=>!a.error);
  rows.sort((a,b)=> (b.cited_by_count||0)-(a.cited_by_count||0));
  rows.forEach(a=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${a.display_name||''}</td>
      <td>${(a.institutions||[]).join(', ')}</td>
      <td>${a.works_count??''}</td>
      <td>${a.cited_by_count??''}</td>
      <td>${a.h_index??''}</td>
      <td>${a.i10_index??''}</td>
      <td><a href="author.html?aid=${encodeURIComponent(a.openalex_key)}">Open</a></td>
    `;
    tbody.appendChild(tr);
  });
  document.getElementById('lastRefreshed').textContent = `Refreshed: ${snapshot.generated_at_utc}`;
  document.getElementById('downloadCsv').onclick = ()=>{
    const csv = toCsv(rows);
    const blob = new Blob([csv], {type:'text/csv'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'researcher_metrics.csv';
    a.click();
    URL.revokeObjectURL(url);
  };
}
document.getElementById('reload').addEventListener('click', ()=>location.reload());
loadData().then(renderTable).catch(err=>{ alert(err.message); });
