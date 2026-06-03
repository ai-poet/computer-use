import { useState } from 'react';
import { CheckCircle2, ChevronDown, ChevronUp, Circle, FileText, Loader2, MinusCircle, XCircle } from 'lucide-react';
import { EmptyState } from '../../shared/ui/EmptyState';
import { cn } from '../../shared/lib/cn';
import type { WorkflowStep } from '../runs/types';
import styles from './WorkflowPanel.module.less';

function StepIcon({ status }: { status: string }) {
  if (status === 'completed') return <CheckCircle2 size={17} className={cn(styles.icon, styles.completed)} />;
  if (status === 'failed') return <XCircle size={17} className={cn(styles.icon, styles.failed)} />;
  if (status === 'in_progress') return <Loader2 size={17} className={cn(styles.icon, styles.running, 'spin')} />;
  if (status === 'skipped') return <MinusCircle size={17} className={styles.icon} />;
  return <Circle size={17} className={styles.icon} />;
}

export function WorkflowPanel({ steps }: { steps: WorkflowStep[] }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const completed = steps.filter((step) => step.status === 'completed' || step.status === 'skipped').length;
  const progress = steps.length ? Math.round((completed / steps.length) * 100) : 0;

  function toggle(id: string) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <section className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>
          <FileText size={17} />
          Workflow
        </h2>
        {steps.length > 0 && <span className={styles.count}>{completed}/{steps.length}</span>}
      </div>
      {steps.length > 0 && (
        <div className={styles.bar}>
          <div className={styles.barFill} style={{ width: `${progress}%` }} />
        </div>
      )}
      {steps.length === 0 ? (
        <EmptyState title="暂无工作流步骤" description="任务启动后会写入 workflow.json" />
      ) : (
        <div className={styles.steps}>
          {steps.map((step, index) => {
            const isExpanded = expanded.has(step.id);
            const canExpand = Boolean(step.summary);
            return (
              <button
                key={step.id}
                className={styles.step}
                onClick={() => canExpand && toggle(step.id)}
              >
                {index < steps.length - 1 && (
                  <span
                    className={cn(
                      styles.connector,
                      (step.status === 'completed' || step.status === 'skipped') && styles.connectorDone
                    )}
                  />
                )}
                <StepIcon status={step.status} />
                <span className={styles.stepMain}>
                  <span className={styles.stepTitleRow}>
                    <span className={styles.index}>{index + 1}</span>
                    <span className={styles.stepTitle}>{step.title}</span>
                    {canExpand && (isExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />)}
                  </span>
                  {!isExpanded && <p className={styles.summary}>{step.summary || step.status}</p>}
                  {isExpanded && step.summary && <p className={styles.expanded}>{step.summary}</p>}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}
