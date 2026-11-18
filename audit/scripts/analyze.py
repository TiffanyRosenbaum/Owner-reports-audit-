#!/usr/bin/env python3 -I
"""Cross-month bill analysis on ALL cached months in data/bills/*.csv (YTD).
Usage: python3 -I audit/scripts/analyze.py [out.json]
Checks: tie-out totals, Check 4 duplicates across any months, accounts on >1 property,
markup % (expect 10%), electric list. Output JSON of findings for the report."""
import csv,glob,re,sys,json,collections,datetime as dt,os
A=lambda r:float(r['amt'].replace('$','').replace(',',''))
def load():
    out=[]
    for f in sorted(glob.glob('data/bills/*.csv')):
        rows=list(csv.reader(open(f)));i=[k for k,r in enumerate(rows) if r and r[0]=='Property Code'][0]
        for r in rows[i+1:]:
            if len(r)>=9 and r[0]!='Totals':
                out.append(dict(file=os.path.basename(f)[:7],prop=r[0],unit=r[1],payee=r[2],acct=r[3],ref=r[4],desc=r[5],amt=r[6],date=dt.datetime.strptime(r[7],'%m-%d-%Y').date(),paid=r[8]))
    return out
def nref(s): return re.sub(r'[\s#]','',s.lower())
def nacct(s):
    s=re.sub(r'\d{8}-','',s.lower()); s=re.sub(r'\s*\(?(\d{1,2}/\d{2}|[a-z]{3}-\d{2})\)?\s*$','',s); return re.sub(r'[\s#\-]|acct','',s)
D=load(); F=collections.defaultdict(list)
UTIL=('59501','59502','59503','59504','59506')
SKIP=('mortgage','loan','interest')
# exact ref reuse (any month), skip Markup pairs and generic refs, skip utility multi-line same date
by=collections.defaultdict(list)
for r in D:
    k=nref(r['ref'])
    if k and re.search(r'\d{4}',k) and not r['acct'].startswith('6600') and r['payee']!='Rosenbaum Realty Group': by[k].append(r)
for k,v in by.items():
    if len(v)<2: continue
    util=all(x['acct'][:5] in UTIL+('53026','59513','59514','59516','59517','59518') for x in v)
    if util and len({x['date'] for x in v})==1: continue   # one multi-line utility bill
    if util and len({nacct(x['ref'])+x['file'] for x in v})==len(v) and len({x['ref'] for x in v})==len(v): continue
    if any(w in (x['acct']+x['desc']).lower() for x in v for w in SKIP): continue
    pr={x['prop'] for x in v}; months={x['file'] for x in v}
    if len({x['date'] for x in v})==1 and len({x['payee'] for x in v})==1 and len(pr)>1: continue  # split
    F['same_ref'].append(dict(ref=v[0]['ref'],kind=('different months' if len(months)>1 else 'same month')+(', different properties' if len(pr)>1 else ''),lines=[(x['prop'],x['unit'],x['payee'],x['amt'],str(x['date']),x['paid']) for x in v]))
# same vendor+property+amount within 30 days (maintenance, not utility/fees)
M=collections.defaultdict(list)
for r in D:
    if not r['acct'][:5] in UTIL and r['payee']!='Rosenbaum Realty Group' and not r['acct'].startswith(('55750','55752')): M[(r['payee'],r['prop'],r['unit'])].append(r)
for k,v in M.items():
    v.sort(key=lambda x:x['date'])
    for a,b in zip(v,v[1:]):
        if abs(A(a)-A(b))<=1 and (b['date']-a['date']).days<=30 and a['ref']!=b['ref'] and A(a)>0: F['same_vendor_prop_amount_30d'].append([k,a['ref'],b['ref'],a['amt'],str(a['date']),str(b['date']),b['paid']])
# utility account on >1 property
P=collections.defaultdict(set)
for r in D:
    if r['acct'][:5] in UTIL and r['ref'] and r['prop']: P[(r['payee'],nacct(r['ref']))].add(r['prop'])
F['account_on_multiple_properties']=[[list(k),sorted(v)] for k,v in P.items() if len(v)>1 and len(k[1])>5]
# markup %
vend=collections.defaultdict(float);mk=collections.defaultdict(float)
for r in D:
    if r['ref']:
        (mk if r['acct'].startswith('6600') else vend)[(r['file'],nref(r['ref']))]+= A(r) if (r['acct'].startswith('6600') or r['payee']!='Rosenbaum Realty Group') else 0
F['markup_not_10pct']=[[k,round(m,2),round(vend[k],2)] for k,m in mk.items() if k in vend and vend[k] and abs(m-vend[k]*.1)>.02]
F['markup_without_vendor_bill']=[k for k in mk if k not in vend]
F['months_loaded']={m:(sum(1 for r in D if r['file']==m),round(sum(A(r) for r in D if r['file']==m),2)) for m in sorted({r['file'] for r in D})}
json.dump(F,open(sys.argv[1] if len(sys.argv)>1 else '/dev/stdout','w'),indent=1,default=str)
print({k:(len(v) if isinstance(v,(list,dict)) else v) for k,v in F.items()},file=sys.stderr)
