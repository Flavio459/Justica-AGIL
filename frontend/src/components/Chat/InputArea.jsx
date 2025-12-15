import React, { useState, useRef } from 'react';
import { Send, Paperclip, Mic, MicOff, Loader2 } from 'lucide-react';

export function InputArea({ onSendMessage, onAttachClick, disabled, preferVoice }) {
    const [input, setInput] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessingVoice, setIsProcessingVoice] = useState(false);
    const recognitionRef = useRef(null);

    const handleSend = () => {
        if (input.trim()) {
            onSendMessage(input);
            setInput('');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const startVoiceRecording = () => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Seu navegador não suporta reconhecimento de voz. Tente o Chrome.');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.lang = 'pt-BR';
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;

        recognitionRef.current.onstart = () => {
            setIsRecording(true);
        };

        recognitionRef.current.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            setInput(transcript);
            setIsRecording(false);
            setIsProcessingVoice(false);
        };

        recognitionRef.current.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            setIsRecording(false);
            setIsProcessingVoice(false);
        };

        recognitionRef.current.onend = () => {
            setIsRecording(false);
        };

        recognitionRef.current.start();
    };

    const stopVoiceRecording = () => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            setIsProcessingVoice(true);
        }
    };

    const handleMicClick = () => {
        if (isRecording) {
            stopVoiceRecording();
        } else {
            startVoiceRecording();
        }
    };

    const placeholder = isRecording
        ? "Estou ouvindo..."
        : preferVoice
            ? "Toque no microfone ou digite aqui..."
            : "Conte o que aconteceu...";

    return (
        <div className="glass-header p-4 border-t border-slate-800/50">
            <div className="max-w-2xl mx-auto flex items-end gap-2">
                {/* Attach button */}
                <button
                    onClick={onAttachClick}
                    className="p-3 text-slate-400 hover:text-blue-400 hover:bg-slate-800/50 rounded-full transition-all duration-200 group"
                    disabled={disabled}
                    title="Anexar arquivo"
                >
                    <Paperclip size={20} className="group-hover:rotate-45 transition-transform" />
                </button>

                {/* Input field */}
                <div className={`flex-1 input-glass rounded-2xl transition-all duration-200 ${isRecording ? 'border-red-500/50 bg-red-500/10' : ''}`}>
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={placeholder}
                        className="w-full bg-transparent text-white p-3 max-h-32 min-h-[48px] resize-none focus:outline-none scrollbar-hide align-bottom placeholder:text-slate-500"
                        disabled={disabled || isRecording}
                        rows={1}
                    />
                </div>

                {/* Send or Mic button */}
                {input.trim() ? (
                    <button
                        onClick={handleSend}
                        disabled={disabled}
                        className="btn-primary p-3 rounded-full transition-all duration-200"
                    >
                        <Send size={20} className="text-white" fill="currentColor" />
                    </button>
                ) : (
                    <button
                        onClick={handleMicClick}
                        disabled={disabled || isProcessingVoice}
                        className={`p-3 rounded-full transition-all duration-200 ${isRecording
                                ? 'bg-red-500 text-white animate-pulse-glow'
                                : isProcessingVoice
                                    ? 'bg-slate-700 text-slate-400'
                                    : 'bg-slate-800 text-slate-400 hover:text-purple-400 hover:bg-slate-700'
                            }`}
                        title={isRecording ? "Parar gravação" : "Falar"}
                    >
                        {isProcessingVoice ? (
                            <Loader2 size={20} className="animate-spin" />
                        ) : isRecording ? (
                            <MicOff size={20} />
                        ) : (
                            <Mic size={20} />
                        )}
                    </button>
                )}
            </div>

            {/* Voice hint */}
            {isRecording && (
                <p className="text-center text-red-400 text-xs mt-2 animate-pulse">
                    🎙️ Gravando... Toque no ícone para parar
                </p>
            )}
        </div>
    );
}
