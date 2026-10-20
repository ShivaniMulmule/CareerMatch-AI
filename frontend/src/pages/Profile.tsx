import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { profileApi } from '../services/api';
import { User, CheckCircle2, AlertCircle, Save } from 'lucide-react';

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

export const Profile: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [targetRole, setTargetRole] = useState(user?.target_role || ROLES[0]);
  const [experienceLevel, setExperienceLevel] = useState(user?.experience_level || EXPERIENCE_LEVELS[0]);

  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name);
      setTargetRole(user.target_role);
      setExperienceLevel(user.experience_level);
    }
  }, [user]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(null);
    setError(null);

    try {
      await profileApi.updateProfile({
        full_name: fullName,
        target_role: targetRole,
        experience_level: experienceLevel
      });
      await refreshUser();
      setSuccess('Profile and career preferences updated successfully.');
    } catch (err: any) {
      setError('Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <span className="text-[11px] font-bold text-[#7657B8] uppercase tracking-wider">Candidate Account</span>
        <h1 className="text-2xl font-bold text-[#111111] mt-0.5">Profile & Career Target</h1>
        <p className="text-xs text-[#555555]">Configure your target engineering discipline and seniority expectations.</p>
      </div>

      {success && (
        <div className="p-4 rounded-xl bg-[#E3F6F1] border border-[#C6EFE4] text-xs text-[#137333] flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-[#F8ECE7] border border-[#F1D0C5] text-xs text-[#C04828] flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-[#E4DDEA] shadow-xs">
        <form onSubmit={handleUpdate} className="space-y-5 text-xs">
          <div>
            <label className="block font-semibold text-[#111111] mb-1">Email Address</label>
            <input
              type="email"
              disabled
              value={user?.email || ''}
              className="w-full p-3 rounded-xl border border-[#E4DDEA] bg-[#F0EDF5]/50 text-[#777777] cursor-not-allowed"
            />
            <span className="text-[10px] text-[#888888] mt-1 block">Account identifier cannot be altered.</span>
          </div>

          <div>
            <label className="block font-semibold text-[#111111] mb-1">Full Name</label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full p-3 rounded-xl border border-[#E4DDEA] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8]"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-[#111111] mb-1">Primary Target Role</label>
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="w-full p-3 rounded-xl border border-[#E4DDEA] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8]"
              >
                {ROLES.map(r => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-semibold text-[#111111] mb-1">Experience Level</label>
              <select
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                className="w-full p-3 rounded-xl border border-[#E4DDEA] bg-[#FAF9FC] focus:bg-white focus:outline-none focus:border-[#7657B8]"
              >
                {EXPERIENCE_LEVELS.map(exp => (
                  <option key={exp} value={exp}>{exp}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="pt-4 border-t border-[#F0EDF5]">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 rounded-xl bg-[#7657B8] hover:bg-[#6345A3] disabled:opacity-60 text-white font-semibold text-xs shadow-xs flex items-center gap-2"
            >
              <Save className="w-3.5 h-3.5" />
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
