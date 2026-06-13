interface Props {
  label: string;
  value: string | number;
}

export default function StatsCard({ label, value }: Props) {
  return (
    <div
      className="
      rounded-xl
      border
      bg-white
      p-6
    "
    >
      <p
        className="
        text-sm
        text-slate-500
      "
      >
        {label}
      </p>

      <h2
        className="
        mt-2
        text-3xl
        font-bold
      "
      >
        {value}
      </h2>
    </div>
  );
}
