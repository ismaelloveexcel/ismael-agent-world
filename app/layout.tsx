import type { Metadata } from 'next';
import './globals.css';
import Sidebar from './components/Sidebar';
import NeuralBackground from './components/NeuralBackground';

export const metadata: Metadata = {
  title: 'Ismael Agent World',
  description: 'Private animated multi-agent AI command center',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-[#0a0a0f] min-h-screen text-white font-sans">
        <NeuralBackground />
        <Sidebar />
        <main className="pl-16 lg:pl-56 min-h-screen relative z-10">
          {children}
        </main>
      </body>
    </html>
  );
}
