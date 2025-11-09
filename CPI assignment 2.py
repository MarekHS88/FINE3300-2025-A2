import pandas as pd

# --- 1. Read each CPI CSV individually ---
ab = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\cc87d421-d0d9-491e-ad44-7d5bdedf0877_A2 Data (1).zip.877\A2 Data\AB.CPI.1810000401.csv")
bc = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\314c1acc-df13-4c77-abeb-457bda01392e_A2 Data (1).zip.92e\A2 Data\BC.CPI.1810000401.csv")
mb = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\accd2b4f-2344-4e69-8363-9d742fdd4533_A2 Data (1).zip.533\A2 Data\MB.CPI.1810000401.csv")
nb = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\fedc8764-3c9f-4b74-b88d-d809e6a80a16_A2 Data (1).zip.a16\A2 Data\NB.CPI.1810000401.csv")
nl = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\020241c9-7619-4a30-b18d-adca8af6b2c2_A2 Data (1).zip.2c2\A2 Data\NL.CPI.1810000401.csv")
ns = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\fcb4dab9-cc3d-4ac6-acef-6ee6dcdf2d28_A2 Data (1).zip.d28\A2 Data\NS.CPI.1810000401.csv")
on = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\8028896b-5791-4bc4-9595-181df16ff367_A2 Data (1).zip.367\A2 Data\ON.CPI.1810000401.csv")
pei = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\46f23d3f-4361-46f2-911c-569dd4dc94d1_A2 Data (1).zip.4d1\A2 Data\PEI.CPI.1810000401.csv")
qc = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\fe9b8cf5-8191-4e45-ae28-704fb586e741_A2 Data (1).zip.741\A2 Data\QC.CPI.1810000401.csv")
sk = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\e4b8dfe0-b438-4524-b12a-22ecaa3702e4_A2 Data (1).zip.2e4\A2 Data\SK.CPI.1810000401.csv")
canada = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\db80cef5-5235-434f-b6f2-f3758dc7a61d_A2 Data (1).zip.61d\A2 Data\Canada.CPI.1810000401.csv")
minimum_wage = pd.read_csv(r"C:\Users\msato\AppData\Local\Temp\42d638ba-3671-4ef6-a1bf-5cc88739be61_A2 Data (1).zip.e61\A2 Data\MinimumWages.csv")


# --- 3. Put them into a dictionary ---
data = {
    "Canada": canada,
    "Alberta": ab,
    "British Columbia": bc,
    "Manitoba": mb,
    "New Brunswick": nb,
    "Newfoundland and Labrador": nl,
    "Nova Scotia": ns,
    "Ontario": on,
    "Prince Edward Island": pei,
    "Quebec": qc,
    "Saskatchewan": sk
}

# --- 4. Print first few rows of each file ---
for name, df in data.items():
    print(f"\n{name}:")
    print(df.head(12))



# =============================
import re

# - convert long and normalize month labels to 'Jan-24' ---
MONTHS = ["Jan-24","Feb-24","Mar-24","Apr-24","May-24","Jun-24",
          "Jul-24","Aug-24","Sep-24","Oct-24","Nov-24","Dec-24"]
MONTH_CAT = pd.CategoricalDtype(MONTHS, ordered=True)

province_names = {
    "Canada":"Canada",
    "Alberta":"Alberta",
    "British Columbia":"British Columbia",
    "Manitoba":"Manitoba",
    "New Brunswick":"New Brunswick",
    "Newfoundland and Labrador":"Newfoundland and Labrador",
    "Nova Scotia":"Nova Scotia",
    "Ontario":"Ontario",
    "Prince Edward Island":"Prince Edward Island",
    "Quebec":"Quebec",
    "Saskatchewan":"Saskatchewan",
}

