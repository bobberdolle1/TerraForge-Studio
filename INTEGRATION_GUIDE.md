# 🔧 Integration Guide - TerraForge Studio v4.x

Руководство по интеграции новых компонентов и улучшений в существующий проект.

---

## 📋 Содержание

1. [Установка зависимостей](#установка-зависимостей)
2. [Error Boundary](#error-boundary)
3. [Skeleton Loaders](#skeleton-loaders)
4. [Keyboard Shortcuts](#keyboard-shortcuts)
5. [Lazy Loading](#lazy-loading)
6. [Доступные компоненты](#доступные-компоненты)
7. [Production Build](#production-build)

---

## 1. Установка зависимостей

```bash
cd frontend-new
npm install
```

Новые зависимости автоматически установятся:
- `rollup-plugin-visualizer` - для анализа bundle
- `sharp` - для генерации PWA иконок

После установки автоматически сгенерируются иконки (через postinstall hook).

---

## 2. Error Boundary

### Обернуть главное приложение

**Файл: `src/main.tsx`**

```tsx
import ErrorBoundary from './components/ErrorBoundary';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
```

### Использовать для критичных компонентов

```tsx
import ErrorBoundary from '@/components/ErrorBoundary';

<ErrorBoundary>
  <CesiumViewer />
</ErrorBoundary>
```

### Custom fallback UI

```tsx
<ErrorBoundary fallback={<div>Что-то пошло не так...</div>}>
  <YourComponent />
</ErrorBoundary>
```

---

## 3. Skeleton Loaders

### Замена loading states

**До:**
```tsx
{isLoading ? <div>Loading...</div> : <MapView />}
```

**После:**
```tsx
import { MapSkeleton } from '@/components/SkeletonLoader';

{isLoading ? <MapSkeleton className="h-96" /> : <MapView />}
```

### Примеры использования

```tsx
import { 
  CardSkeleton, 
  TableSkeleton, 
  ListSkeleton,
  ThumbnailGridSkeleton 
} from '@/components/SkeletonLoader';

// Для карточек
{isLoading ? <CardSkeleton /> : <Card data={data} />}

// Для таблиц
{isLoading ? <TableSkeleton rows={5} columns={4} /> : <Table />}

// Для списков
{isLoading ? <ListSkeleton items={3} /> : <List />}

// Для галереи thumbnails
{isLoading ? <ThumbnailGridSkeleton count={6} /> : <Gallery />}
```

---

## 4. Keyboard Shortcuts

### Добавить в главный layout

**Файл: `src/App.tsx`**

```tsx
import KeyboardShortcuts from '@/components/KeyboardShortcuts';

function App() {
  return (
    <div className="app">
      <YourContent />
      <KeyboardShortcuts />
    </div>
  );
}
```

### Custom shortcuts

```tsx
const customShortcuts = [
  {
    keys: ['Ctrl', 'G'],
    description: 'Generate terrain',
    action: () => handleGenerate(),
  },
  {
    keys: ['Ctrl', 'D'],
    description: 'Download result',
    action: () => handleDownload(),
  },
];

<KeyboardShortcuts shortcuts={customShortcuts} />
```

---

## 5. Lazy Loading

### Использовать готовые lazy компоненты

```tsx
import LazyComponents from '@/components/LazyComponents';

// Вместо обычного импорта
// import CesiumViewer from './CesiumViewer';

// Используйте lazy версию
<LazyComponents.CesiumViewer {...props} />
```

### Создать свой lazy component

```tsx
import { lazy, Suspense } from 'react';
import { MapSkeleton } from '@/components/SkeletonLoader';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function MyComponent() {
  return (
    <Suspense fallback={<MapSkeleton className="h-full" />}>
      <HeavyComponent />
    </Suspense>
  );
}
```

---

## 6. Доступные компоненты

### AccessibleButton

```tsx
import { AccessibleButton } from '@/components/AccessibleButton';

<AccessibleButton 
  variant="primary"
  size="lg"
  isLoading={loading}
  leftIcon={<Save className="w-5 h-5" />}
  onClick={handleSave}
>
  Save Project
</AccessibleButton>
```

**Варианты:**
- `primary` - синяя кнопка (основное действие)
- `secondary` - серая кнопка
- `outline` - кнопка с обводкой
- `ghost` - прозрачная кнопка
- `danger` - красная кнопка (удаление)

**Размеры:**
- `sm` - маленькая
- `md` - средняя (по умолчанию)
- `lg` - большая

### Tooltip

```tsx
import { Tooltip } from '@/components/Tooltip';

<Tooltip content="Создать новый проект" position="top">
  <button>New</button>
</Tooltip>
```

**Позиции:**
- `top` (по умолчанию)
- `bottom`
- `left`
- `right`

---

## 7. Production Build

### Сборка с анализом

```bash
npm run build
```

После сборки откроется `dist/stats.html` с визуализацией bundle:
- Размеры chunks
- Зависимости
- Gzip/Brotli размеры

### Оптимизация

Bundle автоматически разделен на chunks:
- `cesium.js` - CesiumJS (~3-4 MB)
- `leaflet.js` - Leaflet
- `react-vendor.js` - React core
- `ui-vendor.js` - UI библиотеки
- `index.js` - основной код приложения

### Проверка производительности

```bash
npm run preview
```

Затем откройте Chrome DevTools:
1. Network → Disable cache
2. Lighthouse → Run audit
3. Проверьте Performance score (должен быть >90)

---

## 🎯 Checklist перед деплоем

- [ ] Установлены все зависимости (`npm install`)
- [ ] Сгенерированы PWA иконки (`npm run generate-icons`)
- [ ] ErrorBoundary обернут вокруг App
- [ ] KeyboardShortcuts добавлен в layout
- [ ] Skeleton loaders заменили loading states
- [ ] Тяжелые компоненты lazy-loaded
- [ ] Запущен build и проверен stats.html
- [ ] Lighthouse score >90
- [ ] Проверена keyboard navigation (Tab, Enter, Escape)
- [ ] Проверены tooltips на всех кнопках

---

## 🐛 Troubleshooting

### Ошибка: "Cannot find module 'sharp'"

```bash
npm install sharp --save-dev
```

### Ошибка: "Icons not generated"

```bash
npm run generate-icons
```

### Bundle слишком большой

Проверьте `dist/stats.html` и найдите большие зависимости:
- Возможно, нужно добавить их в `manualChunks`
- Проверьте, что не импортируете неиспользуемые библиотеки

### Lighthouse score низкий

1. Проверьте Network tab - убедитесь, что chunks загружаются отдельно
2. Проверьте bundle size - должен быть <500KB для main chunk
3. Убедитесь, что images оптимизированы (WebP)
4. Проверьте, что используется code splitting

---

**Последнее обновление**: 22 октября 2025  
**Версия**: 4.0.0

