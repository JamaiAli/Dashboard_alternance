import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Upload, Download, FileText, Loader2, X, Trash2 } from 'lucide-react';
import type { Application } from '../../types';

interface DocumentManagerProps {
    application: Application;
    onClose: () => void;
}

interface AppDocument {
    id: string;
    application_id: string;
    type: 'CV' | 'LM' | 'Other';
    version_name: string;
    file_path: string;
}

export function DocumentManager({ application, onClose }: DocumentManagerProps) {
    const [documents, setDocuments] = useState<AppDocument[]>([]);
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState<{ type: 'error' | 'success', msg: string } | null>(null);
    const [uploading, setUploading] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [docType, setDocType] = useState<'CV' | 'LM' | 'Other'>('CV');
    const [versionName, setVersionName] = useState('');

    const API_BASE = 'http://localhost:8000/api/v1';

    const fetchDocuments = useCallback(async () => {
        setLoading(true);
        setStatus(null);
        try {
            const res = await axios.get(`${API_BASE}/documents/application/${application.id}`);
            setDocuments(res.data);
        } catch (error) {
            console.error("Error fetching documents:", error);
            setStatus({ type: 'error', msg: 'Échec du chargement de la liste des documents.' });
        } finally {
            setLoading(false);
        }
    }, [application.id]);

    useEffect(() => {
        fetchDocuments();
    }, [fetchDocuments]);

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus(null);

        if (!file) {
            setStatus({ type: 'error', msg: 'Veuillez d\'abord sélectionner un fichier.' });
            return;
        }
        if (!versionName.trim()) {
            setStatus({ type: 'error', msg: 'Veuillez entrer un nom de version (ex: V1, Révisé).' });
            return;
        }

        setUploading(true);
        const formData = new FormData();
        formData.append('application_id', application.id);
        formData.append('type', docType);
        formData.append('version_name', versionName.trim());
        formData.append('file', file);

        try {
            console.log("Starting upload to:", `${API_BASE}/documents/upload`);
            await axios.post(`${API_BASE}/documents/upload`, formData);
            setFile(null);
            setVersionName('');
            setStatus({ type: 'success', msg: 'Document téléchargé avec succès !' });
            await fetchDocuments(); // refresh list
        } catch (error: any) {
            console.error("Upload error details:", error.response?.data || error.message);
            setStatus({ 
                type: 'error', 
                msg: error.response?.data?.detail || 'L\'envoi a échoué. Vérifiez si le serveur tourne sur :8000' 
            });
        } finally {
            setUploading(false);
        }
    };

    const handleDownload = async (docId: string, filename: string) => {
        try {
            const response = await axios.get(`${API_BASE}/documents/download/${docId}`, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Error downloading document:", error);
        }
    };

    const handleDelete = async (docId: string) => {
        try {
            await axios.delete(`${API_BASE}/documents/${docId}`);
            await fetchDocuments();
        } catch (error) {
            console.error("Error deleting document:", error);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 border border-[#00ffcc]/30 rounded-lg shadow-2xl shadow-[#00ffcc]/10 w-full max-w-2xl max-h-[90vh] overflow-y-auto outline-none">
                <div className="flex justify-between items-center p-4 border-b border-gray-800 sticky top-0 bg-gray-900 z-10">
                    <h2 className="text-xl text-[#00ffcc] font-mono font-bold flex items-center gap-2">
                        <FileText className="w-5 h-5" />
                        DOCUMENTS : {application.company?.name || 'Entreprise'}
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    {/* Status Message */}
                    {status && (
                        <div className={`p-3 rounded-md text-sm font-mono flex items-center gap-2 ${
                            status.type === 'success' 
                                ? 'bg-[#00ffcc]/10 text-[#00ffcc] border border-[#00ffcc]/30' 
                                : 'bg-red-500/10 text-red-500 border border-red-500/30'
                        }`}>
                            {status.type === 'success' ? '✓ ' : '⚠ '}
                            {status.msg}
                        </div>
                    )}

                    {/* Upload Section */}
                    <form onSubmit={handleUpload} className="bg-gray-800 p-4 rounded-lg border border-gray-700 space-y-4">
                        <h3 className="text-sm text-gray-400 font-mono">NOUVEAU TÉLÉCHARGEMENT</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <label className="text-xs text-gray-500 font-mono">TYPE DE DOCUMENT</label>
                                <select
                                    className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded p-2 focus:border-[#00ffcc] focus:ring-1 focus:ring-[#00ffcc] focus:outline-none"
                                    value={docType}
                                    onChange={(e) => setDocType(e.target.value as 'CV' | 'LM' | 'Other')}
                                >
                                    <option value="CV">CV</option>
                                    <option value="LM">Lettre de Motivation (LM)</option>
                                    <option value="Other">Autre</option>
                                </select>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs text-gray-500 font-mono">NOM DE LA VERSION</label>
                                <input
                                    type="text"
                                    placeholder="ex: CV_Cyber_V2"
                                    className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded p-2 focus:border-[#00ffcc] focus:ring-1 focus:ring-[#00ffcc] focus:outline-none"
                                    value={versionName}
                                    onChange={(e) => setVersionName(e.target.value)}
                                    required
                                />
                            </div>
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs text-gray-500 font-mono">FICHIER</label>
                            <input
                                type="file"
                                className="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-[#00ffcc]/10 file:text-[#00ffcc] hover:file:bg-[#00ffcc]/20"
                                onChange={(e) => setFile(e.target.files?.[0] || null)}
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={uploading}
                            className="w-full bg-[#00ffcc] text-gray-900 font-bold py-2 px-4 rounded hover:bg-[#00ffcc]/80 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-[#00ffcc]/20"
                        >
                            {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                            {uploading ? 'ENVOI EN COURS...' : 'TÉLÉCHARGER MAINTENANT'}
                        </button>
                    </form>

                    {/* Document List */}
                    <div className="space-y-3">
                        <h3 className="text-sm text-gray-400 font-mono border-b border-gray-800 pb-2">DOCUMENTS JOINTS</h3>
                        {loading ? (
                            <div className="flex justify-center p-4"><Loader2 className="w-6 h-6 text-[#00ffcc] animate-spin" /></div>
                        ) : documents.length === 0 ? (
                            <p className="text-gray-500 text-sm italic">Aucun document joint pour le moment.</p>
                        ) : (
                            <div className="grid gap-3">
                                {documents.map(doc => (
                                    <div key={doc.id} className="bg-gray-800 border border-gray-700 rounded-lg p-3 flex items-center justify-between group">
                                        <div className="flex items-center gap-3">
                                            <div className="bg-[#00ffcc]/10 p-2 rounded">
                                                <FileText className="w-5 h-5 text-[#00ffcc]" />
                                            </div>
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <span className="font-mono text-sm font-bold text-gray-200">{doc.type}</span>
                                                    <span className="text-gray-400 text-xs">- {doc.version_name}</span>
                                                </div>
                                                <div className="text-xs text-gray-500 font-mono truncate max-w-[200px]">{doc.file_path.split(/[/\\]/).pop()}</div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <button
                                                onClick={() => handleDownload(doc.id, doc.file_path.split(/[/\\]/).pop() || 'téléchargement')}
                                                className="p-2 text-gray-400 hover:text-[#00ffcc] bg-gray-900 rounded transition-colors"
                                                title="Télécharger"
                                            >
                                                <Download className="w-4 h-4" />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(doc.id)}
                                                className="p-2 text-gray-400 hover:text-red-400 bg-gray-900 rounded transition-colors opacity-0 group-hover:opacity-100"
                                                title="Supprimer"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
