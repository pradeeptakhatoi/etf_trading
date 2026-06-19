import openpyxl
import pandas as pd
import io

# ── Load Excel (local file) ──────────────────────────────────────────────────
wb = openpyxl.load_workbook('D:\\work\\etf_trading\\ETF Ki Dukan Updated VIdhi.xlsx')
ws = wb['MW-ETF-05-Apr-2026']
data = list(ws.iter_rows(values_only=True))
xlsx_df = pd.DataFrame(data[1:], columns=['SYMBOL','UNDERLYING','OPEN','HIGH','LOW','LTP','VOLUME'])
xlsx_df['SOURCE'] = 'Excel (05-Apr-2026)'
for col in ['OPEN','HIGH','LOW','LTP','VOLUME']:
    xlsx_df[col] = pd.to_numeric(xlsx_df[col], errors='coerce')

# ── Load Google Sheet (live CSV) ─────────────────────────────────────────────
csv_raw = """SYMBOL,UNDERLYING ASSET,OPEN,HIGH,LOW,LTP,VOLUME
ITBEES,Nifty IT TRI,32.81,33.66,32.32,33.48,"22,154,853"
NIFTYBEES,Nifty 50,256.99,259.29,251.7,259.29,"21,918,815"
METALIETF,Nifty Metal Index,11.46,11.76,11.15,11.55,"11,174,048"
PHARMABEES,Nifty Pharma TRI,22.29,22.48,21.69,22.4,"7,796,398"
MIDCAPETF,Mirae Asset Mutual Fund - Mirae Asset Nifty Midcap 150 ETF,20.19,20.26,19.6,20.2,"7,079,001"
PVTBANIETF,Nifty Private Bank Index,25.75,25.75,24.18,24.92,"6,446,448"
MODEFENCE,Nifty India Defence Total Return Index,83.89,83.95,81.16,83.75,"4,736,740"
SMALLCAP,Mirae Asset Nifty Smallcap 250 Momentum Quality 100 ETF,40.56,40.56,37.81,38.99,"3,741,749"
HDFCSML250,HDFC NIFTY Smallcap 250 ETF,148.7,148.75,143.87,148.47,"3,660,084"
PSUBNKBEES,Nifty PSU Bank,88.97,90.9,87.41,90.79,"3,487,161"
ALPHA,NIFTY Alpha 50 Index,44.69,44.7,42.36,43.5,"3,361,602"
QUAL30IETF,ICICI Prudential Nifty 200 Quality 30 ETF,19.02,19.34,18.88,19.33,"3,276,726"
ALPL30IETF,Nifty Alpha Low-Volatility 30 Index,24.95,24.96,24.35,24.9,"2,983,562"
SML100CASE,Nifty Smallcap 100 Index,9.15,9.15,8.61,8.88,"2,510,088"
NEXT50IETF,Nifty Next 50,67.2,67.2,63.26,65.45,"2,341,823"
MONIFTY500,Motilal Oswal Nifty 500 ETF,21.39,21.42,20.81,21.33,"2,232,875"
TOP100CASE,Zerodha Nifty 100 ETF,9.69,9.77,9.48,9.76,"2,119,780"
MOMENTUM50,Nifty 500 Momentum 50 Total Return Index,46.67,48.5,45.3,46.98,"2,083,754"
BANKBEES,Nifty Bank,527.5,534.19,515.98,532.83,"1,938,226"
MOM30IETF,ICICI Prudential Nifty 200 Momentum 30 ETF,28.29,28.29,27.39,28.16,"1,672,364"
FMCGIETF,Nifty FMCG Index,48.85,49.63,48.57,49.6,"1,599,890"
CPSEETF,CPSE ETF,102,102,98.9,100.76,"1,555,534"
OILIETF,Nifty Oil & Gas Index,10.95,11.06,10.75,11,"1,532,332"
GROWWPOWER,BSE Power Index - TRI,10.18,10.21,9.91,10.12,"1,424,792"
MON100,Nasdaq100,238.79,240.5,235.21,239,"1,272,827"
MOM100,Nifty Midcap 100,60.38,60.38,56.15,57.9,"1,242,933"
MOREALTY,Motilal Oswal Nifty Realty ETF,65.91,67.59,64,67.17,"1,226,625"
LOWVOLIETF,Nifty 100 Low Volatility 30 Index,20.29,20.39,19.84,20.33,"1,091,820"
MIDCAP,Nifty Midcap 50 Index,15.69,15.69,15.14,15.69,"988,702"
FINIETF,ICICI Prudential Nifty Financial Services Ex-Bank ETF,29.18,29.18,27.4,28.4,"822,843"
AUTOIETF,Nifty Auto Index,25,25,24.2,24.87,"810,990"
MULTICAP,Nifty500 Multicap 50:25:25 Index,14.67,14.67,14.2,14.61,"787,896"
ALPHAETF,Mirae Asset Nifty 200 Alpha 30 ETF,22.59,22.59,21.8,22.55,"779,018"
MIDSMALL,Mirae Asset Nifty MidSmallcap400 Momentum Quality 100 ETF,46.39,46.39,42.85,44.15,"743,776"
VAL30IETF,Nifty200 Value 30 Index,14.4,14.86,14.13,14.86,"723,012"
MOCAPITAL,Nifty Capital Market Total Return Index,45.2,45.2,43.07,44.5,"666,231"
TOP10ADD,Nifty Top 10 Equal Weight Index,85.62,86.5,83.05,86.1,"616,744"
ICICIB22,S&P BSE BHARAT 22 index,120.15,120.15,113.01,115.98,"609,745"
BSE500IETF,S&P BSE 500 index,35.42,35.48,34.5,35.4,"574,227"
HEALTHY,Nifty Healthcare TRI,14.5,14.65,13.97,14.35,"561,566"
GROWWRAIL,Nifty India Railways PSU Index,29,29.05,28.17,29.05,"552,498"
GROWWNET,Index,8.17,8.42,7.98,8.42,"540,127"
MOMENTUM30,Nifty 200 Momentum 30 Index,28.28,28.9,26.91,27.5,"529,960"
AONETOTAL,Nifty Total Market Index,10.86,10.86,10.32,10.62,"516,507"
MASPTOP50,S&P 500 Top 50 Total Return Index,68.07,69.51,68.07,69.51,"497,820"
NIFTY100EW,Nifty 100 Equal Weight Index,29.99,30.7,29.84,30.18,"414,950"
INFRAIETF,ICICI Prudential Nifty Infrastructure ETF,88.87,89.68,86.8,89.6,"409,312"
ENERGY,Nifty Energy,35.35,35.57,34.61,35.47,"402,774"
MIDSELIETF,S&P BSE Midcap Select Index,15.77,15.98,15.45,15.98,"396,895"
MAFANG,NYSE FANG+ Total Return Index,154.53,154.53,153,154.53,"396,893"
NV20IETF,Nifty50 Value 20,13.74,13.74,13.07,13.5,"385,133"
MSCIINDIA,MSCI India Index,27.99,28.14,26.62,27.89,"363,728"
BFSI,Nifty Financial Services Index,24.03,24.94,24.03,24.87,"334,215"
SBINEQWETF,Nifty50 Equal Weight,31.7,31.7,29.64,31,"332,241"
TOP15IETF,Nifty Top 15 Equal Weight Index,9.39,9.57,9.17,9.43,"306,868"
CHEMICAL,Nifty Chemicals Index (TRI),25.44,25.99,24.82,25.99,"305,228"
GROWWEV,Nifty EV and New Age Automotive Index,26.99,27.17,26.36,27.14,"298,180"
MONQ50,Nasdaq Q-50 Total Return Index,104.94,109.32,101.85,109.32,"282,063"
AXISVALUE,Nifty500 Value 50 TRI,32.49,32.49,30.2,31.14,"279,088"
HDFCSENSEX,SENSEX,82.85,83,80.9,82.78,"246,243"
MAHKTECH,Hang Seng TECH Total Return Index,22.58,22.58,22.58,22.58,"238,097"
CONSUMER,Nifty India New AgeConsumption,10,10.15,9.69,9.94,"226,806"
AONETMMQ50,Nifty Total Market Momentum Quality 50 TRI,9.3,9.3,8.77,9.03,"221,619"
MOMIDMTM,Nifty Midcap 150 Momentum 50 Total Return Index,59.3,59.3,54.78,56.99,"207,236"
MOVALUE,Motilal Oswal S&P BSE Enhanced Value ETF,107.02,109.3,105.01,106.54,"189,578"
GROWWN200,Nifty 200 Index- Total Return Index,10.33,10.36,10.06,10.25,"183,335"
CONSUMBEES,Nifty India Consumption TRI,116.89,118.03,114.51,117.47,"181,366"
GROWWHOSPI,BSE Hospitals Index,44.9,46,43.4,44.52,"158,138"
ABSLPSE,Aditya Birla Sun Life Nifty PSE ETF,9.95,10.06,9.81,10.05,"151,333"
HNGSNGBEES,Hang Seng Index,479.8,496.02,463.66,478,"151,188"
DEFENCE,BSE India Defence,62.35,62.59,60.25,62.32,"136,990"
MAKEINDIA,Nifty India Manufacturing Total Return Index,148.77,148.77,140.12,144.01,"134,458"
FLEXIADD,Nifty500 Flexicap Quality 30 TRI,9.18,9.39,8.99,9.37,"120,083"
TNIDETF,Nifty India Digital Index,77.98,80.08,75.72,79,"114,851"
ELM250,Nifty LargeMidcap 250 TRI,14.85,15.04,14.43,14.99,"108,149"
"""

