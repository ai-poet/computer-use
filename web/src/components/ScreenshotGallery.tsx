import { useState, useEffect, useCallback } from 'react';
import { X, ChevronLeft, ChevronRight, Grid3X3, List, Download, ImageIcon } from 'lucide-react';
import type { Screenshot } from '../types';

interface ScreenshotGalleryProps {
  screenshots: Screenshot[];
  viewMode?: 'grid' | 'list';
}

export function ScreenshotGallery({ screenshots, viewMode: initialView = 'grid' }: ScreenshotGalleryProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(initialView);
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);

  const openLightbox = (index: number) => setLightboxIndex(index);
  const closeLightbox = () => setLightboxIndex(null);

  const goPrev = useCallback(() => {
    if (lightboxIndex === null) return;
    setLightboxIndex(lightboxIndex === 0 ? screenshots.length - 1 : lightboxIndex - 1);
  }, [lightboxIndex, screenshots.length]);

  const goNext = useCallback(() => {
    if (lightboxIndex === null) return;
    setLightboxIndex(lightboxIndex === screenshots.length - 1 ? 0 : lightboxIndex + 1);
  }, [lightboxIndex, screenshots.length]);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (lightboxIndex === null) return;
      if (e.key === 'Escape') closeLightbox();
      if (e.key === 'ArrowLeft') goPrev();
      if (e.key === 'ArrowRight') goNext();
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [lightboxIndex, goPrev, goNext]);

  if (!screenshots.length) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <ImageIcon size={32} className="text-text-tertiary mb-2" />
        <p className="text-sm text-text-tertiary">暂无截图</p>
      </div>
    );
  }

  const sourceLabel = (source: string) => {
    const map: Record<string, string> = { web: '网页', app: '应用', android: '安卓' };
    return map[source] || source;
  };

  const sourceColor = (source: string) => {
    const map: Record<string, string> = {
      web: 'bg-primary-100 text-primary-700',
      app: 'bg-success-100 text-success-700',
      android: 'bg-warning-100 text-warning-700'
    };
    return map[source] || 'bg-bg-tertiary text-text-secondary';
  };

  return (
    <div>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-text-secondary">
          截图索引 ({screenshots.length}张)
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-1.5 rounded transition-colors ${viewMode === 'grid' ? 'bg-bg-tertiary text-text-primary' : 'text-text-tertiary hover:text-text-secondary'}`}
            title="网格视图"
          >
            <Grid3X3 size={16} />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-1.5 rounded transition-colors ${viewMode === 'list' ? 'bg-bg-tertiary text-text-primary' : 'text-text-tertiary hover:text-text-secondary'}`}
            title="列表视图"
          >
            <List size={16} />
          </button>
        </div>
      </div>

      {/* Grid View */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {screenshots.map((shot, index) => (
            <button
              key={shot.id}
              onClick={() => openLightbox(index)}
              className="group relative aspect-video rounded-lg overflow-hidden border border-border-subtle hover:border-border-default transition-all hover:shadow-md"
            >
              <img
                src={shot.url}
                alt={shot.label}
                className="w-full h-full object-cover transition-transform group-hover:scale-105"
                loading="lazy"
              />
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2">
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${sourceColor(shot.source)}`}>
                  {sourceLabel(shot.source)}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* List View */}
      {viewMode === 'list' && (
        <div className="space-y-2">
          {screenshots.map((shot, index) => (
            <button
              key={shot.id}
              onClick={() => openLightbox(index)}
              className="flex items-center gap-3 w-full p-2 rounded-lg border border-border-subtle hover:border-border-default hover:bg-surface-hover transition-all text-left"
            >
              <img
                src={shot.url}
                alt={shot.label}
                className="w-16 h-10 object-cover rounded"
                loading="lazy"
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-text-primary truncate">{shot.filename}</p>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${sourceColor(shot.source)}`}>
                  {sourceLabel(shot.source)}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Lightbox */}
      {lightboxIndex !== null && (
        <div className="lightbox-overlay" onClick={closeLightbox}>
          <button
            onClick={(e) => { e.stopPropagation(); closeLightbox(); }}
            className="absolute top-4 right-4 p-2 rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors"
          >
            <X size={20} />
          </button>

          {screenshots.length > 1 && (
            <>
              <button
                onClick={(e) => { e.stopPropagation(); goPrev(); }}
                className="absolute left-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors"
              >
                <ChevronLeft size={24} />
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); goNext(); }}
                className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors"
              >
                <ChevronRight size={24} />
              </button>
            </>
          )}

          <div className="flex flex-col items-center" onClick={(e) => e.stopPropagation()}>
            <img
              src={screenshots[lightboxIndex].url}
              alt={screenshots[lightboxIndex].label}
              className="lightbox-image"
            />
            <div className="mt-3 flex items-center gap-3">
              <span className="text-white/80 text-sm">
                {lightboxIndex + 1} / {screenshots.length}
              </span>
              <a
                href={screenshots[lightboxIndex].url}
                download={screenshots[lightboxIndex].filename}
                className="inline-flex items-center gap-1 text-white/80 text-sm hover:text-white transition-colors"
                onClick={(e) => e.stopPropagation()}
              >
                <Download size={14} />
                下载
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
