import { useParams } from "react-router-dom";
import { algorithms } from "../config/algorithm";
import AlgorithmPage from "../components/algorithm/AlgorithmPage";
import AlgorithmHeader from "../components/algorithm/AlgorithmHeader";
import InputPanel from "../components/algorithm/InputPanel";
import ActionButtons from "../components/algorithm/ActionButtons";
import VisualizationPanel from "../components/algorithm/VisualizationPanel";
import ResultCard from "../components/algorithm/ResultCard";
import ComplexityCard from "../components/algorithm/ComplexityCard";
import TracePanel from "../components/algorithm/TracePanel";

export default function AlgorithmRunner() {
  const { algorithmId } = useParams();
  const algorithm = algorithms.find((algo) => algo.id === algorithmId);

  if (!algorithm) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-slate-100 bg-white shadow-sm">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 rounded-lg border-2 border-dashed border-slate-200" />
          <p className="text-xs text-slate-300">Algorithm not found</p>
        </div>
      </div>
    );
  }

  return (
    <AlgorithmPage
      header={
        <AlgorithmHeader
          title={algorithm.title}
          description={algorithm.description}
        />
      }
      input={
        <InputPanel fields={algorithm.inputs} values={{}} onChange={() => {}} />
      }
      actions={<ActionButtons runLabel="Run Algorithm" onRun={() => {}} />}
      visualization={<VisualizationPanel />}
      result={<ResultCard title="Result" value="Waiting…" />}
      complexity={
        <ComplexityCard
          time={algorithm.complexity.time}
          space={algorithm.complexity.space}
        />
      }
      trace={<TracePanel steps={[]} />}
    />
  );
}
