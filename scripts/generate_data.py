"""Deterministic synthetic data generator. Standard library only."""
from pathlib import Path
import csv, json, random, math, calendar, datetime as dt, hashlib, shutil, textwrap, html, re
CONFIG = [dict(slug='PowerBI-Transport-Cost-Analytics', title='Transport Cost Analytics', pl='Koszty transportu i wykorzystanie floty', accent='#16B8A6', tag='LOGISTICS INTELLIGENCE', fact='Transport', grain='Jedna zrealizowana wysyłka (ShipmentID).', question='Które kierunki generują przekroczenia kosztów i gdzie warto zbadać konsolidację dostaw?', pages=['01 | Przegląd kosztów', '02 | Kierunki i klienci', '03 | Wykorzystanie i scenariusz']), dict(slug='PowerBI-Production-Controlling', title='Production Controlling', pl='Koszt jednostkowy, odchylenia i efektywność', accent='#F0AE49', tag='MANUFACTURING INTELLIGENCE', fact='Production', grain='Jedna partia produkcyjna (BatchID), jeden produkt i jedna linia.', question='Czy wzrost kosztu wynika z wolumenu, zużycia materiału czy sprawności produkcji?', pages=['01 | Wynik produkcji', '02 | Odchylenia kosztów', '03 | Jakość i efektywność']), dict(slug='PowerBI-Profitability-Management', title='Profitability Management', pl='Rentowność klientów po kosztach dostawy', accent='#8D9CFF', tag='MANAGEMENT INTELLIGENCE', fact='Sales', grain='Jedna pozycja faktury sprzedaży (LineID), przypisana do jednej wysyłki.', question='Którzy klienci pozostają rentowni po rabatach i przypisaniu kosztów transportu?', pages=['01 | Wynik zarządczy', '02 | Klienci i produkty', '03 | Most marży i decyzje'])]

def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding='utf-8')

