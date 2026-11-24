"""Rule-based baseline for screening internship postings.

Labels: "Good fit", "Check carefully", "Risky".
Every label comes with human-readable reasons so a person can verify it.
"""
import json
import re
from dataclasses import dataclass, field

FEE_PATTERNS = [
    r"registration fee", r"security deposit", r"training fee", r"joining fee",
    r"processing fee", r"certificate fee", r"caution money", r"refundable",
    r"pay (?:rs\.?|inr|₹)\s*\d", r"(?:rs\.?|inr|₹)\s*\d[\d,]*\s*(?:as|for)\s*(?:fee|deposit|registration|kit)",
    r"upfront (?:payment|fee)", r"pay (?:a )?fee",
]
DUBIOUS_PATTERNS = {
    "guaranteed placement/income": r"guaranteed (?:placement|job|income)|earn up to .{0,20}(?:per day|daily)",
    "no interview / instant selection": r"no interview|instant (?:selection|joining)|direct selection",
    "contact only via WhatsApp/personal email": r"whatsapp (?:only|us)|contact (?:us )?(?:on|via) whatsapp|@(?:gmail|yahoo|hotmail)\.com",
    "commission-only pay": r"commission[- ]only|performance[- ]based (?:pay|stipend) only",
    "'comment INTERESTED' lead funnel": r"comment\s*[\"“]?#?interested",
    "shortened or unofficial apply link": r"\b(?:rb\.gy|bit\.ly|tinyurl\.com)/",
    "training / edtech / placement-assistance company": r"ed-?tech|placement (?:assistance|support)|learning (?:solutions|organization)|career guidance|industry-oriented training",
    "unpaid but promises a large job offer": r"(?=[\s\S]*\bunpaid\b)[\s\S]*expect a salary of",
}

def _num(x):
    return int(x.replace(",", "")) if x else None

def pay_and_hiring_flags(text):
    """Numeric red flags that need parsing, not just a regex hit."""
    flags = []
    posted = re.search(r"Opportunities posted:\s*(\d+)", text)
    hired = re.search(r"Candidates hired:\s*(\d+)", text)
    if posted and hired:
        p, h = int(posted.group(1)), int(hired.group(1))
        if h >= 1000:
            flags.append(f"mass hiring claim ({h} 'hired')")
        elif p >= 100 and h / p < 0.1:
            flags.append(f"posts a lot, hires very few ({h} hired of {p} posted)")
    fixed, variable = [], []
    for m in re.finditer(r"(Variable Pay:\s*)?₹\s*([\d,]+)(?:\s*-\s*([\d,]+))?\s*/month", text):
        lo, hi = _num(m.group(2)), _num(m.group(3)) or _num(m.group(2))
        (variable if m.group(1) else fixed).append((lo, hi))
    if fixed:
        lo = min(a for a, _ in fixed); hi = max(b for _, b in fixed)
        if lo < 8000:
            flags.append(f"very low stipend (from ₹{lo:,}/month)")
        if variable and max(b for _, b in variable) and min(a for a, _ in variable) / hi >= 0.25:
            flags.append("a big part of the pay is 'variable'")
    lpa = [int(x) for m in re.finditer(r"(\d+)\s*(?:[–-]\s*(\d+))?\s*LPA", text) for x in m.groups() if x]
    if lpa and re.search(r"fresher", text, re.I) and max(lpa) >= 10:
        flags.append("pay far above normal for a fresher")
    return flags

@dataclass
class Result:
    label: str
    reasons: list = field(default_factory=list)

def load_profile(path="profile.json"):
    with open(path) as f:
        return json.load(f)

def _has(patterns, text):
    return [p for p in patterns if re.search(p, text, re.I)]

def fee_flags(text):
    return _has(FEE_PATTERNS, text)

def dubious_flags(text):
    return ([name for name, p in DUBIOUS_PATTERNS.items() if re.search(p, text, re.I)]
            + pay_and_hiring_flags(text))

def skill_overlap(text, skills):
    t = text.lower()
    return sorted({s for s in skills if re.search(r"\b" + re.escape(s) + r"\b", t)})

def in_target_city(location, text, profile):
    blob = f"{location} {text}".lower()
    return any(c in blob for c in profile["target_cities"])

def location_ok(location, text, profile):
    blob = f"{location} {text}".lower()
    if any(c in blob for c in profile["target_cities"]):
        return True
    return bool(profile.get("accept_remote")) and bool(re.search(r"work from home|remote", blob))

def screen(posting, profile):
    """posting: dict with title, company, location, text. Returns Result."""
    text = f"{posting.get('title','')} {posting.get('text','')}"
    reasons = []
    fees = fee_flags(text)
    dub = dubious_flags(text)
    skills = skill_overlap(text, profile["skills"])
    loc = location_ok(posting.get("location", ""), text, profile)
    city = in_target_city(posting.get("location", ""), text, profile)
    need = 1 if city else 2

    if fees:
        reasons.append("Mentions a fee or deposit")
    reasons += [f"Red flag: {d}" for d in dub]
    if fees or len(dub) >= 2:
        return Result("Risky", reasons)

    if not loc:
        reasons.append("Location is outside your target cities")
    if len(skills) < need:
        reasons.append(f"Only {len(skills)} matching skill(s)")
    else:
        reasons.append("Matches skills: " + ", ".join(skills))
    if dub:
        return Result("Check carefully", reasons)
    if loc and len(skills) >= need:
        return Result("Good fit", reasons)
    return Result("Check carefully", reasons)
