import { useRef, useState } from 'react';
import { FileUp, Loader2, Upload } from 'lucide-react';
import { Button } from '../../shared/ui/Button';
import { parseBatchImport, toCreateBatchPayload } from './batchImportModel';
import type { BatchRunInput, CreateBatchRunsPayload } from './types';
import styles from './RunSidebar.module.less';

type Props = {
  onCreateBatch: (payload: CreateBatchRunsPayload) => Promise<unknown>;
};

export function RunBatchImport({ onCreateBatch }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [filename, setFilename] = useState('');
  const [rows, setRows] = useState<BatchRunInput[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [maxWorkers, setMaxWorkers] = useState(2);
  const [submitting, setSubmitting] = useState(false);

  async function readFile(file: File) {
    const parsed = parseBatchImport(await file.text(), file.name);
    setFilename(file.name);
    setRows(parsed.rows);
    setErrors(parsed.errors);
  }

  async function submit() {
    if (!rows.length || errors.length) return;
    setSubmitting(true);
    try {
      await onCreateBatch(toCreateBatchPayload(rows, maxWorkers, filename));
      setRows([]);
      setErrors([]);
      setFilename('');
      if (inputRef.current) inputRef.current.value = '';
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className={styles.batch}>
      <div className={styles.batchTop}>
        <span className={styles.batchTitle}>
          <Upload size={14} />
          批量导入
        </span>
        <label className={styles.fileButton}>
          <FileUp size={14} />
          选择队列
          <input
            ref={inputRef}
            type="file"
            accept=".json,.csv,application/json,text/csv"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) void readFile(file);
            }}
          />
        </label>
      </div>

      <div className={styles.batchMeta}>
        <span>{filename || '支持 JSON / CSV'}</span>
        <label className={styles.workerControl}>
          并行
          <input
            className={styles.workerInput}
            type="number"
            min={1}
            max={20}
            value={maxWorkers}
            onChange={(event) => setMaxWorkers(Number(event.target.value) || 1)}
          />
        </label>
      </div>

      {(rows.length > 0 || errors.length > 0) && (
        <div className={styles.batchStatus}>
          {rows.length > 0 && <span>{rows.length} 个任务待创建</span>}
          {errors.slice(0, 3).map((error) => (
            <span key={error} className={styles.errorText}>{error}</span>
          ))}
          {errors.length > 3 && <span className={styles.errorText}>还有 {errors.length - 3} 个错误</span>}
        </div>
      )}

      <Button
        variant="secondary"
        full
        disabled={!rows.length || errors.length > 0 || submitting}
        onClick={submit}
      >
        {submitting ? <Loader2 size={15} className="spin" /> : <Upload size={15} />}
        {submitting ? '导入中...' : '创建并行任务'}
      </Button>
    </section>
  );
}
