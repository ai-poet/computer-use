import { useState } from 'react';
import type { FormEvent } from 'react';
import { ChevronDown, ChevronUp, Loader2, Play } from 'lucide-react';
import { Button } from '../../shared/ui/Button';
import { cn } from '../../shared/lib/cn';
import type { CreateRunPayload } from './types';
import {
  EMPTY_RUN_DRAFT,
  hasValidationErrors,
  toCreateRunPayload,
  validateRunDraft
} from './runModel';
import type { RunDraft, RunValidationErrors } from './runModel';
import styles from './RunSidebar.module.less';

type Props = {
  onCreate: (payload: CreateRunPayload) => Promise<unknown>;
};

export function RunCreateForm({ onCreate }: Props) {
  const [form, setForm] = useState<RunDraft>({ ...EMPTY_RUN_DRAFT });
  const [errors, setErrors] = useState<RunValidationErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  function updateField(field: keyof RunDraft, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function validate() {
    const nextErrors = validateRunDraft(form);
    setErrors(nextErrors);
    return !hasValidationErrors(nextErrors);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!validate()) return;

    setSubmitting(true);
    try {
      await onCreate(toCreateRunPayload(form));
      setForm({ ...EMPTY_RUN_DRAFT });
      setErrors({});
      setShowAdvanced(false);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className={styles.form} onSubmit={submit}>
      <label className={styles.field}>
        <span className={styles.label}>产品名</span>
        <input
          className={styles.input}
          value={form.product_name}
          onChange={(event) => updateField('product_name', event.target.value)}
          onBlur={validate}
          placeholder="输入产品名称"
        />
        {errors.product_name ? (
          <span className={styles.errorText}>{errors.product_name}</span>
        ) : (
          <span className={styles.charCount}>{form.product_name.length}/80</span>
        )}
      </label>

      <label className={styles.field}>
        <span className={styles.label}>官网 URL</span>
        <input
          className={styles.input}
          value={form.url}
          onChange={(event) => updateField('url', event.target.value)}
          onBlur={validate}
          placeholder="https://example.com"
        />
        {errors.url && <span className={styles.errorText}>{errors.url}</span>}
      </label>

      <button
        type="button"
        className={styles.advancedButton}
        onClick={() => setShowAdvanced((value) => !value)}
      >
        {showAdvanced ? <ChevronUp size={13} /> : <ChevronDown size={13} />} 高级选项
      </button>

      {showAdvanced && (
        <>
          <label className={cn(styles.field, styles.advanced)}>
            <span className={styles.label}>下载链接（可选）</span>
            <input
              className={styles.input}
              value={form.download_url}
              onChange={(event) => updateField('download_url', event.target.value)}
              onBlur={validate}
              placeholder="直接指向安装包的 URL"
            />
            {errors.download_url && <span className={styles.errorText}>{errors.download_url}</span>}
          </label>

          <label className={cn(styles.field, styles.advanced)}>
            <span className={styles.label}>邮箱 Provider 覆盖（可选）</span>
            <select
              className={styles.input}
              value={form.email_provider}
              onChange={(event) => updateField('email_provider', event.target.value)}
            >
              <option value="">继承全局配置</option>
              <option value="auto">auto</option>
              <option value="mailosaur">mailosaur</option>
              <option value="imap">imap</option>
            </select>
          </label>

          <label className={cn(styles.field, styles.advanced)}>
            <span className={styles.label}>固定邮箱覆盖（可选）</span>
            <input
              className={styles.input}
              value={form.email_address}
              onChange={(event) => updateField('email_address', event.target.value)}
              placeholder="留空继承全局；仅 IMAP 生效"
            />
          </label>
        </>
      )}

      <Button variant="primary" full disabled={submitting}>
        {submitting ? <Loader2 size={15} className="spin" /> : <Play size={15} />}
        {submitting ? '提交中...' : '新建分析'}
      </Button>
    </form>
  );
}
