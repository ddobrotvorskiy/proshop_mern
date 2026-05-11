# Feature Flags Testing Guide

## Quick Start

### 1. Prerequisites

✓ Both servers are running:
- Backend: `http://localhost:5000` (port 5000)
- Frontend: `http://localhost:3000` (port 3000)

✓ Database is connected:
- MongoDB running on `mongodb://localhost:27017/proshop`

✓ Sample data imported:
```bash
npm run data:import
```

This creates:
- **Admin user:** admin@example.com / 123456
- **Regular user:** john@example.com / 123456
- Sample products, orders, reviews
- Features file at: `/tmp/features.json`

### 2. Access Feature Flags Dashboard

#### Step 1: Open Browser
Go to: **http://localhost:3000**

#### Step 2: Login as Admin
Click "Sign In" and use:
- Email: `admin@example.com`
- Password: `123456`

#### Step 3: Navigate to Feature Flags
In the header, click:
**Admin** → **Feature Flags**

Or go directly to:
**http://localhost:3000/admin/feature-flags**

### 3. What You'll See

#### Features Table
- **25 feature flags** from the specification
- **Columns:**
  - ID (e.g., `search_v2`)
  - Name (e.g., "New Search Algorithm")
  - Status (Disabled/Testing/Enabled)
  - Traffic % (0-100)
  - Modified (YYYY-MM-DD)
  - Actions (buttons)

#### Summary Cards
- **Enabled:** Count of Enabled features
- **Testing:** Count of Testing features
- **Disabled:** Count of Disabled features
- **Total:** Total feature count (25)

#### Filters
- Filter by Status (All/Enabled/Testing/Disabled)
- Search by ID, name, or description

#### Actions
For each feature:
1. **Toggle Button** - Switch between Disabled ↔ Testing
2. **Traffic Button** - Adjust traffic % (only for Testing)
3. **Enable Button** - Promote to Enabled

---

## Testing Scenarios

### Scenario 1: Enable a Feature

1. Find a **Disabled** feature (e.g., `dark_mode`)
2. Click **Enable** button
3. Confirm in modal
4. Feature status changes to **Enabled**
5. Traffic % becomes **100%**

### Scenario 2: Start a Canary Test

1. Find an **Enabled** feature (e.g., `paypal_express_buttons`)
2. Click **Toggle** button
3. Confirm state change to **Testing**
4. Feature status is now **Testing**
5. Traffic % defaults to **10%**

### Scenario 3: Increase Traffic During Test

1. Find a **Testing** feature (e.g., `dark_mode`)
2. Click **Traffic** button (only visible for Testing)
3. Adjust slider or enter exact value (e.g., 50)
4. Click **Confirm**
5. Traffic % updates to **50%**
6. Last Modified date updates

### Scenario 4: Disable a Feature

1. Click **Toggle** on any feature
2. Choose state **Disabled**
3. Feature status becomes **Disabled**
4. Traffic % becomes **0%**

### Scenario 5: Check Dependencies

1. Find `semantic_search` (depends on `search_v2`)
2. Try to enable it
3. See warning: "Dependency 'search_v2' is in status 'Testing', not 'Enabled'"
4. The operation still succeeds with warning

### Scenario 6: Search and Filter

1. Type in search box: "search"
2. Only search-related features appear
3. Filter by Status: "Testing"
4. Only Testing features appear
5. Clear search/filter to see all

### Scenario 7: Auto-Refresh

1. Keep page open
2. In another tab/window, access same page and change a feature
3. After ~7 seconds, first page auto-refreshes
4. Changes from other admin visible

---

## Backend API Testing

### Test with curl

#### Get All Features
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:5000/api/features
```

#### Get Single Feature
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:5000/api/features/dark_mode
```

#### Set Feature State
```bash
curl -X PATCH \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"state":"Testing"}' \
  http://localhost:5000/api/features/dark_mode/state
```

#### Adjust Traffic Percentage
```bash
curl -X PATCH \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"percentage":50}' \
  http://localhost:5000/api/features/dark_mode/traffic
```

### Get Admin Token

1. Login to frontend as admin
2. Open DevTools (F12)
3. Go to Storage → Local Storage
4. Find `userInfo` → token value
5. Copy token and use in curl requests

---

## Troubleshooting

### Page Shows 404

**Problem:** Page not found when accessing `/admin/feature-flags`

**Solution:**
- Check if React frontend is running on port 3000
- Check browser console for errors (F12)
- Try refreshing page (Ctrl+Shift+R)
- Check if you're logged in as admin

### Cannot See Feature Flags Link

**Problem:** "Feature Flags" link missing from Admin menu

