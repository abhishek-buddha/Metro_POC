// Main layout with sidebar navigation
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Users,
  Clock,
  Calendar,
  FileText,
  Award,
  LogOut,
  Bell,
  MessageSquare
} from 'lucide-react';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const location = useLocation();

  const sidebarItems = [
    { icon: Home, label: 'HR Home', path: '/' },
    { icon: Users, label: 'Employee Management', path: '/' },
    { icon: Clock, label: 'Attendance Management', path: '/attendance' },
    { icon: Calendar, label: 'Leave Management', path: '/leave' },
    { icon: FileText, label: 'Actions', path: '/actions' },
    { icon: LogOut, label: 'Off-Boarding', path: '/offboarding' },
    { icon: FileText, label: 'Reports', path: '/reports' },
    { icon: Award, label: 'Promotions & Transfers', path: '/promotions' },
  ];

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-16 bg-white border-r border-gray-200 flex flex-col items-center py-4 space-y-6">
        {/* Metro Logo */}
        <div className="mb-4">
          <div className="w-10 h-10 flex items-center justify-center bg-indigo-600 rounded-lg shadow-sm">
            <span className="text-2xl font-bold text-white">m</span>
          </div>
        </div>

        {/* Navigation Icons */}
        <div className="flex-1 flex flex-col items-center space-y-6">
          {sidebarItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={index}
                to={item.path}
                className={`w-10 h-10 flex items-center justify-center rounded-lg transition-colors ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-500 hover:bg-gray-100'
                }`}
                title={item.label}
              >
                <Icon size={20} />
              </Link>
            );
          })}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-3.5 flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-3">
            <div className="text-2xl font-bold text-gray-900">
              metro
            </div>
            <div className="text-xs text-gray-500 tracking-wide">BRANDS</div>
          </div>

          <div className="flex-1 max-w-xl mx-8">
            <div className="relative">
              <input
                type="text"
                placeholder="Search menu options..."
                className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-indigo-500"
              />
              <span className="absolute right-3 top-2 text-xs text-gray-400">⌘+k</span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button className="p-2 hover:bg-gray-100 rounded-lg">
              <Bell size={20} className="text-gray-600" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg">
              <MessageSquare size={20} className="text-gray-600" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg">
              <MessageSquare size={20} className="text-gray-600" />
            </button>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">SR</span>
              </div>
              <div className="text-sm">
                <div className="font-medium text-gray-800">S RENEESH RAJA</div>
                <div className="text-xs text-gray-500">HRM (Showroom)</div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
