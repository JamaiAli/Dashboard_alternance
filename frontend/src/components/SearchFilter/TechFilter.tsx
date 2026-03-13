import { Search, Filter } from 'lucide-react';

interface TechFilterProps {
    searchTerm: string;
    onSearchChange: (value: string) => void;
}

export function TechFilter({ searchTerm, onSearchChange }: TechFilterProps) {
    return (
        <div className="flex gap-4 items-center flex-1 max-w-2xl bg-cyber-dark border border-gray-700 rounded p-2 focus-within:border-cyber-cyan transition-colors">
            <div className="relative flex-1 flex items-center">
                <Search className="w-4 h-4 text-gray-500 absolute left-3" />
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => onSearchChange(e.target.value)}
                    placeholder="Filter by tech stack (e.g. 'Docker', 'React')..."
                    className="w-full bg-transparent border-none text-gray-300 pl-10 pr-4 py-2 focus:outline-none placeholder-gray-600 font-mono text-sm"
                />
            </div>
            <div className="border-l border-gray-700 pl-4 pr-2 flex items-center cursor-pointer hover:text-cyber-cyan transition-colors text-gray-500">
                <Filter className="w-4 h-4 mr-2" />
                <span className="text-xs">FILTERS</span>
            </div>
        </div>
    );
}
