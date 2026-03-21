'use client';

import { useRef, useEffect, FormEvent, KeyboardEvent } from 'react';

export type Mode = 'think' | 'deep' | 'brainstorm';

const MODE_K: Record<Mode, number> = {
  think: 5,
  deep: 10,
  brainstorm: 15,
};

export function getKForMode(mode: Mode): number {
  return MODE_K[mode];
}

export default function ChatInput({
  onSend,
  disabled,
  mode,
  onModeChange,
  sidebarOpen,
}: {
  onSend: (query: string, k: number) => void;
  disabled: boolean;
  mode: Mode;
  onModeChange: (mode: Mode) => void;
  sidebarOpen?: boolean;
}) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: FormEvent) => {
    e?.preventDefault();
    const query = textareaRef.current?.value.trim();
    if (!query || disabled) return;
    onSend(query, getKForMode(mode));
    if (textareaRef.current) {
      textareaRef.current.value = '';
      textareaRef.current.style.height = '24px';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    const resize = () => {
      el.style.height = '24px';
      el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
    };
    el.addEventListener('input', resize);
    return () => el.removeEventListener('input', resize);
  }, []);

  return (
    <div
      className={`fixed bottom-0 right-0 px-6 pb-8 pt-5 bg-gradient-to-t from-[var(--bg-main)] via-[var(--bg-main)]/90 to-transparent transition-[left] duration-200 ${
        sidebarOpen ? 'left-[280px]' : 'left-0'
      }`}
    >
      <form onSubmit={handleSubmit} className="max-w-[720px] mx-auto">
        <div className="bg-[var(--bg-input)] border border-[var(--border)] rounded-3xl px-5 py-4">
          <textarea
            ref={textareaRef}
            placeholder="Ask Anything..."
            rows={1}
            maxLength={2000}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            className="w-full bg-transparent border-none text-[var(--text-primary)] text-base resize-none outline-none min-h-[24px] max-h-[120px] placeholder:text-[var(--text-muted)] disabled:opacity-50"
          />
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-[var(--border)]">
            <button
              type="button"
              className="p-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              aria-label="Attach"
            >
            </button>
            <div className="flex gap-2 flex-wrap">
              <ModeButton
                active={mode === 'think'}
                onClick={() => onModeChange('think')}
                icon={<ThinkIcon />}
                label="Think Bigger"
              />
              <ModeButton
                active={mode === 'deep'}
                onClick={() => onModeChange('deep')}
                icon={<SearchIcon />}
                label="Deep Search"
              />
              <ModeButton
                active={mode === 'brainstorm'}
                onClick={() => onModeChange('brainstorm')}
                icon={<BrainstormIcon />}
                label="Brainstorm Mode"
              />
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}

function ModeButton({
  active,
  onClick,
  icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center gap-1.5 px-3.5 py-2 rounded-full text-sm font-sans transition-all ${
        active
          ? 'bg-[var(--accent-teal)]/15 border border-[var(--accent-teal)] text-[var(--accent-teal)]'
          : 'bg-[var(--bg-main)] border border-[var(--border)] text-[var(--text-secondary)] hover:bg-white/5 hover:text-[var(--text-primary)]'
      }`}
    >
      <span className="w-4 h-4 shrink-0">{icon}</span>
      {label}
    </button>
  );
}

function AttachmentIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
    </svg>
  );
}

function ThinkIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-full h-full">
      <path d="M9 18h6M10 22h4M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14" />
    </svg>
  );
}

function SearchIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-full h-full">
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  );
}

function BrainstormIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-full h-full">
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
      <circle cx="12" cy="12" r="3" />
      <path d="M12 9v6M9 12h6" />
    </svg>
  );
}
