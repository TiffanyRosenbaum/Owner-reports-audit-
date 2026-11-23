#!/usr/bin/env python3 -I
"""Full YTD analysis (Mon run). Bill-level (all lines of a bill summed) checks on ALL cached months.
Usage: python3 -I audit/scripts/analyze_full.py PROPS.csv LEASES.csv OUT.json [AF_BILLS.csv ...]
PROPS/LEASES are the Rentvine property / lease report CSV exports (see RENTVINE_DATA.md)."""
import csv,glob,re,sys,json,collections,datetime as dt,os
sys.argv=[sys.argv[0]]+sys.argv[1:]
PROPS,LEASES,OUT=sys.argv[1:4]
A=lambda s:float(s.replace('$','').replace(',','')) if s.strip() else 0.0
def nref(s): return re.sub(r'[\s#]','',s.lower())
def nacct(s):
    s=re.sub(r'\d{8}-','',s.lower()); s=re.sub(r'\s*\(?(\d{1,2}/\d{2}|[a-z]{3}-\d{2})\)?\s*$','',s); return re.sub(r'[\s#\-]|acct','',s)
def D8(s):
    try: return dt.datetime.strptime(s,'%m-%d-%Y').date()
    except: return None
def table(p,key):
    r=list(csv.reader(open(p)));h=[i for i,x in enumerate(r) if x and x[0]==key][0]; return r[h],[x for x in r[h+1:] if x and x[0]!='Totals']
rows=[]
for f in sorted(glob.glob('data/bills/*.csv')):
    h,R=table(f,'Property Code')
    for r in R:
        if len(r)>=9: rows.append(dict(m=os.path.basename(f)[:7],prop=r[0],unit=r[1],payee=r[2],acct=r[3],ref=r[4],desc=r[5],amt=A(r[6]),date=D8(r[7]),paid=r[8]=='Yes'))
ph,P=table(PROPS,'Property ID');lh,L=table(LEASES,'Property Code')
PR={x[1]:dict(id=x[0],active=x[2]=='Yes',cb=D8(x[3]),ce=D8(x[4]),fee=x[5],owner=x[6],portfolio=x[7],units=x[8],pay=dict(elec=x[9],water=x[10],gas=x[11],sewer=x[12],trash=x[13])) for x in P}
LS=collections.defaultdict(list)
for x in L:
    LS[(x[0],x[1])].append(dict(tenants=x[2],mi=D8(x[3]),st=D8(x[4]),en=D8(x[5]),oe=D8(x[6]),pls=x[7],ls=x[8],rent=A(x[9]) if x[9] else 0))
F=collections.defaultdict(list)
UT={'59501':'elec','59502':'gas','59503':'sewer','59504':'trash','59506':'water'}
UTX=tuple(UT)+('59513','59514','59516','59517','59518','53026')
isutil=lambda r:r['acct'][:5] in UTX
RRG='Rosenbaum Realty Group'
vendor=[r for r in rows if r['payee']!=RRG and not r['acct'].startswith(('55750','55752'))]
# ---- bills (all lines of same ref+payee+date)
GEN=re.compile(r'(?i)[a-z\s\-/]*(20\d\d)?')
generic=lambda ref: bool(re.fullmatch(r'(?i)[a-z\s\-/&]+\s*(20\d\d)?',ref.strip()))
B=collections.defaultdict(list)
for r in vendor:
    if r['ref']: B[(nref(r['ref']),r['payee'],r['date'])].append(r)
def tot(v): return round(sum(x['amt'] for x in v),2)
def props(v): return sorted({x['prop'] for x in v if x['prop']})
byref=collections.defaultdict(list)
for k,v in B.items():
    if re.search(r'\d{4}',k[0]) and not generic(v[0]['ref']) and not any(w in (x['acct']+x['desc']).lower() for x in v for w in('mortgage','loan','interest','markup')): byref[(k[0],k[1])].append((k[2],v))
