import { Metadata } from 'next';
import AgentsClient from './AgentsClient';

export const metadata: Metadata = {
  title: 'Agents | Ismael Agent World',
};

export default function AgentsPage() {
  return <AgentsClient />;
}
