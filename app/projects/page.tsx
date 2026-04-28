import { Metadata } from 'next';
import ProjectsClient from './ProjectsClient';

export const metadata: Metadata = {
  title: 'Projects | Ismael Agent World',
};

export default function ProjectsPage() {
  return <ProjectsClient />;
}