gs_df = pd.read_csv(io.StringIO(csv_raw))
gs_df.columns = ['SYMBOL','UNDERLYING','OPEN','HIGH','LOW','LTP','VOLUME']
gs_df['SOURCE'] = 'Google Sheet (live)'
for col in ['OPEN','HIGH','LOW','LTP']:
    gs_df[col] = pd.to_numeric(gs_df[col], errors='coerce')
gs_df['VOLUME'] = gs_df['VOLUME'].astype(str).str.replace(',','').astype(float)

# ── Row / Symbol comparison ──────────────────────────────────────────────────
xlsx_syms = set(xlsx_df['SYMBOL'])
gs_syms   = set(gs_df['SYMBOL'])

print('=== STRUCTURAL COMPARISON ===')
print('Excel rows   : {}'.format(len(xlsx_df)))
print('GSheet rows  : {}'.format(len(gs_df)))
print('Symbols only in Excel  : {}'.format(xlsx_syms - gs_syms))
print('Symbols only in GSheet : {}'.format(gs_syms - xlsx_syms))
print('Common symbols         : {}'.format(len(xlsx_syms & gs_syms)))
print()

# ── Field-level diff on common symbols ──────────────────────────────────────
xl = xlsx_df.set_index('SYMBOL')
gs = gs_df.set_index('SYMBOL')
common = list(xlsx_syms & gs_syms)

