import { useEffect, useState } from 'react';
import { Download, FileText, Maximize2, Minimize2, Printer } from 'lucide-react';
import { listScreenshots } from '../../shared/lib/api';
import { Button } from '../../shared/ui/Button';
import { EmptyState } from '../../shared/ui/EmptyState';
import { MarkdownRenderer } from './MarkdownRenderer';
import { ScreenshotGallery } from './ScreenshotGallery';
import type { Screenshot } from './types';
import styles from './ReportPanel.module.less';

export function ReportPanel({ report, runId }: { report: string; runId: string }) {
  const [screenshots, setScreenshots] = useState<Screenshot[]>([]);
  const [showToc, setShowToc] = useState(false);

  useEffect(() => {
    if (!runId) {
      setScreenshots([]);
      return;
    }
    listScreenshots(runId).then(setScreenshots);
  }, [runId, report]);

  function download() {
    const blob = new Blob([report], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `report-${runId || new Date().toISOString().slice(0, 10)}.md`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  const isGenerating = Boolean(runId && !report);

  return (
    <section className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>
          <FileText size={17} />
          最终报告
        </h2>
        <div className={styles.actions}>
          <Button iconOnly variant={showToc ? 'secondary' : 'ghost'} onClick={() => setShowToc((value) => !value)} disabled={!report}>
            {showToc ? <Minimize2 size={15} /> : <Maximize2 size={15} />}
          </Button>
          <Button iconOnly variant="ghost" onClick={download} disabled={!report}>
            <Download size={15} />
          </Button>
          <Button iconOnly variant="ghost" onClick={() => window.print()} disabled={!report}>
            <Printer size={15} />
          </Button>
        </div>
      </div>
      <div className={styles.content}>
        {isGenerating ? (
          <div className={styles.skeleton}>
            <span />
            <span />
            <span />
            <span />
          </div>
        ) : report ? (
          <>
            <MarkdownRenderer content={report} showToc={showToc} runId={runId} />
            {screenshots.length > 0 && (
              <div className={styles.screenshots}>
                <h3 className={styles.subhead}>截图索引</h3>
                <ScreenshotGallery screenshots={screenshots} />
              </div>
            )}
          </>
        ) : (
          <EmptyState title="最终报告尚未生成" description="分析完成后会自动显示在这里" />
        )}
      </div>
    </section>
  );
}
