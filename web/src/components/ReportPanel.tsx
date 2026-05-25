import { FileText } from 'lucide-react';

export function ReportPanel({ report }: { report: string }) {
  return (
    <div className="panel report">
      <h2>
        <FileText size={18} /> 最终报告
      </h2>
      <pre>{report || '最终报告尚未生成。'}</pre>
    </div>
  );
}
