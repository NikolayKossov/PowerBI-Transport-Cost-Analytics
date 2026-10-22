"""Offline data/model checks; deliberately does not claim execution of DAX or M."""
from pathlib import Path
import csv, json, math, sqlite3, datetime as dt

ROOT=Path(__file__).resolve().parents[1]
config=json.loads((ROOT/'project.json').read_text(encoding='utf-8'))
fact=config['fact']
checks=[]
def check(ok,label):
 if not ok: raise AssertionError(label)
 checks.append(label)
def rows(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def num(row,key):return float(row[key])
def same(a,b,label,tol=.011):check(abs(a-b)<=tol,label)
def keyed(data,key):
 check(len({x[key] for x in data})==len(data),f'Unique key: {key}')
 return {x[key]:x for x in data}
raw={p.stem:rows(p) for p in (ROOT/'data/raw').glob('*.csv')}
dims={p.stem:rows(p) for p in (ROOT/'data/dimensions').glob('*.csv')}
data=rows(ROOT/'data/curated'/f'{fact}.csv')
check(bool(data),'Nonempty fact')
keyed(data,{'Transport':'ShipmentID','Production':'BatchID','Sales':'LineID'}[fact])
for name,dd in dims.items():
 key='Date' if name=='Date' else name+'ID';lookup=keyed(dd,key)
 check(all(x[key] in lookup for x in data),f'Foreign key: {name}')
expected=[str(dt.date(2024,1,1)+dt.timedelta(days=i)) for i in range(731)]
check([x['Date'] for x in dims['Date']]==expected,'Contiguous full 2024–2025 calendar')
S=lambda col:sum(num(x,col) for x in data)

if fact=='Transport':
 shipment=keyed(raw['shipments'],'ShipmentID');invoice=keyed(raw['invoices'],'ShipmentID');route=keyed(dims['Route'],'RouteID')
 fx={(x['Date'],x['Currency']):float(x['RateToPLN']) for x in raw['fx']}
 check(len(fx)==len(raw['fx']),'Unique date/currency FX keys')
 check(set(shipment)==set(invoice)=={x['ShipmentID'] for x in data},'Complete shipment/invoice matching')
 for x in data:
  inv=invoice[x['ShipmentID']];src=shipment[x['ShipmentID']]
  same(num(x,'ActualCostPLN'),round(sum(num(inv,k) for k in ['Base','Fuel','Toll'])*fx[x['Date'],inv['Currency']],2),'FX cost reconciliation')
  same(num(x,'BudgetCostPLN'),num(src,'DistanceKm')*num(route[x['RouteID']],'BudgetPLNPerKm'),'Route budget reconciliation')
  check(0<num(x,'Pallets')<=num(x,'CapacityPallets'),'Valid load and capacity')
  same(num(x,'LoadedPalletKm'),num(src,'Pallets')*num(src,'DistanceKm'),'Loaded pallet-km')
  same(num(x,'CapacityPalletKm'),num(src,'CapacityPallets')*num(src,'DistanceKm'),'Capacity pallet-km')
 totals={'Koszt transportu':S('ActualCostPLN'),'Odchylenie budżetu':S('ActualCostPLN')/S('BudgetCostPLN')-1,'Wykorzystanie':S('LoadedPalletKm')/S('CapacityPalletKm'),'Wysyłki':len(data)}
 check(0<=sum(num(x,'ActualCostPLN')*max(0,1-num(x,'Pallets')/num(x,'CapacityPallets')/.85) for x in data)<=S('ActualCostPLN'),'Scenario bounded by actual cost')
elif fact=='Production':
 orders=keyed(raw['orders'],'BatchID');mes=keyed(raw['mes'],'BatchID');rates=keyed(raw['rates'],'LineID');products=keyed(dims['Product'],'ProductID')
 check(set(orders)==set(mes)=={x['BatchID'] for x in data},'Complete ERP/MES matching')
 for x in data:
  src=orders[x['BatchID']];machine=mes[x['BatchID']];rate=rates[x['LineID']];std=num(products[x['ProductID']],'StandardUnitCost')
  same(num(x,'GoodUnits')+num(x,'ScrapUnits'),num(x,'TotalUnits'),'Good + scrap = total',0)
  labor=round(num(machine,'LaborHours')*num(rate,'LaborRate'),2);energy=round(num(machine,'EnergyKWh')*num(rate,'EnergyRate'),2)
  same(num(x,'ActualCostPLN'),round(num(src,'MaterialCostPLN')+labor+energy,2),'ERP/MES/rate cost reconciliation')
  same(num(x,'FlexibleBudgetPLN'),num(machine,'GoodUnits')*std,'Flexible budget grain')
  same(num(x,'StaticBudgetPLN'),num(src,'PlannedUnits')*std,'Static budget grain')
  check(0<num(x,'IdealMinutes')<=num(x,'RunMinutes')<=num(x,'PlannedMinutes'),'OEE components within bounds')
 same((S('ActualCostPLN')-S('FlexibleBudgetPLN'))+(S('FlexibleBudgetPLN')-S('StaticBudgetPLN')),S('ActualCostPLN')-S('StaticBudgetPLN'),'Variance bridge closes')
 totals={'Koszt produkcji':S('ActualCostPLN'),'Koszt / dobra sztuka':S('ActualCostPLN')/S('GoodUnits'),'Braki':S('ScrapUnits')/S('TotalUnits'),'OEE':S('IdealMinutes')/S('PlannedMinutes')*S('GoodUnits')/S('TotalUnits')}
else:
 sales=keyed(raw['sales'],'LineID');cost=keyed(raw['cogs'],'LineID');freight=keyed(raw['freight'],'ShipmentID');targets=keyed(raw['targets'],'ClientID')
 check(set(sales)==set(cost)=={x['LineID'] for x in data},'Complete sales/COGS matching')
 shipment_totals={}
 for x in raw['sales']:shipment_totals[x['ShipmentID']]=shipment_totals.get(x['ShipmentID'],0)+num(x,'NetRevenuePLN')
 allocations={}
 for x in data:
  src=sales[x['LineID']];sid=x['ShipmentID']
  same(num(x,'NetRevenuePLN'),num(src,'GrossPLN')-num(src,'DiscountPLN'),'Net revenue bridge')
  same(num(x,'COGSPLN'),num(cost[x['LineID']],'COGSPLN'),'COGS source reconciliation')
  same(num(x,'AllocatedFreightPLN'),num(freight[sid],'FreightPLN')*num(src,'NetRevenuePLN')/shipment_totals[sid],'Freight allocation denominator',1e-7)
  same(num(x,'TargetContributionPLN'),num(src,'NetRevenuePLN')*num(targets[x['ClientID']],'TargetMargin'),'Client target reconciliation',1e-7)
  allocations[sid]=allocations.get(sid,0)+num(x,'AllocatedFreightPLN')
 for sid,total in allocations.items():same(total,num(freight[sid],'FreightPLN'),'Shipment-level allocation closes',1e-7)
 same(S('AllocatedFreightPLN'),sum(num(x,'FreightPLN') for x in raw['freight']),'Total freight not duplicated',1e-6)
 contribution=S('NetRevenuePLN')-S('COGSPLN')-S('AllocatedFreightPLN')
 totals={'Przychód netto':S('NetRevenuePLN'),'Kontrybucja':contribution,'Marża po dostawie':contribution/S('NetRevenuePLN'),'Transport / przychód':S('AllocatedFreightPLN')/S('NetRevenuePLN')}

reference=json.loads((ROOT/'docs/control-totals.json').read_text(encoding='utf-8'))
for k,v in totals.items():same(v,reference[k]['value'],'Published KPI: '+k,1e-6)
model=json.loads((ROOT/'model/Analytics.SemanticModel/model.bim').read_text(encoding='utf-8'))['model']
tables={x['name']:x for x in model['tables']}
for rel in model['relationships']:
 check(rel['fromTable'] in tables and rel['toTable'] in tables,'Relationship table exists')
 check(rel['crossFilteringBehavior']=='oneDirection','Unidirectional relationships')
 for side in ['from','to']:check(rel[side+'Column'] in {x['name'] for x in tables[rel[side+'Table']]['columns']},'Relationship column exists')
for table in tables.values():
 for part in table['partitions']:check(part['source']['type']=='m' and part['mode']=='import','M import partition')
for visual in (ROOT/'model/Analytics.Report').rglob('visual.json'):
 v=json.loads(visual.read_text(encoding='utf-8'))
 for role in v['visual'].get('query',{}).get('queryState',{}).values():
  for proj in role['projections']:
   kind=next(iter(proj['field']));field=proj['field'][kind];tab=field['Expression']['SourceRef']['Entity']
   check(tab in tables,'Visual table exists')
   check(field['Property'] in {x['name'] for x in tables[tab]['measures' if kind=='Measure' else 'columns']},'Visual binding exists')
 check(v['position']['x']+v['position']['width']<=1440 and v['position']['y']+v['position']['height']<=900,'Visual fits canvas')
for name,table in tables.items():
 if name=='Scenario':continue
 embedded='\n'.join(table['partitions'][0]['source']['expression'])
 check(embedded.strip()==(ROOT/'power-query'/f'{name}.m').read_text(encoding='utf-8').strip(),'M source copy in sync')
# Run real SQL against a separately loaded in-memory database.
db=sqlite3.connect(':memory:')
for name,rr in {**dims,fact:data}.items():
 cols=list(rr[0])
 # Explicit text keys preserve leading zeroes; SQLite converts arithmetic inputs as needed.
 db.execute('CREATE TABLE "'+name+'" ('+','.join('"'+k+'" TEXT' for k in cols)+')')
 db.executemany('INSERT INTO "'+name+'" VALUES ('+','.join('?' for _ in cols)+')',[[x[k] for k in cols] for x in rr])
result=db.execute((ROOT/'sql/analysis.sql').read_text(encoding='utf-8')).fetchall()
check(bool(result),'SQL analysis executes with nonempty output')
sumidx=3 if fact=='Transport' else 1
expected_total=S('ActualCostPLN') if fact!='Sales' else S('NetRevenuePLN')
same(sum(float(x[sumidx]) for x in result),expected_total,'SQL grouped total reconciles',.001)
report={'status':'PASS','fact_rows':len(data),'checks_executed':len(checks),'distinct_checks':sorted(set(checks)),'report_pages':3,'native_visuals':len(list((ROOT/'model/Analytics.Report').rglob('visual.json'))),'measure_count':len(tables[fact]['measures']),'desktop_refresh_executed':False,'dax_execution_verified':False,'power_query_execution_verified':False,'note':'Python/SQLite and structural checks only. Native Desktop refresh/render is still required.'}
(ROOT/'docs/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','fact_rows','checks_executed','native_visuals','measure_count']},ensure_ascii=False))
