import React from 'react';
import { Wrench, DollarSign, Landmark, HelpCircle } from 'lucide-react';

const categories = [
    {
        id: 'maintenance',
        label: 'Manutenção',
        description: 'Vazamentos, infiltrações, reparos',
        icon: Wrench,
        color: 'blue'
    },
    {
        id: 'financial',
        label: 'Cobranças',
        description: 'Multas, taxas indevidas',
        icon: DollarSign,
        color: 'green'
    },
    {
        id: 'deposit',
        label: 'Caução',
        description: 'Devolução do depósito',
        icon: Landmark,
        color: 'purple'
    },
    {
        id: 'other',
        label: 'Outro',
        description: 'Outra situação',
        icon: HelpCircle,
        color: 'slate'
    }
];

const colorClasses = {
    blue: 'bg-blue-500/20 text-blue-400 group-hover:bg-blue-500/30',
    green: 'bg-green-500/20 text-green-400 group-hover:bg-green-500/30',
    purple: 'bg-purple-500/20 text-purple-400 group-hover:bg-purple-500/30',
    slate: 'bg-slate-500/20 text-slate-400 group-hover:bg-slate-500/30'
};

export function CategorySelector({ onSelect }) {
    return (
        <div className="py-4">
            <p className="text-slate-400 text-sm mb-4 text-center">
                Ou escolha uma categoria:
            </p>
            <div className="grid grid-cols-2 gap-3 max-w-sm mx-auto">
                {categories.map((cat) => {
                    const Icon = cat.icon;
                    return (
                        <button
                            key={cat.id}
                            onClick={() => onSelect(cat.id)}
                            className="category-card rounded-xl p-4 text-left group"
                        >
                            <div className={`w-10 h-10 rounded-full ${colorClasses[cat.color]} flex items-center justify-center mb-3 transition-colors`}>
                                <Icon size={20} />
                            </div>
                            <h3 className="text-white font-medium text-sm">{cat.label}</h3>
                            <p className="text-slate-500 text-xs mt-1">{cat.description}</p>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
