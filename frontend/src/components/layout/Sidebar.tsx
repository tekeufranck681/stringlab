import { useState } from "react";
import { LayoutDashboard, Info, ChevronDown } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

interface SidebarItem {
  title: string;
  path: string;
  badge?: string;
}

interface SidebarGroupProps {
  title: string;
  items: SidebarItem[];
}

function SidebarGroup({ title, items }: SidebarGroupProps) {
  const [open, setOpen] = useState(true);
  const location = useLocation();

  return (
    <div className="mb-1">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between rounded-md px-2.5 py-1.5 text-left transition-colors hover:bg-[#0F1923]"
      >
        <span className="text-[10px] font-medium uppercase tracking-widest text-[#3A5A78]">
          {title}
        </span>
        <ChevronDown
          size={12}
          className={`text-[#3A5A78] transition-transform duration-200 ${open ? "rotate-180" : ""}`}
        />
      </button>

      <div
        className={`overflow-hidden transition-all duration-250 ${
          open ? "max-h-64" : "max-h-0"
        }`}
      >
        {items.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                group my-0.5 flex items-center justify-between rounded-md py-1.5 pl-4 pr-2.5
                border-l-2 text-[12.5px] transition-all duration-150
                ${
                  isActive
                    ? "border-cyan-400 bg-[#060B11] text-cyan-400"
                    : "border-transparent text-[#5A7394] hover:border-cyan-400 hover:bg-[#060B11] hover:text-cyan-400"
                }
              `}
            >
              <span>{item.title}</span>
              {item.badge && (
                <span className="rounded bg-[#0E4F5C] px-1.5 py-0.5 text-[9px] font-medium tracking-wide text-cyan-400">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside
      className="flex h-screen w-64 flex-col border-r border-[#1A2740] bg-[#080D14]"
      style={{ fontFamily: "var(--font-mono, 'JetBrains Mono', monospace)" }}
    >
      {/* Header */}
      <div className="flex items-center gap-2.5 border-b border-[#1A2740] px-5 py-4">
        <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-md bg-[#0E4F5C]">
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            aria-hidden="true"
          >
            <path
              d="M2 4h12M2 8h8M2 12h10"
              stroke="#22D3EE"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>
        </div>
        <div>
          <p className="text-sm font-medium tracking-wide text-cyan-400">
            StringLab
          </p>
          <p className="text-[10px] uppercase tracking-widest text-[#3A5A78]">
            String Algorithms
          </p>
        </div>
      </div>

      {/* Nav */}
      <div className="flex-1 overflow-y-auto p-2.5 [scrollbar-color:#1A2740_transparent] [scrollbar-width:thin]">
        <Link
          to="/"
          className={`
            mb-3 flex items-center gap-2 rounded-md px-2.5 py-1.5 text-sm transition-colors
            ${
              location.pathname === "/"
                ? "bg-[#0E2D3A] text-cyan-400"
                : "text-[#7A9BB8] hover:bg-[#0F1923] hover:text-[#E2EAF4]"
            }
          `}
        >
          <LayoutDashboard size={15} />
          Dashboard
        </Link>

        <div className="my-2 h-px bg-[#1A2740]" />

        <SidebarGroup
          title="Analysis & Properties"
          items={[
            { title: "Palindrome Detection", path: "/algorithm/palindrome" },
            { title: "Character Frequency", path: "/algorithm/frequency" },
            {
              title: "Longest Palindromic Substring",
              path: "/algorithm/longest-palindrome",
            },
          ]}
        />

        <SidebarGroup
          title="Search & Matching"
          items={[
            { title: "Find Occurrences", path: "/algorithm/find-occurrences" },
            {
              title: "Occurrence Counter",
              path: "/algorithm/occurrence-counter",
            },
            { title: "KMP Search", path: "/algorithm/kmp", badge: "KMP" },
          ]}
        />

        <SidebarGroup
          title="Comparison & Similarity"
          items={[
            { title: "Anagram Detection", path: "/algorithm/anagram" },
            { title: "Edit Distance", path: "/algorithm/edit-distance" },
            { title: "LCS", path: "/algorithm/lcs" },
          ]}
        />

        <SidebarGroup
          title="Transformation & Encoding"
          items={[
            { title: "Reverse Transformation", path: "/algorithm/reverse" },
            { title: "Caesar Cipher", path: "/algorithm/caesar" },
            { title: "Run Length Encoding", path: "/algorithm/rle" },
          ]}
        />
      </div>

      {/* Footer */}
      <div className="border-t border-[#1A2740] p-2.5">
        <button className="flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-xs text-[#3A5A78] transition-colors hover:bg-[#0F1923] hover:text-[#7A9BB8]">
          <Info size={14} />
          About StringLab
        </button>
      </div>
    </aside>
  );
}
