import { useState, useEffect } from 'react';
import axios from 'axios';
import { Terminal } from 'lucide-react';
import { KanbanBoard } from './components/KanbanBoard';
import { AnalyticsWidget } from './components/Analytics/AnalyticsWidget';
import { TechFilter } from './components/SearchFilter/TechFilter';
import { COLUMNS } from './types';
import type { Application, ApplicationStatus } from './types';
import {
  DndContext,
  DragOverlay,
  rectIntersection,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import type { DragStartEvent, DragOverEvent, DragEndEvent } from '@dnd-kit/core';
import { sortableKeyboardCoordinates, arrayMove } from '@dnd-kit/sortable';
import { ApplicationCard } from './components/KanbanBoard/ApplicationCard';
import { AddApplicationModal } from './components/Modals/AddApplicationModal';
import { ImportUrlModal } from './components/Modals/ImportUrlModal';

const API_BASE = 'http://localhost:8000/api/v1';

function App() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeId, setActiveId] = useState<string | null>(null);
  const [initialStatus, setInitialStatus] = useState<ApplicationStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [initialData, setInitialData] = useState<{ job_url?: string; raw_description?: string; company_name?: string; contract_type?: string; sector?: string; location?: string; salary?: string; description?: string; benefits?: string; job_title?: string } | undefined>();

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const fetchApplications = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/applications/`);
      setApplications(res.data);
    } catch (error) {
      console.error("Error fetching applications:", error);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, []);

  const findContainer = (id: string) => {
    if (COLUMNS.some(col => col.id === id)) return id as ApplicationStatus;
    return applications.find(app => app.id === id)?.status;
  };

  const handleDragStart = (event: DragStartEvent) => {
    const id = event.active.id as string;
    setActiveId(id);
    const app = applications.find(a => a.id === id);
    if (app) setInitialStatus(app.status);
  };

  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    const activeContainer = findContainer(activeId);
    const overContainer = findContainer(overId);

    if (!activeContainer || !overContainer || activeContainer === overContainer) {
      return;
    }

    setApplications((prev) => {
      const activeIndex = prev.findIndex(i => i.id === activeId);
      if (activeIndex === -1) return prev;

      const newItems = [...prev];
      newItems[activeIndex] = { ...newItems[activeIndex], status: overContainer };
      
      // Move item to the end of the new container visually to avoid flickering
      const item = newItems.splice(activeIndex, 1)[0];
      newItems.push(item);
      
      return newItems;
    });
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    const currentActiveId = active.id as string;
    const currentInitialStatus = initialStatus;
    
    setActiveId(null);
    setInitialStatus(null);
    
    if (!over) {
      // If dropped outside, we might need to revert if optimistically moved
      fetchApplications(true);
      return;
    }

    const overId = over.id as string;
    const overContainer = findContainer(overId);
    const activeApp = applications.find(app => app.id === currentActiveId);

    if (!activeApp || !overContainer) {
      fetchApplications(true);
      return;
    }

    // Persist status change if occurred
    if (overContainer !== currentInitialStatus) {
      try {
        await axios.put(`${API_BASE}/applications/${activeApp.id}`, {
          company_id: activeApp.company_id,
          status: overContainer,
        });
        // Silent success refresh
        fetchApplications(true);
      } catch (error) {
        console.error("Failed to update status on server:", error);
        alert("Erreur de synchronisation. Rechargement du tableau...");
        fetchApplications();
      }
    } else {
      // Potential reorder within the same column (purely visual for now as index isn't persisted)
      const overAppId = overId;
      if (currentActiveId !== overAppId) {
        const activeIndex = applications.findIndex(a => a.id === currentActiveId);
        const overIndex = applications.findIndex(a => a.id === overAppId);
        if (activeIndex !== -1 && overIndex !== -1) {
          setApplications((items) => arrayMove(items, activeIndex, overIndex));
        }
      }
    }
  };

  const filteredApplications = applications.filter(app => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    const companyNameMatch = app.company?.name.toLowerCase().includes(term);
    const techMatch = app.company?.tech_stack?.some(tech => tech.toLowerCase().includes(term));
    return companyNameMatch || techMatch;
  });

  const activeApplication = activeId ? applications.find(app => app.id === activeId) : null;

  const handleImportSuccess = (data: { job_url: string; raw_description: string; company_name?: string; contract_type?: string; sector?: string; location?: string; salary?: string; description?: string; benefits?: string; job_title?: string }) => {
    setIsImportOpen(false);
    setInitialData(data);
    setIsAddOpen(true);
  };

  return (
    <div className="min-h-screen bg-cyber-black text-gray-300 font-mono p-4 md:p-6 flex flex-col">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end mb-6 border-b border-cyber-green/30 pb-4 gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold flex items-center gap-3 text-cyber-green">
            <Terminal className="w-8 h-8" />
            [NEXUS]
          </h1>
          <p className="text-sm text-gray-500 mt-2">&gt; STATUT SYSTÈME : EN LIGNE</p>
        </div>

        <TechFilter searchTerm={searchTerm} onSearchChange={setSearchTerm} />
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0">
        <aside className="lg:col-span-1 flex flex-col gap-6">
          <AnalyticsWidget applications={applications} />

          <div className="border border-cyber-cyan/30 p-4 rounded bg-cyber-darker flex-1">
            <div className="flex justify-between items-center mb-4 border-b border-gray-800 pb-2">
              <h3 className="text-cyber-cyan font-bold text-sm">PALETTE_DE_COMMANDES</h3>
            </div>
            <button
              onClick={() => { setInitialData(undefined); setIsAddOpen(true); }}
              className="w-full text-left px-4 py-3 bg-cyber-green/10 text-cyber-green hover:bg-cyber-green/20 transition-all font-bold border border-cyber-green rounded mb-3 flex justify-between items-center group"
            >
              <span>+ AJOUTER_CANDIDATURE</span>
              <span className="opacity-0 group-hover:opacity-100 transition-opacity">_</span>
            </button>
            <button
              onClick={() => setIsImportOpen(true)}
              className="w-full text-left px-4 py-3 bg-cyber-cyan/5 text-gray-400 hover:text-cyber-cyan hover:bg-cyber-cyan/10 transition-all border border-gray-800 hover:border-cyber-cyan rounded mb-3"
            >
              &gt; IMPORTER_VIA_URL
            </button>
            <button
              onClick={() => alert("L'interface des documents est accessible par candidature dans les cartes du tableau Kanban.")}
              className="w-full text-left px-4 py-3 bg-cyber-cyan/5 text-gray-400 hover:text-cyber-cyan hover:bg-cyber-cyan/10 transition-all border border-gray-800 hover:border-cyber-cyan rounded"
            >
              &gt; VOIR_DOCUMENTS
            </button>
          </div>
        </aside>

        <section className="lg:col-span-3 border border-cyber-green/30 p-4 rounded bg-cyber-dark shadow-[0_0_15px_rgba(0,255,65,0.05)] flex flex-col min-h-[600px]">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-sm md:text-base text-cyber-cyan">&gt; vue_actuelle : tableau_kanban.exe</h2>
            <span className="text-xs text-gray-500">Filtré : {filteredApplications.length} entrées</span>
          </div>

          <div className="flex-1 overflow-hidden">
            {loading ? (
              <div className="h-full flex items-center justify-center text-cyber-cyan animate-pulse">
                [CHARGEMENT_MODULE_DONNÉES...]
              </div>
            ) : (
              <DndContext
                sensors={sensors} collisionDetection={rectIntersection}
                onDragStart={handleDragStart} onDragOver={handleDragOver} onDragEnd={handleDragEnd}
              >
              <KanbanBoard applications={filteredApplications} onRefresh={fetchApplications} />
                <DragOverlay>
                  {activeApplication ? <ApplicationCard application={activeApplication} onRefresh={fetchApplications} /> : null}
                </DragOverlay>
              </DndContext>
            )}
          </div>
        </section>
      </main>

      {isAddOpen && (
        <AddApplicationModal
          onClose={() => setIsAddOpen(false)}
          onSuccess={fetchApplications}
          initialData={initialData}
        />
      )}

      {isImportOpen && (
        <ImportUrlModal
          onClose={() => setIsImportOpen(false)}
          onSuccess={handleImportSuccess}
        />
      )}
    </div>
  );
}

export default App;
