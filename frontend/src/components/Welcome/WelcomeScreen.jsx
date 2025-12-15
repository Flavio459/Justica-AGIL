import React, { useState } from 'react';
import { MessageCircle, Mic, Heart, Shield, Sparkles, Info, ExternalLink } from 'lucide-react';

export function WelcomeScreen({ onStart, onPreferenceSelect }) {
    const [showTerms, setShowTerms] = useState(false);

    const getGreeting = () => {
        const hour = new Date().getHours();
        if (hour < 12) return 'Bom dia';
        if (hour < 18) return 'Boa tarde';
        return 'Boa noite';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 flex flex-col items-center justify-center p-6">
            {/* Decorative elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl" />
                <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
            </div>

            {/* Main content */}
            <div className="relative z-10 max-w-md w-full text-center">
                {/* Avatar */}
                <div className="mb-6 relative inline-block">
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-purple-500/30 animate-float">
                        <span className="text-3xl">👋</span>
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-7 h-7 bg-green-500 rounded-full border-4 border-slate-900 flex items-center justify-center">
                        <Sparkles size={12} className="text-white" />
                    </div>
                </div>

                {/* Greeting */}
                <h1 className="text-2xl font-bold text-white mb-1">
                    {getGreeting()}!
                </h1>
                <p className="text-lg text-slate-300 mb-2">
                    Sou a <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 font-semibold">Ju</span>, sua assistente
                </p>

                {/* Empathy message */}
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-4 mb-4 border border-slate-700/50">
                    <p className="text-slate-300 text-sm leading-relaxed">
                        Sei como é frustrante lidar com problemas no imóvel e não ser ouvido.
                        <span className="text-blue-400"> Vou te ajudar a fazer sua reclamação</span> no site do governo de forma simples.
                    </p>
                </div>

                {/* Legal Disclaimer - Accessible Language */}
                <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-3 mb-6 text-left">
                    <div className="flex items-start gap-2">
                        <Info size={16} className="text-blue-400 mt-0.5 flex-shrink-0" />
                        <div>
                            <p className="text-slate-400 text-xs leading-relaxed">
                                O Justiça Ágil é uma <span className="text-slate-300">ferramenta que te ajuda a preencher sua reclamação</span> no Consumidor.gov.br.
                                <span className="text-slate-300"> Você é quem está fazendo a reclamação</span>, não somos advogados.
                            </p>
                            <button
                                onClick={() => setShowTerms(true)}
                                className="text-blue-400 text-xs mt-1 hover:underline flex items-center gap-1"
                            >
                                Ver Termos de Uso <ExternalLink size={10} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Features */}
                <div className="flex justify-center gap-6 mb-6">
                    <div className="flex flex-col items-center gap-1">
                        <div className="w-9 h-9 rounded-full bg-blue-500/20 flex items-center justify-center">
                            <Shield size={16} className="text-blue-400" />
                        </div>
                        <span className="text-[10px] text-slate-400">Seguro</span>
                    </div>
                    <div className="flex flex-col items-center gap-1">
                        <div className="w-9 h-9 rounded-full bg-purple-500/20 flex items-center justify-center">
                            <Heart size={16} className="text-purple-400" />
                        </div>
                        <span className="text-[10px] text-slate-400">Empático</span>
                    </div>
                    <div className="flex flex-col items-center gap-1">
                        <div className="w-9 h-9 rounded-full bg-green-500/20 flex items-center justify-center">
                            <Sparkles size={16} className="text-green-400" />
                        </div>
                        <span className="text-[10px] text-slate-400">Simples</span>
                    </div>
                </div>

                {/* Preference selection */}
                <p className="text-slate-400 text-sm mb-3">Como prefere conversar?</p>
                <div className="flex gap-3 justify-center">
                    <button
                        onClick={() => onPreferenceSelect('text')}
                        className="flex-1 max-w-[130px] bg-slate-800/80 hover:bg-slate-700/80 border border-slate-600/50 hover:border-blue-500/50 rounded-xl p-3 transition-all duration-300 group"
                    >
                        <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-blue-500/20 group-hover:bg-blue-500/30 flex items-center justify-center transition-colors">
                            <MessageCircle size={20} className="text-blue-400" />
                        </div>
                        <span className="text-white font-medium text-sm">Texto</span>
                        <p className="text-[10px] text-slate-500 mt-0.5">Digitar mensagens</p>
                    </button>

                    <button
                        onClick={() => onPreferenceSelect('voice')}
                        className="flex-1 max-w-[130px] bg-slate-800/80 hover:bg-slate-700/80 border border-slate-600/50 hover:border-purple-500/50 rounded-xl p-3 transition-all duration-300 group"
                    >
                        <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-purple-500/20 group-hover:bg-purple-500/30 flex items-center justify-center transition-colors">
                            <Mic size={20} className="text-purple-400" />
                        </div>
                        <span className="text-white font-medium text-sm">Voz</span>
                        <p className="text-[10px] text-slate-500 mt-0.5">Falar comigo</p>
                    </button>
                </div>

                {/* Skip option */}
                <button
                    onClick={() => onStart()}
                    className="mt-6 text-slate-500 hover:text-slate-300 text-xs transition-colors"
                >
                    Pular e começar direto →
                </button>
            </div>

            {/* Terms Modal */}
            {showTerms && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-900 rounded-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto border border-slate-700">
                        <div className="sticky top-0 bg-slate-900 p-4 border-b border-slate-800 flex justify-between items-center">
                            <h2 className="text-white font-semibold">Termos de Uso</h2>
                            <button
                                onClick={() => setShowTerms(false)}
                                className="text-slate-400 hover:text-white"
                            >
                                ✕
                            </button>
                        </div>
                        <div className="p-4 text-slate-300 text-sm space-y-4">
                            <section>
                                <h3 className="text-white font-medium mb-2">O que é o Justiça Ágil?</h3>
                                <p className="text-slate-400">
                                    O Justiça Ágil é uma <strong className="text-slate-300">ferramenta tecnológica de automação</strong> que facilita o acesso aos canais oficiais de defesa do consumidor (Procon/Consumidor.gov.br).
                                </p>
                            </section>

                            <section>
                                <h3 className="text-white font-medium mb-2">O que NÃO somos</h3>
                                <ul className="text-slate-400 space-y-1 list-disc list-inside">
                                    <li>Não prestamos serviços jurídicos</li>
                                    <li>Não somos advogados</li>
                                    <li>Não substituímos a consulta a um profissional</li>
                                </ul>
                            </section>

                            <section>
                                <h3 className="text-white font-medium mb-2">Sua responsabilidade</h3>
                                <p className="text-slate-400">
                                    Você é o único responsável pela veracidade das informações que fornece e pela decisão de protocolar a reclamação. Você está exercendo seu direito constitucional de petição (Art. 5º, XXXIV da CF/88) de forma direta e autônoma.
                                </p>
                            </section>

                            <section>
                                <h3 className="text-white font-medium mb-2">Privacidade</h3>
                                <p className="text-slate-400">
                                    Seus dados são processados de forma efêmera e não são armazenados em nossos servidores. Você mantém controle total sobre suas informações.
                                </p>
                            </section>

                            <section>
                                <h3 className="text-white font-medium mb-2">Limitações</h3>
                                <p className="text-slate-400">
                                    Não garantimos o resultado das reclamações protocoladas. A taxa de sucesso depende da conduta da empresa reclamada e da análise do órgão competente. Para casos complexos ou valores elevados, recomendamos consultar um advogado.
                                </p>
                            </section>
                        </div>
                        <div className="p-4 border-t border-slate-800">
                            <button
                                onClick={() => setShowTerms(false)}
                                className="w-full btn-primary py-3 rounded-xl text-white font-medium"
                            >
                                Entendi
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
