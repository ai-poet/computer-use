import { Terminal } from 'lucide-react';

export function LogPanel({ log }: { log: string }) {
  return (
    <div className="panel">
      <h2>
        <Terminal size={18} /> 实时日志
      </h2>
      <pre className="log">{log || '等待事件...'}</pre>
    </div>
  );
}
