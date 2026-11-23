#!/usr/bin/env python3 -I
"""Turn analyze_full.py JSON into a ranked findings list (findings.json). Usage: build_findings.py FULL.json PROPS.csv OUT.json"""
import json,csv,sys,collections,re
F=json.load(open(sys.argv[1]))
r=list(csv.reader(open(sys.argv[2])));h=[i for i,x in enumerate(r) if x and x[0]=='Property ID'][0]
OWN={x[1]:x[6] for x in r[h+1:]}
out=[];n=[0]
def owner(p): 
    p=p if isinstance(p,str) else (p[0] if p else '')
    return OWN.get(p,'(ledger / no property)')
def add(sev,check,prop,unit,what,vendor,acct,ref,amt,date,paid,action,group='',oi=''):
    n[0]+=1;p=prop if isinstance(prop,str) else ', '.join(prop) if prop else ''
    u=unit if isinstance(unit,str) else ', '.join(unit) if unit else ''
    out.append(dict(id=n[0],sev=sev,check=check,owner=owner(prop),prop=p,unit=u,what=what,vendor=vendor,acct=acct if isinstance(acct,str) else '; '.join(acct),ref=ref,amt=round(amt,2),date=date,paid=paid,action=action,group=group,oi=oi))
OIREF={'00007604':'OI-001/002/003','0727621137':'OI-005','176-370-106':'OI-006','569-479-000':'OI-008','714121':'OI-004','0223612022':'OI-009','961-089-003':'OI-007'}
def oi(ref):
    for k,v in OIREF.items():
        if k in ref: return v
    return ''
def pd(a,b): 
    s={a['paid'],b['paid']}; return 'Paid' if s=={'Yes'} else ('Unpaid' if 'No' in s and 'Yes' not in s else 'Part unpaid')
# --- RED: reference reuse / duplicates
for x in F['same_ref']:
    a,b=x['a'],x['b']
    if 'Summer Place' in a['payee']: continue
    if x['util'] and not x['same_total'] and not x['kind'].startswith('same month, diff'):
        add('YELLOW','4 Duplicate (utility)',b['prop'] or a['prop'],b['unit'] or a['unit'],f"Utility account has two bills for the same month tag at different amounts: {a['amt']} ({a['date']}) and {b['amt']} ({b['date']}). Compare service dates.",a['payee'],b['acct'],b['ref'],b['amt'],b['date'],pd(a,b),'Compare to the utility statement; one may be a partial/corrected bill.',oi=oi(b['ref']));continue
    kind=x['kind']
    what=f"Reference {b['ref']} appears on two bills ({kind}): {a['amt']} on {a['date']} and {b['amt']} on {b['date']}"+(' — same total' if x['same_total'] else ' — different totals')
    add('RED','4 Duplicate / reused reference',b['prop'] or a['prop'],b['unit'] or a['unit'],what,a['payee'],b['acct'],b['ref'],(b['amt'] if x['same_total'] else b['amt']),b['date'],pd(a,b),'Compare to the vendor invoice; void the duplicate and credit the owner if both were paid.' if pd(a,b)!='Unpaid' else 'Void one copy before payment.',group=kind,oi=oi(b['ref']))
# repeated lines in a bill
for x in F['repeated_line_in_bill']:
    if 'Summer Place' in x['payee'] or 'Inszone' in x['payee']: continue
    sev='RED' if '714121' in x['ref'] else 'YELLOW'
    add(sev,'4 Duplicate (lines in one bill)',x['prop'],x['unit'],f"Bill has the same {x['acct1']} line (${x['line_amt']:,.2f}) {x['repeat']} times. May be two real items or one posted twice.",x['payee'],x['acct1'],x['ref'],x['line_amt']*(x['repeat']-1),x['date'],'Paid' if x['paid']=='Yes' else 'Unpaid','Compare to invoice.',oi=oi(x['ref']))
# maintenance same vendor+property+amount (recurring services removed)
REC=('55000','57500','54011','59508','59254','53010','5008','55500','50500','59509','59507')
for x in F['same_vendor_prop_amount_30d']:
    a,b=x['a'],x['b']
    if any(c.startswith(REC) for c in b['acct']): continue
    add('RED','4 Duplicate (same vendor/property/amount within 30 days)',b['prop'],b['unit'],f"Same vendor, property/unit and amount (${b['amt']:,.2f}) on {a['date']} (ref {a['ref']}) and {b['date']} (ref {b['ref']}).",b['payee'],b['acct'],b['ref'],b['amt'],b['date'],pd(a,b),'Confirm two separate jobs; otherwise void one.')
