// JavaScript port of screener/rules.py. Keep the two in sync (tests compare them).
const FEE_PATTERNS = [
  /registration fee/i, /security deposit/i, /training fee/i, /joining fee/i,
  /processing fee/i, /certificate fee/i, /caution money/i, /refundable/i,
  /pay (?:rs\.?|inr|₹)\s*\d/i,
  /(?:rs\.?|inr|₹)\s*\d[\d,]*\s*(?:as|for)\s*(?:fee|deposit|registration|kit)/i,
  /upfront (?:payment|fee)/i, /pay (?:a )?fee/i,
];
const DUBIOUS_PATTERNS = {
  "guaranteed placement/income": /guaranteed (?:placement|job|income)|earn up to .{0,20}(?:per day|daily)/i,
  "no interview / instant selection": /no interview|instant (?:selection|joining)|direct selection/i,
  "contact only via WhatsApp/personal email": /whatsapp (?:only|us)|contact (?:us )?(?:on|via) whatsapp|@(?:gmail|yahoo|hotmail)\.com/i,
  "commission-only pay": /commission[- ]only|performance[- ]based (?:pay|stipend) only/i,
  "'comment INTERESTED' lead funnel": /comment\s*["“]?#?interested/i,
  "shortened or unofficial apply link": /\b(?:rb\.gy|bit\.ly|tinyurl\.com)\//i,
  "training / edtech / placement-assistance company": /ed-?tech|placement (?:assistance|support)|learning (?:solutions|organization)|career guidance|industry-oriented training/i,
  "unpaid but promises a large job offer": /(?=[\s\S]*\bunpaid\b)[\s\S]*expect a salary of/i,
};
const toNum = (x) => (x ? parseInt(x.replace(/,/g, ""), 10) : null);

function payAndHiringFlags(text) {
  const flags = [];
  const posted = text.match(/Opportunities posted:\s*(\d+)/i);
  const hired = text.match(/Candidates hired:\s*(\d+)/i);
  if (posted && hired) {
    const p = parseInt(posted[1], 10), h = parseInt(hired[1], 10);
    if (h >= 1000) flags.push(`mass hiring claim (${h} 'hired')`);
    else if (p >= 100 && h / p < 0.1) flags.push(`posts a lot, hires very few (${h} hired of ${p} posted)`);
  }
  const fixed = [], variable = [];
  for (const m of text.matchAll(/(Variable Pay:\s*)?₹\s*([\d,]+)(?:\s*-\s*([\d,]+))?\s*\/month/g)) {
    const lo = toNum(m[2]), hi = toNum(m[3]) || toNum(m[2]);
    (m[1] ? variable : fixed).push([lo, hi]);
  }
  if (fixed.length) {
    const lo = Math.min(...fixed.map((f) => f[0])), hi = Math.max(...fixed.map((f) => f[1]));
    if (lo < 8000) flags.push(`very low stipend (from ₹${lo.toLocaleString("en-IN")}/month)`);
    if (variable.length && Math.max(...variable.map((v) => v[1])) && Math.min(...variable.map((v) => v[0])) / hi >= 0.25)
      flags.push("a big part of the pay is 'variable'");
  }
  const lpa = [];
  for (const m of text.matchAll(/(\d+)\s*(?:[–-]\s*(\d+))?\s*LPA/g)) for (const g of [m[1], m[2]]) if (g) lpa.push(parseInt(g, 10));
  if (lpa.length && /fresher/i.test(text) && Math.max(...lpa) >= 10) flags.push("pay far above normal for a fresher");
  return flags;
}
const feeFlags = (text) => FEE_PATTERNS.filter((p) => p.test(text));
const dubiousFlags = (text) =>
  Object.entries(DUBIOUS_PATTERNS).filter(([, p]) => p.test(text)).map(([n]) => n).concat(payAndHiringFlags(text));
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const skillOverlap = (text, skills) =>
  [...new Set(skills.filter((s) => new RegExp("\\b" + esc(s) + "\\b", "i").test(text)))].sort();
const inTargetCity = (loc, text, profile) => {
  const blob = `${loc} ${text}`.toLowerCase();
  return profile.target_cities.some((c) => blob.includes(c));
};
const locationOk = (loc, text, profile) => {
  const blob = `${loc} ${text}`.toLowerCase();
  return inTargetCity(loc, text, profile) || (!!profile.accept_remote && /work from home|remote/.test(blob));
};

function screen(posting, profile) {
  const text = `${posting.title || ""} ${posting.text || ""}`;
  const reasons = [];
  const fees = feeFlags(text), dub = dubiousFlags(text), skills = skillOverlap(text, profile.skills);
  const loc = locationOk(posting.location || "", text, profile);
  const city = inTargetCity(posting.location || "", text, profile);
  const need = city ? 1 : 2;
  if (fees.length) reasons.push("Mentions a fee or deposit");
  dub.forEach((d) => reasons.push("Red flag: " + d));
  if (fees.length || dub.length >= 2) return { label: "Risky", reasons };
  if (!loc) reasons.push("Location is outside your target cities");
  if (skills.length < need) reasons.push(`Only ${skills.length} matching skill(s)`);
  else reasons.push("Matches skills: " + skills.join(", "));
  if (dub.length) return { label: "Check carefully", reasons };
  if (loc && skills.length >= need) return { label: "Good fit", reasons };
  return { label: "Check carefully", reasons };
}
if (typeof module !== "undefined") module.exports = { screen };
