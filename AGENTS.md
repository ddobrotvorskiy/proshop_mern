# AGENTS.md – ProShop MERN Guide

## Project Structure

**MERN monorepo** with root-level npm scripts coordinating front and back:
- `backend/` – Express.js server (Node ES modules), runs on `:5000`
- `frontend/` – React app with Redux, runs on `:3000`
- Root `package.json` orchestrates both via `concurrently` and holds **all backend dependencies** (no separate `backend/package.json`)

**Key entry points:**
- Backend: `backend/server.js` → routes at `/api/{products,users,orders,upload}`
- Frontend: `frontend/src/index.js` → `App.js` defines all routes
- Frontend state: Redux store in `frontend/src/store.js` (no Redux Toolkit; uses classic Redux + redux-thunk)

**Backend layout:**
```
backend/
├── server.js           # Express app entry point
├── seeder.js           # DB seed/destroy script
├── config/
│   └── db.js           # Mongoose connection
├── controllers/        # Business logic (thin routes delegate here)
│   ├── productController.js
│   ├── userController.js
│   └── orderController.js
├── data/               # Sample seed data
│   ├── products.js
│   └── users.js
├── middleware/
│   ├── authMiddleware.js   # protect + admin
│   └── errorMiddleware.js  # notFound + errorHandler
├── models/
│   ├── userModel.js
│   ├── productModel.js
│   └── orderModel.js
├── routes/
│   ├── productRoutes.js
│   ├── userRoutes.js
│   ├── orderRoutes.js
│   └── uploadRoutes.js
└── utils/
    └── generateToken.js    # JWT sign (30d expiry)
```

**Frontend layout:**
```
frontend/src/
├── App.js              # All React Router routes
├── index.js            # ReactDOM.render + Redux Provider
├── store.js            # Redux store (20 slices)
├── bootstrap.min.css   # Vendored Bootstrap CSS (local file, not npm)
├── actions/            # Thunk action creators
├── constants/          # Redux action type strings
├── reducers/           # Redux reducers
├── components/         # Shared UI components (Header, Footer, etc.)
└── screens/            # Page-level components (15 screens)
```

---

## Essential Dev Commands

```bash
# Root level (both frontend + backend dev mode)
npm run dev

# Backend only (nodemon watches for changes)
npm run server

# Frontend only (React dev server)
npm run client

# Production start (serves frontend build as static)
npm start

# Database seeding (requires MONGO_URI in .env)
npm run data:import    # Wipes all data, inserts fresh sample data
npm run data:destroy   # Wipes all data (no re-seed)

# Frontend production build
cd frontend && npm run build
# OR via root (used by Heroku):
npm run heroku-postbuild
```

---

## Required Environment Setup

Create `.env` in repo root (see `.env.example`):
```
NODE_ENV=development
PORT=5000
MONGO_URI=mongodb://localhost:27017/proshop
JWT_SECRET=your_jwt_secret_key_here
PAYPAL_CLIENT_ID=your_paypal_sandbox_client_id_here
```

**Critical:** Backend uses ES modules (`"type": "module"` in root `package.json`). All backend imports must include `.js` extension or will fail. `__dirname` is not available in ES modules — the codebase uses `path.resolve()` as a workaround (`server.js:35`).

---

## Database

**MongoDB** (via Mongoose v5, no migrations). Schemas in `backend/models/`:

| Model | Key fields |
|---|---|
| `userModel.js` | `name`, `email`, `password` (bcrypt hashed), `isAdmin` (Boolean, default `false`) |
| `productModel.js` | `user` (ref), `name`, `image`, `brand`, `category`, `description`, `reviews[]`, `rating`, `numReviews`, `price`, `countInStock` |
| `orderModel.js` | `user` (ref), `orderItems[]`, `shippingAddress`, `paymentMethod`, `paymentResult`, `taxPrice`, `shippingPrice`, `totalPrice`, `isPaid`, `paidAt`, `isDelivered`, `deliveredAt` |

All models have `timestamps: true`. `userModel` has a `matchPassword()` method and a pre-save bcrypt hook.

**Seeder** (`backend/seeder.js`) is destructive: `data:import` deletes **all** collections, then inserts fresh data from `backend/data/`.

---

## API Routes & Auth

Backend routes in `backend/routes/`, logic in `backend/controllers/`:

| Route | Methods | Auth |
|---|---|---|
| `/api/products` | `GET` (list, paginated), `POST` (create) | public / admin |
| `/api/products/top` | `GET` (top 3 by rating) | public |
| `/api/products/:id` | `GET`, `PUT`, `DELETE` | public / admin |
| `/api/products/:id/reviews` | `POST` | protected |
| `/api/users` | `POST` (register), `GET` (list) | public / admin |
| `/api/users/login` | `POST` | public |
| `/api/users/profile` | `GET`, `PUT` | protected |
| `/api/users/:id` | `GET`, `PUT`, `DELETE` | admin |
| `/api/orders` | `POST` (create), `GET` (list all) | protected / admin |
| `/api/orders/myorders` | `GET` | protected |
| `/api/orders/:id` | `GET` | protected |
| `/api/orders/:id/pay` | `PUT` | protected |
| `/api/orders/:id/deliver` | `PUT` | admin |
| `/api/upload` | `POST` (single image) | — |
| `/api/config/paypal` | `GET` (returns `PAYPAL_CLIENT_ID`) | public |
| `/uploads/*` | Static file serving | public (always active) |

