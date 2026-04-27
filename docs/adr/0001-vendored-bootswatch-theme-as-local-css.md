# 0001 — Vendored Bootswatch theme as a local CSS file

- **Status:** Accepted
- **Confidence:** HIGH — явно видно в коде; лицензионный заголовок в первых строках файла неопровержим

---

## Context

Приложению нужна CSS-библиотека для UI. Стандартный путь в CRA-проектах — установить Bootstrap через npm и импортировать из `node_modules`. Однако разработчик хотел использовать не vanilla Bootstrap, а конкретную тему Bootswatch (Lux), придающую приложению тёмный navbar, шрифт Nunito Sans и кастомные цветовые токены.

## Decision

Bootstrap не устанавливался через npm. Вместо этого файл темы Bootswatch v4.5.2 "Lux" был скачан вручную и положен в репозиторий как `frontend/src/bootstrap.min.css` (173 КБ). Файл импортируется напрямую в точке входа:

```js
// frontend/src/index.js:5
import './bootstrap.min.css'
```

Доказательство в самом файле — лицензионный заголовок на строках 1��6:

```css
/*!
 * Bootswatch v4.5.2
 * Homepage: https://bootswatch.com
 * Copyright 2012-2020 Thomas Park
 * Licensed under MIT
 * Based on Bootstrap
*/
```

Файл также содержит `@import url("https://fonts.googleapis.com/css2?family=Nunito+Sans...")` — характерная черта темы Lux.

## Alternatives

| Вариант | Почему не выбран (инференция) |
|---|---|
| `npm install bootstrap` + `import 'bootstrap/dist/css/bootstrap.min.css'` | Даёт только vanilla Bootstrap без темы; потребовал бы дополнительных CSS-оверрайдов |
| CDN-ссылка в `public/index.html` | Зависимость от внешнего сервиса при каждой загрузке; нет SRI-пина для Bootswatch |
| `npm install bootswatch` | Возможный вариант, но требует указать тему в импорте; vendoring проще для учебного проекта |
| CSS-in-JS (styled-components, Emotion) | Не совместим с react-bootstrap компонентами без дополнительной настройки |

## Consequences

**Плюсы:**
- Файл включается в webpack-бандл — нет сетевого запроса за CSS при загрузке приложения.
- Тема зафиксирована: случайное обновление Bootswatch не сломает UI.
- Нет зависимости от CDN Bootswatch.

**Минусы:**
- Обновление Bootstrap/Bootswatch требует ручной замены файла. Нет `package.json`-версии, связанной с реальным файлом — версия `4.5.2` нигде не зафиксирована в зависимостях.
- 173 КБ CSS попадают в webpack-бандл, а не кэшируются браузером отдельно как CDN-ресурс.
- Если `@import url(...)` для Google Fonts заблокирован (корпоративный прокси, офлайн), шрифт Nunito Sans не загрузится, но Bootstrap продолжит работать с fallback-шрифтом.
- Файл содержит неиспользуемые компоненты Bootstrap — PurgeCSS не подключён, CSS не минифицируется повторно при сборке.
