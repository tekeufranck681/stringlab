interface Props {
  title: string;
  description: string;
}

export default function AlgorithmHeader({ title, description }: Props) {
  return (
    <div className="items-left border-b border-slate-100 pb-5">
      <p className="mt-1 text-xs text-slate-400">
        {description}
      </p>
    </div>
  );
}
