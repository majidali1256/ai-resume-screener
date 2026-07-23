"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  Sparkles,
  RefreshCw,
  ShieldCheck,
  Zap,
  ArrowRight,
  Download,
  Copy,
  Check,
} from "lucide-react";

interface AssessmentResult {
  match_score: number;
  score_rationale: string;
  matched_requirements: string[];
  missing_requirements: string[];
  suggestions: string[];
  limitations?: string[];
  grounding?: {
    is_grounded: boolean;
    confidence_score: number;
    unsupported_claims: string[];
  };
}

export default function Home() {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"matched" | "missing" | "suggestions">("matched");

  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleJdFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setJdFile(e.target.files[0]);
    }
  };

  const handleDemoScan = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8001/api/demo");
      if (!res.ok) throw new Error("Backend server error");
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch demo benchmark scan");
    } finally {
      setIsLoading(false);
    }
  };

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resumeFile) {
      setError("Please select a candidate resume file (.pdf, .docx, .txt)");
      return;
    }
    if (!jdText.trim() && !jdFile) {
      setError("Please provide a job description (text or file)");
      return;
    }

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("resume_file", resumeFile);
    if (jdFile) {
      formData.append("jd_file", jdFile);
    }
    if (jdText.trim()) {
      formData.append("jd_text", jdText);
    }

    try {
      const response = await fetch("http://localhost:8001/api/scan", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to connect to scanner API" }));
        const message = typeof errorData.detail === "string" ? errorData.detail : "Scanning failed. Check API key and backend logs.";
        throw new Error(message);
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred during scan.");
    } finally {
      setIsLoading(false);
    }
  };

  const copyResultJSON = () => {
    if (!result) return;
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400 border-emerald-500/50 bg-emerald-500/10";
    if (score >= 60) return "text-amber-400 border-amber-500/50 bg-amber-500/10";
    return "text-rose-400 border-rose-500/50 bg-rose-500/10";
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white">
      {/* Background Glow Orbs */}
      <div className="fixed top-0 left-1/4 w-96 h-96 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-10 right-1/4 w-96 h-96 bg-purple-600/15 rounded-full blur-3xl pointer-events-none" />

      {/* Header / Navbar */}
      <header className="border-b border-slate-800/80 backdrop-blur-md bg-slate-950/60 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-indigo-300">
                MATCH.AI
              </span>
              <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">
                v2.0 Next.js
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={handleDemoScan}
              disabled={isLoading}
              className="text-xs font-semibold px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center space-x-2"
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Load Quick Demo</span>
            </button>
            <a
              href="https://github.com/majidali1256/ai-resume-screener"
              target="_blank"
              rel="noreferrer"
              className="text-xs font-medium text-slate-400 hover:text-slate-200 transition"
            >
              GitHub Repo
            </a>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="text-center max-w-3xl mx-auto mb-10">
          <motion.h1
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl sm:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-indigo-300"
          >
            AI Resume Screener & Feedback System
          </motion.h1>
          <p className="mt-4 text-base sm:text-lg text-slate-400">
            Upload candidate resumes, compare against job descriptions, get deterministic match scores (0–100), missing keywords, and AI rewrite suggestions.
          </p>
        </div>

        {/* Form & Scanner Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-5 space-y-6">
            <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                <Upload className="w-5 h-5 text-indigo-400" />
                <span>Upload Documents</span>
              </h2>

              <form onSubmit={handleScan} className="space-y-5">
                {/* Resume Upload Dropzone */}
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-2">
                    Candidate Resume (.pdf, .docx, .txt) *
                  </label>
                  <div className="relative border-2 border-dashed border-slate-700 hover:border-indigo-500/60 rounded-xl p-4 text-center cursor-pointer transition bg-slate-900/40">
                    <input
                      type="file"
                      accept=".pdf,.docx,.doc,.txt"
                      onChange={handleResumeChange}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <FileText className="w-8 h-8 text-indigo-400 mx-auto mb-2" />
                    {resumeFile ? (
                      <div>
                        <p className="text-sm font-semibold text-emerald-400 truncate">{resumeFile.name}</p>
                        <p className="text-xs text-slate-400">{(resumeFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-xs font-medium text-slate-300">Click or drag resume here</p>
                        <p className="text-[10px] text-slate-500 mt-1">Supports PDF, DOCX, TXT (Max 10MB)</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Job Description Text Area */}
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-2">
                    Job Description Specification *
                  </label>
                  <textarea
                    rows={6}
                    value={jdText}
                    onChange={(e) => setJdText(e.target.value)}
                    placeholder="Paste job description requirements, qualifications, and required skills..."
                    className="w-full rounded-xl bg-slate-900/80 border border-slate-800 p-3 text-xs text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition resize-none"
                  />
                </div>

                {/* Optional JD File Upload */}
                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">
                    Or Upload JD File (Optional)
                  </label>
                  <input
                    type="file"
                    accept=".pdf,.docx,.doc,.txt"
                    onChange={handleJdFileChange}
                    className="block w-full text-xs text-slate-400 file:mr-4 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-300 hover:file:bg-slate-700 cursor-pointer"
                  />
                </div>

                {error && (
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-start space-x-2">
                    <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                    <span>{error}</span>
                  </div>
                )}

                {/* Submit Scan Button */}
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-3 px-4 rounded-xl font-semibold text-sm bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-600/30 transition flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin text-white" />
                      <span>Analyzing Resume with Gemini AI...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 text-indigo-200" />
                      <span>Start AI Assessment</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Results Output Section */}
          <div className="lg:col-span-7">
            <AnimatePresence mode="wait">
              {result ? (
                <motion.div
                  key="results"
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-6"
                >
                  {/* Score Overview Card */}
                  <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
                    <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
                      <div className="space-y-2 text-center sm:text-left">
                        <div className="flex items-center justify-center sm:justify-start space-x-2">
                          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                            Assessment Score
                          </span>
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                            <ShieldCheck className="w-3 h-3 mr-1 text-emerald-400" /> Grounded Verification
                          </span>
                        </div>
                        <h3 className="text-2xl font-bold text-white">
                          {result.match_score >= 80
                            ? "High Candidate Match"
                            : result.match_score >= 60
                            ? "Moderate Candidate Match"
                            : "Low Requirement Match"}
                        </h3>
                        <p className="text-xs text-slate-400 max-w-md">
                          {result.score_rationale}
                        </p>
                      </div>

                      {/* Score Circle Gauge */}
                      <div
                        className={`w-28 h-28 rounded-full border-4 flex flex-col items-center justify-center shrink-0 ${getScoreColor(
                          result.match_score
                        )}`}
                      >
                        <span className="text-3xl font-extrabold tracking-tight">{result.match_score}%</span>
                        <span className="text-[10px] uppercase font-bold text-slate-400">Score</span>
                      </div>
                    </div>

                    <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between">
                      <button
                        onClick={copyResultJSON}
                        className="text-xs text-slate-400 hover:text-slate-200 transition flex items-center space-x-1"
                      >
                        {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                        <span>{copied ? "Copied JSON!" : "Copy Raw JSON"}</span>
                      </button>
                      <button
                        onClick={() => window.print()}
                        className="text-xs text-indigo-400 hover:text-indigo-300 transition flex items-center space-x-1"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Export Assessment</span>
                      </button>
                    </div>
                  </div>

                  {/* Tabs & Content */}
                  <div className="glass-card rounded-2xl p-6">
                    <div className="flex border-b border-slate-800 mb-6">
                      <button
                        onClick={() => setActiveTab("matched")}
                        className={`pb-3 px-4 text-xs font-semibold border-b-2 transition flex items-center space-x-2 ${
                          activeTab === "matched"
                            ? "border-emerald-500 text-emerald-400"
                            : "border-transparent text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Matched Requirements ({result.matched_requirements.length})</span>
                      </button>

                      <button
                        onClick={() => setActiveTab("missing")}
                        className={`pb-3 px-4 text-xs font-semibold border-b-2 transition flex items-center space-x-2 ${
                          activeTab === "missing"
                            ? "border-rose-500 text-rose-400"
                            : "border-transparent text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <AlertTriangle className="w-4 h-4" />
                        <span>Missing Keywords ({result.missing_requirements.length})</span>
                      </button>

                      <button
                        onClick={() => setActiveTab("suggestions")}
                        className={`pb-3 px-4 text-xs font-semibold border-b-2 transition flex items-center space-x-2 ${
                          activeTab === "suggestions"
                            ? "border-amber-500 text-amber-400"
                            : "border-transparent text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <Lightbulb className="w-4 h-4" />
                        <span>Rewrite Suggestions ({result.suggestions.length})</span>
                      </button>
                    </div>

                    {/* Tab Panels */}
                    {activeTab === "matched" && (
                      <div className="space-y-3">
                        {result.matched_requirements.length === 0 ? (
                          <p className="text-xs text-slate-500 italic">No matched requirements found.</p>
                        ) : (
                          result.matched_requirements.map((req, idx) => (
                            <div
                              key={idx}
                              className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-slate-200 text-xs flex items-start space-x-3"
                            >
                              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                              <span>{req}</span>
                            </div>
                          ))
                        )}
                      </div>
                    )}

                    {activeTab === "missing" && (
                      <div className="space-y-3">
                        {result.missing_requirements.length === 0 ? (
                          <p className="text-xs text-slate-500 italic">No missing requirements flagged!</p>
                        ) : (
                          result.missing_requirements.map((req, idx) => (
                            <div
                              key={idx}
                              className="p-3 rounded-xl bg-rose-500/5 border border-rose-500/20 text-slate-200 text-xs flex items-start space-x-3"
                            >
                              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                              <span>{req}</span>
                            </div>
                          ))
                        )}
                      </div>
                    )}

                    {activeTab === "suggestions" && (
                      <div className="space-y-3">
                        {result.suggestions.length === 0 ? (
                          <p className="text-xs text-slate-500 italic">No rewrite suggestions generated.</p>
                        ) : (
                          result.suggestions.map((sug, idx) => (
                            <div
                              key={idx}
                              className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 text-slate-200 text-xs flex items-start space-x-3"
                            >
                              <Lightbulb className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                              <span>{sug}</span>
                            </div>
                          ))
                        )}
                      </div>
                    )}
                  </div>
                </motion.div>
              ) : (
                <div className="glass-card rounded-2xl p-12 text-center border-dashed border-2 border-slate-800">
                  <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto mb-4 border border-indigo-500/20">
                    <Sparkles className="w-8 h-8" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">Ready for Assessment</h3>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto mb-6">
                    Upload a candidate resume and job description on the left, then click &quot;Start AI Assessment&quot; to generate match scores and recommendations.
                  </p>
                  <button
                    onClick={handleDemoScan}
                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition inline-flex items-center space-x-2"
                  >
                    <Zap className="w-3.5 h-3.5 text-amber-400" />
                    <span>Run Demo Benchmark Test</span>
                  </button>
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>
    </div>
  );
}
