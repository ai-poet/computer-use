import { useEffect, useState } from 'react';

export function useRunStream(runId: string) {
  const [log, setLog] = useState('');

  useEffect(() => {
    if (!runId) return;
    const ws = new WebSocket(`ws://${window.location.host}/api/runs/${runId}/stream`);
    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      setLog((prev) => `${prev}${payload.chunk}`.slice(-20000));
    };
    return () => {
      ws.close();
      setLog('');
    };
  }, [runId]);

  return log;
}
