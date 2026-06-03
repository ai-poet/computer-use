import { useCallback, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Check, Copy } from 'lucide-react';
import { Button } from '../../shared/ui/Button';
import { screenshotUrl } from '../../shared/lib/api';
import { cn } from '../../shared/lib/cn';
import styles from './MarkdownRenderer.module.less';

function slugify(text: string) {
  return text.toLowerCase().replace(/[^\w\u4e00-\u9fa5\s-]/g, '').replace(/\s+/g, '-');
}

function CodeBlock({ code, language }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false);

  const copy = useCallback(async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }, [code]);

  return (
    <div className={styles.codeBlock}>
      {language && (
        <div className={styles.codeHeader}>
          <span>{language}</span>
          <Button iconOnly variant="ghost" onClick={copy} title="复制">
            {copied ? <Check size={14} /> : <Copy size={14} />}
          </Button>
        </div>
      )}
      <pre className={cn(styles.pre, language && styles.withHeader)}>
        <code>{code}</code>
      </pre>
    </div>
  );
}

export function MarkdownRenderer({ content, showToc, runId }: { content: string; showToc: boolean; runId: string }) {
  const headings = useMemo(() => {
    const result: Array<{ level: number; text: string; id: string }> = [];
    const regex = /^(#{1,6})\s+(.+)$/gm;
    let match: RegExpExecArray | null;
    while ((match = regex.exec(content)) !== null) {
      const text = match[2].trim();
      result.push({ level: match[1].length, text, id: slugify(text) });
    }
    return result;
  }, [content]);

  function scrollTo(id: string) {
    document.getElementById(`md-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  return (
    <div className={styles.wrap}>
      {showToc && headings.length > 0 && (
        <nav className={styles.toc}>
          <p className={styles.tocTitle}>目录</p>
          {headings.map((heading, index) => (
            <button
              key={`${heading.id}-${index}`}
              className={cn(styles.tocButton, heading.level >= 3 && styles.tocLevel3)}
              onClick={() => scrollTo(heading.id)}
            >
              {heading.text}
            </button>
          ))}
        </nav>
      )}
      <div className={cn(styles.body, 'markdown-body')}>
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => <h1 id={`md-${slugify(String(children))}`}>{children}</h1>,
            h2: ({ children }) => <h2 id={`md-${slugify(String(children))}`}>{children}</h2>,
            h3: ({ children }) => <h3 id={`md-${slugify(String(children))}`}>{children}</h3>,
            code: ({ children, className }) => {
              const language = className?.replace('language-', '') || '';
              if (!className) return <code className={styles.inlineCode}>{children}</code>;
              return <CodeBlock code={String(children).replace(/\n$/, '')} language={language} />;
            },
            pre: ({ children }) => <>{children}</>,
            a: ({ href, children }) => (
              <a href={href} target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            ),
            img: ({ src, alt }) => {
              const resolved = runId && src ? screenshotUrl(runId, String(src)) : String(src || '');
              return <img src={resolved} alt={alt || ''} className={styles.image} loading="lazy" />;
            }
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
