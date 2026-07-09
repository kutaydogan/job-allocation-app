import './globals.css';
import type { Metadata } from 'next';
export const metadata: Metadata = { title: 'Job Allocation MVP', description: 'Lokale Job Allocation App' };
export default function RootLayout({ children }: { children: React.ReactNode }) { return <html lang="de"><body>{children}</body></html>; }
