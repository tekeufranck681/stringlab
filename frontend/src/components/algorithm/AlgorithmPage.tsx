import { ReactNode } from "react";

interface Props {
  header: ReactNode;
  input: ReactNode;
  actions: ReactNode;
  visualization: ReactNode;
  result: ReactNode;
  trace: ReactNode;
  complexity: ReactNode;
  controls?: ReactNode;
}

export default function AlgorithmPage({
  header,
  input,
  actions,
  visualization,
  result,
  trace,
  complexity,
  controls,
}: Props) {
  return (
    <div className="space-y-5">
      {header}

      <div className="grid gap-4 xl:grid-cols-3">
        {/* Main column */}
        <div className="space-y-4 xl:col-span-2">
          <div className="rounded-xl border border-slate-100 bg-white shadow-sm">
            <div className="p-4">{input}</div>
            <div className="border-t border-slate-100 px-4 py-3">{actions}</div>
          </div>

          {visualization}

          {controls && <div>{controls}</div>}

          {result}
        </div>

        {/* Sidebar column */}
        <div className="space-y-4">
          {complexity}
          {trace}
        </div>
      </div>
    </div>
  );
}
