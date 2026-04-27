# Code Review: ProShop MERN

---

## 1. HOTSPOTS

**`backend/controllers/orderController.js` → `addOrderItems`**
🔴 **critical**
`if (orderItems && orderItems.length === 0)` — `return` стоит после `throw`, т.е. ветка unreachable. Параллельно вся логика создания заказа живёт в `else`-блоке вместо раннего выхода, что без причины увеличивает вложенность.
→ Убрать `return` после `throw`, заменить `if/else` на guard clause: `if (!orderItems || !orderItems.length) { ... throw }` / затем плоский код.

---

**`frontend/src/screens/OrderScreen.js` → `OrderScreen`**
🔴 **critical**
`addDecimals` определяется внутри render-функции под условием `if (!loading)` — при каждом рендере создаётся заново, а при `loading === true` вызов `order.itemsPrice = ...` упадёт с `Cannot read properties of undefined` (order ещё не загружен). Присвоение `order.itemsPrice` мутирует Redux state напрямую.
→ Вынести `addDecimals` за пределы компонента, `itemsPrice` вычислять через `useMemo` или локальную переменную без мутации объекта из store.

---

**`frontend/src/screens/PlaceOrderScreen.js` → `PlaceOrderScreen`**
🔴 **critical**
`cart.itemsPrice`, `cart.shippingPrice`, `cart.taxPrice`, `cart.totalPrice` присваиваются напрямую объекту из Redux store на каждом рендере — это прямая мутация state. Кроме того, `disabled={cart.cartItems === 0}` сравнивает массив с числом — всегда `false`, кнопка никогда не дизейблится при пустой корзине.
→ Вынести расчёт цен в локальные переменные или `useMemo`, кнопку исправить на `cart.cartItems.length === 0`.

---

**`frontend/src/screens/ProductScreen.js` → `ProductScreen`**
🟡 **medium**
`useEffect` зависит от `match` целиком, хотя использует только `match.params.id` — вызывает лишние перезапуски при любом изменении `match`. Проверка `product._id !== match.params.id` не сбрасывает состояние review при смене продукта, если `successProductReview` уже `true`.
→ Добавить `match.params.id` в deps вместо `match`, добавить `dispatch({ type: PRODUCT_CREATE_REVIEW_RESET })` при смене id.

---

**`frontend/src/screens/ProfileScreen.js` → `ProfileScreen`**
🟢 **cosmetic**
Пустой JSX-блок `{}` между двумя `<Message>` — артефакт редактирования.
→ Удалить.

---

## 2. EDGE CASES

**`backend/controllers/orderController.js` → `updateOrderToPaid`**
🔴 **critical**
`req.body.payer.email_address` — нет проверки на существование `req.body.payer`. Если PayPal вернёт ответ без `payer` (ошибка, отмена), сервер упадёт с `Cannot read properties of undefined`.
→ Добавить проверку `req.body.payer?.email_address` или явный guard перед обращением к `payer`.

---

**`backend/routes/uploadRoutes.js` → обработчик `POST /`**
🔴 **critical**
`res.send(`/${req.file.path}`)` — нет проверки `req.file`. Если multer отбросил файл по типу через `fileFilter`, `req.file` будет `undefined` и сервер упадёт. Кроме того, `cb('Images only!')` передаёт строку как error вместо `new Error(...)` — multer не передаст это в Express error handler корректно.
→ Добавить `if (!req.file) return res.status(400).json(...)`, ошибку оборачивать в `new Error('Images only!')`.

---

**`backend/middleware/authMiddleware.js` → `protect`**
🟡 **medium**
Если `User.findById` вернёт `null` (пользователь удалён, но токен ещё действует) — `req.user` будет `null`, `next()` вызовется, и последующие контроллеры упадут на `req.user._id`.
→ Добавить проверку `if (!req.user) { res.status(401); throw new Error('User not found') }` после `findById`.

---

**`backend/controllers/userController.js` → `registerUser`**
🟡 **medium**
Нет валидации формата email и минимальной длины пароля на уровне контроллера. Mongoose-схема тоже не валидирует формат email. Можно зарегистрироваться с `email: "x"` и `password: "1"`.
→ Добавить валидацию через `validator` или хотя бы `if (!email.includes('@'))` и минимальную длину пароля.

---

**`backend/controllers/productController.js` → `getProductById`**
🟡 **medium**
Нет проверки формата ObjectId — при запросе `GET /api/products/invalid-string` Mongoose бросает `CastError`, который попадает в errorHandler, но возвращает 500 вместо 400/404.
→ Добавить проверку `mongoose.Types.ObjectId.isValid(req.params.id)` перед `findById`.

---

**`frontend/src/screens/CartScreen.js` → `CartScreen`**
🟡 **medium**
`qty` парсится как `Number(location.search.split('=')[1])` — жёсткий разбор строки без URLSearchParams. При дополнительных query-параметрах или другом порядке параметров сломается.
→ Заменить на `new URLSearchParams(location.search).get('qty')`.

---

**`frontend/src/store.js` → hydration из localStorage**
🟡 **medium**
`JSON.parse(localStorage.getItem('cartItems'))` — нет `try/catch`. Если в localStorage окажется невалидный JSON (ручное изменение, другое приложение на том же домене), store не инициализируется и приложение упадёт с белым экраном.
→ Обернуть каждый `JSON.parse` в `try/catch` с fallback на дефолтное значение.

