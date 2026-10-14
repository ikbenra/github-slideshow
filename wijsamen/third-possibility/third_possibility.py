#!/usr/bin/env python3
"""Auditable comparison of fictional alternatives; NOT a real-world decision system."""
import argparse
import json

MEASURES = {"public_benefit": "max", "autonomy": "max", "harm": "min", "resource_cost": "min"}

def validate(data):
    rules = data["constraints"]
    for key, upper in [("min_public_benefit",100),("max_harm",100),("min_feasibility",1)]:
        if not 0 <= rules[key] <= upper:
            raise ValueError("Invalid constraint: "+key)
    ids=set()
    for a in data["alternatives"]:
        if a["id"] in ids:
            raise ValueError("Duplicate alternative")
        ids.add(a["id"])
        if not isinstance(a["rights_compatible"], bool):
            raise ValueError("Rights gate must be boolean")
        for key in list(MEASURES)+["feasibility"]:
            v=a[key]
            cap=1 if key=="feasibility" else 100
            if not isinstance(v,list) or len(v)!=2 or any(type(x) not in (int,float) for x in v) or not 0<=v[0]<=v[1]<=cap:
                raise ValueError("Invalid interval: "+a["id"]+"/"+key)

def reasons(a,r):
    failures=[]
    if not a["rights_compatible"]: failures.append("rights gate")
    if a["public_benefit"][0] < r["min_public_benefit"]: failures.append("public benefit lower bound")
    if a["harm"][1] > r["max_harm"]: failures.append("harm upper bound")
    if a["feasibility"][0] < r["min_feasibility"]: failures.append("feasibility lower bound")
    return failures

def dominates_robustly(a,b):
    strict=False
    for name, direction in MEASURES.items():
        al,ah=a[name]; bl,bh=b[name]
        if direction=="max":
            if al<bh: return False
            strict |= al>bh
        else:
            if ah>bl: return False
            strict |= ah<bl
    return strict

def analyse(data):
    validate(data)
    opts=data["alternatives"]
    exclusions={a["id"]:reasons(a,data["constraints"]) for a in opts}
    eligible=[a for a in opts if not exclusions[a["id"]]]
    comparisons=[{"better":a["id"],"than":b["id"]} for a in eligible for b in eligible
                 if a["id"]!=b["id"] and dominates_robustly(a,b)]
    dominated={p["than"] for p in comparisons}
    return {
        "case":data["case"],
        "status":"FICTIONAL_INPUTS_NOT_EMPIRICAL_EVIDENCE",
        "eligible":[a["id"] for a in eligible],
        "excluded":{k:v for k,v in exclusions.items() if v},
        "robust_dominance":comparisons,
        "undominated_eligible":[a["id"] for a in eligible if a["id"] not in dominated],
        "warning":"Logical illustration only; no automatic legal, care, ecological or policy decisions."
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("scenario")
    args=parser.parse_args()
    with open(args.scenario,encoding="utf-8") as handle:
        scenario=json.load(handle)
    print(json.dumps(analyse(scenario),ensure_ascii=False,indent=2))
