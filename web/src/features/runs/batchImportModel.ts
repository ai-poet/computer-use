import type { BatchRunInput, CreateBatchRunsPayload } from './types';

export type BatchImportResult = {
  rows: BatchRunInput[];
  errors: string[];
};

type ImportRow = Record<string, unknown>;

const URL_RE = /^https?:\/\/\S+$/i;

export function parseBatchImport(text: string, filename: string): BatchImportResult {
  const trimmed = text.trim();
  if (!trimmed) return { rows: [], errors: ['队列文件为空'] };

  if (filename.toLowerCase().endsWith('.json') || trimmed.startsWith('[') || trimmed.startsWith('{')) {
    return parseJsonImport(trimmed, filename);
  }
  return parseCsvImport(text, filename);
}

export function toCreateBatchPayload(
  rows: BatchRunInput[],
  maxWorkers: number,
  queueName: string
): CreateBatchRunsPayload {
  return {
    rows,
    max_workers: maxWorkers,
    queue_name: queueName || 'web-import',
    sandbox_image: 'linux',
    android: true
  };
}

function parseJsonImport(text: string, filename: string): BatchImportResult {
  try {
    const parsed = JSON.parse(text);
    const rawRows = Array.isArray(parsed)
      ? parsed
      : Array.isArray(parsed?.rows)
        ? parsed.rows
        : [];
    if (!rawRows.length) return { rows: [], errors: ['JSON 需要是数组，或包含 rows 数组'] };
    return normalizeRows(rawRows, fallbackCategory(filename));
  } catch (error) {
    return { rows: [], errors: [`JSON 解析失败: ${error instanceof Error ? error.message : '未知错误'}`] };
  }
}

function parseCsvImport(text: string, filename: string): BatchImportResult {
  const records = parseCsvRecords(text);
  if (records.length < 2) return { rows: [], errors: ['CSV 至少需要表头和一行数据'] };

  const headers = records[0].map((item) => item.trim());
  const rows = records.slice(1).filter((record) => record.some((cell) => cell.trim()));
  const objects = rows.map((record) => {
    const row: ImportRow = {};
    headers.forEach((header, index) => {
      row[header] = record[index] || '';
    });
    return row;
  });
  return normalizeRows(objects, fallbackCategory(filename));
}

function normalizeRows(rawRows: unknown[], fallback: string): BatchImportResult {
  const rows: BatchRunInput[] = [];
  const errors: string[] = [];
  const seen = new Set<string>();

  rawRows.forEach((raw, index) => {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
      errors.push(`第 ${index + 1} 行不是对象`);
      return;
    }
    const row = raw as ImportRow;
    const productName = stringField(row, 'product_name') || stringField(row, 'name');
    const url = stringField(row, 'url');
    const downloadUrl = stringField(row, 'download_url');
    const category = stringField(row, 'category') || stringField(row, 'queue_category') || fallback;

    if (!productName) {
      errors.push(`第 ${index + 1} 行缺少 product_name/name`);
      return;
    }
    if (productName.length > 80) {
      errors.push(`第 ${index + 1} 行产品名超过 80 字符`);
      return;
    }
    if (!URL_RE.test(url)) {
      errors.push(`第 ${index + 1} 行 URL 无效`);
      return;
    }
    if (downloadUrl && !URL_RE.test(downloadUrl)) {
      errors.push(`第 ${index + 1} 行下载链接无效`);
      return;
    }

    const key = `${productName}\n${url}`;
    if (seen.has(key)) return;
    seen.add(key);
    rows.push({
      product_name: productName,
      url,
      download_url: downloadUrl || null,
      category
    });
  });

  return { rows, errors };
}

function parseCsvRecords(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let cell = '';
  let quoted = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];
    if (quoted) {
      if (char === '"' && next === '"') {
        cell += '"';
        i += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        cell += char;
      }
      continue;
    }
    if (char === '"') {
      quoted = true;
    } else if (char === ',') {
      row.push(cell.trim());
      cell = '';
    } else if (char === '\n') {
      row.push(cell.trim());
      rows.push(row);
      row = [];
      cell = '';
    } else if (char !== '\r') {
      cell += char;
    }
  }
  row.push(cell.trim());
  rows.push(row);
  return rows;
}

function stringField(row: ImportRow, key: string): string {
  const value = row[key];
  return typeof value === 'string' ? value.trim() : '';
}

function fallbackCategory(filename: string): string {
  const stem = filename.replace(/\.(json|csv)$/i, '');
  if (stem.startsWith('queue.')) return stem.slice('queue.'.length) || 'web-import';
  if (stem.startsWith('queue-')) return stem.slice('queue-'.length) || 'web-import';
  return stem || 'web-import';
}