---

**`frontend/src/actions/userActions.js` → `logout`**
🟡 **medium**
`document.location.href = '/login'` — жёсткий hard navigation вместо React Router `history.push`. Обходит роутер, сбрасывает весь React state и вызывает полную перезагрузку страницы.
→ Передавать `history` как параметр в action creator или использовать `window.location.replace('/login')` осознанно, либо перейти на react-router `useHistory`.

---

## 3. OUTDATED DEPS

| Пакет | Текущая | Последняя | Уровень |
|---|---|---|---|
| `mongoose` | 5.10.6 | 9.5.0 | 🔴 **critical** — v5 не получает security-патчи; `useCreateIndex` удалена в Driver 4+, вызывает предупреждения |
| `react` / `react-dom` | 16.13.1 | 19.2.5 | 🔴 **critical** — React 16 не получает обновлений; `ReactDOM.render` deprecated в 18+ |
| `jsonwebtoken` | 8.5.1 | 9.0.3 | 🔴 **critical** — v9 закрывает уязвимость с алгоритмом `none` |
| `axios` | 0.20.0 | 1.15.2 | 🟡 **medium** — v0.x закрыта, v1 breaking changes в interceptors |
| `react-scripts` | 3.4.3 | 5.0.1 | 🟡 **medium** — webpack 4 вместо 5, нет поддержки новых синтаксов |
| `dotenv` | 8.2.0 | 17.4.2 | 🟡 **medium** |
| `express` | 4.17.1 | 5.2.1 | 🟡 **medium** — Express 5 выпущен, async error handling встроен |
| `react-router-dom` | 5.2.0 | 7.14.2 | 🟡 **medium** — v6/v7 полностью другой API |
| `redux` | 4.0.5 | 5.0.1 | 🟢 **cosmetic** |
| `bcryptjs` | 2.4.3 | 3.0.3 | 🟢 **cosmetic** |
| `react-paypal-button-v2` | 2.6.2 | 2.6.3 | 🟢 **cosmetic** — пакет заброшен, официальный SDK: `@paypal/react-paypal-js` |

---

## 4. HARDCODED VALUES

**`backend/controllers/productController.js` → `getProducts`**
🟡 **medium**
`const pageSize = 10` — магическое число прямо в теле функции, не вынесено в конфиг.
→ Вынести в `constants/config.js` или переменную окружения `PAGE_SIZE`.

---

**`backend/controllers/productController.js` → `getTopProducts`**
🟡 **medium**
`.limit(3)` — хардкод количества top-товаров.
→ Вынести рядом с `pageSize`.

---

**`backend/utils/generateToken.js` → `generateToken`**
🟡 **medium**
`expiresIn: '30d'` — срок жизни токена зашит в коде, не настраивается через env.
→ Вынести в `process.env.JWT_EXPIRE || '30d'`.

---

**`frontend/src/screens/PlaceOrderScreen.js` → `PlaceOrderScreen`**
🟡 **medium**
`cart.shippingPrice = addDecimals(cart.itemsPrice > 100 ? 0 : 100)` и `0.15 * cart.itemsPrice` — бесплатная доставка от $100 и налог 15% захардкожены прямо в компоненте.
→ Вынести в именованные константы или конфиг; в реальном проекте это должно считаться на бэкенде.

---

**`frontend/src/screens/OrderScreen.js` → `addPayPalScript`**
🟢 **cosmetic**
`` script.src = `https://www.paypal.com/sdk/js?client-id=${clientId}` `` — URL PayPal SDK в JSX.
→ Вынести URL в конфиг-файл.

---

**`backend/controllers/productController.js` → `createProduct`**
🟢 **cosmetic**
Строки `'Sample name'`, `'/images/sample.jpg'`, `'Sample brand'` и т.д. — placeholder-строки прямо в контроллере.
→ Вынести в объект-шаблон `PRODUCT_DEFAULTS`.

---

## 5. DEAD CODE

**`frontend/src/actions/userActions.js` → `logout`**
🟡 **medium**
`userRegisterReducer` слушает `USER_LOGOUT` и сбрасывается — но `userRegister` state нигде не используется после регистрации для защиты маршрутов. `USER_DETAILS_RESET` диспатчится при логауте избыточно — уже покрывается `USER_LOGOUT` в `userLoginReducer`.
→ Проверить, нужен ли `USER_LOGOUT` в `userRegisterReducer`.

---

**`backend/config/db.js` → `connectDB`**
🟡 **medium**
Опции `useUnifiedTopology: true`, `useNewUrlParser: true`, `useCreateIndex: true` — все три deprecated и выброшены из Mongoose 6+/MongoDB Driver 4+. При текущей Mongoose 5 они ещё принимаются, но генерируют предупреждения на новых версиях driver.
→ Удалить все три опции (в Mongoose 6+ они игнорируются или кидают ошибку).

---

**`frontend/src/screens/ProfileScreen.js`**
🟢 **cosmetic**
Пустой JSX-выражение `{}` между двумя `<Message>`.
→ Удалить.

---

**`frontend/src/index.js` → `serviceWorker`**
🟢 **cosmetic**
`serviceWorker.unregister()` — service worker импортируется и сразу отключается. Файл `serviceWorker.js` подключён, но никогда не активируется.
→ Удалить импорт и файл, если PWA не планируется.
