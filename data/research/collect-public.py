"""Bounded public product/location fact collection; no images, credentials or prices.
URLs/parameters below were discovered from public manufacturer pages and their UI code.
Responses cached outside repository; only normalized facts and request hashes retained.
"""
import hashlib,json,re,time,urllib.request,urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
CACHE=Path('/tmp/wanna-gs-data-20260921');CACHE.mkdir(exist_ok=True)
SOURCES={};RECORDS=[];CHECKED='2026-09-21';VERSION='CAT-CANDIDATES-20260921-v1'
def fetch(url,params=None):
    key=url+'|'+json.dumps(params,sort_keys=True);digest=hashlib.sha256(key.encode()).hexdigest();p=CACHE/digest
    if not p.exists():
        time.sleep(1.05)
        req=urllib.request.Request(url,data=urllib.parse.urlencode(params).encode() if params else None,headers={'User-Agent':'WannaGSResearch/1.0 (bounded public product facts; local prototype)'})
        raw=urllib.request.urlopen(req,timeout=30).read();p.write_bytes(raw)
    raw=p.read_bytes();sid='SRC-'+digest[:12]
    SOURCES[sid]={'source_id':sid,'url':url,'method':'POST read-only public listing' if params else 'GET','parameters':params,'checked_at':CHECKED,'response_sha256':hashlib.sha256(raw).hexdigest(),'stored':'normalized_facts_only','raw_cache':'local /tmp only; not deployed'}
    return raw.decode(),sid

def add(name,brand,category,size,flavor,url,sid,raw_name=None,extra=None):
    name=re.sub(r'\s+',' ',name).strip();key=(brand+'|'+name+'|'+str(size)).lower()
    if any(r['normalized_key']==key for r in RECORDS):return
    r={'sku':'DEMO-'+hashlib.sha256(key.encode()).hexdigest()[:12].upper(),'name':name,'brand':brand,'category':category,'flavor':flavor,'size':size,'aliases':[], 'attributes':{},'origin':'reference_verified','source_id':sid,'source_url':url,'checked_at':CHECKED,'product_confidence':'high_for_observed_fields','trend_confidence':'unverified','normalized_key':key,'raw_name':raw_name or name,'field_origin':{'name':'manufacturer_public','brand':'manufacturer_public','flavor':'manufacturer_public' if flavor else 'unverified','size':'manufacturer_public' if size else 'unverified','category':'research_classification'},'gs25_availability':'simulated_not_verified','price_origin':'simulated_only','inventory_origin':'simulated_only','source_price_copied':False,'review_status':'candidate_independent_review_pending','research_version':'R20260921-v1','catalog_version':VERSION,'research_case_ids':['RC-01','RC-02','RC-03']}
    if extra:r.update(extra)
    RECORDS.append(r)

def collect_otoki():
    # Category links discovered through manufacturer product categories, not guessed APIs.
    listing='https://www.otokimall.com/front/product/product_list.ajax'
    categories=[(23,'밥·죽·누룽지'),(16,'라면·면류'),(33,'간편조리·냉동식')]
    # additional public top-level category ids discovered from menu links
    menu,_=fetch('https://www.otokimall.com/front/product/category/23')
    soup=BeautifulSoup(menu,'html.parser')
    for a in soup.select('a[href]'):
        t=a.get_text(' ',strip=True);m=re.search(r'/front/product/category/(\d+)',a['href'])
        if m and t in ['탕/국/찌개/간편조리','피자/만두/치킨','떡볶이/핫도그/간식']:
            val=(int(m.group(1)),'간편조리·냉동식')
            if val not in categories:categories.append(val)
    for cid,cat in categories:
        params={'type':'search','scate':cid,'sbrand':0,'keyword':'','keywordRe':'','storeNo':0,'depthCheck':2,'ptype':0,'psort':'pop','listBtn':0,'pageSize':80,'page':1}
        html,sid=fetch(listing,params);page='https://www.otokimall.com/front/product/category/'+str(cid)
        SOURCES[sid]['public_page']=page;SOURCES[sid]['provenance']='official_manufacturer_public_listing'
        items=BeautifulSoup(html,'html.parser').select('.prd-item')
        for item in items:
            e=item.select_one('.name');a=item.select_one('a[pno]')
            if not e or not a:continue
            raw=e.get_text(' ',strip=True)
            if re.search('선물|선택|랜덤|골라|기획|굿즈|체험|B2B|업소|박스',raw):continue
            # Pack promotions collapse to observed single product+mass; never invent flavor/mass.
            clean=re.sub(r'\[[^\]]*\]','',raw).strip()
            m=re.search(r'(?i)(\d+(?:\.\d+)?)\s*(KG|ML|G|L)\b',clean)
            if not m:m=re.search(r'(?i)(\d+(?:\.\d+)?)\s*(KG|ML|G|L)(?=[xX×*\d\s)])',clean)
            if not m:continue
            n=clean[:m.start()].rstrip(' (');size=m.group(1)+m.group(2).lower()
            if '+' in n or '/' in n:continue
            n=re.sub(r'\s+',' ',n).strip()
            if n.startswith('오뚜기 '):n=n[len('오뚜기 '):]
            # Large wholesale packs do not support the convenience-store demo distribution.
            mass=float(m.group(1))*(1000 if m.group(2).lower() in ['kg','l'] else 1)
            if mass>600:continue
            add(n+' '+size,'오뚜기',cat,size,None,a['href'],sid,raw,{'unit_derivation':'source mass; multipack count omitted for simulated one-unit catalog'})
        print('otoki',cid,len(items),'cumulative',len(RECORDS),flush=True)

