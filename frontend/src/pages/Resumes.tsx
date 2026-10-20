import React, { useState, useEffect } from 'react';
import { resumeApi } from '../services/api';
import { Resume } from '../types';
import {
  FileText,
  Upload,
  Trash2,
  Calendar,
  Layers,
  GraduationCap,
  Briefcase,
  AlertCircle,
  CheckCircle2,
  Download,
  Eye,
  X
} from 'lucide-react';

export const Resumes: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [previewResume, setPreviewResume] = useState<Resume | null>(null);

  const fetchResumes = async () => {
    try {
      const res = await resumeApi.list();
      setResumes(res.resumes);
    } catch (err: any) {
      setError('Failed to load resumes.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setUploading(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const newResume = await resumeApi.upload(formData);
      setResumes(prev => [newResume, ...prev]);
      setSuccess(`Successfully uploaded and parsed "${file.name}".`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload PDF resume.');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!window.confirm(`Are you sure you want to delete "${name}"?`)) return;
    try {
      await resumeApi.delete(id);
      setResumes(prev => prev.filter(r => r.id !== id));
      setSuccess(`Deleted "${name}".`);
      if (previewResume?.id === id) setPreviewResume(null);
    } catch (err: any) {
      setError('Failed to delete resume.');
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <span className="text-[11px] font-bold text-[#7657B8] uppercase tracking-wider">Candidate Assets</span>
          <h1 className="text-2xl font-bold text-[#111111] mt-0.5">Resume Version Library</h1>
          <p className="text-xs text-[#555555]">Manage, version, and inspect extracted resume sections for matching.</p>
        </div>

        {/* Upload Button */}
        <div>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
            id="lib-resume-upload"
          />
          <label
            htmlFor="lib-resume-upload"
            className="cursor-pointer inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#7657B8] hover:bg-[#6345A3] text-white font-semibold text-xs shadow-sm shadow-[#7657B8]/20 transition-all hover:scale-102"
          >
            {uploading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Extracting PDF...
              </>
            ) : (
              <>
                <Upload className="w-3.5 h-3.5" />
                Upload New Resume PDF
              </>
            )}
          </label>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-[#F8ECE7] border border-[#F1D0C5] text-xs text-[#C04828] flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="p-4 rounded-xl bg-[#E3F6F1] border border-[#C6EFE4] text-xs text-[#137333] flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {/* Resumes Grid */}
      {loading ? (
        <div className="py-12 flex justify-center">
          <div className="w-8 h-8 border-3 border-[#EDE5F8] border-t-[#7657B8] rounded-full animate-spin"></div>
        </div>
      ) : resumes.length === 0 ? (
        <div className="p-12 rounded-3xl bg-white border border-[#E4DDEA] text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-[#EDE5F8] text-[#7657B8] flex items-center justify-center mx-auto">
            <FileText className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-base text-[#111111]">No resumes uploaded yet</h3>
          <p className="text-xs text-[#555555] max-w-sm mx-auto">
            Upload your PDF resume to extract structural experience, qualifications, and project evidence.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resumes.map((r) => (
            <div
              key={r.id}
              className="bg-white p-5 rounded-2xl border border-[#E4DDEA] hover:border-[#7657B8] transition-colors shadow-xs flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="w-9 h-9 rounded-xl bg-[#EDE5F8] text-[#7657B8] flex items-center justify-center shrink-0">
                    <FileText className="w-5 h-5" />
                  </div>
                  <button
                    onClick={() => handleDelete(r.id, r.original_filename)}
                    title="Delete resume"
                    className="p-1.5 rounded-lg text-[#888888] hover:text-[#C04828] hover:bg-[#F8ECE7] transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div>
                  <h3 className="font-bold text-sm text-[#111111] truncate" title={r.original_filename}>
                    {r.original_filename}
                  </h3>
                  <span className="text-[11px] font-semibold text-[#7657B8] bg-[#EDE5F8] px-2 py-0.5 rounded-full inline-block mt-1">
                    {r.detected_role || 'Candidate'}
                  </span>
                </div>

                <div className="space-y-1.5 text-xs text-[#555555] pt-2 border-t border-[#F0EDF5]">
                  <div className="flex items-center gap-2">
                    <Briefcase className="w-3.5 h-3.5 text-[#777777]" />
                    <span>Exp: {r.experience_summary?.total_years_display || 'Not clearly specified'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <GraduationCap className="w-3.5 h-3.5 text-[#777777]" />
                    <span className="truncate" title={r.education_summary?.education_display}>
                      {r.education_summary?.education_display || 'Degree not specified'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-[10px] text-[#888888]">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>Uploaded: {r.created_at.slice(0, 10)}</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-[#F0EDF5] flex items-center justify-between">
                <button
                  onClick={() => setPreviewResume(r)}
                  className="text-xs font-semibold text-[#7657B8] hover:underline flex items-center gap-1"
                >
                  <Eye className="w-3.5 h-3.5" /> Inspect Parsed Text
                </button>
                {r.download_url && r.download_url !== '#' && (
                  <a
                    href={r.download_url}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1.5 rounded-lg text-[#555555] hover:text-[#111111] hover:bg-[#FAF9FC]"
                    title="Download File"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Text Preview Modal */}
      {previewResume && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white w-full max-w-2xl rounded-3xl p-6 border border-[#E4DDEA] shadow-2xl max-h-[85vh] flex flex-col">
            <div className="flex justify-between items-center pb-4 border-b border-[#F0EDF5]">
              <div>
                <h3 className="font-bold text-base text-[#111111]">{previewResume.original_filename}</h3>
                <span className="text-[11px] text-[#555555]">
                  Extracted Content ({previewResume.char_count} chars • {previewResume.word_count} words)
                </span>
              </div>
              <button
                onClick={() => setPreviewResume(null)}
                className="p-1.5 rounded-lg text-[#555555] hover:bg-[#FAF9FC]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="overflow-y-auto py-4 text-xs font-mono text-[#333333] whitespace-pre-wrap leading-relaxed bg-[#FAF9FC] p-4 rounded-xl mt-4 border border-[#E4DDEA]">
              {previewResume.extracted_text_preview}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
