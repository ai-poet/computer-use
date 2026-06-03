import { useEffect, useState } from 'react';
import type { HookEvent, RunLogState, RunStreamMessage, TerminalLine } from './types';

const MAX_LINES = 1200;
const MAX_RAW_CHARS = 80_000;
const MAX_EVENTS = 300;

function eventToLine(event: HookEvent, index: number): TerminalLine {
  const name = event.event || 'hook';
  const tool = event.tool ? ` ${event.tool}` : '';
  const command = event.command ? ` · ${event.command}` : '';
  const ok = typeof event.ok === 'boolean' ? ` · ${event.ok ? 'ok' : 'error'}` : '';
  return {
    id: `events.jsonl:${event.ts || Date.now()}:${index}`,
    source: 'events.jsonl',
    kind: 'hook',
    text: `${name}${tool}${ok}${command}`,
    tone: event.ok === false ? 'error' : 'muted',
    raw: JSON.stringify(event),
    meta: event
  };
}

export function useRunStream(runId: string): RunLogState {
  const [state, setState] = useState<RunLogState>({
    lines: [],
    rawLog: '',
    events: [],
    isConnected: false
  });

  useEffect(() => {
    setState({ lines: [], rawLog: '', events: [], isConnected: false });
    if (!runId) return;

    const encoded = encodeURIComponent(runId);
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${protocol}://${window.location.host}/api/runs/${encoded}/stream`);

    ws.onopen = () => setState((prev) => ({ ...prev, isConnected: true }));
    ws.onclose = () => setState((prev) => ({ ...prev, isConnected: false }));
    ws.onerror = () => setState((prev) => ({ ...prev, isConnected: false }));
    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data) as RunStreamMessage;
      setState((prev) => {
        const nextEvents = payload.events
          ? [...prev.events, ...payload.events].slice(-MAX_EVENTS)
          : prev.events;
        const hookLines = payload.events?.map(eventToLine) || [];
        const nextLines = [...prev.lines, ...(payload.lines || []), ...hookLines].slice(-MAX_LINES);
        const nextRaw = `${prev.rawLog}${payload.chunk || ''}`.slice(-MAX_RAW_CHARS);
        return {
          lines: nextLines,
          rawLog: nextRaw,
          events: nextEvents,
          isConnected: prev.isConnected
        };
      });
    };

    return () => {
      ws.close();
    };
  }, [runId]);

  return state;
}
