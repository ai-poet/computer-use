import { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, Loader2, Lock, X } from 'lucide-react';
import { getSettings, updateSettings } from '../../shared/lib/api';
import { Button } from '../../shared/ui/Button';
import type { SettingsStatus, SettingsUpdate } from './types';
import styles from './SettingsModal.module.less';

type Props = {
  open: boolean;
  onClose: () => void;
};

type Form = {
  provider: string;
  mailosaur_server_id: string;
  mailosaur_server_domain: string;
  mailosaur_api_key: string;
  imap_host: string;
  imap_port: string;
  imap_username: string;
  imap_password: string;
  imap_folder: string;
  imap_ssl: string;
  email_address: string;
  alias_mode: string;
};

const EMPTY_FORM: Form = {
  provider: 'auto',
  mailosaur_server_id: '',
  mailosaur_server_domain: '',
  mailosaur_api_key: '',
  imap_host: '',
  imap_port: '',
  imap_username: '',
  imap_password: '',
  imap_folder: '',
  imap_ssl: 'true',
  email_address: '',
  alias_mode: 'plus'
};

function statusToForm(status: SettingsStatus): Form {
  return {
    provider: status.provider || 'auto',
    mailosaur_server_id: status.mailosaur_server_id || '',
    mailosaur_server_domain: status.mailosaur_server_domain || '',
    mailosaur_api_key: '',
    imap_host: status.imap_host || '',
    imap_port: status.imap_port || '',
    imap_username: status.imap_username || '',
    imap_password: '',
    imap_folder: status.imap_folder || '',
    imap_ssl: status.imap_ssl || 'true',
    email_address: status.email_address || '',
    alias_mode: status.alias_mode || 'plus'
  };
}

