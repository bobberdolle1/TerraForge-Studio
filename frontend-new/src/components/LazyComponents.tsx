import { lazy, Suspense } from 'react';
import { MapSkeleton, CardSkeleton } from './SkeletonLoader';

/**
 * Lazy-loaded components with Suspense wrappers
 * Improves initial load time by code splitting
 */

// CesiumJS is heavy, load it only when needed
export const CesiumViewer = lazy(() => 
  import('./CesiumViewer').catch(() => ({
    default: () => <div>Failed to load 3D viewer</div>
  }))
);

// Wrap with Suspense and skeleton
export const CesiumViewerWithSuspense = (props: any) => (
  <Suspense fallback={<MapSkeleton className="h-full" />}>
    <CesiumViewer {...props} />
  </Suspense>
);

// History panel - not needed on initial load
export const HistoryPanel = lazy(() => 
  import('./HistoryPanel').catch(() => ({
    default: () => <div>Failed to load history</div>
  }))
);

export const HistoryPanelWithSuspense = (props: any) => (
  <Suspense fallback={<CardSkeleton />}>
    <HistoryPanel {...props} />
  </Suspense>
);

// Settings panel
export const SettingsPanel = lazy(() => 
  import('./SettingsPanel').catch(() => ({
    default: () => <div>Failed to load settings</div>
  }))
);

export const SettingsPanelWithSuspense = (props: any) => (
  <Suspense fallback={<CardSkeleton />}>
    <SettingsPanel {...props} />
  </Suspense>
);

// Cache management UI
export const CacheManager = lazy(() => 
  import('./CacheManager').catch(() => ({
    default: () => <div>Failed to load cache manager</div>
  }))
);

export const CacheManagerWithSuspense = (props: any) => (
  <Suspense fallback={<CardSkeleton />}>
    <CacheManager {...props} />
  </Suspense>
);

export default {
  CesiumViewer: CesiumViewerWithSuspense,
  HistoryPanel: HistoryPanelWithSuspense,
  SettingsPanel: SettingsPanelWithSuspense,
  CacheManager: CacheManagerWithSuspense,
};
