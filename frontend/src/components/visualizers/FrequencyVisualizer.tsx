interface Props {
  frequency: Record<string, number>;
}

export default function FrequencyVisualizer({ frequency }: Props) {
  return (
    <div className="space-y-3 font-logo">
      {Object.entries(frequency).map(([char, count]) => (
        <div key={char} className="flex items-center gap-3">
          <span className="w-6">{char}</span>

          <div
            className="
              h-6
              rounded
              bg-violet-500
              "
            style={{
              width: `${count * 30}px`,
            }}
          />

          <span>{count}</span>
        </div>
      ))}
    </div>
  );
}
