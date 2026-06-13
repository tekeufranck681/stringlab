import { ReactNode } from "react";

interface Props {
  title?: string;
  children?: ReactNode;
}

export default function VisualizationPanel({
  title = "Visualization",
  children,
}: Props) {
  return (
    <div className="rounded-xl border border-slate-100 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-3">
        <h3 className="text-xs font-medium uppercase tracking-widest text-slate-400">
          {title}
        </h3>
      </div>

      <div className="flex min-h-[400px] items-center justify-center rounded-b-xl p-6">
        {children || (
          <div className="flex flex-col items-center gap-2">
            <div className="h-80 w-150 rounded-lg border-2 border-dashed border-slate-200" />
            <span className="text-xs text-slate-300">
              Visualization will appear here
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
