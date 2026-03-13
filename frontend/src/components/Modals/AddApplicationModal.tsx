import { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, X, Plus } from 'lucide-react';
import type { ApplicationStatus, ApplicationType } from '../../types';

interface AddApplicationModalProps {
    onClose: () => void;
    onSuccess: () => void;
    initialData?: { job_url?: string; raw_description?: string; company_name?: string; contract_type?: string; sector?: string; location?: string; salary?: string; description?: string; benefits?: string; job_title?: string };
}

interface Company {
    id: string;
    name: string;
    sector: string | null;
}

const API_BASE = 'http://localhost:8000/api/v1';

export function AddApplicationModal({ onClose, onSuccess, initialData }: AddApplicationModalProps) {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [loading, setLoading] = useState(false);

    const [isNewCompany, setIsNewCompany] = useState(!!initialData?.company_name);
    const [selectedCompanyId, setSelectedCompanyId] = useState('');
    const [newCompanyName, setNewCompanyName] = useState(initialData?.company_name || '');
    const [newCompanySector, setNewCompanySector] = useState(initialData?.sector || '');

    const [status, setStatus] = useState<ApplicationStatus>('Wishlist');
    const [type, setType] = useState<ApplicationType>((initialData?.contract_type as ApplicationType) || 'Alternance');
    const [salary, setSalary] = useState('');
    const [jobUrl, setJobUrl] = useState(initialData?.job_url || '');
    const [rawDesc, setRawDesc] = useState(initialData?.raw_description || '');

    useEffect(() => {
        const fetchCompanies = async () => {
            try {
                const res = await axios.get(`${API_BASE}/companies/`);
                setCompanies(res.data);
                if (res.data.length > 0) setSelectedCompanyId(res.data[0].id);
                else setIsNewCompany(true);
            } catch (e) {
                console.error("Error fetching companies:", e);
                setIsNewCompany(true);
            }
        };
        fetchCompanies();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            let finalCompanyId = selectedCompanyId;

            // 1. Create company if new
            if (isNewCompany) {
                try {
                    const compRes = await axios.post(`${API_BASE}/companies/`, {
                        name: newCompanyName,
                        sector: newCompanySector || null,
                    });
                    finalCompanyId = compRes.data.id;
                } catch {
                    // Company might already exist (unique name constraint), try to find it
                    const existingRes = await axios.get(`${API_BASE}/companies/`);
                    const existing = existingRes.data.find(
                        (c: { id: string; name: string }) => c.name.toLowerCase() === newCompanyName.toLowerCase()
                    );
                    if (existing) {
                        finalCompanyId = existing.id;
                    } else {
                        throw new Error("Failed to create or find company");
                    }
                }
            }

            // 2. Create Application
            await axios.post(`${API_BASE}/applications/`, {
                company_id: finalCompanyId,
                status,
                type,
                salary_proposed: salary ? parseFloat(salary) : null,
                job_url: jobUrl || null,
                raw_description: rawDesc || null,
                date_sent: new Date().toISOString(),
                last_contact_date: new Date().toISOString()
            });

            onSuccess();
            onClose();
        } catch (error) {
            console.error("Error creating application:", error);
            alert("Failed to create application");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 border border-[#00ffcc]/30 rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center p-4 border-b border-gray-800 sticky top-0 bg-gray-900 z-10">
                    <h2 className="text-xl text-[#00ffcc] font-mono font-bold flex items-center gap-2">
                        <Plus className="w-5 h-5" />
                        ADD_APPLICATION.exe
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* COMPANY SECTION */}
                    <div className="space-y-4 bg-gray-800 p-4 rounded-lg border border-gray-700">
                        <div className="flex justify-between items-center mb-2">
                            <h3 className="text-sm text-gray-400 font-mono">COMPANY DETAILS</h3>
                            <button
                                type="button"
                                onClick={() => setIsNewCompany(!isNewCompany)}
                                className="text-xs text-[#00ffcc] hover:underline focus:outline-none"
                            >
                                {isNewCompany ? "Select Existing" : "+ Create New"}
                            </button>
                        </div>

                        {isNewCompany ? (
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-1">
                                    <label className="text-xs text-gray-500 font-mono">COMPANY NAME *</label>
                                    <input type="text" className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded p-2 focus:border-[#00ffcc] focus:ring-1 focus:ring-[#00ffcc] focus:outline-none" required value={newCompanyName} onChange={e => setNewCompanyName(e.target.value)} />
                                </div>
                                <div className="space-y-1">
                                    <label className="text-xs text-gray-500 font-mono">SECTOR</label>
                                    <input type="text" className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded p-2 focus:border-[#00ffcc] focus:ring-1 focus:ring-[#00ffcc] focus:outline-none" value={newCompanySector} onChange={e => setNewCompanySector(e.target.value)} />
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-1">
                                <label className="text-xs text-gray-500 font-mono">SELECT COMPANY *</label>
                                <select className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded p-2 focus:border-[#00ffcc] focus:ring-1 focus:ring-[#00ffcc] focus:outline-none" value={selectedCompanyId} onChange={e => setSelectedCompanyId(e.target.value)}>
                                    {companies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </select>
                            </div>
                        )}
                    </div>

                    {/* APPLICATION SECTION */}
                    <div className="space-y-4 bg-gray-800 p-4 rounded-lg border border-gray-700">
                        <h3 className="text-sm text-gray-400 font-mono mb-2">APPLICATION DETAILS</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <label className="text-xs text-gray-500 font-mono">STATUS *</label>
                                <select className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded p-2 focus:border-[#00ffcc] focus:outline-none" value={status} onChange={e => setStatus(e.target.value as ApplicationStatus)}>
                                    <option value="Wishlist">Wishlist</option>
                                    <option value="Applied">Applied</option>
                                    <option value="Interview">Interview</option>
                                    <option value="Technical Test">Technical Test</option>
                                    <option value="Offer">Offer</option>
                                    <option value="Rejected">Rejected</option>
                                </select>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs text-gray-500 font-mono">TYPE *</label>
                                <select className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded p-2 focus:border-[#00ffcc] focus:outline-none" value={type} onChange={e => setType(e.target.value as ApplicationType)}>
                                    <option value="Alternance">Alternance</option>
                                    <option value="Stage">Stage</option>
                                </select>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs text-gray-500 font-mono">SALARY PROPOSED (€)</label>
                                <input type="number" step="1000" className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded p-2 focus:border-[#00ffcc] focus:outline-none" value={salary} onChange={e => setSalary(e.target.value)} />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs text-gray-500 font-mono">JOB URL</label>
                                <input type="url" className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded p-2 focus:border-[#00ffcc] focus:outline-none" value={jobUrl} onChange={e => setJobUrl(e.target.value)} />
                            </div>
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs text-gray-500 font-mono">RAW DESCRIPTION</label>
                            <textarea rows={4} className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded p-2 focus:border-[#00ffcc] focus:outline-none" value={rawDesc} onChange={e => setRawDesc(e.target.value)} />
                        </div>
                    </div>

                    <button type="submit" disabled={loading} className="w-full bg-[#00ffcc] text-gray-900 font-bold py-3 px-4 rounded hover:bg-[#00ffcc]/80 transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
                        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'SAVE APPLICATION'}
                    </button>
                </form>
            </div>
        </div>
    );
}