def row(v): return dict(prop=props(v),unit=sorted({x['unit'] for x in v if x['unit']}),payee=v[0]['payee'],acct=sorted({x['acct'] for x in v}),ref=v[0]['ref'],amt=tot(v),date=str(v[0]['date']),paid='Yes' if all(x['paid'] for x in v) else ('Partly' if any(x['paid'] for x in v) else 'No'),lines=len(v),desc=v[0]['desc'][:80])
for (k,payee),bl in byref.items():
    if len(bl)<2: continue
    bl.sort(key=lambda t:t[0])
    for (d1,v1),(d2,v2) in zip(bl,bl[1:]):
        util=all(isutil(x) for x in v1+v2)
        sameprop=set(props(v1))==set(props(v2)) or not props(v1) or not props(v2)
        kind='same month' if (d1.year,d1.month)==(d2.year,d2.month) else 'different months'
        if len(set(props(v1)+props(v2)))>1: kind+=', different properties'
        rec=dict(kind=kind,util=util,same_total=abs(tot(v1)-tot(v2))<=1.0,a=row(v1),b=row(v2))
        if util and kind.startswith('different months'): F['util_ref_reuse_diff_months_NOT_FLAGGED'].append(rec); continue
        F['same_ref'].append(rec)
# duplicate lines inside one bill (identical acct+amt repeated, same ref/date)
for k,v in B.items():
    c=collections.Counter((x['acct'],x['amt'],x['prop']) for x in v)
    for (a,m,p),n in c.items():
        if n>1 and m>0 and not isutil(v[0]) : F['repeated_line_in_bill'].append(dict(row(v),repeat=n,line_amt=m,acct1=a))
# same ref used by DIFFERENT payees (non-utility)
byref2=collections.defaultdict(list)
for k,v in B.items():
    if re.search(r'\d{4}',k[0]) and not generic(v[0]['ref']) and not isutil(v[0]) and not v[0]['acct'].startswith(('6600',)): byref2[k[0]].append(v)
for k,l in byref2.items():
    if len({v[0]['payee'] for v in l})>1:
        F['same_ref_different_payees'].append(dict(ref=l[0][0]['ref'],bills=[row(v) for v in l]))
# same bill posted on two ledgers: identical acct+amount lines, one with blank property
for k,v in B.items():
    c=collections.defaultdict(list)
    for x in v: c[(x['acct'],x['amt'])].append(x)
    for (a,m),l in c.items():
        if len(l)>1 and m>0 and len({x['prop'] for x in l})>1 and not isutil(l[0]): F['posted_on_two_ledgers'].append(dict(row(v),line_amt=m,props_seen=sorted({x['prop'] or '(blank ledger)' for x in l})))
# maintenance same vendor+property+amount within 30d, different ref
M=collections.defaultdict(list)
for k,v in B.items():
    if not isutil(v[0]) and not v[0]['acct'].startswith(('6600','43')): M[(v[0]['payee'],tuple(props(v)),tuple(sorted({x['unit'] for x in v})))].append((v[0]['date'],v))
for k,l in M.items():
    l.sort(key=lambda t:t[0])
    for (d1,v1),(d2,v2) in zip(l,l[1:]):
        if (d2-d1).days<=30 and abs(tot(v1)-tot(v2))<=1 and tot(v1)>0 and nref(v1[0]['ref'])!=nref(v2[0]['ref']): F['same_vendor_prop_amount_30d'].append(dict(a=row(v1),b=row(v2)))
        elif (d2-d1).days<=30 and tot(v1)>0 and tot(v2)>0 and abs(tot(v1)-tot(v2))>1 and k[1] and k[2] and v1[0]['desc'].strip().lower()==v2[0]['desc'].strip().lower() and nref(v1[0]['ref'])!=nref(v2[0]['ref']): F['same_vendor_unit_same_work_30d_diff_amount'].append(dict(a=row(v1),b=row(v2)))
# utility: same account+property, two bills in same service month
U=collections.defaultdict(list)
for k,v in B.items():
    if v[0]['acct'][:5] in UT and v[0]['ref']: U[(v[0]['payee'],nacct(v[0]['ref']))].append((k[2],v))