def collect_bing():
    html,sid=fetch('https://www.bing.co.kr/product/getProductList',{'pdt_code':'','page_cnt':128,'search_name':'','tag_type':'1','lang':'KO'})
    families={i['FAMILY_IDX']:i for i in json.loads(html)['list']}
    # Representative bounded families selected across ice cream, dairy, coffee, drinks and snacks.
    selected=[123,38,43,51,111,25,35,31,248,247,76,77,78,79,6,17,18,7,8,11,13,14,20,23,156]
    for fid in selected:
        f=families[fid];url='https://www.bing.co.kr/product/detail?PDT='+str(fid)
        html,fsid=fetch(url);soup=BeautifulSoup(html,'html.parser');family=f['FAMILY_NAME'].strip()
        variants=[]
        for li in soup.select('li.product_item'):
            match=re.search(r'choose_cate\((\d+)\)',li.get('onclick',''))
            if not match:continue
            info,isid=fetch('https://www.bing.co.kr/product/get_family_ind_info',{'family_ind_idx':int(match.group(1)),'PDT':fid,'lang':'KO'})
            obj=json.loads(info)
            SOURCES[isid]['public_page']=url;SOURCES[isid]['provenance']='official_manufacturer_public_product_selector'
            for prod in obj.get('prodList',[]):
                variants.append((prod['PROD_IDX'],prod['PROD_NAME'],isid))
        if not variants:
            for li in soup.select('#taste_area li'):
                match=re.search(r'get_volume_list\((\d+)\)',li.get('onclick',''));label=li.select_one('.name')
                if match and label:
                    flavor=label.get_text(' ',strip=True)
                    name=flavor if family in flavor else family+' '+flavor
                    variants.append((int(match.group(1)),name,fsid))
        if not variants:
            # Single variant pages expose initial size; myname is volume id, not product id.
            if soup.select('#volume_area button[myname]'):variants.append((None,family,fsid))
        if fid in [76,77,78,79,80]:cat='스낵·과자·초콜릿'
        elif fid in [111,142,153,115,109,25,26,123,65,71,72,38,39,40,43,45,48,52,53]:cat='커피·우유·요거트'
        elif fid in [35,93,36,31,248,247,51]:cat='음료·생수·차'
        elif fid==156:cat='샌드위치·버거·빵'
        else:cat='디저트·아이스크림'
        for prod,name,isid in variants:
            if prod is None:
                vsid=fsid;sizes=[b.get_text(' ',strip=True) for b in soup.select('#volume_area button[myname]')]
            else:
                vals,vsid=fetch('https://www.bing.co.kr/product/get_volume_list',{'prod_idx':prod,'lang':'KO'})
                sizes=[v['AMT_INFO'] for v in json.loads(vals)['list']]
            SOURCES[vsid]['public_page']=url;SOURCES[vsid]['provenance']='official_manufacturer_public_flavor_volume_selector'
            for size in sizes[:2]:
                if not re.fullmatch(r'\d+(?:\.\d+)?\s*(?:ml|mL|ML|g|G)',size):continue
                mass=float(re.match(r'[\d.]+',size).group())
                if mass>1000:continue
                add(name+' '+size,'빙그레',cat,size,None,url,vsid,extra={'name_source_id':isid,'family_source_id':fsid,'source_family':family})
        print('bing',fid,family,'cumulative',len(RECORDS),flush=True)

def save():
    (ROOT/'catalog-candidates.json').write_text(json.dumps(RECORDS,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'sources-metadata.json').write_text(json.dumps(list(SOURCES.values()),ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
    try:collect_otoki();collect_bing()
    finally:save()
