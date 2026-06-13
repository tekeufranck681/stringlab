interface Props {
  title: string;
  value: string | number;
  success?: boolean;
}

export default function ResultCard({ title, value, success = true }: Props) {
  return (
    <div className="rounded-xl border border-slate-100 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-3">
        <h3 className="text-xs font-medium uppercase tracking-widest text-slate-400">
          {title}
        </h3>
      </div>

      <div className="flex items-center justify-center px-5 py-5">
        <div className="flex items-center gap-2">
          <span
            className={`h-1.5 w-1.5 rounded-full ${success ? "bg-emerald-400" : "bg-rose-400"}`}
          />
          <span
            className={`font-mono text-2xl font-semibold ${
              success ? "text-emerald-600" : "text-rose-500"
            }`}
          >
            {value}
          </span>
        </div>
      </div>
    </div>
  );
}
