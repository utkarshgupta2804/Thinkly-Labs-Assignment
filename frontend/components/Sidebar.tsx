'use client';

import { useState } from 'react';

const suggestedQuestions = [
  'What are the best tax saving schemes in India?',
  'How does PPF work and what are its benefits?',
  'What is ELSS and how can it help save tax?',
  'How to invest in mutual funds for beginners?',
  'What are the current FD rates in India?',
  'How does NPS work for retirement planning?',
  'What is the income tax slab for FY 2024-25?',
  'How to save tax under Section 80C?',
  'What is SIP and how does it work?',
  'Best ways to plan for retirement in India?',
];

export default function Sidebar({
  isOpen,
  onClose,
  history,
  onHistoryClick,
  currentChatId,
  onSuggestedClick,
}: {
  isOpen: boolean;
  onClose: () => void;
  history: { id: string; title: string }[];
  onHistoryClick: (id: string) => void;
  currentChatId: string | null;
  onSuggestedClick?: (query: string) => void;
}) {
  const [search, setSearch] = useState('');

  if (!isOpen) return null;

  return (
    <>
      <div
        className="fixed inset-0 bg-black/50 z-40 lg:hidden"
        onClick={onClose}
        aria-hidden="true"
      />
      <aside className="fixed left-0 top-0 bottom-0 z-50 w-[280px] min-w-[280px] bg-[var(--bg-sidebar)] border-r border-[var(--border)] flex flex-col p-5 pb-4">
      <div className="mb-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[var(--accent-teal)] via-[var(--accent-yellow)] to-[var(--accent-orange)] shrink-0" />
          <span className="text-lg font-semibold tracking-tight">Thinkly Labs Finance Bot</span>
        </div>
        <button
          onClick={onClose}
          className="lg:hidden p-2 -mr-2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
          aria-label="Close sidebar"
        >
          <CloseIcon className="w-5 h-5" />
        </button>
      </div>

      <nav className="flex flex-col gap-1 mb-6 overflow-y-auto max-h-[280px]">
        <h3 className="text-[0.7rem] font-semibold tracking-wider text-[var(--text-muted)] mb-2 uppercase">
          Suggested
        </h3>
        {suggestedQuestions.map((question) => (
          <button
            key={question}
            type="button"
            onClick={() => {
              onSuggestedClick?.(question);
              onClose();
            }}
            className="flex items-start gap-3 px-3.5 py-3 w-full text-left text-[var(--text-secondary)] rounded-lg text-[0.9rem] hover:bg-white/5 hover:text-[var(--text-primary)] transition-colors"
          >
            <QuestionIcon className="w-5 h-5 shrink-0 opacity-80 mt-0.5" />
            <span>{question}</span>
          </button>
        ))}
      </nav>

      <div className="flex-1 overflow-y-auto">
        <h3 className="text-[0.7rem] font-semibold tracking-wider text-[var(--text-muted)] mb-3 uppercase">
          TOMORROW
        </h3>
        <ul className="list-none">
          {history.map(({ id, title }) => (
            <li
              key={id}
              onClick={() => onHistoryClick(id)}
              className={`px-3.5 py-2.5 text-[0.88rem] rounded-lg cursor-pointer mb-0.5 truncate transition-colors ${
                id === currentChatId
                  ? 'bg-white/10 text-[var(--text-primary)]'
                  : 'text-[var(--text-secondary)] hover:bg-white/5 hover:text-[var(--text-primary)]'
              }`}
            >
              {title.length > 35 ? `${title.slice(0, 35)}...` : title}
            </li>
          ))}
        </ul>
      </div>
    </aside>
    </>
  );
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  );
}

function CloseIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path d="M18 6 6 18M6 6l12 12" />
    </svg>
  );
}

function QuestionIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <circle cx="12" cy="12" r="10" />
      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
      <path d="M12 17h.01" />
    </svg>
  );
}
