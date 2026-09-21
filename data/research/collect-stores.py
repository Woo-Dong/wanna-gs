"""At most 20 public pages, 10 unique GS25 location facts; never geocode or copy imagery."""
import importlib.util,json,re
from bs4 import BeautifulSoup
from pathlib import Path
spec=importlib.util.spec_from_file_location('collection',Path(__file__).with_name('collect-public.py'));c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
queue=['https://sav.purpleo.kr/article/39204'];seen=set();stores=[];addresses=set();excluded=[]
while queue and len(stores)<10 and len(seen)<20:
    url=queue.pop(0)
    if url in seen:continue
    seen.add(url);html,sid=c.fetch(url);s=BeautifulSoup(html,'html.parser')
    graph=[]
    for el in s.select('script[type="application/ld+json"]'):graph.extend(json.loads(el.string).get('@graph',[]))
    place=next((o for o in graph if o.get('@type')=='Place'),None)
    page=next((o for o in graph if o.get('@type')=='WebPage'),{})
    if not place:continue
    p={v['name']:v['value'] for v in place.get('additionalProperty',[])}
    address=p.get('도로명주소');geo=place.get('geo',{})
    if address and address not in addresses and geo:
        addresses.add(address)
        stores.append({'store_id':'STORE-PUBLIC-'+place['identifier']['value'],'name':place['name'],'brand':'GS25','address':address,'lot_address':p.get('지번주소'),'lat':geo['latitude'],'lng':geo['longitude'],'coordinate_system':'WGS84_as_reported','origin':'public_data_redistributor','source_id':sid,'source_url':url,'upstream_dataset':'소상공인시장진흥공단_상가(상권)정보','upstream_record_id':p.get('상가업소번호'),'source_published_at':page.get('datePublished'),'source_modified_at':page.get('dateModified'),'checked_at':c.CHECKED,'coordinate_confidence':'reported_public_coordinates_not_field_surveyed','current_operating_status':'unverified','inventory_origin':'simulated_only','ownership_origin':'synthetic_demo_assignment','service_participation':'simulated_not_affiliated','review_status':'candidate_independent_review_pending'})
    else:excluded.append({'url':url,'reason':'duplicate_address_or_missing_coordinate'})
    for a in s.select('a[href]'):
        href=a['href'];label=a.get_text(' ',strip=True).split('바로가기')[0]
        if re.fullmatch(r'https://sav.purpleo.kr/article/\d+',href) and re.search(r'GS\s*25|지에스\s*25|쥐에스\s*25',label,re.I) and href not in seen and href not in queue:queue.append(href)
    print(place['name'],len(stores),len(queue),flush=True)
(c.ROOT/'stores-candidates.json').write_text(json.dumps(stores,ensure_ascii=False,indent=2)+'\n')
(c.ROOT/'stores-sources-metadata.json').write_text(json.dumps({'sources':list(c.SOURCES.values()),'excluded':excluded,'public_pages_requested':len(seen),'remaining_observed_links':queue},ensure_ascii=False,indent=2)+'\n')
