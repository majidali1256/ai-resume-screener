"use client";

import React, { useState, useEffect } from "react";
import { 
  BookOpen, 
  Upload, 
  Search, 
  Sparkles, 
  Database, 
  Layers, 
  CheckCircle2, 
  FileText, 
  Clock, 
  BrainCircuit, 
  ChevronRight, 
  AlertCircle,
  Code,
  ListOrdered,
  RefreshCw,
  Zap,
  HelpCircle,
  BookMarked,
  Copy,
  Check
} from "lucide-react";

interface ChunkResult {
  score: number;
  chunk_id: string;
  text: string;
  document_name?: string;
  token_estimate?: number;
}

interface Module {
  module_number: number;
  module_title: string;
  estimated_minutes: number;
  key_concepts: string[];
  learning_objectives: string[];
  action_steps: string[];
  review_questions: string[];
}

interface Terminology {
  term: string;
  definition: string;
}

interface StudyPlan {
  title: string;
  target_topic: string;
  overview: string;
  estimated_total_hours: number;
  modules: Module[];
  key_terminology: Terminology[];
  checkpoint_tips: string[];
  retrieved_chunks_used?: number;
}

interface IngestStats {
  filename: string;
  total_characters: number;
  total_chunks: number;
  stored_vectors: number;
  collection_name: string;
}