export function SettingsModal({ open, onClose }: Props) {
  const [status, setStatus] = useState<SettingsStatus | null>(null);
  const [form, setForm] = useState<Form>({ ...EMPTY_FORM });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    setError('');
    setSaved(false);
    getSettings()
      .then((data) => {
        setStatus(data);
        setForm(statusToForm(data));
      })
      .catch((err) => setError(err instanceof Error ? err.message : '加载配置失败'))
      .finally(() => setLoading(false));
  }, [open]);

  const provider = form.provider;
  const showMailosaur = provider === 'auto' || provider === 'mailosaur';
  const showImap = provider === 'auto' || provider === 'imap';

  function set<K extends keyof Form>(key: K, value: Form[K]) {
    setForm((current) => ({ ...current, [key]: value }));
    setSaved(false);
  }

  // 只提交用户改过的字段;敏感字段留空=保持不变。
  const dirty = useMemo<SettingsUpdate>(() => {
    if (!status) return {};
    const base = statusToForm(status);
    const out: SettingsUpdate = {};
    (Object.keys(form) as Array<keyof Form>).forEach((key) => {
      const isSecret = key === 'mailosaur_api_key' || key === 'imap_password';
      if (isSecret) {
        if (form[key].trim() !== '') out[key] = form[key].trim();
      } else if (form[key] !== base[key]) {
        out[key] = form[key];
      }
    });
    return out;
  }, [form, status]);

  async function save() {
    setSaving(true);
    setError('');
    try {
      const next = await updateSettings(dirty);
      setStatus(next);
      setForm(statusToForm(next));
      setSaved(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  }

  if (!open) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <header className={styles.header}>
          <h2 className={styles.title}>全局邮箱注册配置</h2>
          <button className={styles.close} onClick={onClose} aria-label="关闭">
            <X size={18} />
          </button>
        </header>

        {loading ? (
          <div className={styles.loading}>
            <Loader2 size={18} className="spin" /> 加载中…
          </div>
        ) : (
          <div className={styles.body}>
            <label className={styles.field}>
              <span className={styles.label}>Provider 策略</span>
              <select
                className={styles.input}
                value={form.provider}
                onChange={(e) => set('provider', e.target.value)}
              >
                <option value="auto">auto（优先 Mailosaur，回退 IMAP）</option>
                <option value="mailosaur">仅 Mailosaur</option>
                <option value="imap">仅 IMAP 固定邮箱</option>
              </select>
            </label>

            {showMailosaur && (
              <fieldset className={styles.group}>
                <legend className={styles.legend}>Mailosaur</legend>
                <SecretField
                  label="API Key"
                  value={form.mailosaur_api_key}
                  configured={status?.mailosaur_api_key_configured}
                  onChange={(v) => set('mailosaur_api_key', v)}
                />
                <Text label="Server ID" value={form.mailosaur_server_id} onChange={(v) => set('mailosaur_server_id', v)} />
                <Text
                  label="Server Domain（可选）"
                  value={form.mailosaur_server_domain}
                  placeholder="留空则用 <server_id>.mailosaur.net"
                  onChange={(v) => set('mailosaur_server_domain', v)}
                />
              </fieldset>
            )}

            {showImap && (
              <fieldset className={styles.group}>
                <legend className={styles.legend}>IMAP 固定邮箱</legend>
                <Text label="Host" value={form.imap_host} onChange={(v) => set('imap_host', v)} />
                <Text label="Port（默认 993）" value={form.imap_port} placeholder="993" onChange={(v) => set('imap_port', v)} />
                <Text label="用户名" value={form.imap_username} onChange={(v) => set('imap_username', v)} />
                <SecretField
                  label="密码 / App Password"
                  value={form.imap_password}
                  configured={status?.imap_password_configured}
                  onChange={(v) => set('imap_password', v)}
                />
                <Text label="邮箱地址" value={form.email_address} onChange={(v) => set('email_address', v)} />
                <Text label="Folder（默认 INBOX）" value={form.imap_folder} placeholder="INBOX" onChange={(v) => set('imap_folder', v)} />
                <label className={styles.field}>
                  <span className={styles.label}>别名模式</span>
                  <select className={styles.input} value={form.alias_mode} onChange={(e) => set('alias_mode', e.target.value)}>
                    <option value="plus">plus（name+pa-xxx，便于区分）</option>
                    <option value="fixed">fixed（直接用固定邮箱）</option>
                  </select>
                </label>
                <label className={styles.field}>
                  <span className={styles.label}>SSL</span>
                  <select className={styles.input} value={form.imap_ssl} onChange={(e) => set('imap_ssl', e.target.value)}>
                    <option value="true">启用</option>
                    <option value="false">关闭</option>
                  </select>
                </label>
              </fieldset>
            )}

            {error && <div className={styles.error}>{error}</div>}

            <div className={styles.actions}>
              <Button variant="ghost" onClick={onClose}>取消</Button>
              <Button variant="primary" onClick={save} disabled={saving}>
                {saving ? <Loader2 size={15} className="spin" /> : saved ? <CheckCircle2 size={15} /> : null}
                {saving ? '保存中…' : saved ? '已保存' : '保存配置'}
              </Button>
            </div>
            <p className={styles.hint}>密钥写入系统钥匙串，不会落盘明文，也不会进任何报告或日志。</p>
          </div>
        )}
      </div>
    </div>
  );
}

function Text({
  label,
  value,
  placeholder,
  onChange
}: {
  label: string;
  value: string;
  placeholder?: string;
  onChange: (v: string) => void;
}) {
  return (
    <label className={styles.field}>
      <span className={styles.label}>{label}</span>
      <input className={styles.input} value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} />
    </label>
  );
}

function SecretField({
  label,
  value,
  configured,
  onChange
}: {
  label: string;
  value: string;
  configured?: boolean;
  onChange: (v: string) => void;
}) {
  return (
    <label className={styles.field}>
      <span className={styles.label}>
        {label}
        {configured && (
          <span className={styles.configured}>
            <Lock size={11} /> 已配置
          </span>
        )}
      </span>
      <input
        className={styles.input}
        type="password"
        value={value}
        placeholder={configured ? '已保存，留空保持不变' : ''}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