diffs = []
for sym in common:
    for col in ['OPEN','HIGH','LOW','LTP','VOLUME']:
        xval = xl.loc[sym, col]
        gval = gs.loc[sym, col]
        if abs(float(xval) - float(gval)) > 0.001:
            diffs.append({'SYMBOL': sym, 'FIELD': col,
                          'EXCEL': xval, 'GSHEET': gval,
                          'DIFF': float(gval) - float(xval)})

print('=== FIELD-LEVEL DIFFERENCES ===')
if diffs:
    diff_df = pd.DataFrame(diffs)
    print(diff_df.to_string(index=False))
else:
    print('No differences found — both sources are IDENTICAL.')
print()

# ── Summary stats comparison ─────────────────────────────────────────────────
for df, label in [(xlsx_df, 'Excel'), (gs_df, 'Google Sheet')]:
    df['CHG_PCT'] = ((df['LTP'] - df['OPEN']) / df['OPEN'] * 100).round(2)

print('=== SUMMARY STATS COMPARISON ===')
print('{:<30} {:>12} {:>12}'.format('Metric', 'Excel', 'GSheet'))
print('-' * 56)
metrics = [
    ('Total ETFs',        len(xlsx_df),                                   len(gs_df)),
    ('Avg Change%',       round(xlsx_df['CHG_PCT'].mean(), 3),            round(gs_df['CHG_PCT'].mean(), 3)),
    ('Positive ETFs',     int((xlsx_df['CHG_PCT'] > 0).sum()),            int((gs_df['CHG_PCT'] > 0).sum())),
    ('Negative ETFs',     int((xlsx_df['CHG_PCT'] < 0).sum()),            int((gs_df['CHG_PCT'] < 0).sum())),
    ('Total Volume',      int(xlsx_df['VOLUME'].sum()),                   int(gs_df['VOLUME'].sum())),
    ('Best (CHG%)',       round(xlsx_df['CHG_PCT'].max(), 2),             round(gs_df['CHG_PCT'].max(), 2)),
    ('Worst (CHG%)',      round(xlsx_df['CHG_PCT'].min(), 2),             round(gs_df['CHG_PCT'].min(), 2)),
]
for label, xv, gv in metrics:
    match = '==' if xv == gv else '!!'
    print('{:<30} {:>12} {:>12}  {}'.format(label, xv, gv, match))

print()
print('=== CONCLUSION ===')
if not diffs and len(xlsx_df) == len(gs_df):
    print('Both sources are PERFECTLY IDENTICAL in all 75 ETFs x 5 price/volume fields.')
    print('The Google Sheet is a direct mirror of the Excel file snapshot (05-Apr-2026).')
    print('This means the Google Sheet has NOT been updated with newer live data.')
else:
    print('Differences exist — see field-level diff above.')
