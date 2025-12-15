import React from 'react';
import { TrendingUp, TrendingDown, AlertCircle, CheckCircle, Info, ChevronRight } from 'lucide-react';

export function ViabilityScore({ score, strengths = [], risks = [], missingInfo = [] }) {
    // Calculate color based on score
    const getScoreColor = () => {
        if (score >= 70) return 'text-green-400';
        if (score >= 40) return 'text-yellow-400';
        return 'text-red-400';
    };

    const getScoreBg = () => {
        if (score >= 70) return 'from-green-500/20 to-emerald-500/10';
        if (score >= 40) return 'from-yellow-500/20 to-amber-500/10';
        return 'from-red-500/20 to-rose-500/10';
    };

    const getScoreLabel = () => {
        if (score >= 70) return 'Alto';
        if (score >= 40) return 'Médio';
        return 'Baixo';
    };

    const getProgressWidth = () => `${Math.min(100, Math.max(0, score))}%`;

    return (
        <div className="bg-slate-900/80 border border-slate-700/50 rounded-2xl overflow-hidden">
            {/* Header with Score */}
            <div className={`p-5 bg-gradient-to-br ${getScoreBg()}`}>
                <div className="flex items-center justify-between mb-3">
                    <div>
                        <h3 className="text-white font-semibold text-sm">Score de Viabilidade</h3>
                        <p className="text-slate-400 text-xs">Análise automatizada do seu caso</p>
                    </div>
                    <div className="text-right">
                        <div className={`text-3xl font-bold ${getScoreColor()}`}>
                            {score}
                        </div>
                        <div className={`text-xs font-medium ${getScoreColor()}`}>
                            {getScoreLabel()}
                        </div>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                        className={`h-full rounded-full transition-all duration-500 ${score >= 70 ? 'bg-green-500' : score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                        style={{ width: getProgressWidth() }}
                    />
                </div>
            </div>

            {/* Strengths */}
            {strengths.length > 0 && (
                <div className="p-4 border-t border-slate-800">
                    <div className="flex items-center gap-2 mb-3">
                        <TrendingUp size={16} className="text-green-400" />
                        <span className="text-green-400 text-sm font-medium">Pontos Fortes</span>
                    </div>
                    <ul className="space-y-2">
                        {strengths.map((item, index) => (
                            <li key={index} className="flex items-start gap-2 text-sm">
                                <CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
                                <span className="text-slate-300">{item}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Risks */}
            {risks.length > 0 && (
                <div className="p-4 border-t border-slate-800">
                    <div className="flex items-center gap-2 mb-3">
                        <TrendingDown size={16} className="text-red-400" />
                        <span className="text-red-400 text-sm font-medium">Riscos Identificados</span>
                    </div>
                    <ul className="space-y-2">
                        {risks.map((item, index) => (
                            <li key={index} className="flex items-start gap-2 text-sm">
                                <AlertCircle size={14} className="text-red-500 mt-0.5 flex-shrink-0" />
                                <span className="text-slate-300">{item}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Missing Info */}
            {missingInfo.length > 0 && (
                <div className="p-4 border-t border-slate-800 bg-amber-900/10">
                    <div className="flex items-center gap-2 mb-3">
                        <Info size={16} className="text-amber-400" />
                        <span className="text-amber-400 text-sm font-medium">Para fortalecer seu caso</span>
                    </div>
                    <ul className="space-y-2">
                        {missingInfo.map((item, index) => (
                            <li key={index} className="flex items-center gap-2 text-sm group cursor-pointer hover:bg-slate-800/50 rounded-lg p-1 -mx-1 transition-colors">
                                <ChevronRight size={14} className="text-amber-500 group-hover:translate-x-1 transition-transform" />
                                <span className="text-slate-300">{item}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Disclaimer */}
            <div className="p-3 border-t border-slate-800 bg-slate-950/50">
                <p className="text-slate-500 text-[10px] text-center">
                    Este score é uma <strong className="text-slate-400">estimativa automatizada</strong> baseada em IA.
                    Não constitui opinião jurídica. Para casos complexos, consulte um advogado.
                </p>
            </div>
        </div>
    );
}
