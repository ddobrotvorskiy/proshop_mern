import asyncHandler from 'express-async-handler'
import {
  readFeatures,
  writeFeatures,
  getTodayDate,
  featureExists,
  getFeature,
  checkDependencies,
  isValidStatus,
  isValidPercentage,
  getCanonicalTrafficPercentage,
} from '../utils/featureFlags.js'

// @desc    Get all features
// @route   GET /api/features
// @access  Private/Admin
const getAllFeatures = asyncHandler(async (req, res) => {
  try {
    const features = await readFeatures()
    const featuresArray = Object.entries(features).map(([featureId, data]) => ({
      feature_id: featureId,
      ...data,
    }))
    res.json({ features: featuresArray })
  } catch (error) {
    res.status(500)
    throw new Error(error.message)
  }
})

// @desc    Get a single feature by ID
// @route   GET /api/features/:featureId
// @access  Private/Admin
const getFeatureById = asyncHandler(async (req, res) => {
  try {
    const { featureId } = req.params
    const features = await readFeatures()

    if (!featureExists(features, featureId)) {
      res.status(404)
      throw new Error(
        `FEATURE_NOT_FOUND: No feature with ID '${featureId}' exists in features.json.`
      )
    }

    const feature = getFeature(features, featureId)
    res.json(feature)
  } catch (error) {
    res.status(res.statusCode === 404 ? 404 : 500)
    throw new Error(error.message)
  }
})

// @desc    Set feature state (Disabled, Testing, Enabled)
// @route   PATCH /api/features/:featureId/state
// @access  Private/Admin
const setFeatureState = asyncHandler(async (req, res) => {
  try {
    const { featureId } = req.params
    const { state } = req.body

    // Validate state parameter
    if (!state) {
      res.status(400)
      throw new Error('state parameter is required')
    }

    if (!isValidStatus(state)) {
      res.status(400)
      throw new Error(
        `INVALID_STATE: State '${state}' is not valid. Must be one of: Disabled, Testing, Enabled (case-sensitive).`
      )
    }

    const features = await readFeatures()

    // Check if feature exists
    if (!featureExists(features, featureId)) {
      res.status(404)
      throw new Error(
        `FEATURE_NOT_FOUND: No feature with ID '${featureId}' exists in features.json.`
      )
    }

    const feature = features[featureId]

    // Update feature state
    feature.status = state
    feature.traffic_percentage = getCanonicalTrafficPercentage(
      state,
      feature.traffic_percentage
    )
    feature.last_modified = getTodayDate()

    // Check dependencies if transitioning to Testing or Enabled
    let warnings = []
    if (state === 'Testing' || state === 'Enabled') {
      warnings = checkDependencies(features, featureId)
    }

    // Write updated features back to file
    await writeFeatures(features)

    // Return updated feature
    const result = getFeature(features, featureId)
    if (warnings.length > 0) {
      result.warnings = warnings
    }
    res.json(result)
  } catch (error) {
    if (!res.statusCode || res.statusCode === 200) {
      res.status(500)
    }
    throw new Error(error.message)
  }
})

// @desc    Adjust traffic percentage for a Testing feature
// @route   PATCH /api/features/:featureId/traffic
// @access  Private/Admin
const adjustTrafficRollout = asyncHandler(async (req, res) => {
  try {
    const { featureId } = req.params
    const { percentage } = req.body

    // Validate percentage parameter
    if (percentage === undefined || percentage === null) {
      res.status(400)
      throw new Error('percentage parameter is required')
    }

    if (!isValidPercentage(percentage)) {
      res.status(400)
      throw new Error(
        `INVALID_PERCENTAGE: percentage must be an integer from 0 to 100, got ${percentage}`
      )
    }

    const features = await readFeatures()

    // Check if feature exists
    if (!featureExists(features, featureId)) {
      res.status(404)
      throw new Error(
        `FEATURE_NOT_FOUND: No feature with ID '${featureId}' exists in features.json.`
      )
    }

    const feature = features[featureId]

    // Validate that feature is in Testing status
    if (feature.status !== 'Testing') {
      res.status(400)
      throw new Error(
        `WRONG_STATUS_FOR_ROLLOUT: adjust_traffic_rollout can only be called on features with status 'Testing'. '${featureId}' is currently '${feature.status}'. Use set_feature_state to change its status first.`
      )
    }

    // Update traffic percentage
    feature.traffic_percentage = percentage
    feature.last_modified = getTodayDate()

    // Write updated features back to file
    await writeFeatures(features)

    // Return updated feature with hint if appropriate
    const result = getFeature(features, featureId)

    if (percentage === 0) {
      result.hint =
        "Traffic is now 0%. Consider using set_feature_state to transition to 'Disabled' instead."
    } else if (percentage === 100) {
      result.hint =
        "Traffic is now 100%. Consider using set_feature_state to promote to 'Enabled'."
    }

    res.json(result)
  } catch (error) {
    if (!res.statusCode || res.statusCode === 200) {
      res.status(500)
    }
    throw new Error(error.message)
  }
})

export { getAllFeatures, getFeatureById, setFeatureState, adjustTrafficRollout }
