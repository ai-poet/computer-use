import { useState } from 'react';
import {
  FileText,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  XCircle,
  Circle,
  Loader2,
  MinusCircle
} from 'lucide-react';
import type { WorkflowStep } from '../types';

interface WorkflowPanelProps {
  steps: WorkflowStep[];
}

function StepIcon({ status }: { status: string }) {
  switch (status) {
    case 'completed':
      return <CheckCircle2 size={18} className="text-success-500" />;
    case 'failed':
      return <XCircle size={18} className="text-error-500" />;
    case 'in_progress':
      return <Loader2 size={18} className="text-primary-500 animate-spin" />;
    case 'skipped':
      return <MinusCircle size={18} className="text-text-tertiary" />;
    default:
      return <Circle size={18} className="text-border-default" />;
  }
}

function StepConnector({
  index,
  total,
  status
}: {
  index: number;
  total: number;
  status: string;
}) {
  if (index >= total - 1) return null;

  const isCompleted = status === 'completed' || status === 'skipped';
  const isInProgress = status === 'in_progress';

  return (
    <div className="absolute left-[11px] top-7 bottom-[-12px] w-0.5">
      <div
        className={`w-full h-full rounded-full transition-colors duration-500 ${
          isCompleted
            ? 'bg-success-500'
            : isInProgress
              ? 'bg-primary-500'
              : 'bg-border-subtle'
        }`}
      />
    </div>
  );
}

export function WorkflowPanel({ steps }: WorkflowPanelProps) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const completedCount = steps.filter((s) => s.status === 'completed').length;
  const progress = steps.length > 0 ? Math.round((completedCount / steps.length) * 100) : 0;

  const toggleExpand = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return (
    <div className="panel">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold flex items-center gap-2 text-text-primary m-0">
          <FileText size={18} className="text-primary-500" />
          Workflow
        </h2>
        {steps.length > 0 && (
          <span className="text-xs text-text-tertiary">
            {completedCount}/{steps.length} 步骤已完成
          </span>
        )}
      </div>

      {/* Progress bar */}
      {steps.length > 0 && (
        <div className="w-full h-1.5 bg-bg-tertiary rounded-full mb-4 overflow-hidden">
          <div
            className="h-full bg-success-500 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* Steps */}
      <div className="space-y-0">
        {steps.map((step, index) => {
          const isExpanded = expanded.has(step.id);
          return (
            <div key={step.id} className="relative">
              <StepConnector index={index} total={steps.length} status={step.status} />
              <button
                onClick={() => toggleExpand(step.id)}
                className="w-full text-left group"
              >
                <div className="flex items-start gap-3 py-2.5 hover:bg-surface-hover rounded-md px-1 -mx-1 transition-colors">
                  <div className="flex-shrink-0 mt-0.5 relative">
                    <StepIcon status={step.status} />
                    {step.status === 'in_progress' && (
                      <span className="absolute inset-0 rounded-full animate-ping opacity-20 bg-primary-500" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-text-tertiary w-5">{index + 1}</span>
                      <span className="text-sm font-medium text-text-primary">{step.title}</span>
                      {step.summary && (
                        <span className="ml-auto flex-shrink-0">
                          {isExpanded ? (
                            <ChevronUp size={14} className="text-text-tertiary" />
                          ) : (
                            <ChevronDown size={14} className="text-text-tertiary" />
                          )}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-text-tertiary mt-0.5 ml-5 truncate">
                      {step.summary || step.status}
                    </p>
                  </div>
                </div>
              </button>

              {/* Expanded details */}
              {isExpanded && step.summary && (
                <div className="ml-11 pl-5 pb-3 animate-fade-in-up">
                  <p className="text-sm text-text-secondary leading-relaxed">{step.summary}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {steps.length === 0 && (
        <p className="text-sm text-text-tertiary text-center py-8">暂无工作流步骤</p>
      )}
    </div>
  );
}
