import React, { useState, useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { InputArea } from './InputArea';
import { CategorySelector } from './CategorySelector';
import { UploadWidget } from './UploadWidget';
import { ReviewScreen } from '../Review/ReviewScreen';
import { WelcomeScreen } from '../Welcome/WelcomeScreen';
import { ViabilityScore } from '../Score/ViabilityScore';
import { ShieldCheck, Loader2, HelpCircle, User } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export function ChatLayout() {
    const [showWelcome, setShowWelcome] = useState(true);
    const [preferVoice, setPreferVoice] = useState(false);
    const [messages, setMessages] = useState([]);
    const [showCategories, setShowCategories] = useState(false);
    const [showUpload, setShowUpload] = useState(false);
    const [showReview, setShowReview] = useState(false);
    const [claimData, setClaimData] = useState(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const [scoreData, setScoreData] = useState(null);
    const [showScore, setShowScore] = useState(false);

    const { user, login, logout } = useAuth();

    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, showCategories, showUpload, isGenerating, isTyping]);

    const handleWelcomeStart = () => {
        setShowWelcome(false);
        setShowCategories(true);
        // Add initial messages with delay for natural feel
        setTimeout(() => {
            setMessages([
                {
                    id: 1,
                    role: 'assistant',
                    content: 'Oi! Que bom ter você aqui. 😊'
                }
            ]);
        }, 300);
        setTimeout(() => {
            setMessages(prev => [...prev, {
                id: 2,
                role: 'assistant',
                content: 'Me conta: o que está te incomodando no seu imóvel? Pode ser algo que o proprietário não resolveu, uma cobrança indevida, ou qualquer outra situação.'
            }]);
        }, 1200);
    };

    const handlePreferenceSelect = (preference) => {
        setPreferVoice(preference === 'voice');
        handleWelcomeStart();
    };

    const handleGenerateClaim = async () => {
        setIsGenerating(true);
        try {
            const lastUserMessage = messages.slice().reverse().find(m => m.role === 'user')?.content || "";

            const response = await fetch('http://localhost:8000/api/claim/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    report: lastUserMessage,
                    forensic_data: {},
                    legal_analysis: {}
                })
            });

            const data = await response.json();
            setClaimData(data);
            setShowReview(true);
        } catch (error) {
            console.error("Erro ao gerar:", error);
            setMessages(prev => [...prev, {
                id: Date.now(),
                role: 'assistant',
                content: 'Ops, tive um probleminha técnico. Mas não se preocupe, vou tentar de novo. Pode repetir o que estava me contando?'
            }]);
        } finally {
            setIsGenerating(false);
        }
    };

    const handleSendMessage = async (text) => {
        const newMessage = { id: Date.now(), role: 'user', content: text };
        setMessages(prev => [...prev, newMessage]);
        setShowCategories(false);

        // Check keywords for special actions
        if (text.toLowerCase().includes("upload") || text.toLowerCase().includes("foto") || text.toLowerCase().includes("anexo") || text.toLowerCase().includes("enviar")) {
            setShowUpload(true);
            return;
        } else if (text.toLowerCase().includes("gerar") || text.toLowerCase().includes("reclamação") || text.toLowerCase().includes("concluir")) {
            handleGenerateClaim();
            return;
        }

        setIsTyping(true);

        try {
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: [...messages, newMessage].map(m => ({ role: m.role, content: m.content }))
                })
            });

            const data = await response.json();

            // Simulate natural typing delay
            setTimeout(async () => {
                setIsTyping(false);
                setMessages(prev => [...prev, {
                    id: Date.now() + 1,
                    role: data.message.role,
                    content: data.message.content
                }]);

                // After a few messages, analyze the case and show score
                const userMessages = [...messages, newMessage].filter(m => m.role === 'user');
                if (userMessages.length >= 2 && !showScore) {
                    try {
                        const analysisResponse = await fetch('http://localhost:8000/api/claim/analyze', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                report: userMessages.map(m => m.content).join(' ')
                            })
                        });
                        const analysisData = await analysisResponse.json();
                        setScoreData(analysisData);
                        setShowScore(true);
                    } catch (e) {
                        console.error("Erro na análise:", e);
                    }
                }
            }, 800 + Math.random() * 500);

        } catch (error) {
            console.error("Erro ao enviar mensagem:", error);
            setTimeout(() => {
                setIsTyping(false);
                setMessages(prev => [...prev, {
                    id: Date.now() + 1,
                    role: 'assistant',
                    content: 'Hm, parece que tive uma pequena falha de conexão. Pode tentar de novo? Estou aqui para te ajudar!'
                }]);
            }, 500);
        }
    };

    const handleCategorySelect = async (categoryId) => {
        setShowCategories(false);
        const categoryLabels = {
            'maintenance': 'Tenho problemas de manutenção no imóvel',
            'financial': 'Recebi cobranças ou multas indevidas',
            'deposit': 'Estão retendo minha caução/depósito',
            'other': 'É outro tipo de problema'
        };
        const text = categoryLabels[categoryId];
        handleSendMessage(text);
    };

    const handleUploadComplete = (fileData) => {
        setShowUpload(false);
        setMessages(prev => [...prev, {
            id: Date.now(),
            role: 'user',
            content: `📎 Enviei: ${fileData.original_name}`
        }]);

        setIsTyping(true);
        setTimeout(() => {
            setIsTyping(false);
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                role: 'assistant',
                content: 'Ótimo, recebi seu arquivo! 📄 Já analisei e isso vai ajudar bastante no seu caso. Quer que eu prepare a reclamação agora? É só dizer "gerar reclamação".'
            }]);
        }, 1500);
    };

    const handleAttachClick = () => {
        setShowUpload(true);
    };

    // Welcome Screen
    if (showWelcome) {
        return (
            <WelcomeScreen
                onStart={handleWelcomeStart}
                onPreferenceSelect={handlePreferenceSelect}
            />
        );
    }

    // Review Screen
    if (showReview && claimData) {
        return (
            <ReviewScreen
                data={claimData}
                onBack={() => setShowReview(false)}
                onConfirm={() => alert("Automação Iniciada! (Fim do MVP Fase 2.1)")}
            />
        );
    }

    return (
        <div className="flex flex-col h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-indigo-950">
            {/* Header */}
            <header className="glass-header flex items-center justify-between p-4 fixed top-0 w-full z-10">
                <div className="flex items-center gap-3">
                    <div className="avatar-assistant w-10 h-10 rounded-full flex items-center justify-center">
                        <span className="text-lg">👩‍⚖️</span>
                    </div>
                    <div>
                        <h1 className="font-semibold text-white text-base leading-tight">Ju</h1>
                        <p className="text-xs text-green-400 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                            Online agora
                        </p>
                    </div>
                </div>

                {/* Botão de atalho para Revisão - ÚTIL PARA TESTE */}
                <button
                    onClick={() => {
                        setClaimData({
                            company_name: '',
                            title: 'Reclamação Teste',
                            facts: '',
                            request: '',
                            value: ''
                        });
                        setShowReview(true);
                    }}
                    className="px-3 py-1.5 bg-purple-600/80 hover:bg-purple-500 text-white text-xs font-medium rounded-lg transition-colors"
                >
                    📝 Ir para Revisão
                </button>
                {/* Login / User Info */}
                <div className="flex items-center gap-2">
                    {user ? (
                        <div className="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700/50">
                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                            <span className="text-xs text-slate-300 font-medium hidden sm:block">
                                {user.name}
                            </span>
                            <button
                                onClick={logout}
                                className="ml-2 text-slate-400 hover:text-red-400 transition-colors"
                                title="Sair"
                            >
                                <span className="text-xs">✕</span>
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={login}
                            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-full shadow-lg transition-all animate-fade-in-up"
                        >
                            🏛️ Entrar com GOV.BR
                        </button>
                    )}
                </div>
            </header>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-4 pt-20 pb-4 scrollbar-hide">
                <div className="max-w-2xl mx-auto flex flex-col gap-1">
                    {messages.map((msg, index) => (
                        <MessageBubble
                            key={msg.id}
                            message={msg}
                            isFirst={index === 0 || messages[index - 1]?.role !== msg.role}
                        />
                    ))}

                    {isTyping && (
                        <div className="flex items-center gap-3 py-2 animate-fade-in-up">
                            <div className="avatar-assistant w-8 h-8 rounded-full flex items-center justify-center text-sm">
                                👩‍⚖️
                            </div>
                            <div className="message-assistant px-4 py-3 flex items-center gap-1">
                                <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full"></span>
                                <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full"></span>
                                <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full"></span>
                            </div>
                        </div>
                    )}

                    {isGenerating && (
                        <div className="flex items-center gap-3 py-4 animate-fade-in-up">
                            <div className="avatar-assistant w-8 h-8 rounded-full flex items-center justify-center">
                                <Loader2 className="animate-spin text-white" size={16} />
                            </div>
                            <div className="message-assistant px-4 py-3">
                                <span className="text-slate-300 text-sm">Preparando sua documentação jurídica...</span>
                            </div>
                        </div>
                    )}

                    {showCategories && (
                        <div className="animate-fade-in-up">
                            <CategorySelector onSelect={handleCategorySelect} />
                        </div>
                    )}

                    {showUpload && (
                        <div className="animate-fade-in-up">
                            <UploadWidget
                                onUploadComplete={handleUploadComplete}
                                onCancel={() => setShowUpload(false)}
                            />
                        </div>
                    )}

                    {showScore && scoreData && (
                        <div className="animate-fade-in-up my-4">
                            <ViabilityScore
                                score={scoreData.viability_score}
                                strengths={scoreData.strengths}
                                risks={scoreData.risks}
                                missingInfo={scoreData.missing_info}
                            />
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <InputArea
                onSendMessage={handleSendMessage}
                onAttachClick={handleAttachClick}
                disabled={showCategories || isGenerating}
                preferVoice={preferVoice}
            />

            {/* Legal Footer */}
            <footer className="bg-slate-950/80 border-t border-slate-800/30 py-2 px-4">
                <p className="text-center text-slate-500 text-[10px] max-w-2xl mx-auto">
                    Ferramenta de automação • Não prestamos serviços jurídicos •
                    <span className="text-slate-400"> Você é o autor da sua reclamação</span>
                </p>
            </footer>
        </div>
    );
}