for x in F['same_ref_different_payees']:
    b=x['bills']; 
    add('RED','4 Duplicate / reused reference',b[0]['prop'],b[0]['unit'],'Reference '+x['ref']+' used by different vendors: '+'; '.join(f"{y['payee']} ${y['amt']:,.2f} ({y['date']})" for y in b),b[0]['payee']+' / '+b[-1]['payee'],b[0]['acct'],x['ref'],min(y['amt'] for y in b),b[-1]['date'],'Paid' if all(y['paid']=='Yes' for y in b) else 'Unpaid','Confirm both jobs happened; void the wrong one.',group='different vendors')
TG=[x for x in F['posted_on_two_ledgers'] if '3333 W 8th' in ' '.join(x['props_seen']) and '(blank ledger)' in x['props_seen']]
if TG:
    add('RED','4 Duplicate (posted on two ledgers)','3333 W 8th / blank (Thatcher Gym) ledger','',f"{len(TG)} invoices (Jan–Nov) have an identical line posted on BOTH the blank owner/company ledger and 3333 W 8th (e.g. "+', '.join(f"{x['payee'][:18]} {x['ref']} ${x['line_amt']:,.2f}" for x in TG[-3:])+"). Seen on 11/16 for Rattlesnake 111472 and B&D 057873; both are now PAID, not voided. Could be an intended split, but equal amounts on both ledgers look like double posting.",'various (Rattlesnake, B&D, NexLvl, Sparklight, ...)','various','see Bills YTD sheet',sum(x['line_amt'] for x in TG),max(x['date'] for x in TG),'Paid','Confirm with accounting whether each is a split; void duplicates and credit the owner.',group='two ledgers')
for x in [y for y in F['posted_on_two_ledgers'] if y not in TG]:
    add('RED','4 Duplicate (posted on two ledgers)','/'.join(x['props_seen']),x['unit'],f"Same invoice line (${x['line_amt']:,.2f}) posted on two ledgers: {', '.join(x['props_seen'])}.",x['payee'],x['acct'],x['ref'],x['line_amt'],x['date'],x['paid'] if x['paid']!='Yes' else 'Paid','Void one copy.',group='two ledgers')
# TEST property
for x in F['bill_on_TEST_property']:
    add('RED','3 Wrong building (TEST property)',x['prop'],'',f"Real vendor bill on TEST Property.",x['payee'],x['acct'],x['ref'],x['amt'],x['date'],'Paid' if x['paid'] else 'Unpaid','Find the correct property and move the bill.',oi=oi(x['ref']))
# accounts on multiple properties
for x in F['account_on_multiple_properties']:
    ms=x['by_month']
    txt='; '.join(f"{m}: {', '.join(p)}" for m,p in list(ms.items())[-6:])
    add('RED','3 Wrong building (account on >1 property)',sorted(set().union(*ms.values()))[:3],'',f"{'Billed to two properties in the SAME month. ' if x['same_month'] else 'Account moved between properties. '}Recent: {txt}",x['payee'],'',x['acct'],0,'', 'Paid/mixed','Confirm which property owns the account; move or credit mis-posted bills.',group='same month' if x['same_month'] else 'moved',oi=oi(x['acct']))
# electric / resident pays
def occ(sev,check,x,txt,act):
    add(sev,check,x['prop'],x['unit'],txt,x['payee'],x['acct'],x['ref'],x['amt'],x['date'],'Paid' if x['paid']=='Yes' else 'Unpaid',act,group=x['kind'])
for x in F['electric_while_occupied']:
    occ('RED','5 Electric while occupied',x,f"Electric bill while unit occupied (tenant: {x['tenant'][:40]}); who-pays: {x['who_pays'] or 'BLANK'}.",'Hold if unpaid; confirm the resident is responsible and bill them; reimburse owner if paid in error.')
for x in F['resident_pays_but_occupied_billed_to_owner']:
    if x['kind']=='elec' : continue
    occ('RED','5 Resident-pays utility billed to owner',x,f"{x['kind'].title()} is 'Resident pays' and the unit is occupied ({x['tenant'][:40]}).",'Bill the resident / reimburse owner.')
for x in F['electric_multiunit_unit_unknown']:
    occ('YELLOW','5 Electric, multi-unit, unit not on bill',x,f"Electric bill on a multi-unit property with no unit on the bill; who-pays: {x['who_pays'] or 'BLANK'}.",'Identify the unit/meter; confirm whose bill it is.')
for x in F['resident_pays_multiunit_unit_unknown']:
    occ('YELLOW','5 Resident-pays utility, multi-unit, unit unknown',x,f"{x['kind'].title()} 'Resident pays' on multi-unit property; unit not on bill.",'Identify unit; confirm occupancy.')
for x in F['resident_pays_no_resident_found']:
    occ('YELLOW','5 Resident-pays utility, no resident found',x,f"{x['kind'].title()} 'Resident pays' but no resident on the lease report for this date (vacant?).",'Verify vacancy; vacant utilities are owner cost.')
