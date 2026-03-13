import { COLUMNS } from '../../types';
import type { Application } from '../../types';
import { KanbanColumn } from './KanbanColumn';

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
