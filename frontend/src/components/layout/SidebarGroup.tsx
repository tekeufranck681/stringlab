import { ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router-dom";

interface SidebarItem {
  title: string;
  path: string;
}

interface Props {
  title: string;
  items: SidebarItem[];
}

export default function SidebarGroup({ title, items }: Props) {
  const [open, setOpen] = useState(true);

  return (
    <div className="mb-2">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between text-xs font-semibold text-gray-300 uppercase tracking-wide"
      >
        {title}

        {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
      </button>

      {open && (
        <div className="mt-2 space-y-1">
          {items.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `
                block rounded-md px-3 py-2 text-sm transition
                ${
                  isActive
                    ? "bg-violet-600 text-white"
                    : "text-gray-300 hover:bg-slate-800"
                }
              `
              }
            >
              {item.title}
            </NavLink>
          ))}
        </div>
      )}
    </div>
  );
}
