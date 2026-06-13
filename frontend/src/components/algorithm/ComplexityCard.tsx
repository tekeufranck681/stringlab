interface Props {
  time: string;
  space: string;
}

export default function ComplexityCard({ time, space }: Props) {
  return (
    <div className="rounded-xl border border-slate-100 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-3">
        <h3 className="text-xs font-medium uppercase tracking-widest text-slate-400">
          Complexity
        </h3>
      </div>

      <div className="flex divide-x divide-slate-100">
        <div className="flex flex-1 flex-col gap-1 px-5 py-4">
          <span className="text-[10px] uppercase tracking-widest text-slate-300">
            Time
          </span>
          <span className="font-mono text-sm font-medium text-slate-700">
            {time}
          </span>
        </div>
        <div className="flex flex-1 flex-col gap-1 px-5 py-4">
          <span className="text-[10px] uppercase tracking-widest text-slate-300">
            Space
          </span>
          <span className="font-mono text-sm font-medium text-slate-700">
            {space}
          </span>
        </div>
      </div>
    </div>
  );
}
