#!/usr/bin/env python3.13 -I
"""Write report .md, audit .xlsx, dashboard .html and baseline .json from findings.json. Usage: build_outputs.py DATE FINDINGS.json FULL.json"""
import json,sys,collections,html,datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
D,FP,FULL=sys.argv[1:4]
f=json.load(open(FP));F=json.load(open(FULL))
order={'Unpaid':0,'Part unpaid':1,'Paid/mixed':2,'Paid':3}
f.sort(key=lambda o:(o['sev']!='RED',order.get(o['paid'],3),o['check'],-o['amt']))
money=lambda x:f"${x:,.2f}"
red=[o for o in f if o['sev']=='RED'];yel=[o for o in f if o['sev']=='YELLOW']
unp=lambda L:[o for o in L if o['paid'] in('Unpaid','Part unpaid')]
s=lambda L:sum(o['amt'] for o in L)
DUPCHK=('4 Duplicate','3 Wrong','1 Renewal')
red_money=[o for o in red if o['check'][0] in '413' and o['check']!='3 Wrong building (account on >1 property)']
occ=[o for o in red if o['check'].startswith('5')]
INC=[ "AppFolio vendor BILLS (Check 3/4/5 for AppFolio) were NOT audited. Realm-X returns results only inline in chat (nothing can be saved to disk), so one-week-at-a-time pulls for Jan–Nov could not be assembled into a dataset. The July–Nov attempt got only partial weeks (07-22 to 08-18) with suspicious empty weeks; Jan–Jun was not delivered. Do not treat AppFolio bills as checked.",
"AppFolio renewal fees (Check 1) NOT checked: Realm-X returned 238 renewals (191 Renewed, 27 Canceled, 15 Did Not Renew, 3 Month-to-Month, 2 Pending) but cannot link a fee to a renewal.",
"Google Drive: folder 'Owner Statement Audit' was created, but the master sheet 'Bills YTD' (47,671 rows, 7.2 MB CSV) was NOT uploaded: the Drive connector rejects any single call over 4.2 MB. I did not split or work around the limit. Decision needed: allow splitting into monthly tabs/files, or upload data/bills/*.csv manually.",
"Water/sewer spike check (5b): only the trailing-3-month baseline was available (cache starts Jan 2026); the same-month-last-year baseline was NOT pulled, so no spike could be confirmed RED; all are YELLOW.",
"Check 1 renewal status verified in Rentvine for 4 of the 8 suspect units (plus OI-010); the other 4 match the same pattern but were not individually checked. 12 unpaid-renewal YELLOWs not individually verified.",
"Check 2 effective-rate review (fee vs scheduled rent) and Check 3 'first-time vendor over $500' were NOT run this time. Fee-setting NAME-vs-CONFIG and watch list were run.",
"Rentvine: all 11 months tie to the report headers (47,671 rows). Voided bills do not appear in the report, so 'caught and voided' could not be counted."]
months=F['months']
# ---------------- xlsx
wb=Workbook();ws=wb.active;ws.title='Summary'
rows=[['Owner Statement Audit',D,'RUN STATUS: INCOMPLETE'],[],['Data not completed']]+[[x] for x in INC]+[[],['Month','Rentvine rows','Amount']]+[[m,v[0],v[1]] for m,v in months.items()]
for r in rows: ws.append(r)
ws.column_dimensions['A'].width=120
def sheet(name,L):
    w=wb.create_sheet(name);hdr=['#','Severity','Check','Owner','Property','Unit','What is wrong','Vendor','Account','Reference','Amount','Bill date','Paid','Action','Group','Open item']
    w.append(hdr)
    for c in w[1]: c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='333333')
    for o in L: w.append([o['id'],o['sev'],o['check'],o['owner'],o['prop'],o['unit'],o['what'],o['vendor'],o['acct'],o['ref'],o['amt'],o['date'],o['paid'],o['action'],o['group'],o['oi']])
    w.freeze_panes='A2';w.auto_filter.ref=w.dimensions
    for col,wd in zip('ABCDEFGHIJKLMNOP',[6,9,34,26,28,22,70,24,24,18,11,11,10,44,14,10]): w.column_dimensions[col].width=wd
