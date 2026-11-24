"""Builds web/index.html (standalone, for GitHub Pages) from src/content.html + rules.js + profile.json."""
import json, sys
src = open("web/src/content.html", encoding="utf-8").read()
rules = open("web/rules.js", encoding="utf-8").read()
profile = json.dumps(json.load(open("profile.json")), indent=2)
page = src.replace("/*RULES*/", rules).replace("/*PROFILE*/", profile)
head, body = page.split("<!--BODY-->")
open("web/index.html", "w", encoding="utf-8").write(
    '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    + head + "</head><body>" + body + "</body></html>\n")
if len(sys.argv) > 1:  # artifact version: no skeleton tags
    open(sys.argv[1], "w", encoding="utf-8").write(head + body)
