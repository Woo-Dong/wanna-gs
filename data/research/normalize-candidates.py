"""Deterministic normalization of observed product facts, not a seed/holdout builder."""
import json,re,hashlib,collections
from pathlib import Path
P=Path(__file__).parent
rows=json.loads((P/'catalog-candidates.json').read_text());out=[];seen=set();excluded=[]
for r in rows:
    name=r['name'];raw=r['raw_name']
    # Partner goods in a manufacturer-owned mall do not prove the umbrella brand.
    if r['brand']=='오뚜기' and any(x in name for x in ['죽장연','청담미역','로이앤메이','저온숙성자연산','리얼 프렌치','LIGHT&JOY']):
        excluded.append({'name':name,'source_url':r['source_url'],'reason':'partner_brand_requires_individual_verification'});continue
    key=re.sub(r'[\s.()]','',r['brand']+'|'+name+'|'+r['size']).lower()
    if key in seen:
        excluded.append({'name':name,'source_url':r['source_url'],'reason':'equivalent_name_and_size_spacing_duplicate'});continue
    seen.add(key)
    if r['brand']=='오뚜기':
        if re.search('뿌셔|팝콘|나쵸|프레첼|크리스피롤',name):r['category']='스낵·과자·초콜릿'
        elif re.search('호빵|십원빵|붕어빵|핫도그|크로크무슈',name):r['category']='샌드위치·버거·빵'
        elif '스위트앤젤' in name:r['category']='디저트·아이스크림'
        r['field_origin']['brand']='official_brand_owned_retail_catalog; umbrella_brand_inference'
        r['brand_confidence']='medium_catalog_owner_inference'
    else:r['brand_confidence']='high_official_manufacturer_catalog'
    # Exact lexical labels only; no nutritional certification or invented flavors.
    terms=[t for t in ['무가당','제로','저당','고단백','식이섬유플러스','매운맛','순한맛','약간매운맛','오리지널','초코','딸기','바나나','메론','불고기','바베큐'] if t in name]
    r['attributes']={'observed_name_terms':terms}
    r['attribute_warning']='name tokens only; do not infer allergy, nutrition, certification or current popularity'
    m=re.search(r'(약간매운맛|매운맛|순한맛|[가-힣]+맛)',name)
    r['flavor']=m.group(1) if m else None
    r['field_origin']['flavor']='exact_source_name_token' if m else 'unverified'
    r['source_type']='official_manufacturer_catalog_or_brand_owned_retail'
    r['published_at']=None;r['evidence_scope']='observed product name and mass/volume; no store availability, demand or popularity claim'
    r['license_or_usage_note']='Only minimal product-identification facts retained; source text/images/prices not redistributed.'
    r['normalization_version']='NORM-20260921-v1'
    out.append(r)
(P/'catalog-candidates.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(P/'normalization-report.json').write_text(json.dumps({'input':len(rows),'output':len(out),'excluded':excluded,'categories':dict(collections.Counter(r['category'] for r in out)),'brand':dict(collections.Counter(r['brand'] for r in out)),'status':'raw_candidate_preparation_only_independent_review_pending'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'input':len(rows),'output':len(out),'categories':dict(collections.Counter(r['category'] for r in out))},ensure_ascii=False))
