#!/usr/bin/env python3 -I
"""AppFolio checks on data/appfolio/bills/*.csv. Usage: analyze_appfolio.py OUT.json"""
import csv,glob,re,sys,json,collections
R=[]
for f in sorted(glob.glob('data/appfolio/bills/2026-*.csv')):
    for r in csv.DictReader(open(f)):
        r['m']=f[-11:-4];r['amt']=float(r['BILL_DETAIL_AMOUNT'] or 0);r['v']=(r['VENDOR_COMPANY_NAME'] or r['VENDOR_NAME']).strip();R.append(r)
nref=lambda s:re.sub(r'[\s#]','',s.lower())
F=collections.defaultdict(list)
# net out reversals: a line with status Unused/negative cancels an earlier identical positive
live=[r for r in R if r['BILL_DETAIL_STATUS']!='Unused' and r['amt']>0]
rev=collections.Counter()
for r in R:
    if r['amt']<0:
        m=re.search(r'Reverse bill\s*(\S+)',r['DESCRIPTION'])
        rev[(m.group(1).lower() if m else '',r['PROPERTY_NAME'],round(-r['amt'],2))]+=1
# duplicates: same bill ref on 2+ different BILL_IDs
B=collections.defaultdict(lambda:collections.defaultdict(list))
for r in live:
    k=nref(r['BILL_REFERENCE'])
    if k and re.search(r'\d{3}',k) and k!='copy' and r['v'] and not r['GL_NUMBER'].startswith(('6520','6525','6515','6140')): B[(k,r['v'])][r['BILL_ID']].append(r)
for (k,v),ids in B.items():
    if len(ids)>1:
        tots={i:round(sum(x['amt'] for x in l),2) for i,l in ids.items()}
        first=[l[0] for l in ids.values()]
        F['same_ref_two_bills'].append(dict(vendor=v,ref=first[0]['BILL_REFERENCE'],props=sorted({x['PROPERTY_NAME'] for x in first}),totals=tots,dates=[x['DATE'] for x in first],paid=[x['BILL_DETAIL_STATUS'] for x in first],same_total=len(set(tots.values()))==1))
# Uploaded Invoice vs work-order bill: same vendor+property+amount, one 7-char random ref, other numeric or -EX- (unreversed)
U=collections.defaultdict(list)
for r in live: U[(r['v'],r['PROPERTY_NAME'],round(r['amt'],2))].append(r)
for k,l in U.items():
    up=[x for x in l if re.fullmatch(r'T[A-Z0-9]{5,7}',x['BILL_REFERENCE'].strip()) and (rev[(x['BILL_REFERENCE'].lower(),x['PROPERTY_NAME'],x['amt'])]==0)]
    wo=[x for x in l if re.fullmatch(r'\d{6,8}',x['BILL_REFERENCE'].strip())]
    if up and wo and k[2]>0: F['uploaded_invoice_plus_workorder_bill'].append(dict(vendor=k[0],prop=k[1],amt=k[2],uploaded=[(x['BILL_REFERENCE'],x['DATE'],x['BILL_DETAIL_STATUS']) for x in up],workorder=[(x['BILL_REFERENCE'],x['DATE'],x['BILL_DETAIL_STATUS']) for x in wo]))
# same vendor+property+amount+description within month window (maintenance)
M=collections.defaultdict(list)
for r in live:
    if r['v'] and not r['GL_NUMBER'].startswith(('6520','6525','6515','6140','6125','7500','6130','6608','6620')) and r['amt']>0: M[(r['v'],r['PROPERTY_NAME'],round(r['amt'],2))].append(r)
for k,l in M.items():
    ids={x['BILL_ID'] for x in l}
    if len(ids)>1:
        l.sort(key=lambda x:x['DATE'])
        for a,b in zip(l,l[1:]):
            if a['BILL_ID']!=b['BILL_ID'] and a['DATE'][:7]==b['DATE'][:7] and nref(a['BILL_REFERENCE'])!=nref(b['BILL_REFERENCE']) : F['same_vendor_prop_amount_same_month'].append(dict(vendor=k[0],prop=k[1],amt=k[2],a=(a['BILL_REFERENCE'],a['DATE'],a['BILL_DETAIL_STATUS']),b=(b['BILL_REFERENCE'],b['DATE'],b['BILL_DETAIL_STATUS'])))
# markup pct (6620 'Markup:' lines vs vendor bill same ref)
V=collections.defaultdict(float);MK=collections.defaultdict(float);P={}
for r in live:
    k=nref(r['BILL_REFERENCE'])
    if not k: continue
    if r['DESCRIPTION'].startswith('Markup') and r['GL_NUMBER']=='6620': MK[k]+=r['amt'];P[k]=r
    elif r['GL_NUMBER']!='6620': V[k]+=r['amt']
F['markup_not_10pct']=[dict(ref=P[k]['BILL_REFERENCE'],prop=P[k]['PROPERTY_NAME'],vendor_amt=round(V[k],2),markup=round(m,2),pct=round(m/V[k]*100,1),status=P[k]['BILL_DETAIL_STATUS']) for k,m in MK.items() if V.get(k) and abs(m/V[k]-.1)>.01]
F['markup_pct_counts']=dict(collections.Counter(round(m/V[k]*100) for k,m in MK.items() if V.get(k)).most_common(8))
F['unpaid_live']=[dict(vendor=r['v'],prop=r['PROPERTY_NAME'],ref=r['BILL_REFERENCE'],amt=r['amt'],date=r['DATE']) for r in live if r['BILL_DETAIL_STATUS']=='Unpaid']
F['rows']={m:sum(1 for r in R if r['m']==m) for m in sorted({r['m'] for r in R})}
json.dump(F,open(sys.argv[1],'w'),indent=1)
print({k:(len(v) if isinstance(v,(list,dict)) else v) for k,v in F.items()})
