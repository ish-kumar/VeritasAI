/**
 * Documents Page - Document Management
 * 
 * View and manage indexed documents:
 * - List all documents
 * - View document details
 * - Delete documents
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api, DocumentInfo } from '@/lib/api';
import {
  FileText,
  Upload,
  RefreshCw,
  AlertTriangle,
  Loader2,
  Plus
} from 'lucide-react';
import { DocumentsTable } from '@/components/DocumentsTable';
import { toast } from 'sonner';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [totalDocs, setTotalDocs] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await api.getDocuments();
      setDocuments(data.documents);
      setTotalDocs(data.total_documents);
      setError(null);
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError('Failed to load documents. Is the backend running?');
      toast.error('Failed to load documents', {
        description: 'Could not connect to backend. Is it running?'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    try {
      setDeletingId(documentId);
      
      const deletePromise = api.deleteDocument(documentId).then(async () => {
        await loadDocuments();
      });

      toast.promise(deletePromise, {
        loading: `Deleting "${documentId}"...`,
        success: 'Document deleted and index rebuilt',
        error: (err: any) => err.response?.data?.detail || 'Failed to delete document',
      });

      await deletePromise;
    } catch (err: any) {
      console.error('Delete failed:', err);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="min-h-screen px-8 py-12">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-12 animate-fade-in">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold mb-3">Document Library</h1>
            <p className="text-xl text-secondary">
              Manage your indexed legal documents
            </p>
          </div>
          <Link
            href="/upload"
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all button-press inline-flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Upload Document
          </Link>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8 p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 animate-fade-in">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-rose-400 font-medium">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="text-center py-20 animate-fade-in">
            <Loader2 className="w-12 h-12 text-blue-400 animate-spin mx-auto mb-4" />
            <p className="text-secondary">Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          /* Empty State */
          <div className="glass border border-white/10 rounded-2xl p-16 text-center animate-fade-in">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center mx-auto mb-6">
              <FileText className="w-10 h-10 text-blue-400" />
            </div>
            <h2 className="text-3xl font-bold mb-3">No Documents Yet</h2>
            <p className="text-secondary mb-8 max-w-md mx-auto">
              Upload your first legal document to start building your knowledge base
            </p>
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all button-press"
            >
              <Upload className="w-5 h-5" />
              Upload Your First Document
            </Link>
          </div>
        ) : (
          /* Document Table */
          <div className="space-y-6 animate-fade-in-up">
            {/* Summary Card */}
            <div className="glass border border-white/10 rounded-2xl p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
                      <FileText className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold">
                        {totalDocs} Document{totalDocs !== 1 ? 's' : ''}
                      </h2>
                      <p className="text-sm text-secondary">
                        {documents.reduce((sum, doc) => sum + doc.chunk_count, 0)} total chunks indexed
                      </p>
                    </div>
                  </div>
                </div>
                <button
                  onClick={loadDocuments}
                  disabled={loading}
                  className="px-4 py-2 glass rounded-lg text-sm font-medium hover:bg-white/10 transition-all inline-flex items-center gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
              </div>
            </div>

            {/* Data Table */}
            <DocumentsTable 
              documents={documents}
              onDelete={handleDelete}
              deletingId={deletingId}
            />

            {/* Note about deletion */}
            <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/20">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-secondary">
                  <strong className="text-amber-400">Note:</strong> Deleting a document will immediately rebuild the FAISS index. 
                  This may take a few seconds depending on the number of remaining documents.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
