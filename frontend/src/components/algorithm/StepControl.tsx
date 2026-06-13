import {
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  Play,
  Pause,
} from "lucide-react";

interface Props {
  currentStep: number;
  totalSteps: number;
  isPlaying?: boolean;
  onPrevious?: () => void;
  onNext?: () => void;
  onPlay?: () => void;
  onReset?: () => void;
}

export default function StepControls({
  currentStep,
  totalSteps,
  isPlaying = false,
  onPrevious,
  onNext,
  onPlay,
  onReset,
}: Props) {
  const progress = totalSteps > 0 ? (currentStep / totalSteps) * 100 : 0;

  return (
    <div className="rounded-xl border border-slate-100 bg-white shadow-sm">
      {/* Progress bar */}
      <div className="h-0.5 w-full overflow-hidden rounded-t-xl bg-slate-100">
        <div
          className="h-full bg-violet-400 transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="flex items-center justify-between px-4 py-3">
        {/* Controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={onReset}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
            title="Reset"
          >
            <RotateCcw size={13} />
          </button>

          <button
            onClick={onPrevious}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 disabled:opacity-30"
            disabled={currentStep <= 0}
          >
            <ChevronLeft size={15} />
          </button>

          <button
            onClick={onPlay}
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-500 text-white transition-colors hover:bg-violet-600 active:scale-95"
          >
            {isPlaying ? <Pause size={13} /> : <Play size={13} />}
          </button>

          <button
            onClick={onNext}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 disabled:opacity-30"
            disabled={currentStep >= totalSteps}
          >
            <ChevronRight size={15} />
          </button>
        </div>

        {/* Step counter */}
        <span className="text-[11px] tabular-nums text-slate-400">
          {currentStep} <span className="text-slate-200">/</span> {totalSteps}
        </span>
      </div>
    </div>
  );
}
