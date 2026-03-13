import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import type { Application, ApplicationStatus } from '../../types';
import { ApplicationCard } from './ApplicationCard';

interface KanbanColumnProps {
    id: ApplicationStatus;
    title: string;
    applications: Application[];
    onRefresh: () => void;
}

export function KanbanColumn({ id, title, applications, onRefresh }: KanbanColumnProps) {
    const { setNodeRef } = useDroppable({
        id: id,
    });

    return (
        <div className="flex flex-col flex-1 min-w-[250px] bg-cyber-black border border-cyber-green/20 rounded shadow-[inset_0_0_10px_rgba(0,255,65,0.02)]">
            <div className="p-3 border-b border-cyber-green/20 bg-cyber-dark/50 flex justify-between items-center">
                <h3 className="font-bold text-cyber-cyan text-sm">{title}</h3>
                <span className="text-xs bg-cyber-darker px-2 py-1 rounded text-gray-400">
                    {applications.length}
                </span>
            </div>

            <div
                ref={setNodeRef}
                className="flex-1 p-2 overflow-y-auto min-h-[300px] kanban-column-scroll"
            >
                <SortableContext
                    items={applications.map(app => app.id)}
                    strategy={verticalListSortingStrategy}
                >
                    {applications.map((app) => (
                        <ApplicationCard key={app.id} application={app} onRefresh={onRefresh} />
                    ))}
                </SortableContext>

                {applications.length === 0 && (
                    <div className="h-full w-full flex items-center justify-center text-gray-600 text-xs text-center p-4 border-2 border-dashed border-gray-800 rounded">
                        Déposez les éléments ici
                    </div>
                )}
            </div>
        </div>
    );
}
