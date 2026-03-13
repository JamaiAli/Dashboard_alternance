import { useState } from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type { Application } from '../../types';
import axios from 'axios';
import { differenceInDays } from 'date-fns';
import { Paperclip, Trash2 } from 'lucide-react';
import { DocumentManager } from '../Documents/DocumentManager';
import { ApplicationDetailModal } from '../Modals/ApplicationDetailModal';

interface ApplicationCardProps {
    application: Application;
    onRefresh: () => void;
}

export function ApplicationCard({ application, onRefresh }: ApplicationCardProps) {
    const [isDocumentManagerOpen, setIsDocumentManagerOpen] = useState(false);
    const [isDetailOpen, setIsDetailOpen] = useState(false);

    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: application.id, data: { ...application } });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

    const handleDelete = async (e: React.MouseEvent) => {
        e.stopPropagation();
        if (!window.confirm("Êtes-vous sûr de vouloir supprimer cette candidature ?")) return;
        try {
            await axios.delete(`http://localhost:8000/api/v1/applications/${application.id}`);
            onRefresh();
        } catch (error) {
            console.error("Failed to delete application:", error);
        }
    };

    const daysInactive = differenceInDays(new Date(), new Date(application.last_contact_date));

    let inactiveClass = '';
    if (daysInactive >= 10 && application.status !== 'Rejected' && application.status !== 'Offer') {
        inactiveClass = 'border-cyber-alert shadow-[0_0_8px_rgba(255,0,60,0.3)] !border-l-4';
    } else if (daysInactive >= 7 && application.status !== 'Rejected' && application.status !== 'Offer') {
        inactiveClass = 'border-cyber-warning shadow-[0_0_8px_rgba(255,176,0,0.3)] !border-l-4';
    }

    return (
        <>
            <div
                ref={setNodeRef}
                style={style}
                {...attributes}
                {...listeners}
                onDoubleClick={(e) => { e.stopPropagation(); setIsDetailOpen(true); }}
                className={`bg-cyber-darker border border-gray-700 p-3 rounded mb-3 cursor-grab hover:border-cyber-cyan transition-colors ${isDragging ? 'opacity-50 ring-2 ring-cyber-cyan z-50' : ''
                    } ${inactiveClass}`}
            >
                <div className="flex justify-between items-start mb-2">
                    <h4 className="font-bold text-cyber-green text-sm truncate pr-2">
                        {application.company?.name || 'Entreprise inconnue'}
                    </h4>
                    <span className="text-[10px] bg-cyber-black px-1 py-0.5 rounded text-gray-400 border border-gray-800">
                        {application.type}
                    </span>
                </div>

                <div className="text-xs text-gray-400 flex flex-col gap-1">
                    <p className="truncate">{application.company?.sector || 'Secteur non défini'}</p>
                    <div className="flex justify-between items-center mt-2 border-t border-gray-800 pt-2">
                        <span className={`text-[10px] ${daysInactive >= 10 ? 'text-cyber-alert' : 'text-gray-500'}`}>
                            Inactif : {daysInactive}j
                        </span>
                        <div className="flex gap-1">
                            <button
                                onPointerDown={(e) => e.stopPropagation()}
                                onClick={() => setIsDocumentManagerOpen(true)}
                                className="bg-gray-800 p-1.5 rounded hover:bg-cyber-cyan/20 hover:text-cyber-cyan transition-colors"
                                title="Gérer les documents"
                            >
                                <Paperclip className="w-4 h-4" />
                            </button>
                            <button
                                onPointerDown={(e) => e.stopPropagation()}
                                onClick={handleDelete}
                                className="bg-gray-800 p-1.5 rounded hover:bg-cyber-alert/20 hover:text-cyber-alert transition-colors"
                                title="Supprimer la candidature"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {isDocumentManagerOpen && (
                <DocumentManager
                    application={application}
                    onClose={() => setIsDocumentManagerOpen(false)}
                />
            )}

            {isDetailOpen && (
                <ApplicationDetailModal
                    application={application}
                    onClose={() => setIsDetailOpen(false)}
                />
            )}
        </>
    );
}
