import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

/**
 * Get path to features.json file
 * @returns {string} Absolute path to features.json
 */
export const getFeaturesFilePath = () => {
  const filePath = process.env.FEATURE_FLAGS_JSON || '/tmp/features.json'
  return filePath
}

/**
 * Read features from JSON file
 * @returns {Promise<Object>} Features object
 * @throws {Error} If file cannot be read or JSON is invalid
 */
export const readFeatures = async () => {
  try {
    const filePath = getFeaturesFilePath()
    const data = await fs.promises.readFile(filePath, 'utf-8')
    return JSON.parse(data)
  } catch (error) {
    if (error.code === 'ENOENT') {
      throw new Error('FILE_READ_ERROR: features.json file not found')
    }
    if (error instanceof SyntaxError) {
      throw new Error('JSON_PARSE_ERROR: features.json contains invalid JSON')
    }
    throw new Error(`FILE_READ_ERROR: ${error.message}`)
  }
}

/**
 * Write features to JSON file atomically (write to temp file, then rename)
 * @param {Object} features - Features object to write
 * @returns {Promise<void>}
 * @throws {Error} If file cannot be written
 */
export const writeFeatures = async (features) => {
  try {
    const filePath = getFeaturesFilePath()
    const dir = path.dirname(filePath)
    const tempFilePath = `${filePath}.tmp.${Date.now()}`

    // Ensure directory exists
    if (!fs.existsSync(dir)) {
      await fs.promises.mkdir(dir, { recursive: true })
    }

    // Write to temporary file
    await fs.promises.writeFile(
      tempFilePath,
      JSON.stringify(features, null, 2),
      'utf-8'
    )

    // Atomic rename
    await fs.promises.rename(tempFilePath, filePath)
  } catch (error) {
    throw new Error(`FILE_WRITE_ERROR: ${error.message}`)
  }
}

/**
 * Get today's date in YYYY-MM-DD format
 * @returns {string} Today's date
 */
export const getTodayDate = () => {
  const today = new Date()
  return today.toISOString().split('T')[0]
}

/**
 * Validate feature ID exists in features object
 * @param {Object} features - Features object
 * @param {string} featureId - Feature ID to check
 * @returns {boolean} True if feature exists
 */
export const featureExists = (features, featureId) => {
  return featureId in features
}

/**
 * Get feature by ID
 * @param {Object} features - Features object
 * @param {string} featureId - Feature ID
 * @returns {Object|null} Feature object or null if not found
 */
export const getFeature = (features, featureId) => {
  if (!featureExists(features, featureId)) {
    return null
  }
  return {
    feature_id: featureId,
    ...features[featureId],
  }
}

/**
 * Check if feature has dependencies and if they are met
 * @param {Object} features - Features object
 * @param {string} featureId - Feature ID to check
 * @returns {Array<string>} Array of warnings (empty if no issues)
 */
export const checkDependencies = (features, featureId) => {
  const feature = features[featureId]
  const warnings = []

  if (!feature.dependencies || feature.dependencies.length === 0) {
    return warnings
  }

  for (const depId of feature.dependencies) {
    const depFeature = features[depId]
    if (!depFeature) {
      warnings.push(
        `Dependency '${depId}' does not exist in features.json.`
      )
    } else if (depFeature.status !== 'Enabled') {
      warnings.push(
        `Dependency '${depId}' is in status '${depFeature.status}', not 'Enabled'. ${featureId} may not function correctly.`
      )
    }
  }

  return warnings
}

/**
 * Validate status value
 * @param {string} status - Status to validate
 * @returns {boolean} True if valid
 */
export const isValidStatus = (status) => {
  return ['Disabled', 'Testing', 'Enabled'].includes(status)
}

/**
 * Validate traffic percentage
 * @param {number} percentage - Percentage to validate
 * @returns {boolean} True if valid (integer 0-100)
 */
export const isValidPercentage = (percentage) => {
  return Number.isInteger(percentage) && percentage >= 0 && percentage <= 100
}

/**
 * Get canonical traffic percentage for a given status
 * @param {string} status - Status (Disabled, Testing, Enabled)
 * @param {number} currentPercentage - Current traffic percentage
 * @returns {number} Canonical traffic percentage
 */
export const getCanonicalTrafficPercentage = (status, currentPercentage) => {
  if (status === 'Disabled') {
    return 0
  }
  if (status === 'Enabled') {
    return 100
  }
  // Testing status: keep current if valid, otherwise use 10 as default
  if (status === 'Testing') {
    if (isValidPercentage(currentPercentage) && currentPercentage >= 1) {
      return currentPercentage
    }
    return 10
  }
  return 10
}
