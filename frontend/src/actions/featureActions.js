import axios from 'axios'
import {
  FEATURE_LIST_REQUEST,
  FEATURE_LIST_SUCCESS,
  FEATURE_LIST_FAIL,
  FEATURE_DETAILS_REQUEST,
  FEATURE_DETAILS_SUCCESS,
  FEATURE_DETAILS_FAIL,
  FEATURE_SET_STATE_REQUEST,
  FEATURE_SET_STATE_SUCCESS,
  FEATURE_SET_STATE_FAIL,
  FEATURE_ADJUST_TRAFFIC_REQUEST,
  FEATURE_ADJUST_TRAFFIC_SUCCESS,
  FEATURE_ADJUST_TRAFFIC_FAIL,
} from '../constants/featureConstants'

/**
 * Get all feature flags
 */
export const listFeatures = () => async (dispatch, getState) => {
  try {
    dispatch({ type: FEATURE_LIST_REQUEST })

    const {
      userLogin: { userInfo },
    } = getState()

    const config = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${userInfo.token}`,
      },
    }

    const { data } = await axios.get('/api/features', config)

    dispatch({
      type: FEATURE_LIST_SUCCESS,
      payload: data.features,
    })
  } catch (error) {
    dispatch({
      type: FEATURE_LIST_FAIL,
      payload:
        error.response && error.response.data.message
          ? error.response.data.message
          : error.message,
    })
  }
}

/**
 * Get single feature by ID
 */
export const getFeatureDetails = (featureId) => async (dispatch, getState) => {
  try {
    dispatch({ type: FEATURE_DETAILS_REQUEST })

    const {
      userLogin: { userInfo },
    } = getState()

    const config = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${userInfo.token}`,
      },
    }

    const { data } = await axios.get(`/api/features/${featureId}`, config)

    dispatch({
      type: FEATURE_DETAILS_SUCCESS,
      payload: data,
    })
  } catch (error) {
    dispatch({
      type: FEATURE_DETAILS_FAIL,
      payload:
        error.response && error.response.data.message
          ? error.response.data.message
          : error.message,
    })
  }
}

/**
 * Set feature state (Disabled, Testing, Enabled)
 */
export const setFeatureState = (featureId, state) => async (
  dispatch,
  getState
) => {
  try {
    dispatch({ type: FEATURE_SET_STATE_REQUEST })

    const {
      userLogin: { userInfo },
    } = getState()

    const config = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${userInfo.token}`,
      },
    }

    const { data } = await axios.patch(
      `/api/features/${featureId}/state`,
      { state },
      config
    )

    dispatch({
      type: FEATURE_SET_STATE_SUCCESS,
      payload: data,
    })

    // Refresh the features list
    dispatch(listFeatures())
  } catch (error) {
    dispatch({
      type: FEATURE_SET_STATE_FAIL,
      payload:
        error.response && error.response.data.message
          ? error.response.data.message
          : error.message,
    })
  }
}

/**
 * Adjust traffic percentage for a Testing feature
 */
export const adjustTrafficRollout = (featureId, percentage) => async (
  dispatch,
  getState
) => {
  try {
    dispatch({ type: FEATURE_ADJUST_TRAFFIC_REQUEST })

    const {
      userLogin: { userInfo },
    } = getState()

    const config = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${userInfo.token}`,
      },
    }

    const { data } = await axios.patch(
      `/api/features/${featureId}/traffic`,
      { percentage },
      config
    )

    dispatch({
      type: FEATURE_ADJUST_TRAFFIC_SUCCESS,
      payload: data,
    })

    // Refresh the features list
    dispatch(listFeatures())
  } catch (error) {
    dispatch({
      type: FEATURE_ADJUST_TRAFFIC_FAIL,
      payload:
        error.response && error.response.data.message
          ? error.response.data.message
          : error.message,
    })
  }
}
