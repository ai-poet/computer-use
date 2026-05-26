import { useState, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check } from 'lucide-react';

interface MarkdownRendererProps {
  content: string;
  showToc?: boolean;
}

function CodeBlock({ code, language }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [code]);

  return (
    <div className="relative group my-4">
      {language && (
        <div className="flex items-center justify-between px-3 py-1.5 bg-bg-secondary border border-border-subtle border-b-0 rounded-t-md">
          <span className="text-xs text-text-tertiary font-mono">{language}</span>
          <button
            onClick={handleCopy}
            className="p-1 rounded hover:bg-bg-tertiary transition-colors"
            title="复制"
          >
            {copied ? (
              <Check size={14} className="text-success-500" />
            ) : (
              <Copy size={14} className="text-text-tertiary" />
            )}
          </button>
        </div>
      )}
      <pre
        className={`overflow-x-auto p-4 bg-bg-tertiary border border-border-subtle ${language ? 'rounded-b-md' : 'rounded-md'}`}
      >
        <code className="text-sm font-mono text-text-primary">{code}</code>
      </pre>
      {!language && (
        <button
          onClick={handleCopy}
          className="absolute top-2 right-2 p-1.5 rounded opacity-0 group-hover:opacity-100 hover:bg-bg-secondary transition-all"
          title="复制"
        >
          {copied ? (
            <Check size={14} className="text-success-500" />
          ) : (
            <Copy size={14} className="text-text-tertiary" />
          )}
        </button>
      )}
    </div>
  );
}

export function MarkdownRenderer({ content, showToc = false }: MarkdownRendererProps) {
  // Extract headings for TOC
  const headings: { level: number; text: string; id: string }[] = [];
  const headingRegex = /^(#{1,6})\s+(.+)$/gm;
  let match;
  while ((match = headingRegex.exec(content)) !== null) {
    const level = match[1].length;
    const text = match[2].trim();
    const id = text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
    headings.push({ level, text, id });
  }

  const scrollToHeading = (id: string) => {
    const el = document.getElementById(`md-heading-${id}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="flex gap-6">
      {/* Table of Contents */}
      {showToc && headings.length > 0 && (
        <nav className="hidden lg:block w-48 flex-shrink-0 sticky top-4 self-start">
          <p className="text-xs font-semibold text-text-tertiary uppercase tracking-wider mb-3">目录</p>
          <ul className="space-y-1">
            {headings.map((h, i) => (
              <li key={i}>
                <button
                  onClick={() => scrollToHeading(h.id)}
                  className={`text-left text-sm hover:text-primary-500 transition-colors ${
                    h.level === 1 ? 'font-medium text-text-primary' : 'text-text-secondary'
                  } ${h.level > 2 ? 'pl-3' : ''}`}
                >
                  {h.text}
                </button>
              </li>
            ))}
          </ul>
        </nav>
      )}

      {/* Content */}
      <div className="markdown-body flex-1 min-w-0">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children, ...props }) => {
              const id = String(children).toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
              return <h1 id={`md-heading-${id}`} {...props}>{children}</h1>;
            },
            h2: ({ children, ...props }) => {
              const id = String(children).toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
              return <h2 id={`md-heading-${id}`} {...props}>{children}</h2>;
            },
            h3: ({ children, ...props }) => {
              const id = String(children).toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
              return <h3 id={`md-heading-${id}`} {...props}>{children}</h3>;
            },
            code: ({ children, className }) => {
              const isInline = !className;
              if (isInline) {
                return (
                  <code className="bg-bg-tertiary px-1.5 py-0.5 rounded text-sm font-mono text-text-primary">
                    {children}
                  </code>
                );
              }
              const language = className?.replace('language-', '') || '';
              return <CodeBlock code={String(children)} language={language} />;
            },
            pre: ({ children }) => <>{children}</>,
            a: ({ href, children }) => (
              <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary-500 hover:underline">
                {children}
              </a>
            ),
            img: ({ src, alt }) => (
              <img src={src} alt={alt} className="max-w-full rounded-lg my-4 border border-border-subtle" />
            ),
            table: ({ children }) => (
              <div className="overflow-x-auto my-4">
                <table className="w-full border-collapse">{children}</table>
              </div>
            ),
            th: ({ children }) => (
              <th className="border border-border-subtle px-3 py-2 text-left font-semibold bg-bg-secondary text-text-primary">
                {children}
              </th>
            ),
            td: ({ children }) => (
              <td className="border border-border-subtle px-3 py-2 text-text-secondary">{children}</td>
            ),
            blockquote: ({ children }) => (
              <blockquote className="border-l-4 border-primary-500 pl-4 my-4 italic text-text-secondary">
                {children}
              </blockquote>
            ),
            ul: ({ children }) => <ul className="list-disc pl-6 mb-4">{children}</ul>,
            ol: ({ children }) => <ol className="list-decimal pl-6 mb-4">{children}</ol>,
            li: ({ children }) => <li className="mb-1 text-text-secondary">{children}</li>,
            p: ({ children }) => <p className="mb-4 leading-relaxed text-text-secondary">{children}</p>,
            hr: () => <hr className="my-6 border-border-subtle" />,
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
