import { useState, useEffect } from 'react';
import { FileText, Download, Printer, Maximize2, Minimize2 } from 'lucide-react';
import { MarkdownRenderer } from './MarkdownRenderer';
import { ScreenshotGallery } from './ScreenshotGallery';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';
import { listScreenshots } from '../api';
import type { Screenshot } from '../types';

interface ReportPanelProps {
  report: string;
  runId?: string;
}

export function ReportPanel({ report, runId }: ReportPanelProps) {
  const [screenshots, setScreenshots] = useState<Screenshot[]>([]);
  const [showToc, setShowToc] = useState(false);

  useEffect(() => {
    if (!runId) {
      setScreenshots([]);
      return;
    }
    listScreenshots(runId).then(setScreenshots);
  }, [runId]);

  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  const isGenerating = !report && runId;

  return (
    <div className="panel report">
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold flex items-center gap-2 text-text-primary m-0">
          <FileText size={18} className="text-primary-500" />
          最终报告
        </h2>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setShowToc(!showToc)}
            className={`p-1.5 rounded transition-colors ${showToc ? 'bg-primary-50 text-primary-600' : 'text-text-tertiary hover:text-text-secondary'}`}
            title="目录"
          >
            {showToc ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
          <button
            onClick={handleDownload}
            disabled={!report}
            className="p-1.5 rounded text-text-tertiary hover:text-text-secondary transition-colors disabled:opacity-40"
            title="导出 Markdown"
          >
            <Download size={14} />
          </button>
          <button
            onClick={handlePrint}
            disabled={!report}
            className="p-1.5 rounded text-text-tertiary hover:text-text-secondary transition-colors disabled:opacity-40"
            title="打印"
          >
            <Printer size={14} />
          </button>
        </div>
      </div>

      {/* Content */}
      {isGenerating ? (
        <LoadingState variant="skeleton-text" count={5} />
      ) : report ? (
        <div>
          <MarkdownRenderer content={report} showToc={showToc} />

          {/* Screenshot gallery */}
          {screenshots.length > 0 && (
            <div className="mt-8 pt-6 border-t border-border-subtle">
              <h3 className="text-lg font-semibold text-text-primary mb-4">截图索引</h3>
              <ScreenshotGallery screenshots={screenshots} />
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          variant="empty"
          title="最终报告尚未生成"
          description="请等待分析完成，报告生成后会自动显示在这里"
        />
      )}
    </div>
  );
}
