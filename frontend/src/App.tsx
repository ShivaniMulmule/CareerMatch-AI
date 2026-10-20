import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { ProtectedRoute } from './components/ProtectedRoute';

// Pages
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Analyze } from './pages/Analyze';
import { Results } from './pages/Results';
import { Resumes } from './pages/Resumes';
import { Jobs } from './pages/Jobs';
import { History } from './pages/History';
import { Recommendations } from './pages/Recommendations';
import { SkillAnalytics } from './pages/SkillAnalytics';
import { Profile } from './pages/Profile';
import { Privacy } from './pages/Privacy';
import { About } from './pages/About';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="flex flex-col min-h-screen bg-[#FAF9FC] text-[#111111]">
          <Navbar />
          <main className="flex-1">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/about" element={<About />} />
              <Route path="/privacy" element={<Privacy />} />

              {/* Protected Workspace Routes */}
              <Route element={<ProtectedRoute />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/analyze" element={<Analyze />} />
                <Route path="/results/:id" element={<Results />} />
                <Route path="/resumes" element={<Resumes />} />
                <Route path="/jobs" element={<Jobs />} />
                <Route path="/history" element={<History />} />
                <Route path="/recommendations" element={<Recommendations />} />
                <Route path="/skills" element={<SkillAnalytics />} />
                <Route path="/profile" element={<Profile />} />
              </Route>

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