sheet('RED unpaid',unp(red));sheet('RED all',red);sheet('YELLOW',yel)
w=wb.create_sheet('Electric occupied');w.append(['Property','Unit','Vendor','Ref','Amount','Date','Paid','Who pays','Tenant'])
for x in F['electric_while_occupied']: w.append([', '.join(x['prop']),', '.join(x['unit']),x['payee'],x['ref'],x['amt'],x['date'],x['paid'],x['who_pays'],x['tenant']])
w=wb.create_sheet('Matching references');w.append(['Kind','Util','Same total','A prop','A amt','A date','A paid','B prop','B amt','B date','B paid','Vendor','Ref'])
for x in F['same_ref']: a,b=x['a'],x['b'];w.append([x['kind'],x['util'],x['same_total'],', '.join(a['prop']),a['amt'],a['date'],a['paid'],', '.join(b['prop']),b['amt'],b['date'],b['paid'],a['payee'],a['ref']])
w=wb.create_sheet('Utility refs diff months (skipped)');w.append(['Vendor','Ref','Prop','A amt','A date','B amt','B date'])
for x in F['util_ref_reuse_diff_months_NOT_FLAGGED']: a,b=x['a'],x['b'];w.append([a['payee'],a['ref'],', '.join(a['prop']),a['amt'],a['date'],b['amt'],b['date']])
w=wb.create_sheet('Markups');w.append(['Month','Ref','Property','Unit','Vendor','Vendor $','Markup $','Pct'])
for x in F['markup_pct']: w.append([x['m'],x['ref'],x['prop'],x['unit'],(x['payee'] or [''])[0],x['vendor_amt'],x['markup'],x['pct']])
wb.save(f'reports/{D}-audit.xlsx')
# ---------------- baseline
base=dict(date=D,status='INCOMPLETE',findings=[dict(sev=o['sev'],paid=o['paid'],prop=o['prop'],issue=o['what'][:200],ref=f"{o['ref']} {money(o['amt'])} {o['date']}",check=o['check']) for o in f],open_items=[f'OI-{i:03d}' for i in range(1,17)])
json.dump(base,open(f'reports/baseline-{D}.json','w'))
# ---------------- md
L=[]
A=L.append
A(f'# Owner Statement Audit — {D} (Monday FULL audit)\n')
A('## ⚠️ RUN STATUS: INCOMPLETE — read this first\n')
for x in INC: A(f'- {x}')
A('')
A(f"## Data status\nRentvine expense lines Jan–Nov: {sum(v[0] for v in months.values()):,} rows, {money(sum(v[1] for v in months.values()))}; every month ties to its report header (Jan 4,601 · Feb 4,048 · Mar 4,292 · Apr 4,384 · May 4,756 · Jun 4,300 · Jul 4,826 · Aug 4,270 · Sep 4,054 · Oct 4,613 · Nov 1–23 3,527). Properties 564, leases 1,622 and 55 active fee settings pulled. AppFolio: fee settings 688 properties (245 not 8%/10%) and 238 renewals pulled; AppFolio bills NOT audited.\n")
A('## Dollars at risk\n'+f"- RED unpaid (still fixable): {money(s(unp(red)))} across {len(unp(red))} items.\n- RED already paid — duplicates/renewal/wrong-building items (excl. occupied-utility bills): {money(s([o for o in red_money if o['paid'] not in ('Unpaid','Part unpaid')]))} across {len([o for o in red_money if o['paid'] not in ('Unpaid','Part unpaid')])} items (amount = the likely-extra copy).\n- RED paid — utility bills on occupied units (electric any who-pays; resident-pays water/sewer/gas/trash): {money(s([o for o in occ if o['paid']=='Paid']))} across {len([o for o in occ if o['paid']=='Paid'])} bills. Many may be legitimate owner costs; the rule flags every one.\n")
def line(o): 
    return f"- **{o['owner'][:30]} — {o['prop']}{', '+o['unit'] if o['unit'] and o['unit']!=o['prop'] else ''}** [{o['paid']}] {o['what']} | {o['vendor'][:28]} {o['acct'][:30]} ref {o['ref']} {money(o['amt'])} {o['date']} | Action: {o['action']}"+(f" ({o['oi']})" if o['oi'] else '')
