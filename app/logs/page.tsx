import { Metadata } from 'next';
import LogsClient from './LogsClient';

export const metadata: Metadata = {
  title: 'Logs | Ismael Agent World',
};

export default function LogsPage() {
  return <LogsClient />;
}
