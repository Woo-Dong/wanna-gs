import type { Metadata } from 'next';
import './style.css';
export const metadata: Metadata = { title: '원하GS 사전점검', description: '한 탭 SQLite 저장·복원 점검' };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="ko"><body>{children}</body></html>; }
