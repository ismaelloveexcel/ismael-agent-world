import { Metadata } from 'next';
import MemoryClient from './MemoryClient';

export const metadata: Metadata = {
  title: 'Memory | Ismael Agent World',
};

export default function MemoryPage() {
  return <MemoryClient />;
}
