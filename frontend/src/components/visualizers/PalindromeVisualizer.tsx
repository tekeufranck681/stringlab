interface Props {
  text: string;
  left: number;
  right: number;
}

export default function PalindromeVisualizer({ text, left, right }: Props) {
  const chars = text.split("");

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Character cells */}
      <div className="flex flex-wrap justify-center gap-2">
        {chars.map((char, index) => {
          const isPointer = index === left || index === right;
          const isBetween = index > left && index < right;
          const isLeft = index === left;
          const isRight = index === right;

          return (
            <div key={index} className="flex flex-col items-center gap-1">
              <div
                className={`
                  flex h-12 w-12 items-center justify-center rounded-lg border-2 text-base font-semibold transition-all duration-200
                  ${
                    isPointer
                      ? "border-violet-400 bg-violet-50 text-violet-700 shadow-sm shadow-violet-100"
                      : isBetween
                        ? "border-slate-200 bg-slate-50 text-slate-500"
                        : "border-slate-200 bg-white text-slate-700"
                  }
                `}
              >
                {char === " " ? (
                  <span className="text-slate-300 text-xs">·</span>
                ) : (
                  char
                )}
              </div>

              {/* Index label */}
              <span className="text-[10px] text-slate-300">{index}</span>

              {/* Pointer arrow */}
              <span
                className={`text-[10px] font-medium transition-opacity duration-200 ${isPointer ? "opacity-100" : "opacity-0"}`}
              >
                {isLeft && isRight ? (
                  <span className="text-violet-500">↑</span>
                ) : isLeft ? (
                  <span className="text-violet-400">L</span>
                ) : (
                  <span className="text-violet-400">R</span>
                )}
              </span>
            </div>
          );
        })}
      </div>

      {/* Pointer info bar */}
      <div className="flex items-center gap-4 rounded-lg border border-slate-100 bg-slate-50 px-5 py-2.5 text-xs text-slate-500">
        <span>
          <span className="font-medium text-violet-500">L</span> = {left} &nbsp;
          <span className="font-mono text-slate-700">"{chars[left]}"</span>
        </span>
        <span className="h-3 w-px bg-slate-200" />
        <span>
          <span className="font-medium text-violet-500">R</span> = {right}{" "}
          &nbsp;
          <span className="font-mono text-slate-700">"{chars[right]}"</span>
        </span>
        <span className="h-3 w-px bg-slate-200" />
        <span>
          match:{" "}
          <span
            className={`font-medium ${chars[left] === chars[right] ? "text-emerald-500" : "text-rose-400"}`}
          >
            {chars[left] === chars[right] ? "yes" : "no"}
          </span>
        </span>
      </div>
    </div>
  );
}
