import { ReactNode } from 'react';
import Navbar from './Navbar';

interface LayoutProps {
  children: ReactNode;
  currentPath?: string;
}

export default function Layout({ children, currentPath }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar currentPath={currentPath} />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {children}
        </div>
      </main>
    </div>
  );
}
