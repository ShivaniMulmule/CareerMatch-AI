import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/api';
import { BrainCircuit, ArrowRight, AlertCircle } from 'lucide-react';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await authApi.login(email, password);
      login(data.access_token, data.user);
      navigate('/dashboard');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to sign in. Please verify your credentials.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md bg-white p-8 rounded-2xl border border-[#E4DDEA] shadow-sm">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#7657B8] to-[#9979DC] text-white flex items-center justify-center mx-auto mb-3 shadow-sm shadow-[#7657B8]/20">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold text-[#111111]">Welcome Back</h2>
          <p className="text-xs text-[#555555] mt-1">Sign in to your CareerMatch AI workspace</p>
        </div>

        {error && (
          <div className="mb-5 p-3 rounded-xl bg-[#F8ECE7] border border-[#F1D0C5] text-xs text-[#C04828] flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#111111] mb-1.5">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="candidate@example.com"
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#E4DDEA] text-sm text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8] transition-colors"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="block text-xs font-semibold text-[#111111]">Password</label>
            </div>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#E4DDEA] text-sm text-[#111111] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8] transition-colors"
            />
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
                Sign In
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-[#555555]">
          Don't have an account?{' '}
          <Link to="/register" className="font-semibold text-[#7657B8] hover:underline">
            Create an account
          </Link>
        </div>
      </div>
    </div>
  );
};
