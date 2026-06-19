import openpyxl
import pandas as pd

wb = openpyxl.load_workbook('D:\\work\\etf_trading\\ETF Ki Dukan Updated VIdhi.xlsx')
ws = wb['MW-ETF-05-Apr-2026']

data = list(ws.iter_rows(values_only=True))
headers = [h.strip() for h in data[0]]
rows = data[1:]

df = pd.DataFrame(rows, columns=headers)
df.columns = ['SYMBOL','UNDERLYING','OPEN','HIGH','LOW','LTP','VOLUME']

df['CHANGE_PCT'] = ((df['LTP'] - df['OPEN']) / df['OPEN'] * 100).round(2)
df['RANGE_PCT'] = ((df['HIGH'] - df['LOW']) / df['LOW'] * 100).round(2)

print('=== DATASET OVERVIEW ===')
print('Total ETFs: {}'.format(len(df)))
print('Date: 05-Apr-2026')
print()

print('=== TOP 15 BY VOLUME (Most Liquid) ===')
top_vol = df.nlargest(15, 'VOLUME')[['SYMBOL','UNDERLYING','LTP','CHANGE_PCT','VOLUME']]
print(top_vol.to_string(index=False))
print()

print('=== TOP 10 GAINERS (Open to LTP) ===')
gainers = df[df['CHANGE_PCT'] > 0].nlargest(10, 'CHANGE_PCT')[['SYMBOL','UNDERLYING','OPEN','LTP','CHANGE_PCT','VOLUME']]
print(gainers.to_string(index=False))
print()

print('=== TOP 10 LOSERS (Open to LTP) ===')
losers = df[df['CHANGE_PCT'] < 0].nsmallest(10, 'CHANGE_PCT')[['SYMBOL','UNDERLYING','OPEN','LTP','CHANGE_PCT','VOLUME']]
print(losers.to_string(index=False))
print()

print('=== HIGHEST INTRADAY RANGE % (Volatility) ===')
volatile = df.nlargest(10, 'RANGE_PCT')[['SYMBOL','UNDERLYING','HIGH','LOW','RANGE_PCT','VOLUME']]
print(volatile.to_string(index=False))
print()

avg_chg = df['CHANGE_PCT'].mean()
pos_count = (df['CHANGE_PCT'] > 0).sum()
neg_count = (df['CHANGE_PCT'] < 0).sum()
flat_count = (df['CHANGE_PCT'] == 0).sum()
pos_pct = (df['CHANGE_PCT'] > 0).mean() * 100
neg_pct = (df['CHANGE_PCT'] < 0).mean() * 100
best_sym = df.loc[df['CHANGE_PCT'].idxmax(), 'SYMBOL']
best_chg = df['CHANGE_PCT'].max()
worst_sym = df.loc[df['CHANGE_PCT'].idxmin(), 'SYMBOL']
worst_chg = df['CHANGE_PCT'].min()
total_vol = df['VOLUME'].sum()

print('=== MARKET BREADTH SUMMARY ===')
print('Avg Change: {:.2f}%'.format(avg_chg))
print('Positive ETFs: {} ({:.0f}%)'.format(pos_count, pos_pct))
print('Negative ETFs: {} ({:.0f}%)'.format(neg_count, neg_pct))
print('Flat ETFs: {}'.format(flat_count))
print('Best Performer: {} ({:.2f}%)'.format(best_sym, best_chg))
print('Worst Performer: {} ({:.2f}%)'.format(worst_sym, worst_chg))
print('Total Volume: {:,}'.format(total_vol))
print()

print('=== SECTOR / THEME GROUPING ===')
categories = {
    'Broad Market': ['NIFTYBEES','BANKBEES','SBINEQWETF','NIFTY100EW','MULTICAP','MONIFTY500','BSE500IETF','AONETOTAL','GROWWN200','ELM250','TOP10ADD','TOP15IETF','HDFCSENSEX','MSCIINDIA'],
    'Midcap/Smallcap': ['MIDCAPETF','HDFCSML250','SML100CASE','MOM100','MIDCAP','MIDSMALL','MIDSELIETF','MOMIDMTM','NEXT50IETF','SMALLCAP'],
    'Sectoral': ['ITBEES','METALIETF','PHARMABEES','PVTBANIETF','PSUBNKBEES','FMCGIETF','OILIETF','AUTOIETF','INFRAIETF','ENERGY','BFSI','FINIETF','HEALTHY','CHEMICAL','CONSUMER','CONSUMBEES'],
    'Factor/Smart Beta': ['ALPHA','QUAL30IETF','ALPL30IETF','MOM30IETF','MOMENTUM50','MOMENTUM30','LOWVOLIETF','VAL30IETF','ALPHAETF','AXISVALUE','MOVALUE','NV20IETF','TOP100CASE','FLEXIADD','AONETMMQ50'],
    'Thematic': ['MODEFENCE','DEFENCE','GROWWPOWER','GROWWRAIL','GROWWEV','GROWWNET','MOREALTY','MOCAPITAL','MAKEINDIA','TNIDETF','GROWWHOSPI','ABSLPSE','CPSEETF','ICICIB22'],
    'International': ['MON100','MAFANG','MAHKTECH','HNGSNGBEES','MASPTOP50','MONQ50'],
}

for cat, symbols in categories.items():
    sub = df[df['SYMBOL'].isin(symbols)]
    if not sub.empty:
        avg = sub['CHANGE_PCT'].mean()
        top = sub.loc[sub['CHANGE_PCT'].idxmax(), 'SYMBOL']
        bot = sub.loc[sub['CHANGE_PCT'].idxmin(), 'SYMBOL']
        print('{}: Avg {:.2f}% | Best: {} | Worst: {}'.format(cat, avg, top, bot))
