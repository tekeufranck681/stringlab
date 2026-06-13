import { Play, Loader2, FlaskConical } from "lucide-react";

interface Props {
  runLabel: string;
  onRun: () => void;
  onLoadExample?: () => void;
  loading?: boolean;
}

export default function ActionButtons({
  runLabel,
  onRun,
  onLoadExample,
  loading = false,
}: Props) {
  return (
    <div className="flex items-center gap-2">
      {onLoadExample && (
        <button
          onClick={onLoadExample}
          className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-500 shadow-sm transition-colors hover:border-slate-300 hover:text-slate-700"
        >
          <FlaskConical size={12} />
          Load Example
        </button>
      )}

      <button
        onClick={onRun}
        disabled={loading}
        className="flex items-center gap-1.5 rounded-lg bg-violet-500 px-3 py-1.5 text-xs font-medium text-white shadow-sm transition-colors hover:bg-violet-600 active:scale-95 disabled:opacity-60"
      >
        {loading ? (
          <Loader2 size={12} className="animate-spin" />
        ) : (
          <Play size={12} />
        )}
        {loading ? "Running…" : runLabel}
      </button>
    </div>
  );
}
