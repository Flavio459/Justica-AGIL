import React, { useState, useEffect } from 'react';
import { FileText, Check, ArrowLeft, Loader2, AlertTriangle, Info, Building2 } from 'lucide-react';

export function ReviewScreen({ data, onBack, onConfirm }) {
    const [formData, setFormData] = useState(data || {
        company_name: '',
        title: '',
        facts: '',
        request: '',
        value: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [hasConfirmed, setHasConfirmed] = useState(false);
    const [submitResult, setSubmitResult] = useState(null);

    useEffect(() => {
        if (data) setFormData(prev => ({ ...prev, ...data }));
    }, [data]);

    // Character count for Gov.br compliance (max 3000 for facts)
    const factsCharCount = (formData.facts || '').length;
    const factsOverLimit = factsCharCount > 3000;

    const handleSubmit = async (dryRun = true) => {
        if (!hasConfirmed) {
            return;
        }

        setIsSubmitting(true);
        setSubmitResult(null);

        try {
            const response = await fetch('http://localhost:8000/api/automation/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    claim_data: {
                        company_name: formData.company_name,
                        facts: formData.facts,
                        request: formData.request
                    },
                    headless: false,  // Sempre mostra o navegador
                    dry_run: dryRun   // Primeiro teste, depois envio real
                })
            });

            const result = await response.json();
            setSubmitResult(result);

            if (result.status === 'success') {
                alert(`✅ Sucesso! Protocolo: ${result.protocol}`);
                onConfirm();
            } else if (result.status === 'dry_run_complete') {
                alert(`🔍 Formulário preenchido! Revise a tela do navegador.\n\nQuando estiver pronto, clique em "Enviar de Verdade".`);
            } else if (result.status === 'login_timeout') {
                alert("⏱️ Tempo esgotado esperando login. Tente novamente.");
            } else {
                alert("❌ Erro: " + (result.error || result.message || "Erro desconhecido"));
            }
        } catch (error) {
            console.error(error);
            alert("❌ Erro de conexão com o Agente Navegador.\n\nVerifique se:\n1. O backend está rodando (porta 8000)\n2. O Chrome está aberto com --remote-debugging-port=9222");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-indigo-950 flex flex-col p-4 md:p-8 overflow-y-auto">
            <div className="max-w-3xl mx-auto w-full">
                <button
                    onClick={onBack}
                    className="flex items-center text-slate-400 hover:text-white mb-6 transition-colors"
                >
                    <ArrowLeft size={16} className="mr-2" /> Voltar ao Chat
                </button>

                <h1 className="text-2xl font-bold text-white mb-2">Revisão Final</h1>
                <p className="text-slate-400 text-sm mb-6">
                    Revise cuidadosamente. Este texto será enviado para o Consumidor.gov.br.
                </p>

                {/* Document Card */}
                <div className="bg-slate-900/80 border border-slate-700/50 rounded-2xl p-5 shadow-xl mb-4">
                    <div className="flex items-center gap-3 mb-5 pb-4 border-b border-slate-800">
                        <div className="p-2 bg-blue-600/20 rounded-lg">
                            <FileText className="text-blue-500" size={20} />
                        </div>
                        <div>
                            <span className="text-xs font-bold text-blue-500 uppercase tracking-wider">Documento</span>
                            <h2 className="text-lg font-semibold text-white">Reclamação Formal</h2>
                        </div>
                    </div>

                    <div className="space-y-5">
                        {/* Campo Empresa - CRÍTICO para automação */}
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-2 flex items-center gap-2">
                                <Building2 size={14} /> Empresa Reclamada
                            </label>
                            <input
                                type="text"
                                value={formData.company_name}
                                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                                placeholder="Ex: Baruke Imóveis, Vivo, Claro..."
                                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                            />
                            <p className="text-slate-500 text-xs mt-1">Nome exato como aparece no Consumidor.gov.br</p>
                        </div>

                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <label className="text-sm font-medium text-slate-400">Os Fatos (Relato)</label>
                                <span className={`text-xs ${factsOverLimit ? 'text-red-400' : 'text-slate-500'}`}>
                                    {factsCharCount}/3000 caracteres
                                </span>
                            </div>
                            <textarea
                                value={formData.facts}
                                onChange={(e) => setFormData({ ...formData, facts: e.target.value })}
                                className={`w-full bg-slate-800 border text-white rounded-lg p-3 h-40 focus:ring-2 focus:ring-blue-500 outline-none resize-y text-sm ${factsOverLimit ? 'border-red-500' : 'border-slate-700'
                                    }`}
                            />
                            {factsOverLimit && (
                                <p className="text-red-400 text-xs mt-1 flex items-center gap-1">
                                    <AlertTriangle size={12} /> Limite de 3000 caracteres do Gov.br excedido
                                </p>
                            )}
                        </div>

                        <div className="grid md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-2">Os Pedidos</label>
                                <textarea
                                    value={formData.request}
                                    onChange={(e) => setFormData({ ...formData, request: e.target.value })}
                                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-3 h-28 focus:ring-2 focus:ring-blue-500 outline-none resize-none text-sm"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-2">Valor Estimado (R$)</label>
                                <input
                                    type="text"
                                    value={formData.value}
                                    onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Legal Disclaimer Before Submission */}
                <div className="bg-amber-900/20 border border-amber-700/30 rounded-xl p-4 mb-4">
                    <div className="flex items-start gap-3">
                        <AlertTriangle size={20} className="text-amber-400 mt-0.5 flex-shrink-0" />
                        <div>
                            <h3 className="text-amber-300 font-medium text-sm mb-1">Antes de enviar</h3>
                            <p className="text-amber-200/80 text-xs leading-relaxed">
                                Você está prestes a protocolar sua reclamação <strong>diretamente no portal Gov.br</strong>.
                                O Justiça Ágil apenas automatiza o preenchimento do formulário com as informações que você forneceu.
                                <strong> Você é o autor da reclamação e responsável por seu conteúdo.</strong>
                            </p>
                        </div>
                    </div>
                </div>

                {/* Confirmation Checkbox */}
                <label className="flex items-start gap-3 mb-6 cursor-pointer group">
                    <input
                        type="checkbox"
                        checked={hasConfirmed}
                        onChange={(e) => setHasConfirmed(e.target.checked)}
                        className="mt-1 w-5 h-5 rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-900"
                    />
                    <span className="text-slate-300 text-sm group-hover:text-white transition-colors">
                        Li, revisei e <strong>confirmo que as informações são verdadeiras</strong>.
                        Entendo que estou fazendo minha própria reclamação e que o Justiça Ágil é apenas uma ferramenta de automação.
                    </span>
                </label>

                {/* Submit Buttons - Two options */}
                <div className="grid md:grid-cols-2 gap-3 mb-4">
                    {/* Test Button (Dry Run) */}
                    <button
                        onClick={() => handleSubmit(true)}
                        disabled={isSubmitting || !hasConfirmed || factsOverLimit || !formData.company_name}
                        className="w-full bg-slate-700 hover:bg-slate-600 text-white font-medium py-3 rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSubmitting ? (
                            <><Loader2 className="animate-spin" size={18} /> Processando...</>
                        ) : (
                            <><FileText size={18} /> Testar Preenchimento</>
                        )}
                    </button>

                    {/* Real Submit Button */}
                    <button
                        onClick={() => handleSubmit(false)}
                        disabled={isSubmitting || !hasConfirmed || factsOverLimit || !formData.company_name || !submitResult}
                        className="w-full btn-primary text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2 transition-all transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                    >
                        {isSubmitting ? (
                            <><Loader2 className="animate-spin" size={18} /> Enviando...</>
                        ) : (
                            <><Check size={18} /> Enviar de Verdade</>
                        )}
                    </button>
                </div>

                {/* Status Info */}
                {submitResult && (
                    <div className={`p-3 rounded-lg text-sm mb-4 ${submitResult.status === 'dry_run_complete' ? 'bg-blue-900/30 border border-blue-700/50 text-blue-300' :
                            submitResult.status === 'success' ? 'bg-green-900/30 border border-green-700/50 text-green-300' :
                                'bg-red-900/30 border border-red-700/50 text-red-300'
                        }`}>
                        <p><strong>Status:</strong> {submitResult.status}</p>
                        {submitResult.protocol && <p><strong>Protocolo:</strong> {submitResult.protocol}</p>}
                        {submitResult.message && <p>{submitResult.message}</p>}
                    </div>
                )}

                {/* Footer Disclaimer */}
                <p className="text-center text-slate-500 text-[10px] mt-4">
                    Ferramenta de automação • Não prestamos serviços jurídicos • Você é o autor da sua reclamação
                </p>
            </div>
        </div>
    );
}

