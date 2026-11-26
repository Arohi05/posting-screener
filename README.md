# Posting Screener

Paste an internship or job posting and get a verdict: **Good fit**, **Check carefully** or **Risky**, with the exact rules that triggered it.

Built for the ATRISI Amplify 7-day Builder Challenge.

## The problem
Students check each LinkedIn, Internshala or Naukri posting by hand, ask seniors on WhatsApp whether a company is genuine, and search for the company's history. That is slow, and many risky postings look normal.

## What it does
- Reads one pasted posting. It does not scrape any site (their terms forbid it).
- Flags fees and deposits, unpaid roles that promise large salaries, mass-hiring claims, "comment INTERESTED" funnels, shortened or gmail-only apply links, training/edtech companies, very low or mostly-variable stipends.
- Checks the posting against your skills and target cities (editable in the page).
- Every verdict comes with reasons, and each reason is one rule you can read in `screener/rules.py` or `web/rules.js`.

## Live demo
https://arohi05.github.io/posting-screener/

## How well it works
Tested on 29 real postings from Internshala and LinkedIn that I labelled by hand (company names removed, see `data/postings.csv`).

| | Accuracy |
|---|---|
| This screener | 79% |
| Always guess "Check carefully" (baseline) | 52% |

It caught 8 of the 9 postings I labelled Risky. None of the 9 asked for a fee, which is why the first version (fee rules only) caught 0 of 9 and scored 34%.

**Limits**
- The rules were written after reading these same 29 postings, so 79% is probably too high. A new set of postings is the fair test.
- Labels are my own judgment, not a ground truth.
- It cannot check whether a company really exists.
- Only 5 of the 29 postings are Good fit, so that class is barely tested.

## Run it
```
python3 evaluate.py data/postings.csv      # accuracy against the baseline
python3 -m pytest -q tests                 # 8 tests
open web/index.html                        # the web page, works offline
```
`web/rules.js` is a port of `screener/rules.py`. The two give the same label and reasons on all 29 postings.

## Deploy on GitHub Pages
Settings, Pages, Source: "Deploy from a branch", Branch: `main`, folder `/web`. The page will be at `https://<your-username>.github.io/<repo-name>/`.

## Never pay
No label means a posting is safe. Do not pay any fee to get an internship or job.
