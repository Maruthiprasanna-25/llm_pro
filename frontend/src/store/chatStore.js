/**
 * Chat store — manages sessions, messages, and streaming state.
 */
import { create } from 'zustand';
import { sessionAPI, chatAPI } from '../services/api';

const useChatStore = create((set, get) => ({
    sessions: [],
    activeSessionId: null,
    messages: [],
    isStreaming: false,
    streamingContent: '',

    // ── Session management ────────────────────────────
    loadSessions: async () => {
        try {
            const { data } = await sessionAPI.list();
            set({ sessions: data.sessions });
        } catch (err) {
            console.error('Failed to load sessions', err);
        }
    },

    createSession: async (title) => {
        const { data } = await sessionAPI.create(title);
        set((state) => ({
            sessions: [data, ...state.sessions],
            activeSessionId: data.id,
            messages: [],
        }));
        return data.id;
    },

    selectSession: async (id) => {
        set({ activeSessionId: id, messages: [], streamingContent: '' });
        try {
            const { data } = await sessionAPI.getMessages(id);
            set({ messages: data });
        } catch (err) {
            console.error('Failed to load messages', err);
        }
    },

    deleteSession: async (id) => {
        await sessionAPI.delete(id);
        set((state) => {
            const sessions = state.sessions.filter((s) => s.id !== id);
            const activeSessionId =
                state.activeSessionId === id ? null : state.activeSessionId;
            return { sessions, activeSessionId, messages: activeSessionId ? state.messages : [] };
        });
    },

    // ── Chat ──────────────────────────────────────────
    sendMessage: async (content) => {
        const { activeSessionId } = get();
        if (!activeSessionId) return;

        // Optimistic: add user message
        const userMsg = { role: 'user', content };
        set((state) => ({
            messages: [...state.messages, userMsg],
            isStreaming: true,
            streamingContent: '',
        }));

        await chatAPI.stream(
            activeSessionId,
            content,
            // onToken
            (token) => {
                set((state) => ({
                    streamingContent: state.streamingContent + token,
                }));
            },
            // onDone
            () => {
                set((state) => ({
                    messages: [
                        ...state.messages,
                        { role: 'assistant', content: state.streamingContent },
                    ],
                    isStreaming: false,
                    streamingContent: '',
                }));
                // Refresh session list (title may have changed)
                get().loadSessions();
            },
            // onError
            (error) => {
                set((state) => ({
                    messages: [
                        ...state.messages,
                        { role: 'assistant', content: `⚠️ Error: ${error}` },
                    ],
                    isStreaming: false,
                    streamingContent: '',
                }));
            }
        );
    },
}));

export default useChatStore;
