/**
 * MessageBubble — styled message bubble with markdown rendering.
 */
import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { speak, stopSpeaking } from '../../utils/tts';

export default function MessageBubble({ role, content }) {
    const isUser = role === 'user';
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [isCopied, setIsCopied] = useState(false);

    // Stop speaking if component unmounts
    useEffect(() => {
        return () => {
            if (isSpeaking) stopSpeaking();
        };
    }, [isSpeaking]);

    const handleToggleSpeak = () => {
        if (isSpeaking) {
            stopSpeaking();
            setIsSpeaking(false);
        } else {
            setIsSpeaking(true);
            speak(content, () => setIsSpeaking(false));
        }
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(content);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
    };

    return (
        <div
            className={`flex animate-slide-up ${isUser ? 'justify-end' : 'justify-start'} mb-6`}
        >
            {/* Avatar */}
            {!isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center mr-3 mt-1 shadow-lg shadow-primary-500/20">
                    <span className="text-xs font-bold text-white">AI</span>
                </div>
            )}

            {/* Bubble Container */}
            <div className={`flex flex-col gap-2 max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
                <div
                    className={`relative group rounded-2xl px-4 py-3 ${isUser
                            ? 'bg-primary-600 text-white rounded-br-md shadow-lg shadow-primary-500/10'
                            : 'glass-panel text-white/90 rounded-bl-md'
                        }`}
                >
                    <div className="prose prose-invert prose-sm max-w-none [&>p]:mb-2 [&>p:last-child]:mb-0 [&>ul]:my-1 [&>ol]:my-1 [&>pre]:bg-black/30 [&>pre]:rounded-lg [&>pre]:p-3">
                        <ReactMarkdown>{content}</ReactMarkdown>
                    </div>
                </div>

                {/* Action Toolbar for Assistant */}
                {!isUser && (
                    <div className="flex items-center gap-1 ml-1">
                        {/* Speaker Toggle */}
                        <button
                            onClick={handleToggleSpeak}
                            className={`p-1.5 rounded-lg transition-all ${isSpeaking
                                    ? 'bg-primary-500/20 text-primary-400'
                                    : 'text-white/30 hover:text-white/60 hover:bg-white/5'
                                }`}
                            title={isSpeaking ? 'Stop reading' : 'Read aloud'}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                                {isSpeaking ? (
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z M9 9h6v6H9V9Z" />
                                ) : (
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.114 5.636a9 9 0 0 1 0 12.728M16.463 8.288a5.25 5.25 0 0 1 0 7.424M6.75 8.25l4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />
                                )}
                            </svg>
                        </button>

                        {/* Copy Button */}
                        <button
                            onClick={handleCopy}
                            className={`p-1.5 rounded-lg transition-all ${isCopied
                                    ? 'text-emerald-400'
                                    : 'text-white/30 hover:text-white/60 hover:bg-white/5'
                                }`}
                            title={isCopied ? 'Copied!' : 'Copy to clipboard'}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                                {isCopied ? (
                                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                                ) : (
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.25c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 1.927-.184" />
                                )}
                            </svg>
                        </button>
                    </div>
                )}
            </div>

            {/* User avatar */}
            {isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center ml-3 mt-1 shadow-lg">
                    <span className="text-xs font-bold text-white">U</span>
                </div>
            )}
        </div>
    );
}
