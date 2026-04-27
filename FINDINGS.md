# Top-10 Critical & Medium Findings — ProShop MERN

## Risk Summary Table

| # | Риск | Где | Что | Как фиксить | Статус |
|---|------|-----|-----|-------------|--------|
| 1 | 🔴 | `backend/controllers/orderController.js::addOrderItems` | `return` после `throw` — недостижимый код; излишняя вложенность `if/else` | Заменить `if/else` на guard clause: `if (!orderItems \|\| !orderItems.length) { throw ... }` | ✅ [6ef3fc5](https://github.com/ddobrotvorskiy/proshop_mern/commit/6ef3fc5) |
| 2 | 🔴 | `frontend/src/screens/PlaceOrderScreen.js::PlaceOrderScreen` | Прямая мутация Redux state: `cart.itemsPrice = ...`; `disabled={cart.cartItems === 0}` сравнивает массив с числом | Вынести расчёт в `useMemo`, кнопку исправить на `cart.cartItems.length === 0` | 🔴 not yet |
| 3 | 🔴 | `backend/controllers/orderController.js::updateOrderToPaid` | Нет проверки `req.body.payer` — упадёт с `Cannot read properties of undefined` при ошибке PayPal | Добавить `req.body.payer?.email_address` или явный guard перед обращением | 🔴 not yet |
| 4 | 🔴 | `backend/routes/uploadRoutes.js` | Нет проверки `req.file`; ошибка передаёт строку вместо `Error` в multer | Добавить `if (!req.file) return res.status(400)...`; ошибку в `new Error(...)` | 🔴 not yet |
| 5 | 🔴 | `frontend/src/screens/OrderScreen.js::OrderScreen` | `addDecimals` создаётся в каждом рендере; мутация `order.itemsPrice` при `loading === false` вызовет undefined | Вынести за пределы компонента, вычислять через `useMemo` без мутации | 🔴 not yet |
| 6 | 🔴 | `package.json::mongoose` | v5.10.6 не получает security-патчи; `useCreateIndex` deprecated в Driver 4+ | Upgrade до v9.x + тестирование | 🔴 not yet |
| 7 | 🔴 | `package.json::react / react-dom` | v16.13.1 не получает обновлений; `ReactDOM.render` deprecated в 18+ | Upgrade до v19.x + замена API | 🔴 not yet |
| 8 | 🔴 | `package.json::jsonwebtoken` | v8.5.1 уязвим; v9.x закрывает уязвимость с алгоритмом `none` | Upgrade до v9.x | 🔴 not yet |
| 9 | 🟡 | `backend/middleware/authMiddleware.js::protect` | Если `User.findById` вернёт `null` — `req.user` будет `null`, упадёт на `req.user._id` | Добавить `if (!req.user) { res.status(401); throw new Error(...) }` | 🔴 not yet |
| 10 | 🟡 | `frontend/src/store.js::hydration` | `JSON.parse(localStorage.getItem(...))` без `try/catch` — белый экран при невалидном JSON | Обернуть каждый `JSON.parse` в `try/catch` с fallback | 🔴 not yet |

