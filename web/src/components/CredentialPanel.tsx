import { Image } from 'lucide-react';
import { useState } from 'react';
import { submitCredential } from '../api';
import type { RunDetail } from '../types';

export function CredentialPanel({ detail, runId }: { detail: RunDetail | null; runId: string }) {
  const requests = detail?.workflow.credential_requests || [];
  const pending = requests.find((item) => item.status === 'pending');
  const [fields, setFields] = useState<Record<string, string>>({});

  async function submit() {
    if (!pending) return;
    await submitCredential(
      runId,
      String(pending.id || ''),
      String(pending.service || 'product credential'),
      fields
    );
    setFields({});
  }

  return (
    <div className="panel">
      <h2>
        <Image size={18} /> Credential
      </h2>
      {!pending ? (
        <p className="muted">当前没有 credential 请求。</p>
      ) : (
        <div className="credential">
          <p>{String(pending.reason || '客户端需要登录信息。')}</p>
          <input
            placeholder="账号"
            value={fields.username || ''}
            onChange={(e) => setFields({ ...fields, username: e.target.value })}
          />
          <input
            placeholder="密码"
            type="password"
            value={fields.password || ''}
            onChange={(e) => setFields({ ...fields, password: e.target.value })}
          />
          <button onClick={submit}>加密保存并提交</button>
        </div>
      )}
    </div>
  );
}
