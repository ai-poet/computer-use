import { useCallback, useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight, Grid3X3, List, X } from 'lucide-react';
import { Button } from '../../shared/ui/Button';
import type { Screenshot } from './types';
import styles from './ScreenshotGallery.module.less';

function sourceLabel(source: Screenshot['source']) {
  return { web: '网页', app: '应用', android: '安卓' }[source];
}

export function ScreenshotGallery({ screenshots }: { screenshots: Screenshot[] }) {
  const [mode, setMode] = useState<'grid' | 'list'>('grid');
  const [active, setActive] = useState<number | null>(null);

  const close = () => setActive(null);
  const prev = useCallback(() => {
    if (active === null) return;
    setActive(active === 0 ? screenshots.length - 1 : active - 1);
  }, [active, screenshots.length]);
  const next = useCallback(() => {
    if (active === null) return;
    setActive(active === screenshots.length - 1 ? 0 : active + 1);
  }, [active, screenshots.length]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (active === null) return;
      if (event.key === 'Escape') close();
      if (event.key === 'ArrowLeft') prev();
      if (event.key === 'ArrowRight') next();
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [active, prev, next]);

  if (!screenshots.length) return null;

  return (
    <div className={styles.gallery}>
      <div className={styles.toolbar}>
        <span className={styles.count}>截图索引 ({screenshots.length} 张)</span>
        <div className={styles.actions}>
          <Button iconOnly variant={mode === 'grid' ? 'secondary' : 'ghost'} onClick={() => setMode('grid')}>
            <Grid3X3 size={15} />
          </Button>
          <Button iconOnly variant={mode === 'list' ? 'secondary' : 'ghost'} onClick={() => setMode('list')}>
            <List size={15} />
          </Button>
        </div>
      </div>
      {mode === 'grid' ? (
        <div className={styles.grid}>
          {screenshots.map((shot, index) => (
            <button key={shot.id} className={styles.shot} onClick={() => setActive(index)}>
              <img src={shot.url} alt={shot.label} loading="lazy" />
              <span className={styles.tag}>{sourceLabel(shot.source)}</span>
            </button>
          ))}
        </div>
      ) : (
        <div className={styles.list}>
          {screenshots.map((shot, index) => (
            <button key={shot.id} className={styles.row} onClick={() => setActive(index)}>
              <img src={shot.url} alt={shot.label} className={styles.thumb} loading="lazy" />
              <span>
                <p className={styles.filename}>{shot.filename}</p>
                <span className={styles.source}>{sourceLabel(shot.source)}</span>
              </span>
            </button>
          ))}
        </div>
      )}
      {active !== null && (
        <div className={styles.overlay} onClick={close}>
          <button className={styles.close} onClick={(event) => { event.stopPropagation(); close(); }}>
            <X size={22} />
          </button>
          {screenshots.length > 1 && (
            <>
              <button className={styles.prev} onClick={(event) => { event.stopPropagation(); prev(); }}>
                <ChevronLeft size={26} />
              </button>
              <button className={styles.next} onClick={(event) => { event.stopPropagation(); next(); }}>
                <ChevronRight size={26} />
              </button>
            </>
          )}
          <img
            src={screenshots[active].url}
            alt={screenshots[active].label}
            className={styles.lightboxImage}
            onClick={(event) => event.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}
