import React, { useState, useRef } from 'react';
import { Upload, X, FileText, Image, CheckCircle, Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

export function UploadWidget({ onUploadComplete, onCancel }) {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const fileInputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setIsDragging(true);
        } else if (e.type === "dragleave") {
            setIsDragging(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFiles(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFiles(e.target.files[0]);
        }
    };

    const handleFiles = async (file) => {
        if (!file) return;

        // Basic client validation
        if (file.size > 10 * 1024 * 1024) {
            alert("Arquivo muito grande. Máximo 10MB.");
            return;
        }

        setIsUploading(true);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Erro no upload");
            }

            const data = await response.json();
            onUploadComplete(data);

        } catch (error) {
            console.error(error);
            alert("Falha ao enviar arquivo.");
            setIsUploading(false);
        }
    };

    return (
        <div className="w-full max-w-sm mx-auto mb-4 animate-in fade-in zoom-in duration-300">
            <div
                className={cn(
                    "relative border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center text-center transition-all bg-slate-800/50",
                    isDragging ? "border-blue-500 bg-slate-800" : "border-slate-600 hover:border-slate-500"
                )}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <button
                    onClick={onCancel}
                    className="absolute top-2 right-2 text-slate-500 hover:text-white"
                >
                    <X size={16} />
                </button>

                {isUploading ? (
                    <div className="flex flex-col items-center py-4">
                        <Loader2 className="animate-spin text-blue-500 mb-2" size={32} />
                        <span className="text-slate-300 text-sm">Enviando evidência...</span>
                    </div>
                ) : (
                    <>
                        <div className="w-12 h-12 rounded-full bg-slate-700 flex items-center justify-center mb-3 text-slate-300">
                            <Upload size={24} />
                        </div>

                        <h3 className="text-white font-medium mb-1">Upload de Evidência</h3>
                        <p className="text-slate-400 text-xs mb-4">
                            Arraste ou clique para enviar fotos ou PDFs.<br />
                            (Máx. 10MB)
                        </p>

                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors shadow-lg shadow-blue-500/20"
                        >
                            Selecionar Arquivo
                        </button>

                        <input
                            ref={fileInputRef}
                            type="file"
                            className="hidden"
                            accept="image/png, image/jpeg, application/pdf"
                            onChange={handleChange}
                        />
                    </>
                )}
            </div>
        </div>
    );
}
