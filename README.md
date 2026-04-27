# ProShop

Интернет-магазин с полным циклом покупки: каталог товаров, корзина, оформление заказа, оплата через PayPal. Есть панель администратора для управления товарами, пользователями и заказами. Проект учебный — исходник курса Brad Traversy на Udemy.

---

## Tech Stack

| Слой | Технология | Версия |
|---|---|---|
| Runtime | Node.js | ≥ 14.6 |
| Backend framework | Express | ^4.17.1 |
| Database | MongoDB + Mongoose | ^5.10.6 |
| Auth | jsonwebtoken + bcryptjs | ^8.5.1 / ^2.4.3 |
| File upload | multer | ^1.4.2 |
| Frontend | React | ^16.13.1 |
| State management | Redux + redux-thunk | ^4.0.5 / ^2.3.0 |
| UI | react-bootstrap | ^1.3.0 |
| Routing | react-router-dom | ^5.2.0 |
| HTTP client | axios | ^0.20.0 |
| Payment | react-paypal-button-v2 | ^2.6.2 |
| Dev runner | concurrently + nodemon | ^5.3.0 / ^2.0.4 |

---

## Структура проекта

```
proshop_mern/
├── backend/
│   ├── config/         # подключение к MongoDB
│   ├── controllers/    # бизнес-логика (products, users, orders)
│   ├── data/           # seed-данные (товары и пользователи)
│   ├── middleware/     # authMiddleware, errorMiddleware
│   ├── models/         # Mongoose-схемы (User, Product, Order)
│   ├── routes/         # Express-роуты
│   ├── utils/          # generateToken (JWT)
│   ├── seeder.js       # скрипт наполнения / очистки БД
│   └── server.js       # точка входа Express
├── frontend/
│   └── src/
│       ├── actions/    # Redux thunk action creators
│       ├── components/ # переиспользуемые компоненты
│       ├── constants/  # строки типов Redux-action
│       ├── reducers/   # Redux reducers
│       ├── screens/    # страницы (15 штук)
│       ├── store.js    # Redux store
│       └── App.js      # React Router маршруты
├── uploads/            # загруженные изображения товаров
├── .env.example        # шаблон переменных окружения
├── package.json        # зависимости backend + npm-скрипты
└── Procfile            # для деплоя на Heroku
```

---

## Быстрый старт

### 1. Prerequisites