for x in F['water_sewer_spike']:
    sev='RED' if False else 'YELLOW'
    add(sev,'5 Water/sewer spike',x['prop'],'',f"{x['month']} total ${x['total']:,.2f} vs trailing-3-month average ${x['trailing3']:,.2f} (+{x['pct']}%). LAST-YEAR baseline not available in cache, so cannot confirm 'both baselines'.",x['payee'],'',x['acct'],x['total'],x['month'],'Paid','Send maintenance to check for a leak if +50%; compare to statement.')
# markups
for x in F['markup_pct']:
    p=x['pct']
    if abs(p-10)<=.5: continue
    vend=x['payee'][0] if x['payee'] else ''
    add('YELLOW','4 Markup not 10%',x['prop'],x['unit'],f"Markup is {p}% of the vendor bill (vendor ${x['vendor_amt']:,.2f}, markup ${x['markup']:,.2f}); expected 10%.",vend,'6600: Vendor Markup Expense',x['ref'],x['markup']-x['vendor_amt']*.1,x['m'],'Paid' if x['paid'] else 'Unpaid','Confirm the owner allows an upcharge above 10% for this vendor.',group=f'{round(p)}%',oi='')
for x in F['markup_without_vendor_bill']:
    add('YELLOW','4 Markup without vendor bill',x['prop'],'',f"Markup bill with no matching vendor bill in the same month.",'Rosenbaum Realty Group','6600: Vendor Markup Expense',x['ref'],x['amt'],x['m'],'Paid' if x['paid'] else 'Unpaid','Find the vendor bill or void the markup.')
# renewals
for x in [("410 E 9th Ave","Unit 4",'2026-05-21','2026-10-22',200),("9230 N. 6th St.","Unit 8",'2026-06-19','2026-10-22',200),("4401 E Contessa St","Unit 2",'2026-07-20','2026-10-22',374.75),("97th Place","97th Place",'2026-07-20','2026-10-22',200),("Pueblo Dr 9 unit Property","1012",'2026-07-24','2026-10-22',200),("1718 E 6th Ave","1732",'2026-07-28','2026-10-22',200),("960 N Jay St","960 N Jay St Apt C",'2026-07-28','2026-10-22',200),("312 E Vine Cir","312 E Vine Cir Apt 202",'2026-07-30','2026-10-22',200)]:
    ver=x[0] in ('410 E 9th Ave','9230 N. 6th St.','97th Place','312 E Vine Cir')
    add('RED','1 Renewal fee',x[0],x[1],f"Two renewal fees for the same renewal term (9/1/26–8/31/27): ${x[4]:,.2f} on {x[2]} and again on {x[3]}. "+("Verified in Rentvine: only ONE renewal exists for that term (Complete)." if ver else "Same pattern as the verified units; renewal list not individually checked."),'Rosenbaum Realty Group','5649: Lease Renewal Fee Expense','',x[4],x[3],'Paid','Reverse the second renewal fee and credit the owner.',group='batch 10/22')
add('RED','1 Renewal fee','2515 S Pantano Pkwy Units 1-3','Unit 1','Renewal fee charged while renewal #399 is still In Progress (re-verified today).','Rosenbaum Realty Group','5649: Lease Renewal Fee Expense','',100,'2026-09-02','Paid','Mark the renewal Complete or reverse the fee.',oi='OI-010')
for x in F['renewal_unpaid']:
    add('YELLOW','1 Renewal fee',x['prop'],x['unit'],'Unpaid renewal fee; renewal status not individually verified in this run.','Rosenbaum Realty Group','5649: Lease Renewal Fee Expense','',x['amt'],x['date'],'Unpaid','Confirm renewal is Complete before paying.')
# property status / contract
for x in F['bill_on_inactive_property']:
    if x['m']>='2026-10': add('YELLOW','3 Wrong building (inactive property)',x['prop'],'','Bill posted to an inactive property.',x['payee'],x['acct'],x['ref'],x['amt'],x['date'],'Paid' if x['paid'] else 'Unpaid','Confirm the property should still be billed.')
for x in F['bill_outside_contract']:
    if x['m']>='2026-09' and x['prop']: add('YELLOW','3 Wrong building (outside contract dates)',x['prop'],'',f"Bill dated {x['date']} outside contract {x['cb']} to {x['ce']}.",x['payee'],x['acct'],x['ref'],x['amt'],x['date'],'Paid' if x['paid'] else 'Unpaid','Confirm contract status.')
for x in F['bill_no_property']:
    if x['m']>='2026-10': add('YELLOW','3 No property on bill',[],'',f"Bill has no property code ({x['desc']}). May be an owner/company/tenant ledger.",x['payee'],x['acct'],x['ref'],x['amt'],x['date'],'Paid' if x['paid'] else 'Unpaid','Resolve the ledger (owner/company/tenant).')
json.dump(out,open(sys.argv[3],'w'),indent=1)
c=collections.Counter((o['sev'],o['paid']) for o in out);print(len(out),c)
