import type { Application } from '../../types';
import { Activity, Target, Percent } from 'lucide-react';

interface AnalyticsWidgetProps {
    applications: Application[];
}

export function AnalyticsWidget({ applications }: AnalyticsWidgetProps) {
    const totalApplied = applications.length;
    const totalInterviews = applications.filter(
        app => app.status === 'Interview' || app.status === 'Technical Test' || app.status === 'Offer'
    ).length;

    const interviewRatio = totalApplied > 0
        ? Math.round((totalInterviews / totalApplied) * 100)
        : 0;

    return (
        <div className="bg-cyber-dark border border-cyber-cyan/30 rounded p-4 shadow-[0_0_15px_rgba(0,240,255,0.05)]">
            <h3 className="text-cyber-cyan font-bold mb-4 flex items-center gap-2 border-b border-cyber-cyan/20 pb-2">
                <Activity className="w-5 h-5" />
                METRICS_OVERVIEW
            </h3>

            <div className="grid grid-cols-3 gap-4">
                <div className="bg-cyber-darker border border-gray-800 p-3 rounded flex flex-col items-center justify-center">
                    <span className="text-gray-500 text-xs mb-1 text-center">TOTAL_SENT</span>
                    <span className="text-2xl font-bold text-gray-200">{totalApplied}</span>
                </div>

                <div className="bg-cyber-darker border border-gray-800 p-3 rounded flex flex-col items-center justify-center relative overflow-hidden group">
                    <div className="absolute inset-0 bg-cyber-green/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <Target className="w-4 h-4 text-cyber-green absolute top-2 right-2 opacity-50" />
                    <span className="text-gray-500 text-xs mb-1 text-center">INTERVIEWS</span>
                    <span className="text-2xl font-bold text-cyber-green">{totalInterviews}</span>
                </div>

                <div className="bg-cyber-darker border border-gray-800 p-3 rounded flex flex-col items-center justify-center relative">
                    <Percent className="w-4 h-4 text-cyber-warning absolute top-2 right-2 opacity-50" />
                    <span className="text-gray-500 text-xs mb-1 text-center">HIT_RATIO</span>
                    <span className={`text-2xl font-bold ${interviewRatio > 20 ? 'text-cyber-green' : 'text-cyber-warning'}`}>
                        {interviewRatio}%
                    </span>
                </div>
            </div>
        </div>
    );
}