**Solution:**
- Make sure you're logged in as **admin user** (not regular user)
- Admin user has `isAdmin: true` in database
- Clear browser cache and try again

### API Returns 401 Unauthorized

**Problem:** API calls fail with 401 error

**Solution:**
- Make sure you have valid Bearer token
- Token might have expired
- Login again and get fresh token
- Check Authorization header format: `Authorization: Bearer {token}`

### Changes Not Persisting

**Problem:** After making changes, they revert on refresh

**Solution:**
- Check if `/tmp/features.json` is writable
- Check backend logs for write errors
- Verify `FEATURE_FLAGS_JSON` environment variable
- Try manually checking file: `cat /tmp/features.json`

### Features.json File Not Found

**Problem:** Backend error: "FILE_READ_ERROR"

**Solution:**
- Initialize features file:
  ```bash
  cp docs/M3/features.json /tmp/features.json
  ```
- Check if file has correct permissions:
  ```bash
  ls -la /tmp/features.json
  chmod 644 /tmp/features.json
  ```

---

## Expected Feature States (Initial)

After `npm run data:import`, features have these initial states:

| Feature ID | Initial Status | Traffic | Notes |
|-----------|------------------|---------|-------|
| search_v2 | Testing | 15% | canary deployment |
| semantic_search | Disabled | 0% | depends on search_v2 |
| search_autosuggest | Testing | 25% | autosuggest feature |
| cart_redesign | Testing | 10% | A/B test |
| save_for_later | Disabled | 0% | depends on cart_redesign |
| guest_cart_persistence | **Enabled** | 100% | kill switch pattern |
| express_checkout | Disabled | 0% | depends on cart_persistence |
| multi_step_checkout_v2 | Testing | 20% | A/B test |
| gift_message | Disabled | 0% | checkout feature |
| paypal_express_buttons | **Enabled** | 100% | kill switch pattern |
| apple_pay | Disabled | 0% | depends on stripe |
| stripe_alternative | Testing | 5% | canary deployment |
| product_recommendations | Testing | 30% | A/B test |
| recently_viewed | **Enabled** | 100% | kill switch pattern |
| infinite_scroll | Disabled | 0% | mobile feature |
| admin_dashboard_v2 | Disabled | 0% | admin only |
| admin_bulk_actions | Disabled | 0% | depends on dashboard_v2 |
| admin_advanced_filters | Testing | 100% | admin only |
| reviews_moderation | Disabled | 0% | moderation queue |
| photo_reviews | Disabled | 0% | depends on moderation |
| verified_purchase_badge | **Enabled** | 100% | kill switch pattern |
| image_lazy_loading | **Enabled** | 100% | kill switch pattern |
| code_splitting_optimisation | Testing | 50% | performance |
| dark_mode | Testing | 20% | A/B test |
| guest_checkout | Disabled | 0% | new feature |

---

## Common Use Cases

### As a Product Manager: Start Canary Deployment

1. Go to Feature Flags dashboard
2. Find new feature (status: Disabled)
3. Click Enable to set to 100%
4. Then click Toggle to set to Testing
5. Set traffic to 5%
6. Monitor for errors
7. After 48h: increase to 25%
8. Continue until 100%

### As a QA Lead: Verify Feature Rollback

1. Feature is causing issues
2. Go to Feature Flags
3. Find feature (status: Testing)
4. Click Toggle to Disabled
5. Feature immediately disabled (no deploy needed)
6. Check error rate drops

### As an Engineer: Test Dependencies

1. Feature depends on another feature
2. Go to dashboard
3. Try to enable dependent feature
4. See dependency warning
5. Confirm both features work together

---

## File Locations

- **Frontend:** `frontend/src/screens/FeatureFlagsScreen.js`
- **Backend:** `backend/controllers/featureController.js`
- **Routes:** `backend/routes/featureRoutes.js`
- **Utils:** `backend/utils/featureFlags.js`
- **Redux Actions:** `frontend/src/actions/featureActions.js`
- **Redux Reducers:** `frontend/src/reducers/featureReducers.js`
- **Redux Constants:** `frontend/src/constants/featureConstants.js`
- **Data File:** `/tmp/features.json` (configurable via `FEATURE_FLAGS_JSON` env)

---

## Next: MCP Server

Once you're comfortable with the UI and API, the next step is building an MCP server that exposes these three tools:

1. **get_feature_info** - Retrieve feature details
2. **set_feature_state** - Change feature state
3. **adjust_traffic_rollout** - Adjust traffic percentage

The MCP server will use these same REST API endpoints under the hood.

---

**Happy Testing!** 🚀

For issues or questions, check `FEATURE_FLAGS_IMPLEMENTATION.md` for architecture details.
