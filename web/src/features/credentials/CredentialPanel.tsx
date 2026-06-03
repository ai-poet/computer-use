import { useState } from 'react';
import { AlertTriangle, CheckCircle2, KeyRound, Loader2, Shield } from 'lucide-react';
import { submitCredential } from '../../shared/lib/api';
import { Button } from '../../shared/ui/Button';
import { EmptyState } from '../../shared/ui/EmptyState';
import type { RunDetail } from '../runs/types';
import styles from './CredentialPanel.module.less';

type SubmitState = 'idle' | 'submitting' | 'success' | 'error';

const fieldLabels: Record<string, string> = {
  username: '账号',
  password: '密码',
  api_key: 'API Key',
  token: 'Token',
  email: '邮箱',
  phone: '手机号'
};

const fieldTypes: Record<string, string> = {
  password: 'password',
  api_key: 'password',
  token: 'password',
  email: 'email',
  phone: 'tel'
};

export function CredentialPanel({ detail, runId }: { detail: RunDetail | null; runId: string }) {
  const requests = detail?.workflow.credential_requests || [];
  const pending = requests.find((item) => item.status === 'pending');
  const [fields, setFields] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitState, setSubmitState] = useState<SubmitState>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const fieldNames = pending?.fields?.length ? pending.fields : ['username', 'password'];

  function validate() {
    const next: Record<string, string> = {};
    fieldNames.forEach((name) => {
      if (!fields[name]?.trim()) next[name] = `${fieldLabels[name] || name} 不能为空`;
      if (name === 'email' && fields[name] && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(fields[name])) {
        next[name] = '请输入有效邮箱';
      }
    });
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function submit() {
    if (!pending || !validate()) return;
    setSubmitState('submitting');
    setErrorMsg('');
    try {
      await submitCredential(runId, String(pending.id || ''), String(pending.service || 'product credential'), fields);
      setSubmitState('success');
      setFields({});
      window.setTimeout(() => setSubmitState('idle'), 2000);
    } catch (err) {
      setSubmitState('error');
      setErrorMsg(err instanceof Error ? err.message : '提交失败');
    }
  }

  return (
    <section className={styles.panel}>
      <h2 className={styles.title}>
        <KeyRound size={17} />
        Credential
      </h2>
      {!pending ? (
        <EmptyState title="当前没有凭证请求" description="分析需要登录信息时会在这里出现" />
      ) : (
        <div className={styles.form}>
          <div className={styles.notice}>
            <Shield size={16} />
            {String(pending.reason || '客户端需要登录信息。')}
          </div>
          {fieldNames.map((name) => (
            <label key={name} className={styles.field}>
              <span className={styles.label}>{fieldLabels[name] || name}</span>
              <input
                className={styles.input}
                type={fieldTypes[name] || 'text'}
                value={fields[name] || ''}
                onChange={(event) => {
                  setFields({ ...fields, [name]: event.target.value });
                  if (errors[name]) setErrors(({ [name]: _removed, ...rest }) => rest);
                }}
              />
              {errors[name] && <span className={styles.errorText}>{errors[name]}</span>}
            </label>
          ))}
          {errorMsg && <div className={styles.errorBox}>{errorMsg}</div>}
          <Button variant={submitState === 'error' ? 'danger' : 'primary'} full onClick={submit} disabled={submitState === 'submitting'}>
            {submitState === 'submitting' && <Loader2 size={15} className="spin" />}
            {submitState === 'success' && <CheckCircle2 size={15} />}
            {submitState === 'error' && <AlertTriangle size={15} />}
            {submitState === 'submitting' ? '提交中...' : submitState === 'success' ? '已提交' : submitState === 'error' ? '提交失败，重试' : '加密保存并提交'}
          </Button>
          <p className={styles.hint}>凭证将加密存储，仅用于本次分析</p>
        </div>
      )}
    </section>
  );
}
