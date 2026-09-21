/** A narrow positive certificate, not a general Korean intent classifier.
 * Uncertain, quoted, negated or corrected prose keeps the ordinary model path.
 * This only restricts generation; it never fabricates or rewrites an answer.
 */
export function explicitExternalOperation(text:string,catalog:readonly {id:string;name:string}[]=[],storeNames:readonly string[]=[]):boolean {
 const value=text.normalize('NFKC').replace(/\s+/g,' ').trim();
 if(/["'“”‘’「」『』`<>]/u.test(value))return false;
 // A request containing non-execution, reported speech, a condition, or a later
 // correction is not certified by this deliberately small positive grammar.
 if(/(?:말고|말아|마세요|마라|하지마|하지 마|않|아니|아닌|안\s|금지|취소|대신|라고|라는|다면|으면|는지|인지|예시|문구|인용|설명)/u.test(value))return false;
 const imperative=String.raw`(?:해\s*(?:줘|주세요|주십시오|주고)|해라|해주세요|해줘|해\s*주시고)`;
 const escape=(v:string)=>v.normalize('NFKC').replace(/\s+/g,' ').replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
 const alternatives=(values:readonly string[])=>[...new Set(values)].sort((a,b)=>b.length-a.length).map(escape).join('|');
 const products=alternatives(catalog.flatMap(p=>[p.name,p.id]));
 const stores=alternatives(storeNames);
 // Every prefix is consumed: arbitrary prose before an imperative could be a
 // quotation, a reported message or an instruction to ignore it.
 const prefixes=[String.raw`(?:지금|바로|먼저|여기서|이번에는|이번엔|부탁인데)\s+`,String.raw`(?:이\s+)?영수증(?:을|도)\s+`];
 if(products)prefixes.push(`(?:${products})(?:을|를|\\s+영수증(?:을|도)?|\\s+상품을)?\\s+`);
 if(stores)prefixes.push(`(?:${stores})(?:에서|에|\\s+방문\\s+(?:전|전에|후))?\\s+`);
 const lead=`(?:${prefixes.join('|')})*`;
 const payment='(?:실제|실물|진짜)\\s*(?:내\\s*|제\\s*)?(?:(?:신용|체크)\\s*)?카드(?:로|를|에서)?\\s*(?:직접\\s*|바로\\s*|지금\\s*)?(?:결제|청구|승인)'+imperative;
 const report='본부(?:에|로)?\\s*(?:(?:매출|실적|거래)\\s*)?보고서?(?:도|를|을)?\\s*(?:실제로\\s*|직접\\s*|바로\\s*)?(?:보내\\s*(?:줘|주세요|주고)|전송'+imperative+'|제출'+imperative+')';
 const command=`(?:${payment}|${report})`;
 return new RegExp(`^${lead}${command}(?:\\s*(?:[,;]\\s*)?(?:(?:그리고|또|이어서)\\s+)?${lead}${command})*\\s*[.!?。！？]*$`,'u').test(value);
}
