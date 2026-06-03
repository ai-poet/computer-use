export type TerminalLineKind =
  | 'session'
  | 'thinking'
  | 'assistant_text'
  | 'tool_use'
  | 'todo'
  | 'tool_result'
  | 'result'
  | 'hook'
  | 'raw';

export type TerminalLine = {
  id: string;
  source: 'run.log' | 'events.jsonl' | string;
  kind: TerminalLineKind;
  text: string;
  tone?: 'normal' | 'muted' | 'accent' | 'success' | 'warning' | 'error';
  indent?: number;
  tool?: string;
  status?: string;
  raw?: string;
  meta?: Record<string, unknown>;
};

export type HookEvent = {
  ts?: string;
  event?: string;
  tool?: string;
  command?: string;
  ok?: boolean;
  message?: string;
  [key: string]: unknown;
};

export type RunStreamMessage = {
  source: 'run.log' | 'events.jsonl';
  chunk?: string;
  lines?: TerminalLine[];
  events?: HookEvent[];
};

export type RunLogState = {
  lines: TerminalLine[];
  rawLog: string;
  events: HookEvent[];
  isConnected: boolean;
};
