import { X, ExternalLink, Building2, Briefcase, Calendar, DollarSign, FileText, MapPin } from 'lucide-react';
import type { Application } from '../../types';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

interface ApplicationDetailModalProps {
    application: Application;
    onClose: () => void;
}

export function ApplicationDetailModal({ application, onClose }: ApplicationDetailModalProps) {
    const formatDate = (dateStr: string | null) => {
        if (!dateStr) return '—';
        try {
            return format(new Date(dateStr), 'dd MMM yyyy', { locale: fr });
        } catch {
            return dateStr;
        }
    };

    const statusLabels: Record<string, string> = {
        Wishlist: 'Liste de souhaits',
        Applied: 'Postulé',
        'Follow-up': 'Relance',
        Interview: 'Entretien',
        'Technical Test': 'Test Technique',
        Offer: 'Offre',
        Rejected: 'Refusé',
    };

    const statusColor: Record<string, string> = {
        Wishlist: 'text-gray-400 border-gray-400',
        Applied: 'text-cyber-cyan border-cyber-cyan',
        'Follow-up': 'text-orange-400 border-orange-400',
        Interview: 'text-yellow-400 border-yellow-400',
        'Technical Test': 'text-purple-400 border-purple-400',
        Offer: 'text-cyber-green border-cyber-green',
        Rejected: 'text-cyber-alert border-cyber-alert',
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
            <div
                className="bg-gray-900 border border-cyber-cyan/30 rounded-lg shadow-2xl shadow-cyber-cyan/10 w-full max-w-2xl max-h-[85vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex justify-between items-center p-5 border-b border-gray-800 sticky top-0 bg-gray-900 z-10">
                    <div>
                        <h2 className="text-xl text-cyber-green font-mono font-bold flex items-center gap-2">
                            <Building2 className="w-5 h-5" />
                            {application.company?.name || 'Entreprise inconnue'}
                        </h2>
                        <p className="text-xs text-gray-500 mt-1 font-mono">ID: {application.id}</p>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-5 space-y-5">
                    {/* Status & Type badges */}
                    <div className="flex gap-3 flex-wrap">
                        <span className={`text-xs font-mono px-3 py-1 rounded border ${statusColor[application.status] || 'text-gray-400 border-gray-400'}`}>
                            {statusLabels[application.status] || application.status}
                        </span>
                        <span className="text-xs font-mono px-3 py-1 rounded border border-gray-600 text-gray-300">
                            {application.type}
                        </span>
                    </div>

                    {/* Info grid */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                            <div className="flex items-center gap-2 text-gray-500 text-xs font-mono mb-1">
                                <Briefcase className="w-3.5 h-3.5" />
                                SECTEUR
                            </div>
                            <p className="text-sm text-gray-200">{application.company?.sector || '—'}</p>
                        </div>

                        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                            <div className="flex items-center gap-2 text-gray-500 text-xs font-mono mb-1">
                                <DollarSign className="w-3.5 h-3.5" />
                                SALAIRE PROPOSÉ
                            </div>
                            <p className="text-sm text-gray-200">
                                {application.salary_proposed ? `${application.salary_proposed}${application.salary_proposed.includes('€') ? '' : ' €'}` : '—'}
                            </p>
                        </div>

                        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                            <div className="flex items-center gap-2 text-gray-500 text-xs font-mono mb-1">
                                <Calendar className="w-3.5 h-3.5" />
                                DATE D'ENVOI
                            </div>
                            <p className="text-sm text-gray-200">{formatDate(application.date_sent)}</p>
                        </div>

                        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                            <div className="flex items-center gap-2 text-gray-500 text-xs font-mono mb-1">
                                <MapPin className="w-3.5 h-3.5" />
                                LIEU
                            </div>
                            <p className="text-sm text-gray-200">{application.location || '—'}</p>
                        </div>
                    </div>

                    {/* Tech Stack */}
                    {application.company?.tech_stack && application.company.tech_stack.length > 0 && (
                        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                            <p className="text-xs text-gray-500 font-mono mb-2">TECH STACK</p>
                            <div className="flex flex-wrap gap-2">
                                {application.company.tech_stack.map((tech, i) => (
                                    <span key={i} className="text-xs bg-cyber-cyan/10 text-cyber-cyan px-2 py-1 rounded border border-cyber-cyan/30">
                                        {tech}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Job URL */}
                    {application.job_url && (
                        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                            <div className="flex items-center gap-2 text-gray-500 text-xs font-mono mb-1">
                                <ExternalLink className="w-3.5 h-3.5" />
                                LIEN DE L'OFFRE
                            </div>
                            <a
                                href={application.job_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-cyber-cyan hover:underline break-all"
                            >
                                {application.job_url}
                            </a>
                        </div>
                    )}

                    {/* Raw Description */}
                    {application.raw_description && (
                        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                            <div className="flex items-center gap-2 text-gray-500 text-xs font-mono mb-2">
                                <FileText className="w-3.5 h-3.5" />
                                DESCRIPTION DE L'OFFRE
                            </div>
                            <p className="text-sm text-gray-300 whitespace-pre-wrap leading-relaxed max-h-60 overflow-y-auto pr-2">
                                {application.raw_description}
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