def to_long(df_wide: pd.DataFrame, jurisdiction: str) -> pd.DataFrame: 
    df = df_wide.copy() 

    # Find month columns 
    month_cols = []
    for c in df.columns:
        s = str(c).strip()
        if re.fullmatch(r"\d{2}-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", s) or \
           re.fullmatch(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2}", s):
            month_cols.append(c)

    # Rename to 'Mon-YY' format (e.g., '24-Jan' -> 'Jan-24')
    ren = {}
    for c in month_cols: 
        s = str(c).strip() # get string version
        if re.fullmatch(r"\d{2}-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", s): # 'YY-Mon'
            yy, mon = s.split("-") # split
            ren[c] = f"{mon}-{yy}" # reformat
    if ren:
        df = df.rename(columns=ren) # apply renaming

    # Melt to long
    month_cols = [c for c in df.columns if str(c) in MONTHS] # updated month cols
    long_df = df.melt(id_vars=["Item"], value_vars=month_cols,
                      var_name="Month", value_name="CPI") # melt
    long_df["Jurisdiction"] = province_names[jurisdiction] # add jurisdiction column
    long_df["Month"] = long_df["Month"].astype(MONTH_CAT) # set month as categorical
    long_df["CPI"] = pd.to_numeric(long_df["CPI"], errors="coerce") # ensure CPI is numeric
    return long_df.dropna(subset=["CPI"]) # drop rows with NaN CPI

# --- Q1 & Q2: build combined dataframe and print first 12 rows ---
long_frames = [] # list to hold long dataframes
for juris, df in data.items(): # iterate each jurisdiction
    long_frames.append(to_long(df, juris)) # convert and add to list

cpi = pd.concat(long_frames, ignore_index=True)[["Item","Month","Jurisdiction","CPI"]] # combine
cpi = cpi.sort_values(["Jurisdiction","Item","Month"]).reset_index(drop=True) # sort and reset index

print("\n=== Combined CPI (first 12 rows) ===") 
print(cpi.head(12).to_string(index=False)) # print first 12 rows

# --- Q3: average month-to-month % change for selected items ---
TARGET_ITEMS = ["Food", "Shelter", "All-items excluding food and energy"] # target items

def avg_mom_change(g: pd.DataFrame) -> float: # group for one jurisdiction-item
    g = g.sort_values("Month") # ensure sorted by month
    pct = g["CPI"].pct_change() * 100.0 # compute MoM % change
    return pct.iloc[1:].mean()  # skip the first NaN

avg_changes = (cpi[cpi["Item"].isin(TARGET_ITEMS)] # filter for target items
               .groupby(["Jurisdiction","Item"], as_index=False) 
               .apply(avg_mom_change) # compute avg MoM change
               .rename(columns={None: "Avg_MoM_Change_%"})) # rename column
avg_changes["Avg_MoM_Change_%"] = avg_changes["Avg_MoM_Change_%"].round(1) # round to 1 decimal

print("\n=== Avg month-to-month change (%) in 2024 ===") 
print(avg_changes.pivot(index="Jurisdiction", columns="Item", values="Avg_MoM_Change_%").to_string()) # print pivot table

# --- Q4: province with highest average change (exclude Canada) ---
prov_only = avg_changes[avg_changes["Jurisdiction"].str.lower() != "canada"].copy() # exclude Canada
winners = (prov_only.sort_values(["Item","Avg_MoM_Change_%"], ascending=[True, False]) # sort
           .groupby("Item").head(1).reset_index(drop=True)) # get top per item
print("\n=== Province with highest avg MoM change ===") 
for _, r in winners.iterrows(): # print each winner
    print(f"{r['Item']}: {r['Jurisdiction']} ({r['Avg_MoM_Change_%']:.1f}%)") # print

# --- Q5: Equivalent salary to $100,000 in Ontario (Dec-24, All-items) ---
ai_dec = cpi[(cpi["Item"]=="All-items") & (cpi["Month"]=="Dec-24")].copy() # filter for All-items Dec-24
ont_cpi = float(ai_dec.loc[ai_dec["Jurisdiction"]=="Ontario","CPI"].iloc[0]) # get Ontario CPI
eq = ai_dec.assign(EquivalentToON_100k = (100_000 * (ai_dec["CPI"]/ont_cpi)).round(0).astype(int)) # compute equivalent salary
print("\n=== Equivalent to $100,000 in Ontario (Dec-24 All-items CPI) ===") 
print(eq[["Jurisdiction","CPI","EquivalentToON_100k"]] 
      .sort_values("Jurisdiction").to_string(index=False)) # print

# --- Q6: Minimum wages — nominal high/low and highest real ---
mw = minimum_wage.copy() # load minimum wage data

# Standardize column names
mw = mw.rename(columns={ 
    "province":"Jurisdiction", "Province":"Jurisdiction",
    "minimumwage":"MinimumWage", "Minimum Wage":"MinimumWage"
}) # rename columns
mw["Jurisdiction"] = mw["Jurisdiction"].astype(str).str.strip()
mw["MinimumWage"] = pd.to_numeric(mw["MinimumWage"], errors="coerce") # ensure numeric

