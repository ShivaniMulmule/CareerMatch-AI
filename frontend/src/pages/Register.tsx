import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/api';
import { BrainCircuit, ArrowRight, AlertCircle } from 'lucide-react';

const ROLES = [
  "Machine Learning Engineer",
  "Data Scientist",
  "Data Analyst",
  "AI Engineer",
  "NLP Engineer",
  "Computer Vision Engineer",
  "Software Engineer",
  "Backend Developer",
  "Frontend Developer",
  "Data Engineer",
  "Cloud Engineer",
  "DevOps Engineer",
  "Business Analyst"
];

const EXPERIENCE_LEVELS = [
  "Fresher",
  "Intern",
  "0-1 years",
  "1-2 years",
  "2-3 years",
  "3-5 years",
  "5+ years"
];

export const Register: React.FC = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [targetRole, setTargetRole] = useState(ROLES[0]);
  const [experienceLevel, setExperienceLevel] = useState(EXPERIENCE_LEVELS[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await authApi.register({
        full_name: fullName,
        email,
        password,
        target_role: targetRole,
        experience_level: experienceLevel
      });
      login(data.access_token, data.user);
      navigate('/dashboard');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to create account. Please check inputs.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md bg-white p-8 rounded-2xl border border-[#E4DDEA] shadow-sm">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#7657B8] to-[#9979DC] text-white flex items-center justify-center mx-auto mb-3 shadow-sm shadow-[#7657B8]/20">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold text-[#111111]">Create an Account</h2>
          <p className="text-xs text-[#555555] mt-1">Start evaluating your resume fit with Explainable AI</p>
        </div>

        {error && (
          <div className="mb-5 p-3 rounded-xl bg-[#F8ECE7] border border-[#F1D0C5] text-xs text-[#C04828] flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#111111] mb-1.5">Full Name</label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Aarav Sharma"
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#E4DDEA] text-sm text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8] transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#111111] mb-1.5">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="aarav@example.com"
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#E4DDEA] text-sm text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8] transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#111111] mb-1.5">Password</label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 6 characters"
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#E4DDEA] text-sm text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8] transition-colors"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-[#111111] mb-1.5">Target Role</label>
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl border border-[#E4DDEA] text-xs text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8] transition-colors"
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#111111] mb-1.5">Experience</label>
              <select
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl border border-[#E4DDEA] text-xs text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8] transition-colors"
              >
                {EXPERIENCE_LEVELS.map((exp) => (
                  <option key={exp} value={exp}>{exp}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl bg-[#7657B8] hover:bg-[#6345A3] disabled:opacity-60 text-white font-semibold text-sm shadow-sm shadow-[#7657B8]/20 transition-all flex items-center justify-center gap-2"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <>
                Create Account
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-[#555555]">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-[#7657B8] hover:underline">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
