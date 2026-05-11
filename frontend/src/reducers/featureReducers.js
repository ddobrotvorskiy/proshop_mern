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
export const featureListReducer = (state = { loading: false, features: [] }, action) => {
  switch (action.type) {
    case FEATURE_LIST_REQUEST:
      return { loading: true, features: state.features }
    case FEATURE_LIST_SUCCESS:
      return { loading: false, features: action.payload }
    case FEATURE_LIST_FAIL:
      return { loading: false, error: action.payload, features: [] }
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
  state = { loading: false, success: false, feature: null },
  action
) => {
  switch (action.type) {
    case FEATURE_SET_STATE_REQUEST:
      return { loading: true, success: false, feature: null }
    case FEATURE_SET_STATE_SUCCESS:
      return { loading: false, success: true, feature: action.payload }
    case FEATURE_SET_STATE_FAIL:
      return { loading: false, error: action.payload, success: false, feature: null }
    case FEATURE_RESET:
      return { loading: false, success: false, feature: null }
    default:
      return state
  }
}

/**
 * Feature adjust traffic reducer
 */
export const featureAdjustTrafficReducer = (
  state = { loading: false, success: false, feature: null },
  action
) => {
  switch (action.type) {
    case FEATURE_ADJUST_TRAFFIC_REQUEST:
      return { loading: true, success: false, feature: null }
    case FEATURE_ADJUST_TRAFFIC_SUCCESS:
      return { loading: false, success: true, feature: action.payload }
    case FEATURE_ADJUST_TRAFFIC_FAIL:
      return { loading: false, error: action.payload, success: false, feature: null }
    case FEATURE_RESET:
      return { loading: false, success: false, feature: null }
    default:
      return state
  }
}
