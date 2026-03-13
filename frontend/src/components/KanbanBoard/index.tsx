import type { Application, ApplicationStatus } from '../../types';
import { KanbanColumn } from './KanbanColumn';

export const COLUMNS: { id: ApplicationStatus; title: string }[] = [
    { id: 'Wishlist', title: 'LISTE DE SOUHAITS' },
    { id: 'Applied', title: 'POSTULÉ' },
    { id: 'Follow-up', title: 'RELANCE' },
    { id: 'Interview', title: 'ENTRETIEN' },
    { id: 'Technical Test', title: 'TEST TECHNIQUE' },
    { id: 'Offer', title: 'OFFRE' },
    { id: 'Rejected', title: 'REFUSÉ' },
];

interface KanbanBoardProps {
    applications: Application[];
    onRefresh: () => void;
}

export function KanbanBoard({ applications, onRefresh }: KanbanBoardProps) {
    return (
        <div className="flex gap-4 h-full overflow-x-auto pb-4">
            {COLUMNS.map((col) => (
                <KanbanColumn
                    key={col.id}
                    id={col.id}
                    title={col.title}
                    applications={applications.filter(app => app.status === col.id)}
                    onRefresh={onRefresh}
                />
            ))}
        </div>
    );
}