accts={}
for k,l in U.items():
    l.sort(key=lambda t:t[0])
    for (d1,v1),(d2,v2) in zip(l,l[1:]):
        tag=lambda v:re.search(r'(\d{1,2}/\d{2}|[A-Za-z]{3}-\d{2})\s*$',v[0]['ref'].strip())
        t1,t2=tag(v1),tag(v2)
        if t1 and t2 and t1.group(1)==t2.group(1) and v1[0]['ref'].strip()!=v2[0]['ref'].strip() or (t1 and t2 and t1.group(1)==t2.group(1) and (d1,v1)[0]!=(d2,v2)[0]):
            F['utility_same_account_same_month_tag'].append(dict(same_total=abs(tot(v1)-tot(v2))<=1,a=row(v1),b=row(v2)))
# check 3: account on multiple properties
AP=collections.defaultdict(lambda:collections.defaultdict(set))
for r in rows:
    if r['acct'][:5] in UT and r['ref'] and r['prop'] and r['payee']!=RRG: AP[(r['payee'],nacct(r['ref']))][r['m']].add(r['prop'])
for k,mm in AP.items():
    if len(k[1])<6: continue
    allp=set().union(*mm.values())
    if len(allp)>1: F['account_on_multiple_properties'].append(dict(payee=k[0],acct=k[1],by_month={m:sorted(p) for m,p in sorted(mm.items())},same_month=any(len(p)>1 for p in mm.values())))
# TEST / inactive / out-of-contract / blank property
for r in rows:
    if r['prop'] and 'TEST' in r['prop'].upper() and r['payee']!=RRG: F['bill_on_TEST_property'].append(dict(m=r['m'],prop=r['prop'],payee=r['payee'],acct=r['acct'],ref=r['ref'],amt=r['amt'],date=str(r['date']),paid=r['paid']))
    p=PR.get(r['prop'])
    if p and r['payee']!=RRG and not r['acct'].startswith(('55750','55752')):
        if not p['active']: F['bill_on_inactive_property'].append(dict(m=r['m'],prop=r['prop'],payee=r['payee'],acct=r['acct'],ref=r['ref'],amt=r['amt'],date=str(r['date']),paid=r['paid']))
        elif (p['cb'] and r['date']<p['cb']) or (p['ce'] and r['date']>p['ce']): F['bill_outside_contract'].append(dict(m=r['m'],prop=r['prop'],cb=str(p['cb']),ce=str(p['ce']),payee=r['payee'],acct=r['acct'],ref=r['ref'],amt=r['amt'],date=str(r['date']),paid=r['paid']))
    if not r['prop'] and r['payee']!=RRG: F['bill_no_property'].append(dict(m=r['m'],payee=r['payee'],acct=r['acct'],ref=r['ref'],amt=r['amt'],date=str(r['date']),paid=r['paid'],desc=r['desc'][:60]))
# first-time vendor on property >$500
seen=collections.defaultdict(list)
for r in sorted(vendor,key=lambda r:r['date']): seen[(r['payee'],r['prop'])].append(r)
# (first appearance in YTD data this month)
# check 5 occupancy
def occupied(prop,unit,d):
    for key in ((prop,unit),)+tuple((prop,u) for (p,u) in LS if p==prop and not unit):
        for l in LS.get(key,[]):
            if l['pls']=='Pending' or l['ls']=='Pending': continue
            s=l['mi'] or l['st']
            if not s or s>d: continue
            e=l['oe'] or (l['en'] if l['ls'].startswith('Closed') else None)
            if e is None or e>=d: return l
    return None
