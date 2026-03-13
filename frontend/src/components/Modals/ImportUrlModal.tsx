import { useState } from 'react';
import axios from 'axios';
import { Loader2, X, Globe } from 'lucide-react';

interface ImportUrlModalProps {
    onClose: () => void;
    onSuccess: (data: {
        job_url: string;
        raw_description: string;
        company_name?: string;
        contract_type?: string;
        sector?: string;
        location?: string;
        salary?: string;
        description?: string;
        benefits?: string;
        job_title?: string;
    }) => void;
}

export function ImportUrlModal({ onClose, onSuccess }: ImportUrlModalProps) {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        if (!url) return;

        setLoading(true);
        try {
            const res = await axios.post('http://localhost:8000/api/v1/scraper/', { url });
            onSuccess({
                job_url: url,
                raw_description: res.data.raw_text,
                company_name: res.data.company_name || undefined,
                contract_type: res.data.contract_type || undefined,
                sector: res.data.sector || undefined,
                location: res.data.location || undefined,
                salary: res.data.salary || undefined,
                description: res.data.description || undefined,
                benefits: res.data.benefits || undefined,
                job_title: res.data.job_title || undefined,
            });
        } catch (err: unknown) {
            console.error("Scraping error:", err);
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail || "Failed to extract text from URL.");
            } else {
                setError("Failed to extract text from URL.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 border border-cyber-cyan/30 rounded-lg shadow-2xl shadow-cyber-cyan/10 w-full max-w-lg outline-none">
                <div className="flex justify-between items-center p-4 border-b border-gray-800">
                    <h2 className="text-xl text-cyber-cyan font-mono font-bold flex items-center gap-2">
                        <Globe className="w-5 h-5" />
                        IMPORT_VIA_URL.exe
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div className="space-y-2">
                        <label className="text-xs text-gray-500 font-mono">JOB POSTING URL</label>
                        <input
                            type="url"
                            placeholder="https://www.welcometothejungle.com/..."
                            className="w-full bg-gray-800 border border-gray-700 text-gray-200 rounded p-3 focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan focus:outline-none transition-colors"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            required
                        />
                    </div>

                    {error && (
                        <div className="text-cyber-alert text-sm border-l-2 border-cyber-alert pl-2 bg-cyber-alert/10 py-1">
                            {error}
                        </div>
                    )}

                    <div className="pt-4 flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 rounded text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                        >
                            CANCEL
                        </button>
                        <button
                            type="submit"
                            disabled={loading || !url}
                            className="bg-cyber-cyan text-gray-900 font-bold py-2 px-6 rounded hover:bg-cyber-cyan/80 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'EXTRACT'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
