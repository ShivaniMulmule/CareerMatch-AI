import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Sparkles,
  LayoutDashboard,
  FileText,
  Briefcase,
  Layers,
  Award,
  BookOpen,
  User as UserIcon,
  LogOut,
  LogIn,
  BrainCircuit
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 bg-[#FAF9FC]/90 backdrop-blur-md border-b border-[#E4DDEA] transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#7657B8] to-[#9979DC] flex items-center justify-center text-white shadow-sm shadow-[#7657B8]/20 group-hover:scale-105 transition-transform">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight text-[#111111] flex items-center gap-1.5">
                CareerMatch <span className="text-[#7657B8] text-xs font-semibold px-1.5 py-0.5 rounded bg-[#EDE5F8]">AI</span>
              </span>
              <p className="text-[10px] text-[#555555] -mt-1 hidden sm:block tracking-wide">Explainable Job Matching</p>
            </div>
          </Link>

          {/* Navigation Links */}
          {user ? (
            <div className="hidden md:flex items-center gap-1 text-sm font-medium">
              <Link
                to="/dashboard"
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                  isActive('/dashboard') ? 'bg-[#EDE5F8] text-[#7657B8]' : 'text-[#555555] hover:text-[#111111] hover:bg-[#F0EDF5]'
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                Dashboard
              </Link>

              <Link
                to="/analyze"
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                  isActive('/analyze') ? 'bg-[#EDE5F8] text-[#7657B8]' : 'text-[#555555] hover:text-[#111111] hover:bg-[#F0EDF5]'
                }`}
              >
                <Sparkles className="w-4 h-4 text-[#7657B8]" />
                Analyze Fit
              </Link>

              <Link
                to="/resumes"
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                  isActive('/resumes') ? 'bg-[#EDE5F8] text-[#7657B8]' : 'text-[#555555] hover:text-[#111111] hover:bg-[#F0EDF5]'
                }`}
              >
                <FileText className="w-4 h-4" />
                Resumes
              </Link>

              <Link
                to="/jobs"
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                  isActive('/jobs') ? 'bg-[#EDE5F8] text-[#7657B8]' : 'text-[#555555] hover:text-[#111111] hover:bg-[#F0EDF5]'
                }`}
              >
                <Briefcase className="w-4 h-4" />
                Jobs
              </Link>

              <Link
                to="/recommendations"
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                  isActive('/recommendations') ? 'bg-[#EDE5F8] text-[#7657B8]' : 'text-[#555555] hover:text-[#111111] hover:bg-[#F0EDF5]'
                }`}
              >
                <Award className="w-4 h-4" />
                Upskill Roadmap
              </Link>

              <Link
                to="/skills"
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                  isActive('/skills') ? 'bg-[#EDE5F8] text-[#7657B8]' : 'text-[#555555] hover:text-[#111111] hover:bg-[#F0EDF5]'
                }`}
              >
                <Layers className="w-4 h-4" />
                Skill Analytics
              </Link>

              <Link
                to="/about"
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                  isActive('/about') ? 'bg-[#EDE5F8] text-[#7657B8]' : 'text-[#555555] hover:text-[#111111] hover:bg-[#F0EDF5]'
                }`}
              >
                <BookOpen className="w-4 h-4" />
                AI Architecture
              </Link>
            </div>
          ) : (
            <div className="hidden md:flex items-center gap-4 text-sm font-medium">
              <Link to="/about" className="text-[#555555] hover:text-[#111111]">How AI Works</Link>
              <Link to="/privacy" className="text-[#555555] hover:text-[#111111]">Responsible AI</Link>
            </div>
          )}

          {/* User actions */}
          <div className="flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-2">
                <Link
                  to="/profile"
                  className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-full bg-white border border-[#E4DDEA] hover:border-[#7657B8] transition-colors"
                >
                  <div className="w-6 h-6 rounded-full bg-[#EDE5F8] text-[#7657B8] font-bold text-xs flex items-center justify-center">
                    {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <span className="text-xs font-medium text-[#111111] max-w-[100px] truncate">
                    {user.full_name.split(' ')[0]}
                  </span>
                </Link>
                <button
                  onClick={handleLogout}
                  title="Logout"
                  className="p-2 rounded-lg text-[#555555] hover:text-[#C04828] hover:bg-[#F8ECE7] transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2.5">
                <Link
                  to="/login"
                  className="px-3.5 py-1.5 text-sm font-medium text-[#555555] hover:text-[#111111] transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-sm font-semibold rounded-xl bg-[#7657B8] hover:bg-[#6345A3] text-white shadow-sm shadow-[#7657B8]/20 transition-all hover:scale-[1.02]"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
