/**
 * ChatPage — full chat page with layout, window, and input.
 */
import AppLayout from '../components/layout/AppLayout';
import ChatWindow from '../components/chat/ChatWindow';
import ChatInput from '../components/chat/ChatInput';
import useChatStore from '../store/chatStore';

export default function ChatPage() {
    const { sendMessage, isStreaming, activeSessionId, createSession } = useChatStore();

    const handleSend = async (content) => {
        // Auto-create a session if none is active
        let sessionId = activeSessionId;
        if (!sessionId) {
            sessionId = await createSession('New Chat');
        }
        await sendMessage(content);
    };

    return (
        <AppLayout>
            <ChatWindow />
            <ChatInput onSend={handleSend} disabled={isStreaming} />
        </AppLayout>
    );
}
