import json,re
from bs4 import BeautifulSoup
M='mirror/'
home=BeautifulSoup(open(M+'index.html'),'html.parser')
order=[]
for a in home.select('a[href^="/recipes/"]'):
    s=a['href'].split('/')[-1]
    if s not in order: order.append(s)
out=[]
for slug in order:
    d=BeautifulSoup(open(M+'recipes/'+slug),'html.parser')
    art=d.find('article')
    r={'slug':slug,'category':art.find('p').get_text(strip=True),'title':art.find('h1').get_text(strip=True)}
    p=art.find('h1').find_next_sibling('p'); r['intro']=p.get_text(strip=True) if p else ''
    ul=art.find('ul',class_='flex-wrap'); r['details']=[li.get_text(strip=True) for li in ul.find_all('li')] if ul else []
    img=d.select_one('div.relative img'); r['image']=img['src'].split('/')[-1]; r['image_alt']=img.get('alt','')
    secs=art.find_all('section')
    def groups(sec,tag):
        g=[]
        for div in sec.find('h2').find_next_sibling('div').find_all('div',recursive=False) or [sec]:
            lab=div.find('p',recursive=False)
            lst=div.find(tag)
            items=[ (li.find('p') or li).get_text(strip=True) for li in lst.find_all('li',recursive=False)]
            g.append({'label':lab.get_text(strip=True) if lab else '','items':items})
        return g
    r['ingredients']=groups(secs[0],'ul'); r['method']=groups(secs[1],'ol')
    aside=art.find('aside'); r['notes']=[]
    if aside:
        r['notes_heading']=aside.find('p').get_text(strip=True)
        for p in aside.find('div').find_all('p'):
            sp=p.find('span'); lab=sp.get_text(strip=True).rstrip('.') if sp else ''
            if sp: sp.extract()
            r['notes'].append({'label':lab,'text':p.get_text(' ',strip=True)})
        extra=[x.get_text(' ',strip=True) for x in aside.find_all(recursive=False)[2:]]
        if extra: r['attribution']=extra
    out.append(r)
json.dump(out,open('recipes.json','w'),ensure_ascii=False,indent=2)
print(json.dumps(out,ensure_ascii=False,indent=1)[:200000])
