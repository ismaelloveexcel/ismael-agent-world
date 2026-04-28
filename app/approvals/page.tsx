import { Metadata } from 'next';
import ApprovalsClient from './ApprovalsClient';

export const metadata: Metadata = {
  title: 'Approvals | Ismael Agent World',
};

export default function ApprovalsPage() {
  return <ApprovalsClient />;
}
