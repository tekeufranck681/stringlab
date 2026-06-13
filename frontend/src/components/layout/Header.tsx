import { Menu } from "lucide-react";

interface HeaderProps {
  onMenuClick?: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="flex items-center gap-4 border-b border-slate-200 bg-white px-6 py-3">
      <button
        className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-md text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 lg:hidden"
        onClick={onMenuClick}
        aria-label="Open sidebar"
      >
        <Menu size={15} />
      </button>

      <span className="text-[10px] font-medium uppercase tracking-widest text-slate-400">
        Interactive String Algorithm Visualizer
      </span>
    </header>
  );
}
