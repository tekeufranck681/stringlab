interface TraceStep {
  step: number;
  message: string;
}

interface Props {
  steps: TraceStep[];
}

export default function TracePanel({ steps }: Props) {
  return (
    <div className="flex h-[400px] flex-col rounded-xl border border-slate-100 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-3">
        <h3 className="text-xs font-medium uppercase tracking-widest text-slate-400">
          Step Log
        </h3>
      </div>

      <div className="flex-1 overflow-y-auto p-3 [scrollbar-color:theme(colors.slate.200)_transparent] [scrollbar-width:thin]">
        {steps.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <span className="text-xs text-slate-300">No steps yet</span>
          </div>
        ) : (
          <div className="space-y-1.5">
            {steps.map((step) => (
              <div
                key={step.step}
                className="flex gap-3 rounded-lg px-3 py-2.5 transition-colors hover:bg-slate-50"
              >
                <span className="mt-0.5 flex h-4 w-4 flex-shrink-0 items-center justify-center rounded bg-slate-100 text-[9px] font-semibold text-slate-400">
                  {step.step}
                </span>
                <p className="text-xs leading-relaxed text-slate-600">
                  {step.message}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
