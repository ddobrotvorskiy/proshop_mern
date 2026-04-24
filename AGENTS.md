# AGENTS.md – ProShop MERN Guide

## Project Structure

**MERN monorepo** with root-level npm scripts coordinating front and back:
- `backend/` – Express.js server (Node ES modules), runs on `:5000`
- `frontend/` – React app with Redux, runs on `:3000`
- Root `package.json` orchestrates both via `concurrently`

**Key entry points:**
- Backend: `backend/server.js` → routes at `/api/{products,users,orders,upload}`
- Frontend: `frontend/src/index.js` → `App.js` defines all routes
- Frontend state: Redux store in `frontend/src/store.js` (no Redux Toolkit; uses classic Redux + redux-thunk)

## Essential Dev Commands

```bash
# Root level (both frontend + backend dev mode)
npm run dev

# Backend only (nodemon watches for changes)
npm run server

# Frontend only (React dev server)
npm run client

# Database seeding (requires MONGO_URI in .env)
npm run data:import    # Loads sample users & products
npm run data:destroy   # Wipes all data

# Frontend production build
cd frontend && npm run build
```

## Required Environment Setup

Create `.env` in repo root before running anything:
```
NODE_ENV=development
PORT=5000
MONGO_URI=<your_mongodb_uri>
JWT_SECRET=abc123
PAYPAL_CLIENT_ID=<your_paypal_sandbox_id>
```

**Critical:** Backend uses ES modules (`"type": "module"` in package.json). All backend imports must include `.js` extension or will fail.

## Database

**MongoDB** (via Mongoose, no migrations). Schema defined in `backend/models/`:
- `userModel.js` – User with `isAdmin` role for auth
- `productModel.js` – Products with ratings/reviews
- `orderModel.js` – Orders with payment & delivery status

Seeder is destructive: `npm run data:import` deletes all collections, then inserts fresh sample data.

## API Routes & Auth

Backend routes in `backend/routes/`:
- `/api/products` – Product CRUD
- `/api/users` – User auth, registration, admin user mgmt
- `/api/orders` – Order CRUD & PayPal payment
- `/api/upload` – File upload (multer)

**Auth:** Bearer token in `Authorization` header. Protected routes use `protect` middleware + optional `admin` middleware (see `backend/middleware/authMiddleware.js:5`).

## Frontend Architecture

**React v16 + React Router v5** (older versions, not v6).

Redux store has 6 slice domains:
- Product management (list, details, create/update/delete, reviews, top-rated)
- Cart (persists to localStorage)
- User auth (login, register, profile, list, admin mgmt)
- Orders (create, details, pay, deliver, list)

Actions in `frontend/src/actions/` dispatch via thunk middleware. Reducers in `frontend/src/reducers/`.

**Routes** (old React Router syntax, no hooks):
- `/` – HomeScreen (products with pagination/search)
- `/product/:id` – ProductScreen (details & reviews)
- `/cart/:id?` – CartScreen
- `/login`, `/register`, `/profile` – User screens
- `/admin/productlist`, `/admin/userlist`, `/admin/orderlist` – Admin screens

## Frontend Quirks

- **React Bootstrap** for UI (not custom CSS framework)
- Cart & user info cached in localStorage; Redux hydrates from storage on init
- No state persistence for orders or products; refresh fetches from API
- Search & pagination via URL params (HomeScreen matches `/search/:keyword/page/:pageNumber`)

## Build & Deployment

**Frontend build:**
```bash
cd frontend && npm run build
```
Creates `frontend/build/`. In production (`NODE_ENV=production`), backend serves frontend as static assets (see `server.js:38-43`).

**Heroku deploy:** Procfile specifies `web: node backend/server.js`. Heroku postbuild script (in root `package.json:14`) auto-builds frontend before server start.

## Common Gotchas

1. **Backend file imports:** Add `.js` extension (e.g., `import User from './models/userModel.js'`) or require fails.
2. **Frontend proxy:** Frontend dev server proxies unmatched requests to `http://127.0.0.1:5000`. Must run both `npm run dev` or manually start backend on `:5000`.
3. **JWT secret:** `process.env.JWT_SECRET` used in both auth middleware (verify) and user controller (sign). Mismatch breaks auth.
4. **localStorage persistence:** Cart & user info persist across sessions. No server-side session store; tokens are stateless.
5. **Admin routes:** Protected by `isAdmin` flag on user doc. `admin` middleware checks `req.user.isAdmin` after `protect` middleware.
6. **No Redux Toolkit:** Uses classic Redux with action types as constants. Actions are thunks, not slices.

## Project Status

⚠️ **Deprecated:** This is an old Udemy course repo. See [proshop-v2](https://github.com/bradtraversy/proshop-v2) for modern version with Redux Toolkit. Expect outdated packages.
