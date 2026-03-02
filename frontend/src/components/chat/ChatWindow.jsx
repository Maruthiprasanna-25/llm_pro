/**
 * ChatWindow — message list with auto-scroll and streaming indicator.
 */
import { useEffect, useRef } from 'react';
import useChatStore from '../../store/chatStore';
import MessageBubble from './MessageBubble';

export default function ChatWindow() {
    const { messages, isStreaming, streamingContent, activeSessionId } = useChatStore();
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, streamingContent]);

    if (!activeSessionId) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className="text-center animate-fade-in">
                    <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-2xl shadow-primary-500/30">
                        <span className="text-3xl">🎓</span>
                    </div>
                    <h2 className="text-2xl font-semibold text-white mb-2">Campus AI</h2>
                    <p className="text-white/40 max-w-md">
                        Start a new chat or select an existing session from the sidebar.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-4xl mx-auto">
                {messages.map((msg, idx) => (
                    <MessageBubble key={idx} role={msg.role} content={msg.content} />
                ))}

                {/* Streaming indicator */}
                {isStreaming && (
                    <div className="flex justify-start mb-4 animate-fade-in">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center mr-3 mt-1 shadow-lg shadow-primary-500/20">
                            <span className="text-xs font-bold text-white">AI</span>
                        </div>
                        <div className="glass-panel rounded-2xl rounded-bl-md px-4 py-3 max-w-[75%]">
                            {streamingContent ? (
                                <p className="text-white/90 whitespace-pre-wrap">{streamingContent}<span className="animate-pulse">▌</span></p>
                            ) : (
                                <div className="flex items-center gap-1.5 py-1">
                                    <div className="typing-dot" style={{ animationDelay: '0ms' }} />
                                    <div className="typing-dot" style={{ animationDelay: '150ms' }} />
                                    <div className="typing-dot" style={{ animationDelay: '300ms' }} />
                                </div>
                            )}
                        </div>
                    </div>
                )}

                <div ref={bottomRef} />
            </div>
        </div>
    );
}