A('## 🔴 RED — FIX TODAY (unpaid first)\n')
for o in unp(red): A(line(o))
A('\n### RED already paid (needs credit/void) — grouped; every item is in the spreadsheet (tab "RED all") and dashboard\n')
byc=collections.defaultdict(list)
for o in red:
    if o['paid'] not in('Unpaid','Part unpaid'): byc[o['check']].append(o)
for c,Lc in sorted(byc.items()):
    A(f"**{c}** — {len(Lc)} items, {money(s(Lc))}")
    if c.startswith('5'): 
        A('  - By month: '+', '.join(f"{m} {n}" for m,n in sorted(collections.Counter(o['date'][:7] for o in Lc).items())))
    else:
        for o in sorted(Lc,key=lambda o:-o['amt'])[:12]: A('  '+line(o))
A('\n## 🟡 YELLOW — PLEASE REVIEW\n')
for o in unp(yel): A(line(o))
yc=collections.defaultdict(list)
for o in yel:
    if o['paid'] not in('Unpaid','Part unpaid'): yc[o['check']].append(o)
A('\n### YELLOW paid / grouped\n')
for c,Lc in sorted(yc.items()): A(f"- **{c}** — {len(Lc)} items, {money(s(Lc))} (see spreadsheet tab YELLOW)")
mk=[o for o in yel if o['check']=='4 Markup not 10%']
A(f"\n**Markup program:** {len(mk)} markup bills are not 10%. {sum(1 for o in mk if o['group']=='20%')} are exactly 20% (Leo Landscaping 84, Tropical Air 29, Phoenix EZ-Keys 26, Dante Dimas 16, Cool Command 14, …); extra over 10% ≈ {money(s(mk))}. One at 40% (Tropical Air 1235448, 22828 S 214th St). One markup with no vendor bill (ref 1244703, 8585 W Santa Cruz Blvd $165). Markups started Aug/Sep 2026. Confirm the owners allow 20%.")
A('\n## 💧 POSSIBLE LEAKS / UTILITY SPIKES (all YELLOW: no last-year baseline)\n')
for o in yel:
    if o['check']=='5 Water/sewer spike': A(f"- {o['prop']} — {o['vendor']} acct {o['ref']}: {o['what']}")
