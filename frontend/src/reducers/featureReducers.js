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
  FEATURE_RESET,
} from '../constants/featureConstants'

/**
 * Feature list reducer - all features
 */
export const featureListReducer = (state = { features: [] }, action) => {
  switch (action.type) {
    case FEATURE_LIST_REQUEST:
      return { loading: true, features: [] }
    case FEATURE_LIST_SUCCESS:
      return { loading: false, features: action.payload }
    case FEATURE_LIST_FAIL:
      return { loading: false, error: action.payload }
    default:
      return state
  }
}

/**
 * Feature details reducer - single feature
 */
export const featureDetailsReducer = (state = { feature: {} }, action) => {
  switch (action.type) {
    case FEATURE_DETAILS_REQUEST:
      return { loading: true, feature: {} }
    case FEATURE_DETAILS_SUCCESS:
      return { loading: false, feature: action.payload }
    case FEATURE_DETAILS_FAIL:
      return { loading: false, error: action.payload }
    default:
      return state
  }
}

/**
 * Feature set state reducer
 */
export const featureSetStateReducer = (
  state = { loading: false, success: false },
  action
) => {
  switch (action.type) {
    case FEATURE_SET_STATE_REQUEST:
      return { loading: true }
    case FEATURE_SET_STATE_SUCCESS:
      return { loading: false, success: true, feature: action.payload }
    case FEATURE_SET_STATE_FAIL:
      return { loading: false, error: action.payload }
    case FEATURE_RESET:
      return { loading: false, success: false }
    default:
      return state
  }
}

/**
 * Feature adjust traffic reducer
 */
export const featureAdjustTrafficReducer = (
  state = { loading: false, success: false },
  action
) => {
  switch (action.type) {
    case FEATURE_ADJUST_TRAFFIC_REQUEST:
      return { loading: true }
    case FEATURE_ADJUST_TRAFFIC_SUCCESS:
      return { loading: false, success: true, feature: action.payload }
    case FEATURE_ADJUST_TRAFFIC_FAIL:
      return { loading: false, error: action.payload }
    case FEATURE_RESET:
      return { loading: false, success: false }
    default:
      return state
  }
}
