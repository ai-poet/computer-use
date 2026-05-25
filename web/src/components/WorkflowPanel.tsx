import { FileText } from 'lucide-react';
import type { WorkflowStep } from '../types';

export function WorkflowPanel({ steps }: { steps: WorkflowStep[] }) {
  return (
    <div className="panel steps">
      <h2>
        <FileText size={18} /> Workflow
      </h2>
      {steps.map((step) => (
        <div className="step" key={step.id}>
          <span className={`dot ${step.status}`} />
          <div>
            <strong>{step.title}</strong>
            <small>{step.summary || step.status}</small>
          </div>
        </div>
      ))}
    </div>
  );
}
