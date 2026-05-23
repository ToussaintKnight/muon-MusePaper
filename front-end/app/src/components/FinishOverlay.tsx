import { useState } from 'react';
import { useContentStore } from '@/store/contentStore';

interface FinishOverlayProps {
  onClose: () => void;
}

export default function FinishOverlay({ onClose }: FinishOverlayProps) {
  const { clicks, issue, saveSession, hasUnsavedChanges } = useContentStore();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const clickCount = clicks.size;
  const totalArticles = issue?.pages.reduce((sum, p) => sum + p.sections.reduce((s, sec) => s + sec.articles.length, 0), 0) ?? 0;
  const ignoreCount = Math.max(0, totalArticles - clickCount);

  const handleSave = async () => {
    setSaving(true);
    const result = await saveSession();
    setSaving(false);
    if (result.success) {
      setSaved(true);
      setTimeout(() => onClose(), 2000);
    }
  };

  return (
    <div className="fixed inset-0 bg-paper/95 z-[200] flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-paper border-2 border-ink p-8 shadow-2xl">
        {/* Masthead mini */}
        <div className="text-center mb-6">
          <h2 className="font-headline text-ink text-2xl font-black uppercase tracking-tight">
            The Daily Muse
          </h2>
          <div className="border-t border-ink mt-2 pt-2">
            <span className="font-caption text-ink-faded text-xs italic tracking-widest">
              {issue?.issue_date} — Edition No. {issue?.issue_number}
            </span>
          </div>
        </div>

        {!saved ? (
          <>
            <div className="text-center mb-8">
              <div className="font-headline text-ink text-lg mb-2">
                Today's Reading Summary
              </div>
              <div className="grid grid-cols-2 gap-4 my-6">
                <div className="text-center p-4 border border-ink">
                  <div className="font-headline text-3xl font-black text-ink">{clickCount}</div>
                  <div className="font-caption text-xs text-ink-faded uppercase tracking-widest">Explored</div>
                </div>
                <div className="text-center p-4 border border-ink">
                  <div className="font-headline text-3xl font-black text-ink-faded">{ignoreCount}</div>
                  <div className="font-caption text-xs text-ink-faded uppercase tracking-widest">Passed</div>
                </div>
              </div>
              <p className="font-body text-ink-light text-sm leading-relaxed">
                Your paper learns from every article you explore. Tomorrow's edition will be better tailored to your interests.
              </p>
            </div>

            <div className="flex gap-3 justify-center">
              <button
                onClick={onClose}
                className="font-body text-xs small-caps tracking-[0.15em] border border-ink px-6 py-3 hover:bg-ink hover:text-paper transition-colors"
              >
                Keep Reading
              </button>
              <button
                onClick={handleSave}
                disabled={saving || !hasUnsavedChanges}
                className="font-body text-xs small-caps tracking-[0.15em] bg-ink text-paper px-6 py-3 border border-ink hover:bg-paper hover:text-ink transition-colors disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save & Close'}
              </button>
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">✓</div>
            <div className="font-headline text-ink text-xl mb-2">Saved</div>
            <p className="font-caption text-ink-faded italic">
              Tomorrow's edition is being prepared.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
