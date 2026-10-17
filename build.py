#!/usr/bin/env python3
"""Build the static Recipe Box site from recipes.json -> site/. Usage: python3 build.py"""
import json, shutil, html
from pathlib import Path
ROOT=Path(__file__).parent; OUT=ROOT/'site'
D=json.loads((ROOT/'recipes.json').read_text())
e=html.escape
FONTS="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,560;0,8..60,600;1,8..60,400&display=swap"
def page(title,body,pre):
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(D['description'])}"><meta name="theme-color" content="#3f4a38">
<meta property="og:title" content="{e(title)}"><meta property="og:image" content="{pre}og.jpg"><link rel="icon" type="image/svg+xml" href="{pre}favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{pre}style.css"></head><body>
<header class="bar"><a class="brand" href="{pre}index.html">{e(D['title'])}</a><nav>{''.join(f'<a href="{pre}{c["id"]}.html">{e(c["name"])}</a>' for c in D['categories'])}</nav>
<a class="btn" href="{pre}the-recipe-box.pdf" download>Download PDF</a></header>
{body}<footer><p class="brand">{e(D['title'])}</p><p>{e(D['footer'])}</p><p><a href="{pre}the-recipe-box.pdf" download>Download PDF</a></p></footer></body></html>'''
def groups(gs,ordered):
    s='';n=0
    for g in gs:
        if g['label']: s+=f'<p class="label">{e(g["label"])}</p>'
        if ordered:
            s+='<ol>'+''.join(f'<li><span class="num">{(n:=n+1):02d}</span><p>{e(i)}</p></li>' for i in g['items'])+'</ol>'
        else: s+='<ul>'+''.join(f'<li>{e(i)}</li>' for i in g['items'])+'</ul>'
    return s
R=D['recipes']
if OUT.exists(): shutil.rmtree(OUT)
(OUT/'recipes').mkdir(parents=True)
shutil.copytree(ROOT/'assets',OUT,dirs_exist_ok=True)   # images, favicon, og.jpg, pdf, style.css
def card(r,pre=''):
    return f'<a class="card" href="{pre}recipes/{r["slug"]}.html"><img src="{pre}cookbook/{r["image"]}" alt="{e(r["image_alt"])}" loading="lazy"><h3>{e(r["title"])}</h3><p>{e(r["attribution"])}</p></a>'
cats=[c for c in D['categories']]
known={c['name'] for c in cats}
for r in R:  # auto-add any category used in recipes but not declared
    if r['category'] not in known:
        known.add(r['category']); cats.append({"name":r['category'],"id":r['category'].lower().replace(' ','-'),"subtitle":""})
cats=[c for c in cats if any(r['category']==c['name'] for r in R)]  # hide empty categories
D['categories']=cats
tiles=''
for c in cats:
    rs=[r for r in R if r['category']==c['name']]
    if not rs: continue
    cover=c.get('cover') or rs[0]['image']
    tiles+=f'<a class="tile" href="{c["id"]}.html" style="background-image:linear-gradient(0deg,rgba(44,36,22,.8),rgba(44,36,22,.1) 60%),url(cookbook/{cover})"><span class="count">{len(rs)} recipe{"s" if len(rs)!=1 else ""}</span><h3>{e(c["name"])}</h3><p>{e(c.get("subtitle",""))}</p></a>'
    body=f'<div class="chead wrap"><p class="crumb"><a href="index.html">{e(D["title"])}</a> / {e(c["name"])}</p><p class="label">{len(rs)} recipe{"s" if len(rs)!=1 else ""}</p><h1 class="title">{e(c["name"])}</h1><p class="intro">{e(c.get("subtitle",""))}</p></div><main class="wrap"><div class="grid">{"".join(card(r) for r in rs)}</div><p class="back"><a href="index.html">← Back to all categories</a></p></main>'
    (OUT/f'{c["id"]}.html').write_text(page(f'{c["name"]} — {D["title"]}',body,''))
home=f'''<section class="hero" style="background-image:linear-gradient(90deg,rgba(44,36,22,.55),rgba(44,36,22,.25),transparent),url(cookbook/{D["hero_image"]})" role="img" aria-label="{e(D["hero_alt"])}">
<div><p class="eyebrow">{e(D["eyebrow"])}</p><h1>{e(D["title"])}</h1><p class="tag">{e(D["tagline"])}</p><a class="btn hb" href="#box">Open the box ↓</a></div></section><main class="wrap" id="box"><p class="label">The box</p><h2 class="boxh">Choose a meal</h2><div class="tiles">{tiles}</div></main>'''
(OUT/'index.html').write_text(page(D['title'],home,''))
catid={c['name']:c['id'] for c in cats}
for r in R:
    sib=[x for x in R if x['category']==r['category']]; i=sib.index(r)
    notes=''
    if r['notes']:
        notes=f'<aside><p class="label">{e(r.get("notes_heading","From the original card"))}</p>'+''.join(f'<p class="note">{"<span>"+e(n["label"])+". </span>" if n["label"] else ""}{e(n["text"])}</p>' for n in r['notes'])+'</aside>'
    pn='<nav class="pn">'
    if i>0: pn+=f'<a href="{sib[i-1]["slug"]}.html"><span>Previous</span>{e(sib[i-1]["title"])}</a>'
    if i<len(sib)-1: pn+=f'<a class="next" href="{sib[i+1]["slug"]}.html"><span>Next</span>{e(sib[i+1]["title"])}</a>'
    pn+='</nav>'
    body=f'''<div class="rhero" style="background-image:linear-gradient(0deg,rgba(44,36,22,.75),rgba(44,36,22,.15),rgba(44,36,22,.2)),url(../cookbook/{r["image"]})" role="img" aria-label="{e(r["image_alt"])}"><div><p class="eyebrow">{e(r["category"])}</p><h1>{e(r["title"])}</h1></div></div>
<article class="wrap narrow"><p class="crumb"><a href="../index.html">{e(D["title"])}</a> / <a href="../{catid[r["category"]]}.html">{e(r["category"])}</a></p><h1 class="title">{e(r["title"])}</h1><p class="intro">{e(r["intro"])}</p>
<ul class="details">{''.join(f'<li>{e(d)}</li>' for d in r["details"])}</ul>
<div class="cols"><section class="ing"><h2>Ingredients</h2>{groups(r["ingredients"],False)}</section><section class="method"><h2>Method</h2>{groups(r["method"],True)}</section></div>{notes}</article>{pn}'''
    (OUT/'recipes'/f'{r["slug"]}.html').write_text(page(f'{r["title"]} — {D["title"]}',body,'../'))
print(f'Built {len(R)} recipes into {OUT}')