export default function StudyCompanionDashboard() {
  const [apiUrl, setApiUrl] = useState<string>(
    process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8002"
  );

  // System State
  const [systemOnline, setSystemOnline] = useState<boolean>(false);
  const [qdrantCollection, setQdrantCollection] = useState<string>("study_companion_chunks");
  const [vectorCount, setVectorCount] = useState<number>(0);

  // Step 1: Ingestion
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isIngesting, setIsIngesting] = useState<boolean>(false);
  const [ingestStats, setIngestStats] = useState<IngestStats | null>(null);
  const [ingestError, setIngestError] = useState<string | null>(null);

  // Step 2: Retrieval
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [retrievedChunks, setRetrievedChunks] = useState<ChunkResult[]>([]);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Step 3: Plan Generation
  const [isGeneratingPlan, setIsGeneratingPlan] = useState<boolean>(false);
  const [studyPlan, setStudyPlan] = useState<StudyPlan | null>(null);
  const [planError, setPlanError] = useState<string | null>(null);
  
  // UI Tabs State
  const [activeTab, setActiveTab] = useState<"modules" | "terms" | "tips" | "json">("modules");
  const [copiedJson, setCopiedJson] = useState<boolean>(false);

  const checkHealth = () => {
    fetch(`${apiUrl}/api/health`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "online") {
          setSystemOnline(true);
          if (data.qdrant_info) {
            setQdrantCollection(data.qdrant_info.collection_name || "study_companion_chunks");
            setVectorCount(data.qdrant_info.vectors_count || 0);
          }
        }
      })
      .catch(() => setSystemOnline(false));
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, [apiUrl]);

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsIngesting(true);
    setIngestError(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch(`${apiUrl}/api/ingest`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Document ingestion failed.");
      }

      const data: IngestStats = await res.json();
      setIngestStats(data);
      setVectorCount(data.stored_vectors);
      setQdrantCollection(data.collection_name);
    } catch (err: any) {
      setIngestError(err.message || "An error occurred during ingestion.");
    } finally {
      setIsIngesting(false);
    }
  };

  const handleSearchRetrieval = async (queryText?: string) => {
    const q = queryText || searchQuery;
    if (!q.trim()) return;

    setIsSearching(true);
    setSearchError(null);

    try {
      const res = await fetch(`${apiUrl}/api/retrieve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, limit: 4 }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Retrieval search failed.");
      }

      const data = await res.json();
      setRetrievedChunks(data.chunks || []);
    } catch (err: any) {
      setSearchError(err.message || "Retrieval error.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleGenerateStudyPlan = async () => {
    if (!searchQuery.trim()) return;

    setIsGeneratingPlan(true);
    setPlanError(null);

    try {
      const res = await fetch(`${apiUrl}/api/generate-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery, limit: 4 }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Study plan generation failed.");
      }

      const planData: StudyPlan = await res.json();
      setStudyPlan(planData);
      setActiveTab("modules");
    } catch (err: any) {
      setPlanError(err.message || "Failed to generate study plan.");
    } finally {
      setIsGeneratingPlan(false);
    }
  };

  const copyJsonToClipboard = () => {
    if (!studyPlan) return;
    navigator.clipboard.writeText(JSON.stringify(studyPlan, null, 2));
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };

  const suggestedTopics = [
    "Neural Networks & Deep Learning",
    "Linear Algebra & Vectors",
    "Data Structures & Algorithms",
    "Computer Vision Architecture"
  ];

  return (
    <div className="min-h-screen bg-[#060913] text-slate-100 flex flex-col font-sans pb-20">
      
      {/* Navbar / Top Header */}
      <header className="border-b border-slate-800/80 bg-[#090d19]/90 backdrop-blur-xl sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3.5">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-purple-600 via-indigo-500 to-emerald-400 p-[1px] shadow-lg shadow-purple-900/30">
              <div className="w-full h-full bg-[#0b0f1d] rounded-[15px] flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-purple-400" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
                AI Study Companion
                <span className="text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30">
                  RAG Vector Pipeline
                </span>
              </h1>
              <p className="text-xs text-slate-400">Zeppelin Lab Fellowship • Week 3 Part 1</p>
            </div>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800">
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-slate-400">Collection:</span>
              <span className="font-mono text-cyan-300 font-medium">{qdrantCollection}</span>
              <span className="text-slate-500">({vectorCount} vectors)</span>
            </div>

            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800">
              <span className={`w-2 h-2 rounded-full ${systemOnline ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`}></span>
              <span className="text-slate-200 font-medium">{systemOnline ? "API Online (Port 8002)" : "Connecting..."}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Layout */}
      <main className="max-w-7xl mx-auto px-6 pt-8 w-full grid grid-cols-1 lg:grid-cols-12 gap-8 flex-1">
        
        {/* Left Column (5 Cols): Ingestion & Vector Retrieval */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Step 1 Card: Document Ingestion */}
          <div className="glass-panel rounded-2xl p-6 relative overflow-hidden">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <span className="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs flex items-center justify-center border border-emerald-500/30">1</span>
                Document Ingestion
              </h2>
              <span className="text-[11px] text-slate-400 bg-slate-800/80 px-2.5 py-1 rounded-md font-mono">.pdf .docx .txt</span>
            </div>

            <form onSubmit={handleFileUpload} className="space-y-4">
              <div className="border-2 border-dashed border-slate-800 hover:border-purple-500/50 transition-all rounded-2xl p-6 text-center cursor-pointer bg-slate-950/40 relative group">
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="absolute inset-0 opacity-0 cursor-pointer w-full h-full z-10"
                />
                <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <Upload className="w-6 h-6 text-purple-400" />
                </div>
                <p className="text-sm font-semibold text-slate-200">
                  {selectedFile ? selectedFile.name : "Choose Syllabus or Study Notes"}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Chunks document into ~350 tokens & indexes into Qdrant DB
                </p>
              </div>

              <button
                type="submit"
                disabled={!selectedFile || isIngesting}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-emerald-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer"
              >
                {isIngesting ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
                    Chunking & Indexing Embeddings...
                  </>
                ) : (
                  <>
                    <Database className="w-4 h-4 text-slate-950" />
                    Ingest & Store in Qdrant
                  </>
                )}
              </button>
            </form>

            {ingestError && (
              <div className="mt-4 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                {ingestError}
              </div>
            )}

            {ingestStats && (
              <div className="mt-4 p-4 rounded-xl bg-slate-900/80 border border-emerald-500/30 space-y-3">
                <div className="flex items-center justify-between text-xs text-emerald-400 font-semibold">
                  <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4" /> Indexing Complete</span>
                  <span className="font-mono text-[10px] bg-emerald-500/15 px-2 py-0.5 rounded border border-emerald-500/30">{ingestStats.collection_name}</span>
                </div>

                <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800 text-center text-xs">
                  <div className="p-2 rounded-lg bg-slate-950/60">
                    <div className="text-[10px] text-slate-500 uppercase font-mono">Document</div>
                    <div className="font-bold text-slate-200 truncate mt-0.5">{ingestStats.filename}</div>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-950/60">
                    <div className="text-[10px] text-slate-500 uppercase font-mono">Chunks</div>
                    <div className="font-bold text-purple-400 mt-0.5">{ingestStats.total_chunks}</div>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-950/60">
                    <div className="text-[10px] text-slate-500 uppercase font-mono">Vectors</div>
                    <div className="font-bold text-cyan-400 mt-0.5">{ingestStats.stored_vectors}</div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Step 2 Card: Qdrant Vector Retrieval */}
          <div className="glass-panel rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <span className="w-6 h-6 rounded-lg bg-cyan-500/20 text-cyan-400 text-xs flex items-center justify-center border border-cyan-500/30">2</span>
                Vector Similarity Search
              </h2>
            </div>

            <form onSubmit={(e) => { e.preventDefault(); handleSearchRetrieval(); }} className="space-y-3">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Enter topic (e.g., Neural Networks)..."
                  className="w-full bg-slate-950/80 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none transition-all pr-24 font-medium"
                />
                <button
                  type="submit"
                  disabled={!searchQuery.trim() || isSearching}
                  className="absolute right-2 top-2 bottom-2 px-3.5 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-xs rounded-lg transition-colors border border-cyan-500/40 font-semibold flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  {isSearching ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
                  Search
                </button>
              </div>

              {/* Quick Topic Chips */}
              <div className="flex flex-wrap gap-1.5 pt-1">
                {suggestedTopics.map((topic, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => { setSearchQuery(topic); handleSearchRetrieval(topic); }}
                    className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 text-slate-400 hover:text-cyan-300 border border-slate-800 transition-colors"
                  >
                    + {topic}
                  </button>
                ))}
              </div>
            </form>

            {searchError && (
              <div className="mt-3 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                {searchError}
              </div>
            )}

            {/* Retrieved Vector Chunks Display */}
            {retrievedChunks.length > 0 && (
              <div className="mt-5 space-y-3">
                <div className="flex items-center justify-between text-xs text-slate-400 px-1 font-mono">
                  <span>Retrieved Qdrant Chunks:</span>
                  <span className="text-cyan-400 font-bold">{retrievedChunks.length} Context Items</span>
                </div>

                <div className="space-y-2.5 max-h-[340px] overflow-y-auto pr-1">
                  {retrievedChunks.map((chunk, idx) => (
                    <div key={idx} className="glass-card glass-card-hover rounded-xl p-3.5 text-xs space-y-2">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="font-mono text-slate-400 font-medium">{chunk.chunk_id}</span>
                        <span className="text-emerald-400 font-bold bg-emerald-500/15 px-2 py-0.5 rounded-full border border-emerald-500/30 font-mono">
                          {(chunk.score * 100).toFixed(1)}% match
                        </span>
                      </div>
                      <p className="text-slate-300 leading-relaxed line-clamp-3">{chunk.text}</p>
                    </div>
                  ))}
                </div>

                <button
                  onClick={handleGenerateStudyPlan}
                  disabled={isGeneratingPlan}
                  className="w-full mt-4 py-3 px-4 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-700 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-sm transition-all shadow-lg shadow-purple-900/30 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  {isGeneratingPlan ? (
                    <>
                      <Sparkles className="w-4 h-4 animate-spin text-white" />
                      Generating JSON Study Plan via Gemini...
                    </>
                  ) : (
                    <>
                      <BrainCircuit className="w-4 h-4 text-purple-300" />
                      Generate AI Study Plan
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Right Column (7 Cols): Interactive AI Study Plan Output */}
        <div className="lg:col-span-7">
          <div className="glass-panel rounded-2xl p-6 min-h-[640px] flex flex-col">
            
            {/* Header & Tabs */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-3">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                Structured JSON Study Plan
              </h2>

              {studyPlan && (
                <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
                  <button
                    onClick={() => setActiveTab("modules")}
                    className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                      activeTab === "modules" ? "bg-purple-600 text-white font-semibold" : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <ListOrdered className="w-3.5 h-3.5" /> Modules
                  </button>
                  <button
                    onClick={() => setActiveTab("terms")}
                    className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                      activeTab === "terms" ? "bg-purple-600 text-white font-semibold" : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <BookMarked className="w-3.5 h-3.5" /> Terms
                  </button>
                  <button
                    onClick={() => setActiveTab("tips")}
                    className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                      activeTab === "tips" ? "bg-purple-600 text-white font-semibold" : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <Zap className="w-3.5 h-3.5" /> Tips
                  </button>
                  <button
                    onClick={() => setActiveTab("json")}
                    className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                      activeTab === "json" ? "bg-purple-600 text-white font-semibold" : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <Code className="w-3.5 h-3.5" /> JSON
                  </button>
                </div>
              )}
            </div>

            {planError && (
              <div className="my-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                {planError}
              </div>
            )}

            {!studyPlan && !isGeneratingPlan && (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-500">
                <div className="w-16 h-16 rounded-3xl bg-slate-900/80 border border-slate-800 flex items-center justify-center mb-4">
                  <Layers className="w-8 h-8 text-purple-400 stroke-[1.5]" />
                </div>
                <p className="text-base font-bold text-slate-300">No Study Plan Generated</p>
                <p className="text-xs text-slate-500 max-w-md mt-1.5 leading-relaxed">
                  Upload study notes on the left, type a target topic, search Qdrant vector DB for relevant chunks, then click <span className="text-purple-400 font-semibold">"Generate AI Study Plan"</span>.
                </p>
              </div>
            )}

            {isGeneratingPlan && (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-400">
                <div className="relative mb-6">
                  <div className="w-16 h-16 rounded-3xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center animate-pulse">
                    <Sparkles className="w-8 h-8 text-purple-400 animate-spin" />
                  </div>
                </div>
                <p className="text-base font-bold text-white">Generating Structured JSON Plan</p>
                <p className="text-xs text-slate-400 max-w-sm mt-1.5">
                  Gemini Flash is processing retrieved Qdrant context chunks & generating Pydantic schema validated JSON...
                </p>
              </div>
            )}

            {studyPlan && (
              <div className="mt-6 flex-1 space-y-6">
                
                {/* Hero Summary Card */}
                <div className="p-5 rounded-2xl bg-gradient-to-r from-purple-900/40 via-indigo-900/30 to-slate-900 border border-purple-500/30 relative overflow-hidden">
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                    <span className="text-xs font-mono font-bold text-purple-300 bg-purple-500/20 px-3 py-1 rounded-full border border-purple-500/30">
                      Target Topic: {studyPlan.target_topic}
                    </span>
                    <span className="text-xs text-slate-300 flex items-center gap-1.5 font-medium bg-slate-900/80 px-2.5 py-1 rounded-lg border border-slate-800">
                      <Clock className="w-3.5 h-3.5 text-purple-400" /> {studyPlan.estimated_total_hours} Hours Total
                    </span>
                  </div>
                  <h3 className="text-lg font-extrabold text-white mb-2">{studyPlan.title}</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">{studyPlan.overview}</p>
                </div>

                {/* TAB 1: MODULES */}
                {activeTab === "modules" && (
                  <div className="space-y-4">
                    {studyPlan.modules.map((mod, idx) => (
                      <div key={idx} className="glass-card glass-card-hover rounded-2xl p-4 space-y-3.5">
                        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                          <h4 className="text-sm font-bold text-slate-100 flex items-center gap-2.5">
                            <span className="w-7 h-7 rounded-xl bg-emerald-500/20 text-emerald-400 text-xs font-extrabold flex items-center justify-center border border-emerald-500/30">
                              {mod.module_number}
                            </span>
                            {mod.module_title}
                          </h4>
                          <span className="text-xs text-slate-400 font-mono bg-slate-950 px-2.5 py-1 rounded-md border border-slate-800">
                            {mod.estimated_minutes} mins
                          </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                          {/* Key Concepts */}
                          <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400 block mb-2 font-mono">
                              Key Concepts
                            </span>
                            <ul className="space-y-1.5">
                              {mod.key_concepts.map((c, i) => (
                                <li key={i} className="text-slate-300 flex items-start gap-1.5">
                                  <ChevronRight className="w-3.5 h-3.5 text-purple-400 shrink-0 mt-0.5" />
                                  <span>{c}</span>
                                </li>
                              ))}
                            </ul>
                          </div>

                          {/* Action Steps */}
                          <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 block mb-2 font-mono">
                              Action Steps
                            </span>
                            <ul className="space-y-1.5">
                              {mod.action_steps.map((a, i) => (
                                <li key={i} className="text-slate-300 flex items-start gap-1.5">
                                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                                  <span>{a}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>

                        {/* Review Questions */}
                        {mod.review_questions && mod.review_questions.length > 0 && (
                          <div className="p-3 rounded-xl bg-purple-950/20 border border-purple-500/20 text-xs">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1 mb-1 font-mono">
                              <HelpCircle className="w-3 h-3 text-indigo-400" /> Review Questions
                            </span>
                            <ul className="space-y-1 pl-4 list-disc text-slate-300 text-[11px]">
                              {mod.review_questions.map((q, i) => (
                                <li key={i}>{q}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* TAB 2: TERMINOLOGY */}
                {activeTab === "terms" && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    {studyPlan.key_terminology && studyPlan.key_terminology.map((t, idx) => (
                      <div key={idx} className="glass-card rounded-xl p-4 space-y-1 border border-slate-800">
                        <div className="font-bold text-emerald-400 text-sm flex items-center gap-1.5">
                          <BookMarked className="w-3.5 h-3.5 text-emerald-400" />
                          {t.term}
                        </div>
                        <p className="text-slate-300 leading-relaxed text-xs pt-1">{t.definition}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* TAB 3: CHECKPOINT TIPS */}
                {activeTab === "tips" && (
                  <div className="space-y-3 text-xs">
                    {studyPlan.checkpoint_tips && studyPlan.checkpoint_tips.map((tip, idx) => (
                      <div key={idx} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-start gap-3">
                        <div className="w-6 h-6 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold shrink-0 mt-0.5 border border-cyan-500/30">
                          {idx + 1}
                        </div>
                        <p className="text-slate-200 leading-relaxed">{tip}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* TAB 4: RAW JSON */}
                {activeTab === "json" && (
                  <div className="relative">
                    <button
                      onClick={copyJsonToClipboard}
                      className="absolute right-3 top-3 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono flex items-center gap-1.5 border border-slate-700 transition-colors z-10 cursor-pointer"
                    >
                      {copiedJson ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" /> Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" /> Copy JSON
                        </>
                      )}
                    </button>
                    <pre className="bg-[#04060d] p-5 rounded-2xl text-xs font-mono text-emerald-400 overflow-x-auto border border-slate-800 max-h-[500px] leading-relaxed">
                      {JSON.stringify(studyPlan, null, 2)}
                    </pre>
                  </div>
                )}

              </div>
            )}
          </div>
        </div>

      </main>
    </div>
  );
}
