export type EmailProvider = 'auto' | 'mailosaur' | 'imap';

export type SettingsStatus = {
  provider: EmailProvider | string;
  mailosaur_server_id: string;
  mailosaur_server_domain: string;
  imap_host: string;
  imap_port: string;
  imap_username: string;
  imap_ssl: string;
  imap_folder: string;
  email_address: string;
  alias_mode: string;
  mailosaur_api_key_configured: boolean;
  imap_password_configured: boolean;
};

// 提交时:非敏感字段直接传;敏感字段仅在用户重新填写时才出现(空串=清除)。
export type SettingsUpdate = Partial<{
  provider: string;
  mailosaur_server_id: string;
  mailosaur_server_domain: string;
  imap_host: string;
  imap_port: string;
  imap_username: string;
  imap_ssl: string;
  imap_folder: string;
  email_address: string;
  alias_mode: string;
  mailosaur_api_key: string;
  imap_password: string;
}>;

export type SavedCredential = {
  credential_id: string;
  label: string;
  source_run?: string | null;
  product?: string | null;
  field_names?: string[];
  created_at?: number;
};