**Auth:** `Authorization: Bearer <token>` header.
- `protect` middleware (`authMiddleware.js:5–31`): verifies JWT, attaches `req.user` (without password).
- `admin` middleware (`authMiddleware.js:33–40`): checks `req.user.isAdmin`; must follow `protect`.

Upload: multer saves to `uploads/` as `fieldname-timestamp.ext`; accepts jpg/jpeg/png only.

---

## Frontend Architecture

**React v16.13 + React Router v5** (not v6). **No TypeScript.** No tests written (CRA test libs installed but unused).

### Redux Store

20 slices in `store.js`, combined from 4 reducer files:

**Products** (`productReducers.js`):
`productList`, `productDetails`, `productDelete`, `productCreate`, `productUpdate`, `productReviewCreate`, `productTopRated`

**Cart** (`cartReducers.js`):
`cart` — persists `cartItems`, `shippingAddress`, `paymentMethod` to localStorage

**Users** (`userReducers.js`):
`userLogin`, `userRegister`, `userDetails`, `userUpdateProfile`, `userList`, `userDelete`, `userUpdate`

**Orders** (`orderReducers.js`):
`orderCreate`, `orderDetails`, `orderPay`, `orderDeliver`, `orderListMy`, `orderList`

**localStorage hydration** (on store init):
- `cartItems` → `cart.cartItems`
- `shippingAddress` → `cart.shippingAddress`
- `userInfo` → `userLogin.userInfo`

(`paymentMethod` is stored by the reducer via `CART_SAVE_PAYMENT_METHOD` but not pre-hydrated in `store.js` initial state.)

### Routes (App.js)

**No `<Switch>` wrapper** — multiple routes can render simultaneously if not using `exact`.

| Path | Screen |
|---|---|
| `/` (exact) | HomeScreen |
| `/search/:keyword` (exact) | HomeScreen |
| `/page/:pageNumber` (exact) | HomeScreen |
| `/search/:keyword/page/:pageNumber` (exact) | HomeScreen |
| `/product/:id` | ProductScreen |
| `/cart/:id?` | CartScreen |
| `/login` | LoginScreen |
| `/register` | RegisterScreen |
| `/profile` | ProfileScreen |
| `/shipping` | ShippingScreen |
| `/payment` | PaymentScreen |
| `/placeorder` | PlaceOrderScreen |
| `/order/:id` | OrderScreen |
| `/admin/userlist` | UserListScreen |
| `/admin/user/:id/edit` | UserEditScreen |
| `/admin/productlist` (exact) | ProductListScreen |
| `/admin/productlist/:pageNumber` (exact) | ProductListScreen |
| `/admin/product/:id/edit` | ProductEditScreen |
| `/admin/orderlist` | OrderListScreen |

### Shared Components (`frontend/src/components/`)

`Header`, `Footer`, `Loader`, `Message`, `Rating`, `Product`, `ProductCarousel`, `Paginate`, `SearchBox`, `CheckoutSteps`, `FormContainer`, `Meta` (react-helmet for `<head>` tags)

---

## Build & Deployment

**Frontend build:**
```bash
cd frontend && npm run build
```
Creates `frontend/build/`. In production (`NODE_ENV=production`), Express serves it as static (`server.js:38–43`) with a catch-all `*` route for client-side routing.

**Heroku:** `Procfile` contains `web: node backend/server.js`. `heroku-postbuild` script installs frontend deps and builds automatically.

**Pagination:** `pageSize` is hardcoded to `10` products per page in `productController.js`. Top products endpoint returns top **3** by rating.

---

## Common Gotchas

1. **Backend ES module imports:** Always include `.js` extension (e.g., `import User from './models/userModel.js'`). Missing extension → runtime failure.

2. **`__dirname` not available in ES modules:** Use `path.resolve()` instead (already done in `server.js:35`). Do not add `import { fileURLToPath } from 'url'` workaround unless `path.resolve()` is insufficient.

3. **No `<Switch>` in App.js:** Multiple `<Route>` components render simultaneously for matching paths. Use `exact` carefully when adding new routes.

4. **Frontend proxy:** `frontend/package.json` proxies unmatched requests to `http://127.0.0.1:5000` (note: `127.0.0.1`, not `localhost`). Backend must be running on `:5000` for API calls to work in dev.

5. **JWT secret:** `process.env.JWT_SECRET` is used by both `authMiddleware.js` (verify) and `generateToken.js` (sign). Tokens expire in **30 days**.

6. **localStorage persistence:** `cart` and `userLogin.userInfo` persist across sessions. Logout clears `userInfo` from localStorage but `cartItems` persist until explicitly removed.

7. **Admin middleware order:** `admin` must always follow `protect` in route declarations — it relies on `req.user` set by `protect`.

8. **No Redux Toolkit:** Uses classic Redux with action type string constants in `frontend/src/constants/`. Actions are thunks, not slices. Do not introduce `createSlice` or `createAsyncThunk` without refactoring the whole store.

9. **Bootstrap CSS is vendored:** `frontend/src/bootstrap.min.css` is a local copy, imported in `index.js`. Do not expect to import Bootstrap from `node_modules` — it's not there as a direct stylesheet dependency.

10. **`morgan` logger** is active in dev mode only (`NODE_ENV === 'development'`). It logs HTTP requests to stdout.

11. **Seeder is destructive:** `npm run data:import` calls `destroyData()` before inserting. Running it on production will wipe all real data.
