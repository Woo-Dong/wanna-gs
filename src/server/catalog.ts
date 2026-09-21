import { createHash } from 'node:crypto';
import rawProducts from '../../data/seed/products.json';
import seedConfig from '../../data/seed/config.json';
import type { Product } from '../contracts/domain';
export const products=rawProducts as Product[];
export const productById=new Map(products.map(p=>[p.sku,p]));
export const categories=[...new Set(products.map(p=>p.category))];
export const catalogHash=createHash('sha256').update(JSON.stringify(products)).digest('hex');
export const catalogVersion=seedConfig.catalog;
// The complete small demo catalog keeps non-literal Korean requests in recall.
// All prices/availability are excluded: the browser reads its current SQLite conditions.
export const catalogContext=products.map(p=>({id:p.sku,name:p.name,brand:p.brand,category:p.category,size:p.size,flavor:p.flavor,aliases:p.aliases,observed:p.attributes.observedNameTerms}));
