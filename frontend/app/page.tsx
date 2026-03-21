'use client';

import { useState, useCallback } from 'react';
import Sidebar from '@/components/Sidebar';
import ChatInput, { getKForMode, type Mode } from '@/components/ChatInput';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'error';
  content: string;
}

interface Chat {
  id: string;
  title: string;
  messages: Message[];
}

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<Mode>('deep');

  const currentChat = chats.find((c) => c.id === currentChatId);
  const messages = currentChat?.messages ?? [];

  const askBackend = useCallback(async (query: string, k: number) => {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, k }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
  }, []);

  const handleSend = useCallback(
    async (query: string, k: number) => {
      const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: query };

      let chatId = currentChatId;
      const isNewChat = !currentChatId || currentChat?.messages.length === 0;

      if (isNewChat) {
        chatId = crypto.randomUUID();
        const title = query.length > 40 ? `${query.slice(0, 40)}...` : query;
        setChats((prev) => [{ id: chatId!, title, messages: [userMsg] }, ...prev.slice(0, 19)]);
        setCurrentChatId(chatId);
      } else {
        setChats((prev) =>
          prev.map((c) =>
            c.id === chatId ? { ...c, messages: [...c.messages, userMsg] } : c
          )
        );
      }

      setLoading(true);

      try {
        const { answer } = await askBackend(query, k);
        const assistantMsg: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: answer,
        };
        setChats((prev) =>
          prev.map((c) =>
            c.id === chatId ? { ...c, messages: [...c.messages, assistantMsg] } : c
          )
        );
      } catch (err) {
        const errorMsg: Message = {
          id: crypto.randomUUID(),
          role: 'error',
          content: err instanceof Error ? err.message : 'Something went wrong.',
        };
        setChats((prev) =>
          prev.map((c) =>
            c.id === chatId ? { ...c, messages: [...c.messages, errorMsg] } : c
          )
        );
      } finally {
        setLoading(false);
      }
    },
    [askBackend, currentChatId, currentChat]
  );

  const handleHistoryClick = useCallback((id: string) => {
    setCurrentChatId(id);
    setSidebarOpen(false);
  }, []);

  const handleNewChat = useCallback(() => {
    setCurrentChatId(null);
    setSidebarOpen(false);
  }, []);

  const showWelcome = messages.length === 0 && !loading;

  return (
    <div className="flex h-screen">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        history={chats.map((c) => ({ id: c.id, title: c.title }))}
        onHistoryClick={handleHistoryClick}
        currentChatId={currentChatId}
        onSuggestedClick={(query) => handleSend(query, getKForMode(mode))}
      />

      <main
        className={`flex-1 flex flex-col min-w-0 bg-[var(--bg-main)] transition-[margin] duration-200 ${
          sidebarOpen ? 'ml-[280px]' : ''
        }`}
      >
        <header className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
          <div className="flex gap-2">
            <button
              onClick={() => setSidebarOpen((o) => !o)}
              className="w-10 h-10 flex items-center justify-center border border-[var(--border)] rounded-lg text-[var(--text-secondary)] hover:bg-white/5 hover:text-[var(--text-primary)]"
              aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
            >
              <MenuIcon open={sidebarOpen} />
            </button>
            <button
              onClick={handleNewChat}
              className="w-10 h-10 flex items-center justify-center border border-[var(--border)] rounded-lg text-[var(--text-secondary)] hover:bg-white/5 hover:text-[var(--text-primary)]"
              aria-label="New Chat"
            >
              <NewChatIcon />
            </button>
          </div>
          <button className="flex items-center gap-2 px-4 py-2.5 bg-[var(--bg-input)] border border-[var(--border)] rounded-full text-sm font-medium">
            <LightningIcon className="w-4 h-4 text-[var(--accent-teal)]" />
            Finance Bot
          </button>
        </header>

        <div className="flex-1 overflow-y-auto px-6 py-10 pb-32">
          {showWelcome && (
            <div className="flex flex-col items-center justify-center min-h-[360px] text-center">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[var(--accent-teal)] via-[var(--accent-yellow)] to-[var(--accent-orange)] mb-6" />
              <h1 className="text-3xl font-bold tracking-tight mb-3 bg-gradient-to-r from-white to-[var(--text-secondary)] bg-clip-text text-transparent">
                Welcome to Grok ZeroPoint
              </h1>
              <p className="text-[var(--text-secondary)] max-w-[480px] leading-relaxed">
                Introducing Grok ZeroPoint — an advanced AI that embraces fearless ideas, and help you
                think beyond the ordinary. Ask anything.
              </p>
            </div>
          )}

          <div className="max-w-[720px] mx-auto space-y-6">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] px-5 py-4 rounded-2xl text-[0.95rem] leading-relaxed whitespace-pre-wrap break-words
                    ${
                      msg.role === 'user'
                        ? 'bg-[var(--bg-input)] border border-[var(--border)]'
                        : msg.role === 'error'
                          ? 'bg-red-500/10 border border-red-500/50 text-red-400'
                          : 'bg-[var(--bg-card)] border border-[var(--border)]'
                    }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="flex gap-1 px-5 py-4">
                  <span className="w-2 h-2 rounded-full bg-[var(--text-muted)] animate-pulse" />
                  <span className="w-2 h-2 rounded-full bg-[var(--text-muted)] animate-pulse [animation-delay:0.2s]" />
                  <span className="w-2 h-2 rounded-full bg-[var(--text-muted)] animate-pulse [animation-delay:0.4s]" />
                </div>
              </div>
            )}
          </div>
        </div>

        <ChatInput
          onSend={handleSend}
          disabled={loading}
          mode={mode}
          onModeChange={setMode}
          sidebarOpen={sidebarOpen}
        />
      </main>
    </div>
  );
}

function MenuIcon({ open }: { open: boolean }) {
  if (open) {
    return (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
        <path d="M18 6 6 18M6 6l12 12" />
      </svg>
    );
  }
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  );
}

function NewChatIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}

function LightningIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z" />
    </svg>
  );
}
