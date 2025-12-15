import React from 'react';

export function MessageBubble({ message, isFirst }) {
    const isUser = message.role === 'user';

    return (
        <div
            className={`flex items-end gap-2 mb-1 ${isUser ? 'justify-end' : 'justify-start'} ${isUser ? 'animate-slide-in-right' : 'animate-slide-in-left'
                }`}
        >
            {/* Avatar for assistant (only on first message of a group) */}
            {!isUser && isFirst && (
                <div className="avatar-assistant w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0">
                    👩‍⚖️
                </div>
            )}

            {/* Spacer when not showing avatar */}
            {!isUser && !isFirst && (
                <div className="w-8 flex-shrink-0" />
            )}

            {/* Message bubble */}
            <div
                className={`max-w-[80%] px-4 py-3 ${isUser
                        ? 'message-user text-white'
                        : 'message-assistant text-slate-100'
                    }`}
            >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {message.content}
                </p>
            </div>
        </div>
    );
}
