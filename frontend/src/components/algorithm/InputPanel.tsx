export interface InputField {
  name: string;
  label: string;
  type: string;
}

interface InputPanelProps {
  fields: InputField[];
  values: Record<string, string>;
  onChange: (name: string, value: string) => void;
}

export default function InputPanel({
  fields,
  values,
  onChange,
}: InputPanelProps) {
  return (
    <div className="rounded-xl border border-slate-100 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-3">
        <h3 className="text-xs font-medium uppercase tracking-widest text-slate-400">
          Input
        </h3>
      </div>

      <div className="grid gap-3 p-4">
        {fields.map((field) => (
          <div key={field.name} className="flex flex-col gap-1.5">
            <label className="text-[10px] font-medium uppercase tracking-widest text-slate-400">
              {field.label}
            </label>
            <input
              type={field.type}
              value={values[field.name] || ""}
              placeholder={`Enter ${field.label.toLowerCase()}…`}
              onChange={(e) => onChange(field.name, e.target.value)}
              className="
                w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2
                font-mono text-sm text-slate-700 outline-none placeholder:text-slate-300
                transition-colors
                focus:border-violet-300 focus:bg-white focus:ring-2 focus:ring-violet-100
                hover:border-slate-300
              "
            />
          </div>
        ))}
      </div>
    </div>
  );
}
