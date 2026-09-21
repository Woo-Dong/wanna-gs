import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: '원하GS(원하지쓰)', description: '원하는 말은 상품으로, 모인 수요는 사장님의 쉬운 판단으로.' };
export default function Layout({children}:{children:React.ReactNode}) {return <html lang="ko"><body>{children}</body></html>;}
