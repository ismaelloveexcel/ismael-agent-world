import { Metadata } from 'next';
import PlaybooksClient from './PlaybooksClient';

export const metadata: Metadata = {
  title: 'Playbooks | Ismael Agent World',
};

export default function PlaybooksPage() {
  return <PlaybooksClient />;
}
