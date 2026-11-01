
import { useEffect, useState } from "react";
import {
  UploadCloud,
  FileText,
  RefreshCw,
  Search,
  Send,
  Loader2,
  BookOpen,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

import {
  getDocuments,
  uploadDocument,
  queryKnowledge,
} from "../services/api";

function KnowledgeBase() {
  const [documents, setDocuments] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [answer, setAnswer] = useState(null);
  const [notice, setNotice] = useState(null);

  async function loadDocuments() {
    setLoadingDocuments(true);

    try {
      const data = await getDocuments();
      setDocuments(Array.isArray(data) ? data : []);
    } catch (error) {
      setNotice({ type: "error", message: error.message });
    } finally {
      setLoadingDocuments(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function handleUpload(event) {
    event.preventDefault();

    if (!selectedFile) {
      setNotice({ type: "error", message: "Please select a document." });
      return;
    }

    setUploading(true);
    setNotice(null);

    try {
      await uploadDocument(selectedFile);

      setNotice({
        type: "success",
        message: `${selectedFile.name} uploaded successfully.`,
      });

      setSelectedFile(null);
      event.target.reset();

      await loadDocuments();
    } catch (error) {
      setNotice({ type: "error", message: error.message });
    } finally {
      setUploading(false);
    }
  }

  async function handleQuestion(event) {
    event.preventDefault();

    if (question.trim().length < 3) {
      setNotice({
        type: "error",
        message: "Please enter a question with at least 3 characters.",
      });
      return;
    }

    setAsking(true);
    setNotice(null);
    setAnswer(null);

    try {
      const result = await queryKnowledge(question.trim(), 4);
      setAnswer(result);
    } catch (error) {
      setNotice({ type: "error", message: error.message });
    } finally {
      setAsking(false);
    }
  }

  const documentName = (doc, index) =>
    doc.filename ||
    doc.file_name ||
    doc.name ||
    doc.title ||
    `Document ${index + 1}`;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Knowledge Base</h2>
        <p className="mt-1 text-sm text-slate-500">
          Upload support documents and retrieve answers using AI-powered RAG.
        </p>
      </div>

      {notice && (
        <div
          className={`flex items-center gap-2 rounded-lg border p-3 text-sm ${
            notice.type === "error"
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-emerald-200 bg-emerald-50 text-emerald-700"
          }`}
        >
          {notice.type === "error" ? (
            <AlertCircle size={17} />
          ) : (
            <CheckCircle2 size={17} />
          )}
          {notice.message}
        </div>
      )}

      {/* Upload section */}
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <div className="mb-5 flex items-center gap-3">
          <div className="rounded-lg bg-indigo-50 p-2 text-indigo-600">
            <UploadCloud size={22} />
          </div>
          <div>
            <h3 className="font-bold">Upload Documents</h3>
            <p className="text-xs text-slate-500">
              Add documents to your RAG knowledge base.
            </p>
          </div>
        </div>

        <form onSubmit={handleUpload}>
          <label className="flex cursor-pointer flex-col items-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-8 text-center transition hover:border-indigo-400 hover:bg-indigo-50/40">
            <FileText className="mb-3 text-indigo-600" size={32} />

            <span className="text-sm font-semibold">
              {selectedFile ? selectedFile.name : "Choose a document"}
            </span>

            <span className="mt-2 text-xs text-slate-500">
              Select a supported PDF, TXT or Markdown file
            </span>

            <input
              type="file"
              accept=".pdf,.txt,.md"
              className="hidden"
              onChange={(event) =>
                setSelectedFile(event.target.files?.[0] || null)
              }
            />
          </label>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-slate-400">
              Maximum upload size is controlled by your backend.
            </p>

            <button
              type="submit"
              disabled={!selectedFile || uploading}
              className="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {uploading && (
                <Loader2 size={16} className="animate-spin" />
              )}
              {uploading ? "Uploading..." : "Upload Document"}
            </button>
          </div>
        </form>
      </section>

      {/* Document list */}
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h3 className="font-bold">Indexed Documents</h3>
            <p className="mt-1 text-xs text-slate-500">
              Documents returned by your backend.
            </p>
          </div>

          <button
            onClick={loadDocuments}
            disabled={loadingDocuments}
            className="rounded-lg border border-slate-200 p-2 hover:bg-slate-50"
            title="Refresh documents"
          >
            <RefreshCw
              size={17}
              className={loadingDocuments ? "animate-spin" : ""}
            />
          </button>
        </div>

        {loadingDocuments ? (
          <div className="flex justify-center p-8">
            <Loader2 className="animate-spin text-indigo-600" />
          </div>
        ) : documents.length === 0 ? (
          <div className="py-8 text-center">
            <BookOpen className="mx-auto mb-3 text-slate-300" size={32} />
            <p className="text-sm font-medium">No documents found</p>
            <p className="mt-1 text-xs text-slate-400">
              Upload your first support document.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc, index) => (
              <div
                key={doc.id ?? index}
                className="flex items-center gap-3 rounded-lg border border-slate-100 p-4"
              >
                <div className="rounded-lg bg-indigo-50 p-2 text-indigo-600">
                  <FileText size={20} />
                </div>

                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold">
                    {documentName(doc, index)}
                  </p>
                  <p className="mt-1 text-xs text-slate-400">
                    {doc.status || "Available in knowledge base"}
                    {doc.chunk_count != null
                      ? ` · ${doc.chunk_count} chunks`
                      : ""}
                  </p>
                </div>

                <CheckCircle2 size={18} className="text-emerald-500" />
              </div>
            ))}
          </div>
        )}
      </section>

      {/* RAG query */}
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <div className="mb-5 flex items-center gap-3">
          <div className="rounded-lg bg-indigo-50 p-2 text-indigo-600">
            <Search size={21} />
          </div>
          <div>
            <h3 className="font-bold">Ask Your Knowledge Base</h3>
            <p className="text-xs text-slate-500">
              Retrieve relevant information from uploaded documents.
            </p>
          </div>
        </div>

        <form onSubmit={handleQuestion} className="flex flex-col gap-3 sm:flex-row">
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Example: What is the refund policy?"
            className="min-w-0 flex-1 rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-indigo-500"
          />

          <button
            type="submit"
            disabled={asking}
            className="flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {asking ? (
              <Loader2 size={17} className="animate-spin" />
            ) : (
              <Send size={17} />
            )}
            {asking ? "Searching..." : "Ask AI"}
          </button>
        </form>

        {answer !== null && (
          <div className="mt-6 space-y-3">
            <h4 className="text-sm font-bold">RAG Response</h4>

            <div className="rounded-xl border border-indigo-100 bg-indigo-50/50 p-5">
              <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-7 text-slate-800">
                {typeof answer === "string"
                  ? answer
                  : JSON.stringify(answer, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

export default KnowledgeBase;