- **Node.js ≥ 14.6** — проверить: `node -v`
- **MongoDB** — нужна запущенная инстанция. Варианты:
  - Локально: [установить MongoDB Community](https://www.mongodb.com/try/download/community) и запустить `mongod`
  - Docker: `docker run -d -p 27017:27017 mongo:5`
  - Облако: создать бесплатный кластер на [MongoDB Atlas](https://www.mongodb.com/atlas), взять connection string

### 2. Переменные окружения

Создать файл `.env` в корне репозитория (рядом с `package.json`):

```
NODE_ENV=development
PORT=5000
MONGO_URI=mongodb://localhost:27017/proshop
JWT_SECRET=замените_на_любую_случайную_строку
PAYPAL_CLIENT_ID=ваш_sandbox_client_id
```

**Описание переменных:**

| Переменная | Где используется | Обязательна |
|---|---|---|
| `NODE_ENV` | включает morgan-логгер в dev; скрывает stack trace в prod | да |
| `PORT` | порт Express, fallback `5000` | нет |
| `MONGO_URI` | строка подключения Mongoose | да |
| `JWT_SECRET` | подпись и верификация JWT-токенов (30 дней) | да |
| `PAYPAL_CLIENT_ID` | отдаётся фронту через `GET /api/config/paypal` | нет* |

\* Без `PAYPAL_CLIENT_ID` кнопка оплаты не загрузится, но остальное работает.

**Как получить PayPal Sandbox Client ID:**
1. Зайти на [developer.paypal.com](https://developer.paypal.com)
2. My Apps & Credentials → создать приложение (тип: Merchant)
3. Скопировать **Client ID** из раздела Sandbox
4. Для тестовой оплаты использовать sandbox buyer account из раздела Sandbox → Accounts

### 3. Установка зависимостей

Зависимости устанавливаются в двух местах: корень (backend) и `frontend/`.

```bash
# backend (из корня репозитория)
npm install

# frontend
cd frontend && npm install
```

### 4. Запуск в dev-режиме

```bash
# из корня репозитория
npm run dev
```

Запускает одновременно:
- backend на `http://localhost:5000` (nodemon, перезапускается при изменениях)
- frontend на `http://localhost:3000` (CRA dev server с hot reload)

Открыть: `http://localhost:3000`

Фронтенд проксирует API-запросы на `http://127.0.0.1:5000` (настроено в `frontend/package.json`).

### 5. Наполнение базы тестовыми данными

```bash
# загрузить товары и пользователей
npm run data:import

# удалить все данные
npm run data:destroy
```

> **Внимание:** `data:import` сначала удаляет все существующие данные, затем вставляет новые.

**Тестовые аккаунты после импорта:**

| Email | Пароль | Роль |
|---|---|---|
| admin@example.com | 123456 | Admin |
| john@example.com | 123456 | Customer |
| jane@example.com | 123456 | Customer |

---

## Сборка для production

```bash
# собрать фронтенд
cd frontend && npm run build

# запустить сервер (отдаёт собранный фронтенд как статику)
cd .. && npm start
```

При `NODE_ENV=production` Express раздаёт `frontend/build/` и обрабатывает все маршруты через `index.html`.

---

## Troubleshooting

### `Error: Cannot connect to MongoDB`
- Убедиться, что MongoDB запущена и доступна по адресу из `MONGO_URI`
- При использовании Atlas: добавить IP в whitelist (Network Access → Add IP Address → Allow from anywhere для разработки)
- Mongoose v5 передаёт `useCreateIndex: true` — эта опция убрана в MongoDB Driver 4+. Если появляется предупреждение `useCreateIndex is not supported`, это не ломает работу, но означает, что Mongoose обновился выше v5

### Фронтенд не достигает backend (`Network Error` в консоли браузера)
- Proxy работает только через `npm run dev` (CRA dev server). При открытии `index.html` напрямую из файловой системы — не работает
- Proxy прописан на `127.0.0.1`, а не `localhost`. Если backend слушает на `0.0.0.0` или IPv6 — proxy может не сработать. Проверить, что `http://127.0.0.1:5000` отвечает
- Убедиться, что обе части запущены: в терминале `npm run dev` должны появиться строки и от nodemon, и от react-scripts

### PayPal кнопка не появляется / ошибка загрузки PayPal SDK
- `PAYPAL_CLIENT_ID` не задан или пустой — `GET /api/config/paypal` вернёт пустую строку, SDK не загрузится
- Использовать именно **Sandbox** Client ID при `NODE_ENV=development`
- Заблокированные расширения браузера (ad blockers) могут блокировать `paypal.com` — проверить в режиме инкогнито

### `SyntaxError: Cannot use import statement` при запуске backend
- В `package.json` в корне должно быть `"type": "module"`. Если его нет — ES-импорты не работают
- Node.js должен быть ≥ 14.6. Проверить: `node -v`
- Все импорты внутри `backend/` должны содержать расширение `.js`: `import User from './models/userModel.js'`

### `Module not found` при импорте в backend
- Проверить, что в импорте есть `.js` в конце: `./config/db.js`, а не `./config/db`
- ES Modules в Node не резолвят расширения автоматически, в отличие от CommonJS

### Загрузка изображений не работает (`/api/upload` возвращает ошибку)
- Папка `uploads/` должна существовать в корне репозитория. Создать вручную: `mkdir uploads`
- Multer принимает только `jpg`, `jpeg`, `png` — другие форматы вернут ошибку `Images only!`

### Порт 5000 занят
- На macOS (начиная с версии Monterey и новее) порт 5000 по умолчанию занят службой AirPlay Receiver (Приемник AirPlay)
- Отключить приемник AirPlay в настройках системы System Settings/Preferences -> General -> AirDrop и Handoff -> выключить
- Или поменять порт в `.env`: `PORT=5001`

### Данные из предыдущего запуска мешают
```bash
npm run data:destroy && npm run data:import
```

---

## Лицензия

MIT © 2020