for k,v in B.items():
    r0=v[0]
    if r0['acct'][:5] not in UT: continue
    kind=UT[r0['acct'][:5]]; d=r0['date']
    p=PR.get(r0['prop']); unitkey=r0['unit']
    multi=p and p['units'].isdigit() and int(p['units'])>1
    l=occupied(r0['prop'],r0['unit'] or r0['prop'],d) if (r0['unit'] or not multi) else None
    pay=p['pay'][kind] if p else '?'
    rec=dict(row(v),kind=kind,who_pays=pay,tenant=(l['tenants'] if l else ''),multi=bool(multi),unit_on_bill=bool(r0['unit']))
    if kind=='elec':
        if l: F['electric_while_occupied'].append(rec)
        elif multi and not r0['unit']: F['electric_multiunit_unit_unknown'].append(rec)
    if pay=='Resident pays':
        if l: F['resident_pays_but_occupied_billed_to_owner'].append(rec)
        elif multi and not r0['unit']: F['resident_pays_multiunit_unit_unknown'].append(rec)
        elif not l: F['resident_pays_no_resident_found'].append(rec)
    if pay=='' : F['who_pays_blank'].append(rec)
# spikes
S=collections.defaultdict(lambda:collections.defaultdict(float));SP={}
for r in vendor:
    if r['acct'][:5] in('59506','59503','59513','59514','59516','59517','59518') and r['ref'] and r['prop']:
        k=(r['payee'],nacct(r['ref'])); S[k][r['m']]+=r['amt']; SP[k]=r['prop']
for k,mm in S.items():
    ms=sorted(mm)
    if len(ms)<4: continue
    last=ms[-1]
    if last=='2026-11': ms=ms[:-1]  # partial month
    if len(ms)<4: continue
    last=ms[-1];prev=[mm[m] for m in ms[-4:-1]]
    avg=sum(prev)/3
    if avg>20 and mm[last]>avg*1.25: F['water_sewer_spike'].append(dict(payee=k[0],acct=k[1],prop=SP[k],month=last,total=round(mm[last],2),trailing3=round(avg,2),pct=round((mm[last]/avg-1)*100),history={m:round(mm[m],2) for m in ms}))
# markups
vsum=collections.defaultdict(float);msum=collections.defaultdict(float);mi={}
for r in rows:
    if not r['ref']: continue
    k=(r['m'],nref(r['ref']))
    if r['acct'].startswith('6600'): msum[k]+=r['amt']; mi[k]=r
    elif r['payee']!=RRG: vsum[k]+=r['amt']; mi.setdefault(k,r)
F['markup_pct']=[dict(m=k[0],ref=mi[k]['ref'],prop=mi[k]['prop'],unit=mi[k]['unit'],paid=mi[k]['paid'],payee=[x['payee'] for x in vendor if x['m']==k[0] and nref(x['ref'])==k[1]][:1],vendor_amt=round(vsum[k],2),markup=round(m,2),pct=round(m/vsum[k]*100,1)) for k,m in msum.items() if vsum.get(k)]
F['markup_without_vendor_bill']=[dict(m=k[0],ref=mi[k]['ref'],prop=mi[k]['prop'],amt=round(m,2),paid=mi[k]['paid']) for k,m in msum.items() if not vsum.get(k)]
# renewals
RN=collections.defaultdict(list)
for r in rows:
    if r['payee']==RRG and (r['acct'].startswith('5649') or 'renew' in r['desc'].lower()) and r['amt']>0: RN[(r['prop'],r['unit'])].append(r)
for k,v in RN.items():
    if len(v)>1: F['renewal_unit_multiple'].append(dict(prop=k[0],unit=k[1],lines=[(str(x['date']),x['amt'],'Yes' if x['paid'] else 'No') for x in v]))
F['renewal_unpaid']=[dict(prop=k[0],unit=k[1],date=str(x['date']),amt=x['amt']) for k,v in RN.items() for x in v if not x['paid']]
F['renewal_total_lines']=sum(len(v) for v in RN.values())
F['months']={m:(sum(1 for r in rows if r['m']==m),round(sum(r['amt'] for r in rows if r['m']==m),2)) for m in sorted({r['m'] for r in rows})}
F['props_with_fee']={p:v['fee'] for p,v in PR.items() if v['active']}
json.dump(F,open(OUT,'w'),indent=1,default=str)
print({k:(len(v) if isinstance(v,(list,dict)) else v) for k,v in F.items() if k!='props_with_fee'},file=sys.stderr)
