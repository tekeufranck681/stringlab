import { ArrowRight, BarChart2, Grid, Layers, FileText } from "lucide-react";
import { Link } from "react-router-dom";

interface StatsCardProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
}

function StatsCard({ label, value, icon }: StatsCardProps) {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-widest text-slate-400">
          {label}
        </span>
        <span className="text-slate-300">{icon}</span>
      </div>
      <span className="text-3xl font-semibold text-slate-800">{value}</span>
    </div>
  );
}

const categories = [
  {
    title: "Analysis & Properties",
    items: [
      "Palindrome Detection",
      "Character Frequency",
      "Longest Palindromic Substring",
    ],
    path: "/algorithm/palindrome",
    accent: "bg-cyan-500",
    text: "text-cyan-600",
    border: "hover:border-cyan-200",
  },
  {
    title: "Search & Matching",
    items: ["Find Occurrences", "Occurrence Counter", "KMP Search"],
    path: "/algorithm/kmp",
    accent: "bg-violet-500",
    text: "text-violet-600",
    border: "hover:border-violet-200",
  },
  {
    title: "Comparison & Similarity",
    items: ["Anagram Detection", "Edit Distance", "LCS"],
    path: "/algorithm/anagram",
    accent: "bg-emerald-500",
    text: "text-emerald-600",
    border: "hover:border-emerald-200",
  },
  {
    title: "Transformation & Encoding",
    items: ["Reverse Transformation", "Caesar Cipher", "Run Length Encoding"],
    path: "/algorithm/reverse",
    accent: "bg-amber-500",
    text: "text-amber-600",
    border: "hover:border-amber-200",
  },
];

export default function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-cyan">StringLab</h1>
        <p className="mt-1 text-sm text-slate-400">
          Select an algorithm from the sidebar to begin.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        <StatsCard
          label="Algorithms"
          value={12}
          icon={<BarChart2 size={16} />}
        />
        <StatsCard label="Categories" value={4} icon={<Grid size={16} />} />
        <StatsCard
          label="Visualizations"
          value={12}
          icon={<Layers size={16} />}
        />
        <StatsCard
          label="Complexity Reports"
          value={12}
          icon={<FileText size={16} />}
        />
      </div>

      {/* Category cards */}
      <div>
        <p className="mb-4 text-xs font-medium uppercase tracking-widest text-slate-400">
          Algorithm Categories
        </p>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {categories.map((cat) => (
            <Link
              key={cat.title}
              to={cat.path}
              className={`group flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:shadow-md ${cat.border}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`h-2 w-2 rounded-full ${cat.accent}`} />
                  <span className={`text-sm font-semibold ${cat.text}`}>
                    {cat.title}
                  </span>
                </div>
                <ArrowRight
                  size={14}
                  className="text-slate-300 transition-transform group-hover:translate-x-0.5 group-hover:text-slate-400"
                />
              </div>
              <ul className="space-y-1.5">
                {cat.items.map((item) => (
                  <li
                    key={item}
                    className="flex items-center gap-2 text-xs text-slate-400"
                  >
                    <span className="h-px w-3 bg-slate-200" />
                    {item}
                  </li>
                ))}
              </ul>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
