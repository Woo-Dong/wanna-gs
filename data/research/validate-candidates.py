"""Validate the source-preparation contract, not app/seed acceptance gates."""
from pathlib import Path
import json,hashlib,collections,math
p=Path(__file__).parent
c=json.loads((p/'catalog-candidates.json').read_text());s=json.loads((p/'stores-candidates.json').read_text());sources=json.loads((p/'sources-metadata.json').read_text());ss=json.loads((p/'stores-sources-metadata.json').read_text())
sids={i['source_id'] for i in sources};ssids={i['source_id'] for i in ss['sources']}
assert len(c)>=200
assert len({i['sku'] for i in c})==len(c)
assert len({i['normalized_key'] for i in c})==len(c)
assert len({i['category'] for i in c})>=7
assert all(i['source_id'] in sids and i['name'] and i['size'] and i['source_url'].startswith('https://') for i in c)
assert all(i['trend_confidence']=='unverified' and i['gs25_availability']=='simulated_not_verified' and i['inventory_origin']=='simulated_only' and i['price_origin']=='simulated_only' for i in c)
assert all(not i['aliases'] for i in c)
assert 8<=len(s)<=12
assert len({i['address'] for i in s})==len(s)
assert all(37.54<i['lat']<37.56 and 127.06<i['lng']<127.08 and i['source_id'] in ssids for i in s)
assert all(i['current_operating_status']=='unverified' for i in s)
result={'checked_at':'2026-09-21','scope':'source_candidates_only','result':'PASS','product_count':len(c),'store_count':len(s),'categories':dict(collections.Counter(i['category'] for i in c)),'source_count':len(sources),'store_source_count':len(ss['sources']),'file_sha256':{n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in ['catalog-candidates.json','stores-candidates.json','sources-metadata.json','stores-sources-metadata.json']},'checks':['at_least_200_observed_product_candidates','unique_internal_sku_and_normalized_key','at_least_7_categories','source_id_reference_integrity','simulation_and_unverified_trend_labels','no_alias_or_holdout_injection','8_to_12_unique_store_addresses','lat_lng_order_and_local_bbox','reported_operation_status_unverified'],'not_verified':['independent_source_review','current_store_operations','GS25_product_availability','20_to_30_recent_trend_products','balanced_final_seed_categories','SQLite_seed_dryrun_and_rollback','application_or_live_model_gates']}
(p/'validation-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
