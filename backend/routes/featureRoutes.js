import express from 'express'
const router = express.Router()
import {
  getAllFeatures,
  getFeatureById,
  setFeatureState,
  adjustTrafficRollout,
} from '../controllers/featureController.js'
import { protect, admin } from '../middleware/authMiddleware.js'

// All feature flag routes require admin authentication
router.use(protect, admin)

// Get all features
router.route('/').get(getAllFeatures)

// Get single feature by ID
router.route('/:featureId').get(getFeatureById)

// Set feature state (Disabled, Testing, Enabled)
router.route('/:featureId/state').patch(setFeatureState)

// Adjust traffic percentage for Testing features
router.route('/:featureId/traffic').patch(adjustTrafficRollout)

export default router