def csvout(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def money(x):
    return round(x, 2)

def dates():
    start = dt.date(2024, 1, 1)
    return [start + dt.timedelta(days=i) for i in range(731)]

def dimdate():
    return [dict(Date=str(d), Year=d.year, Month=d.month, YearMonth=d.strftime('%Y-%m'), Quarter='Q' + str((d.month - 1) // 3 + 1)) for d in dates()]

def clients():
    return [dict(ClientID=f'C{i:03}', Client=f'Klient {i:02}', Segment=['Przemysł', 'Dystrybucja', 'OEM'][i % 3], Market=['Polska', 'Niemcy', 'Czechy', 'Francja'][i % 4]) for i in range(1, 25)]

def products():
    return [dict(ProductID=f'P{i:02}', Product=f'Komponent {i:02}', Family=['Stal', 'Aluminium', 'Montaż'][i % 3], StandardUnitCost=35 + i * 7) for i in range(1, 13)]

def generate(c):
    r = random.Random(430 + CONFIG.index(c))
    raw = {}
    dims = {'Date': dimdate(), 'Client': clients()}
    facts = []
    if c['fact'] == 'Transport':
        dims['Route'] = [dict(RouteID=f'R{i:02}', Route=f'Łódź → {city}', Market=market, Scope='Krajowy' if market == 'Polska' else 'Zagraniczny', DistanceKm=km, BudgetPLNPerKm=rate) for (i, (city, market, km, rate)) in enumerate([('Warszawa', 'Polska', 140, 4.8), ('Poznań', 'Polska', 210, 4.5), ('Gdańsk', 'Polska', 340, 4.3), ('Berlin', 'Niemcy', 480, 5.2), ('Praga', 'Czechy', 450, 4.9), ('Lyon', 'Francja', 1550, 5.8)], 1)]
        dims['Carrier'] = [dict(CarrierID=f'T{i}', Carrier=f'Przewoźnik {i}') for i in range(1, 5)]
        raw['fx'] = [dict(Date=str(d), Currency=cur, RateToPLN=1.0 if cur == 'PLN' else round(4.28 + 0.12 * math.sin(d.month / 2), 4)) for d in dates() for cur in ['PLN', 'EUR']]
        fx = {(x['Date'], x['Currency']): x['RateToPLN'] for x in raw['fx']}
        raw['shipments'] = []
        raw['invoices'] = []
        for i in range(7200):
            d = dates()[r.randrange(731)]
            route = r.choice(dims['Route'])
            cap = r.choice([18, 33])
            load = r.randint(7, cap)
            cur = 'PLN' if route['Scope'] == 'Krajowy' else 'EUR'
            rate = fx[str(d), cur]
            planned = money(route['DistanceKm'] * route['BudgetPLNPerKm'])
            factor = r.uniform(0.91, 1.09) + (0.13 if route['RouteID'] == 'R06' and d.year == 2025 else 0)
            base = money(planned * 0.78 * factor / rate)
            fuel = money(planned * 0.16 * factor / rate)
            toll = money(planned * 0.06 / rate)
            s = dict(ShipmentID=f'S{i + 1:06}', Date=str(d), RouteID=route['RouteID'], ClientID=r.choice(dims['Client'])['ClientID'], CarrierID=r.choice(dims['Carrier'])['CarrierID'], Pallets=load, CapacityPallets=cap, DistanceKm=route['DistanceKm'], Deliveries=r.randint(1, 3), OnTime=int(r.random() > 0.08))
            inv = dict(ShipmentID=s['ShipmentID'], Currency=cur, Base=base, Fuel=fuel, Toll=toll)
            raw['shipments'].append(s)
            raw['invoices'].append(inv)
            facts.append(dict(**s, ActualCostPLN=money((base + fuel + toll) * rate), BudgetCostPLN=planned, LoadedPalletKm=load * s['DistanceKm'], CapacityPalletKm=cap * s['DistanceKm']))
    elif c['fact'] == 'Production':
        dims.pop('Client')
        dims['Product'] = products()
        dims['Line'] = [dict(LineID=f'L{i}', Line=f'Linia {i}', Technology=['Cięcie', 'Obróbka', 'Montaż'][i - 1]) for i in range(1, 4)]
        raw['orders'] = []
        raw['mes'] = []
        raw['rates'] = [dict(LineID=f'L{i}', LaborRate=48 + i * 4, EnergyRate=1.1 + i * 0.05) for i in range(1, 4)]
        rates = {x['LineID']: x for x in raw['rates']}
        for i in range(4320):
            d = r.choice(dates())
            p = r.choice(dims['Product'])
            line = r.choice(dims['Line'])['LineID']
            planned = r.randint(90, 220)
            total = max(1, int(planned * r.uniform(0.88, 1.08)))
            scrap = int(total * r.uniform(0.015, 0.075 if line == 'L2' else 0.035))
            good = total - scrap
            run = round(r.uniform(300, 420), 2)
            ideal = round(run * r.uniform(0.76, 0.95) / total, 4)
            std = p['StandardUnitCost']
            material = money(total * std * 0.68 * r.uniform(0.96, 1.06))
            labor = round(good * std * 0.22 / rates[line]['LaborRate'] * r.uniform(0.95, 1.1), 3)
            energy = round(good * std * 0.1 / rates[line]['EnergyRate'] * r.uniform(0.94, 1.12), 3)
            order = dict(BatchID=f'B{i + 1:06}', Date=str(d), ProductID=p['ProductID'], LineID=line, PlannedUnits=planned, MaterialCostPLN=material)
            mes = dict(BatchID=order['BatchID'], TotalUnits=total, GoodUnits=good, ScrapUnits=scrap, PlannedMinutes=480, RunMinutes=run, IdealMinutes=round(ideal * total, 4), LaborHours=labor, EnergyKWh=energy)
            raw['orders'].append(order)
            raw['mes'].append(mes)
            facts.append(dict(**order, **{k: v for (k, v) in mes.items() if k != 'BatchID'}, LaborCostPLN=money(labor * rates[line]['LaborRate']), EnergyCostPLN=money(energy * rates[line]['EnergyRate']), ActualCostPLN=money(material + money(labor * rates[line]['LaborRate']) + money(energy * rates[line]['EnergyRate'])), FlexibleBudgetPLN=good * std, StaticBudgetPLN=planned * std))
    else:
        dims['Product'] = products()
        raw['sales'] = []
        raw['cogs'] = []
        raw['freight'] = []
        raw['targets'] = [dict(ClientID=x['ClientID'], TargetMargin=0.2 if x['Segment'] == 'OEM' else 0.24) for x in dims['Client']]
        targets = {x['ClientID']: x['TargetMargin'] for x in raw['targets']}
        for i in range(2400):
            d = r.choice(dates())
            cl = r.choice(dims['Client'])
            shipment = f'D{i + 1:05}'
            lines = []
            freight = money(r.uniform(170, 590) * (1.3 if cl['Market'] == 'Francja' else 1))
            raw['freight'].append(dict(ShipmentID=shipment, FreightPLN=freight))
            for j in range(r.randint(2, 5)):
                p = r.choice(dims['Product'])
                qty = r.randint(15, 90)
                gross = money(qty * p['StandardUnitCost'] * r.uniform(1.32, 1.55))
                discount = money(gross * (0.15 if cl['ClientID'] == 'C007' else r.uniform(0.01, 0.09)))
                net = money(gross - discount)
                cost = money(qty * p['StandardUnitCost'] * r.uniform(0.96, 1.06))
                lid = f'{shipment}-{j + 1}'
                s = dict(LineID=lid, ShipmentID=shipment, Date=str(d), ClientID=cl['ClientID'], ProductID=p['ProductID'], Quantity=qty, GrossPLN=gross, DiscountPLN=discount, NetRevenuePLN=net)
                raw['sales'].append(s)
                raw['cogs'].append(dict(LineID=lid, COGSPLN=cost))
                lines.append(dict(**s, COGSPLN=cost))
            total = sum((x['NetRevenuePLN'] for x in lines))
            for s in lines:
                facts.append(dict(**s, AllocatedFreightPLN=freight * s['NetRevenuePLN'] / total, TargetContributionPLN=s['NetRevenuePLN'] * targets[cl['ClientID']]))
    return (raw, dims, facts)

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    selected = json.loads((root/'project.json').read_text(encoding='utf-8'))
    config = next(c for c in CONFIG if c['slug']==selected['slug'])
    raw,dims,facts = generate(config)
    for name,data in raw.items(): csvout(root/'data/raw'/(name+'.csv'),data)
    for name,data in dims.items(): csvout(root/'data/dimensions'/(name+'.csv'),data)
    csvout(root/'data/curated'/(config['fact']+'.csv'),facts)
    print('Regenerated deterministic demo data. Run python scripts/validate.py')
