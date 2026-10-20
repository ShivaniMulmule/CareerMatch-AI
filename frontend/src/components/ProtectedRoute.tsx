import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const ProtectedRoute: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF9FC]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-[#EDE5F8] border-t-[#7657B8] rounded-full animate-spin"></div>
          <p className="text-xs text-[#555555] font-medium">Authenticating session...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};
