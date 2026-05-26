import { useState } from 'react';
import { KeyRound, CheckCircle2, AlertTriangle, Loader2, Shield } from 'lucide-react';
import { submitCredential } from '../api';
import { EmptyState } from './EmptyState';
import type { RunDetail } from '../types';

interface CredentialPanelProps {
  detail: RunDetail | null;
  runId: string;
}

type SubmitState = 'idle' | 'submitting' | 'success' | 'error';

export function CredentialPanel({ detail, runId }: CredentialPanelProps) {
  const requests = detail?.workflow.credential_requests || [];
  const pending = requests.find((item) => item.status === 'pending');
  const [fields, setFields] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitState, setSubmitState] = useState<SubmitState>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  // Determine which fields to show based on pending.fields or default to username/password
  const fieldNames = pending?.fields?.length
    ? pending.fields
    : ['username', 'password'];

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

  function validate(): boolean {
    const e: Record<string, string> = {};
    fieldNames.forEach((name) => {
      if (!fields[name]?.trim()) {
        e[name] = `${fieldLabels[name] || name} 不能为空`;
      }
      if (name === 'email' && fields[name] && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(fields[name])) {
        e[name] = '请输入有效的邮箱地址';
      }
    });
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function submit() {
    if (!pending || !validate()) return;
    setSubmitState('submitting');
    setErrorMsg('');
    try {
      await submitCredential(
        runId,
        String(pending.id || ''),
        String(pending.service || 'product credential'),
        fields
      );
      setSubmitState('success');
      setFields({});
      setTimeout(() => setSubmitState('idle'), 2000);
    } catch (err) {
      setSubmitState('error');
      setErrorMsg(err instanceof Error ? err.message : '提交失败');
    }
  }

  return (
    <div className="panel">
      <h2 className="text-base font-semibold flex items-center gap-2 text-text-primary m-0 mb-4">
        <KeyRound size={18} className="text-primary-500" />
        Credential
      </h2>

      {!pending ? (
        <EmptyState
          variant="empty"
          title="当前没有 credential 请求"
          description="分析过程中需要登录信息时会自动显示"
        />
      ) : (
        <div className="credential">
          <div className="flex items-start gap-2 p-3 bg-primary-50 border border-primary-100 rounded-md mb-3">
            <Shield size={16} className="text-primary-500 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-text-secondary m-0">
              {String(pending.reason || '客户端需要登录信息。')}
            </p>
          </div>

          {fieldNames.map((name) => (
            <div key={name}>
              <label className="block text-xs font-medium text-text-secondary mb-1">
                {fieldLabels[name] || name}
              </label>
              <input
                type={fieldTypes[name] || 'text'}
                placeholder={`请输入${fieldLabels[name] || name}`}
                value={fields[name] || ''}
                onChange={(e) => {
                  setFields({ ...fields, [name]: e.target.value });
                  if (errors[name]) {
                    setErrors((prev) => {
                      const next = { ...prev };
                      delete next[name];
                      return next;
                    });
                  }
                }}
                className={`w-full min-h-[36px] border rounded-md px-3 text-sm bg-surface transition-colors ${
                  errors[name] ? 'border-error-500' : 'border-border-default'
                }`}
              />
              {errors[name] && (
                <span className="text-xs text-error-500 mt-1 block">{errors[name]}</span>
              )}
            </div>
          ))}

          {errorMsg && (
            <div className="flex items-center gap-2 p-2 bg-error-50 border border-error-100 rounded-md">
              <AlertTriangle size={14} className="text-error-500" />
              <span className="text-xs text-error-600">{errorMsg}</span>
            </div>
          )}

          <button
            onClick={submit}
            disabled={submitState === 'submitting'}
            className={`w-full py-2 rounded-md text-sm font-medium transition-all inline-flex items-center justify-center gap-2 ${
              submitState === 'success'
                ? 'bg-success-500 text-white'
                : submitState === 'error'
                  ? 'bg-error-500 text-white'
                  : 'bg-primary-500 text-white hover:bg-primary-600'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {submitState === 'submitting' && <Loader2 size={16} className="animate-spin" />}
            {submitState === 'success' && <CheckCircle2 size={16} />}
            {submitState === 'error' && <AlertTriangle size={16} />}
            {submitState === 'submitting'
              ? '提交中...'
              : submitState === 'success'
                ? '已提交'
                : submitState === 'error'
                  ? '提交失败，重试'
                  : '加密保存并提交'}
          </button>

          <p className="text-xs text-text-tertiary text-center">
            凭证将加密存储，仅用于本次分析
          </p>
        </div>
      )}
    </div>
  );
}