# Map any codes/variants to the same names used in your CPI frame
name_map = {
    # full names
    "Canada":"Canada",
    "Alberta":"Alberta",
    "British Columbia":"British Columbia",
    "Manitoba":"Manitoba",
    "New Brunswick":"New Brunswick",
    "Newfoundland and Labrador":"Newfoundland and Labrador",
    "Nova Scotia":"Nova Scotia",
    "Ontario":"Ontario",
    "Prince Edward Island":"Prince Edward Island",
    "Quebec":"Quebec",
    "Saskatchewan":"Saskatchewan",
    # possible abbreviations appearing in wage file
    "AB":"Alberta", "BC":"British Columbia", "MB":"Manitoba", "NB":"New Brunswick",
    "NL":"Newfoundland and Labrador", "NS":"Nova Scotia", "ON":"Ontario",
    "PEI":"Prince Edward Island", "QC":"Quebec", "SK":"Saskatchewan"
}
mw["Jurisdiction"] = mw["Jurisdiction"].map(name_map).fillna(mw["Jurisdiction"]) # map names

# Dec-24 All-items CPI table from earlier
ai_dec = cpi[(cpi["Item"]=="All-items") & (cpi["Month"]=="Dec-24")][["Jurisdiction","CPI"]].drop_duplicates() # filter for All-items Dec-24

# Merge and report any misses
mw_dec = mw.merge(ai_dec, on="Jurisdiction", how="left", validate="one_to_one") # merge
missing = mw_dec[mw_dec["CPI"].isna()]["Jurisdiction"].tolist() # find any missing CPI
if missing:
    print("\n[Warning] No Dec-24 CPI match for:", ", ".join(missing)) # warn if any missing

# Compute real wage only for rows with CPI present
mw_dec["RealMinWage_base"] = mw_dec["MinimumWage"] * (100.0 / mw_dec["CPI"]) # real wage in base-year $

# Nominal high/low (ignore NaNs in MinimumWage)
nom_hi = mw_dec.loc[mw_dec["MinimumWage"].idxmax()] # row with max nominal wage
nom_lo = mw_dec.loc[mw_dec["MinimumWage"].idxmin()] # row with min nominal wage

# Highest real (drop NaNs first to avoid idxmax -> NaN)
valid_real = mw_dec.dropna(subset=["RealMinWage_base"]) # drop NaNs
real_hi = valid_real.loc[valid_real["RealMinWage_base"].idxmax()] # row with max real wage

print("\n=== Minimum wage results ===") 
print(f"Highest nominal: {nom_hi['Jurisdiction']} @ ${nom_hi['MinimumWage']:.2f}") # print highest nominal
print(f"Lowest nominal : {nom_lo['Jurisdiction']} @ ${nom_lo['MinimumWage']:.2f}") # print lowest nominal
print(f"Highest real   : {real_hi['Jurisdiction']} (real ${real_hi['RealMinWage_base']:.2f} in base-year $)") # print highest

# --- Q7: Annual change in Services CPI (Jan→Dec 2024) ---
svc = cpi[cpi["Item"]=="Services"].copy() # filter for Services item
svc_jan = svc[svc["Month"]=="Jan-24"][["Jurisdiction","CPI"]].rename(columns={"CPI":"JanCPI"}) # Jan data
svc_dec = svc[svc["Month"]=="Dec-24"][["Jurisdiction","CPI"]].rename(columns={"CPI":"DecCPI"}) # Dec data
svc_chg = svc_jan.merge(svc_dec, on="Jurisdiction", how="inner") # merge Jan and Dec
svc_chg["AnnualChange_%"] = ((svc_chg["DecCPI"]/svc_chg["JanCPI"]) - 1.0) * 100.0 # compute annual change %
svc_chg["AnnualChange_%"] = svc_chg["AnnualChange_%"].round(1) # round to 1 decimal

print("\n=== Services CPI annual change (Jan-24 → Dec-24) ===") 
print(svc_chg.sort_values("Jurisdiction").to_string(index=False)) # print sorted

# --- Q8: Region with highest Services inflation ---
top = svc_chg.iloc[svc_chg["AnnualChange_%"].idxmax()] # get the row with max change
print(f"\nRegion with highest Services inflation: {top['Jurisdiction']} ({top['AnnualChange_%']:.1f}%)") # print
