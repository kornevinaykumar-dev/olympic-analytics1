"""Generate the Olympic dataset CSV without requiring the DB."""
import csv, os, random
random.seed(42)

COUNTRIES = ["United States","China","Japan","Great Britain","Russia","Germany",
"France","Australia","Italy","South Korea","Netherlands","Canada","Brazil","India",
"Spain","Hungary","New Zealand","Kenya","Jamaica","Cuba"]
SPORTS = ["Athletics","Swimming","Gymnastics","Cycling","Rowing","Boxing","Wrestling",
"Weightlifting","Shooting","Archery","Fencing","Judo","Sailing","Diving","Hockey"]
YEARS = [2000,2004,2008,2012,2016,2020,2024]

def strength(idx, sport):
    base = max(1, 14 - idx) * 0.7
    boost = {"Athletics":1.4,"Swimming":1.3,"Gymnastics":1.1}.get(sport,1.0)
    return base * boost

out = os.path.join(os.path.dirname(__file__), "olympic_dataset.csv")
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Country","Year","Sport","Athletes","Previous_Gold","Previous_Silver",
                "Previous_Bronze","Participation_Count","Total_Previous_Medals",
                "Target_Medal_Category"])
    prev = {}
    count = 0
    for yi, year in enumerate(YEARS):
        for idx, c in enumerate(COUNTRIES):
            for s in SPORTS:
                st = strength(idx, s)
                g = max(0, int(random.gauss(st*0.4, 1.2)))
                si = max(0, int(random.gauss(st*0.5, 1.3)))
                b = max(0, int(random.gauss(st*0.6, 1.4)))
                pg,ps,pb = prev.get((c,s),(0,0,0))
                target = "None"
                if g>0: target="Gold"
                elif si>0: target="Silver"
                elif b>0: target="Bronze"
                w.writerow([c,year,s,random.randint(2,30),pg,ps,pb,yi+1,pg+ps+pb,target])
                prev[(c,s)] = (g,si,b)
                count += 1
print(f"Wrote {count} rows to {out}")