A('\n**Utility duplicates (5c):** see RED "Duplicate / reused reference" and YELLOW "Duplicate (utility)". Utility refs repeated in different months were NOT flagged ('+str(len(F['util_ref_reuse_diff_months_NOT_FLAGGED']))+' pairs in spreadsheet tab).')
A('\n## 🔁 OPEN ITEMS STILL OPEN (first seen on/before 2026-10-01 → at least 53 days)\n')
OI=[('OI-001','960 N Jay St Aug sewer+water 8/1 and 8/10 ($86.00 each) both still posted and paid'),('OI-002','960 N Jay St May water 5/1 ($93.12 in 2 lines) and 5/11 ($93.12) still both posted'),('OI-003','960 N Jay St 9/25 $88.84 (20230825-00007604 9/26) now PAID; also note it equals the 4/8 water bill $88.84, and a new 10/26 bill $82.00 uses the same odd reference'),('OI-004','1750 E 6th Ave invoice 714121 $1,102.20 still posted twice'),('OI-005','APS 0727621137 still on 10919 W Carmelita (9/26 $9.49, 10/26 $240.05, 11/26 $69.68 UNPAID)'),('OI-006','SRP 176-370-106 5034 E Holmes: 9/22 $91.45 and 9/28 $20.75 both posted and paid'),('OI-007','TEST Property: SRP 961-089-003 $216.10 still UNPAID on TEST property; plus a new Repair Masters $100 (713556, 7/30) UNPAID on TEST Property'),('OI-008','SRP 569-479-000: $275.32 appears twice (8/26 on 9/9 and 9/26 on 9/15) with no property, plus 9/26 $144.87; all paid'),('OI-009','APS 0223612022: $183.01 (RRG reimbursement) and $41.52 still on no-property ledgers, paid'),('OI-010','Renewal #399 (lease 1267) still In Progress; $100 fee already paid'),('OI-011','Fee setting 46 still named $99 but configured $150'),('OI-012','Fee setting 49 still named $499 lease but configured $450'),('OI-013','AppFolio P20-005 Unit 1 10% / Unit 2 7.5% unchanged'),('OI-014','AppFolio Martha Beher P05-077 9% vs P21-023 8% unchanged'),('OI-015','AppFolio TEST-ONLY 1% and blank $1-flat record still Active (TEST MFR, TEST SFR, XX Corp are now Hidden)'),('OI-016','8580 W Monaco rekey #63809 markup still present; 10% upcharge not confirmed')]
for i,t in OI: A(f'- {i}: Open — {t}')
A('\n## ✅ RESOLVED SINCE LAST REPORT\n- None confirmed. The two Thatcher Gym/3333 W 8th duplicates flagged 11/16 (Rattlesnake 111472, B&D 057873) are now PAID, not voided. Cannataro 1267238 (two vendors) is still posted and paid. Farrell Ct SRP bills and Carmelita $69.68 are still unpaid.')
A('\n## 📋 WATCH LIST CHANGES\n- Rentvine fee settings: 20 settings are not 8%/10% (7%, 7.5%, 6%, 5%, 4%, 8.5%, flat fees). Setting 56 (name: 5% or $100 per unit, whichever greater) configured as 5% only — confirm the minimum is applied; setting 54 shows 20% renewal without the $450 minimum in config.\n- AppFolio: 245 of 688 not 8%/10% (32 flat). Items not previously listed: other Kocisko owners at 7.5% (P20-009, P20-015, P20-016, P20-019); Bluevolt Horizon Path LLC P26-006 $125 flat vs P26-007 10%; Raymond Minhoto P14-037 9% vs TF-2501 $1,800 flat; Royal Family Trust P21-031 B 8.5% and P23-003 9% among 8% properties; Ashley Dioso several 0%/$0 flat records. Full list: data/appfolio/fee-watchlist.md.')
A(f"\n## Counts\n- Findings (items): {len(red)} RED, {len(yel)} YELLOW. Counts are grouped ITEMS (a bill, a pair of bills or an account), not lines. Electric-while-occupied: {len(F['electric_while_occupied'])} bills ({money(sum(x['amt'] for x in F['electric_while_occupied']))}).\n- Known exceptions skipped: Summer Place Terrace HOA two-month bills, Inszone insurance, utility refs repeated across different months ({len(F['util_ref_reuse_diff_months_NOT_FLAGGED'])}), recurring monthly services (landscaping, pest, pool, HOA, taxes, inspections) excluded from the 30-day same-amount rule, Jan/Nov renewal pairs (two different terms).\n- Caught-and-voided: not countable (voided bills are not in the report).")
open(f'reports/{D}.md','w').write('\n'.join(L))
# ---------------- dashboard
data=json.dumps([{k:o[k] for k in('id','sev','check','owner','prop','unit','what','vendor','ref','amt','date','paid','action','oi')} for o in f]).replace('</','<\\/')
inc=''.join(f'<li>{html.escape(x)}</li>' for x in INC)
page=f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Owner Statement Audit</title>
<style>:root{{--bg:#f7f7f5;--fg:#1d1d1b;--mut:#666;--card:#fff;--red:#b3261e;--yel:#8a6100;--bd:#ddd}}@media(prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#161616;--fg:#eee;--mut:#aaa;--card:#222;--red:#ff8a80;--yel:#ffd54f;--bd:#444}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;padding:16px;max-width:1200px;margin:auto}}h1{{font-size:22px;margin:0 0 4px}}.warn{{border:2px solid var(--red);background:var(--card);padding:10px 14px;border-radius:8px;margin:12px 0}}.warn b{{color:var(--red)}}
.tiles{{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}}.tile{{background:var(--card);border:1px solid var(--bd);border-radius:8px;padding:10px 14px;cursor:pointer;min-width:150px}}.tile b{{font-size:22px;display:block}}
.bar{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}input,select{{padding:6px;border:1px solid var(--bd);border-radius:6px;background:var(--card);color:var(--fg)}}table{{width:100%;border-collapse:collapse;background:var(--card)}}th,td{{border-bottom:1px solid var(--bd);padding:6px 8px;text-align:left;vertical-align:top;font-size:13px}}th{{position:sticky;top:0;background:var(--card);cursor:pointer}}.R{{color:var(--red);font-weight:600}}.Y{{color:var(--yel);font-weight:600}}.wrap{{overflow-x:auto}}small{{color:var(--mut)}}</style></head><body>
<h1>Owner Statement Audit — {D}</h1><small>Monday full audit · Rentvine Jan 1–Nov 23 (47,671 lines, tied) · AppFolio fees only</small>
<div class=warn><b>RUN STATUS: INCOMPLETE.</b><ul>{inc}</ul></div>
<div class=tiles id=tiles></div>
<div class=bar><select id=sev><option value="">All severities</option><option>RED</option><option>YELLOW</option></select><select id=paid><option value="">Paid + unpaid</option><option value=U>Unpaid only</option><option>Paid</option></select><select id=chk><option value="">All checks</option></select><input id=q placeholder="Search property, vendor, ref, owner…" size=36><span id=cnt></span></div>
<div class=wrap><table><thead><tr><th>Sev</th><th>Check</th><th>Owner / property</th><th>What is wrong</th><th>Vendor · ref</th><th>$</th><th>Date</th><th>Paid</th><th>Action</th></tr></thead><tbody id=tb></tbody></table></div>
<script>const D={data};const $=i=>document.getElementById(i);const m=x=>'$'+x.toLocaleString(undefined,{{minimumFractionDigits:2,maximumFractionDigits:2}});
const un=o=>o.paid==='Unpaid'||o.paid==='Part unpaid';
[...new Set(D.map(o=>o.check))].sort().forEach(c=>{{const e=document.createElement('option');e.textContent=c;$('chk').appendChild(e)}});
const tiles=[['RED unpaid',D.filter(o=>o.sev==='RED'&&un(o)),()=>{{$('sev').value='RED';$('paid').value='U';$('chk').value=''}}],['RED paid',D.filter(o=>o.sev==='RED'&&!un(o)),()=>{{$('sev').value='RED';$('paid').value='Paid';$('chk').value=''}}],['YELLOW unpaid',D.filter(o=>o.sev==='YELLOW'&&un(o)),()=>{{$('sev').value='YELLOW';$('paid').value='U';$('chk').value=''}}],['YELLOW paid',D.filter(o=>o.sev==='YELLOW'&&!un(o)),()=>{{$('sev').value='YELLOW';$('paid').value='Paid';$('chk').value=''}}]];
tiles.forEach(([t,L,fn])=>{{const d=document.createElement('div');d.className='tile';d.innerHTML='<b>'+L.length+'</b>'+t+'<br><small>'+m(L.reduce((a,o)=>a+o.amt,0))+'</small>';d.onclick=()=>{{fn();r()}};$('tiles').appendChild(d)}});
function r(){{const q=$('q').value.toLowerCase(),s=$('sev').value,p=$('paid').value,c=$('chk').value;const L=D.filter(o=>(!s||o.sev===s)&&(!c||o.check===c)&&(!p||(p==='U'?un(o):!un(o)))&&(!q||JSON.stringify(o).toLowerCase().includes(q)));$('cnt').textContent=L.length+' items';
$('tb').innerHTML=L.slice(0,600).map(o=>'<tr><td class='+o.sev[0]+'>'+o.sev+'</td><td>'+o.check+'</td><td>'+esc(o.owner)+'<br><b>'+esc(o.prop)+'</b> '+esc(o.unit)+'</td><td>'+esc(o.what)+(o.oi?' <small>('+o.oi+')</small>':'')+'</td><td>'+esc(o.vendor)+'<br>'+esc(o.ref)+'</td><td>'+m(o.amt)+'</td><td>'+o.date+'</td><td>'+o.paid+'</td><td>'+esc(o.action)+'</td></tr>').join('')+(L.length>600?'<tr><td colspan=9>Showing first 600 of '+L.length+'. Narrow the filters or use the spreadsheet.</td></tr>':'')}}
function esc(s){{return String(s).replace(/[&<>]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]))}}
['sev','paid','chk'].forEach(i=>$(i).onchange=r);$('q').oninput=r;$('sev').value='RED';$('paid').value='U';r();</script></body></html>"""
open(f'reports/{D}-dashboard.html','w').write(page)
print(len(red),len(yel),len(unp(red)),round(s(unp(red)),2),len(page))
