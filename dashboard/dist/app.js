/* 계산 함수는 화면과 검증에서 함께 사용한다. */
function calculate(data, start, end, threshold, scope) {
  const selected = data.filter(r => +r.date.slice(0,4)>=start && +r.date.slice(0,4)<=end && (scope==='full'||+r.date.slice(5,7)<=8));
  const groups = new Map();
  for (const r of selected) { const y=+r.date.slice(0,4); if(!groups.has(y)) groups.set(y,[]); groups.get(y).push(r); }
  return [...groups].map(([year, values])=>{
    values.sort((a,b)=>a.date.localeCompare(b.date));
    let low=0,high=0,runLow=0,runHigh=0,longLow=0,longHigh=0,missing=0;
    for(const row of values){const absent=row.tmax===null;const hot=!absent&&row.tmax>=threshold;
      low+=Number(hot);high+=Number(hot||absent);missing+=Number(absent);
      runLow=hot?runLow+1:0;runHigh=hot||absent?runHigh+1:0;
      longLow=Math.max(longLow,runLow);longHigh=Math.max(longHigh,runHigh);
    }
    return {year,days:values.length,low,high,longLow,longHigh,missing};
  });
}
if(typeof module!=='undefined') module.exports={calculate};
if(typeof document!=='undefined') {
 const $=id=>document.getElementById(id);
 for(let y=2006;y<=2026;y++){for(const id of ['start','end']){const o=document.createElement('option');o.value=y;o.textContent=y+'년';$(id).append(o);}}
 $('start').value='2006';$('end').value='2025';
 const range=(a,b,d=0)=>{if(Math.abs(a-b)<1e-9)return a.toFixed(d);while(a.toFixed(d)===b.toFixed(d)&&d<4)d++;return `${a.toFixed(d)}~${b.toFixed(d)}`;};
 function render(){
   let start=+$('start').value,end=+$('end').value;let message='';
   if(start>end){end=start;$('end').value=String(end);message='종료 연도를 시작 연도에 맞췄습니다. ';}
   if(end===2026){$('scope').value='janaug';message+='2026년 포함: 모든 연도를 1~8월로 맞춰 비교합니다.';}
   $('scope').disabled=end===2026;
   const scope=$('scope').value,threshold=+$('threshold').value;
   const values=calculate(window.WEATHER_DATA,start,end,threshold,scope);
   $('notice').textContent=message||`${start}~${end}년 · ${scope==='full'?'1~12월':'1~8월'} · 일최고기온 ${threshold}℃ 이상`;
   const avg=key=>values.reduce((sum,r)=>sum+r[key],0)/values.length;
   $('hot').textContent=range(avg('low'),avg('high'),1)+'일';
   $('run').textContent=range(avg('longLow'),avg('longHigh'),1)+'일';
   $('missing').textContent=values.reduce((sum,r)=>sum+r.missing,0)+'일';
   $('rows').innerHTML=values.map(r=>`<tr><td>${r.year}</td><td>${r.days}일</td><td>${range(r.low,r.high)}일</td><td>${range(100*r.low/r.days,100*r.high/r.days,2)}%</td><td>${range(r.longLow,r.longHigh)}일</td></tr>`).join('');
   const W=1000,H=320,left=46,top=32,bottom=44,space=(W-left-20)/values.length,max=Math.max(10,...values.map(r=>r.high))*1.2;
   const y=v=>H-bottom-v/max*(H-top-bottom);
   let svg=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${start}~${end}년 연도별 고온일수. 정확한 값은 아래 표에 있습니다."><title>연도별 고온일수</title>`;
   for(let i=0;i<=4;i++){let v=max*i/4;svg+=`<line x1="${left}" x2="980" y1="${y(v)}" y2="${y(v)}" stroke="#e3e8ee"/><text x="38" y="${y(v)+4}" text-anchor="end" fill="#596778" font-size="13">${v.toFixed(0)}</text>`;}
   values.forEach((r,i)=>{const x=left+space*i+space*.15,width=space*.7;svg+=`<rect x="${x}" y="${y(r.low)}" width="${width}" height="${y(0)-y(r.low)}" fill="${r.year<=2015?'#2563a6':'#d66036'}"/><text x="${x+width/2}" y="${y(r.high)-8}" text-anchor="middle" font-size="13" fill="#243447">${range(r.low,r.high)}</text><text x="${x+width/2}" y="${H-19}" text-anchor="middle" font-size="12" fill="#596778">${r.year}</text>`;});
   $('chart').innerHTML=svg+'</svg>';return {start,end,scope,threshold,annual:values};
 }
 for(const id of ['start','end','scope','threshold']) $(id).addEventListener('change',render);
 render();
 if(document.modelContext?.registerTool){try{Promise.resolve(document.modelContext.registerTool({name:'set_heat_filters',description:'창원 더위 대시보드의 기간과 고온 기준을 변경합니다.',inputSchema:{type:'object',properties:{start:{type:'integer',minimum:2006,maximum:2026},end:{type:'integer',minimum:2006,maximum:2026},threshold:{type:'integer',enum:[28,30,33]},scope:{type:'string',enum:['full','janaug']}},required:['start','end','threshold','scope'],additionalProperties:false},annotations:{readOnlyHint:false},execute(input){if(!input||!Number.isInteger(input.start)||!Number.isInteger(input.end)||input.start<2006||input.end>2026||input.start>input.end||![28,30,33].includes(input.threshold)||!['full','janaug'].includes(input.scope))throw new Error('분석 조건을 확인해주세요.');for(const key of ['start','end','threshold','scope'])$(key).value=String(input[key]);return render();}})).catch(()=>{});}catch{}}
}
