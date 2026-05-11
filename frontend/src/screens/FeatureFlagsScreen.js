import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Table, Button, Form, Alert, Badge, Spinner, Modal } from 'react-bootstrap'
import { listFeatures, setFeatureState, adjustTrafficRollout } from '../actions/featureActions'
import { FEATURE_RESET } from '../constants/featureConstants'

const FeatureFlagsScreen = () => {
  const dispatch = useDispatch()
  const { features, loading, error } = useSelector((state) => state.featureList)
  const {
    loading: stateLoading,
    error: stateError,
    success: stateSuccess,
  } = useSelector((state) => state.featureSetState)
  const {
    loading: trafficLoading,
    error: trafficError,
    success: trafficSuccess,
  } = useSelector((state) => state.featureAdjustTraffic)

  const [statusFilter, setStatusFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [editingFeature, setEditingFeature] = useState(null)
  const [trafficPercentage, setTrafficPercentage] = useState(0)
  const [showModal, setShowModal] = useState(false)

  // Load features on mount and setup auto-refresh
  useEffect(() => {
    dispatch(listFeatures())

    // Setup auto-refresh every 7 seconds
    const interval = setInterval(() => {
      dispatch(listFeatures())
    }, 7000)

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [dispatch])

  // Handle state change success
  useEffect(() => {
    if (stateSuccess) {
      setShowModal(false)
      dispatch({ type: FEATURE_RESET })
    }
  }, [stateSuccess, dispatch])

  // Handle traffic change success
  useEffect(() => {
    if (trafficSuccess) {
      setShowModal(false)
      dispatch({ type: FEATURE_RESET })
    }
  }, [trafficSuccess, dispatch])

  const handleStateChange = (featureId, newState) => {
    setEditingFeature({ featureId, newState })
    setShowModal(true)
  }

  const handleTrafficChange = (feature) => {
    setEditingFeature({
      featureId: feature.feature_id,
      type: 'traffic',
      currentTraffic: feature.traffic_percentage,
    })
    setTrafficPercentage(feature.traffic_percentage)
    setShowModal(true)
  }

  const confirmStateChange = () => {
    if (editingFeature && editingFeature.newState) {
      dispatch(setFeatureState(editingFeature.featureId, editingFeature.newState))
    }
  }

  const confirmTrafficChange = () => {
    if (editingFeature && editingFeature.type === 'traffic') {
      dispatch(
        adjustTrafficRollout(editingFeature.featureId, parseInt(trafficPercentage))
      )
    }
  }

  // Filter features
  const filteredFeatures = features.filter((feature) => {
    const matchStatus = statusFilter === 'all' || feature.status === statusFilter
    const matchSearch =
      feature.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      feature.feature_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      feature.description.toLowerCase().includes(searchTerm.toLowerCase())
    return matchStatus && matchSearch
  })

  const getStatusBadge = (status) => {
    let variant = 'secondary'
    if (status === 'Enabled') variant = 'success'
    if (status === 'Testing') variant = 'warning'
    if (status === 'Disabled') variant = 'danger'
    return <Badge bg={variant}>{status}</Badge>
  }

  const getTrafficColor = (percentage) => {
    if (percentage === 0) return 'danger'
    if (percentage <= 25) return 'info'
    if (percentage <= 75) return 'warning'
    return 'success'
  }

  return (
    <div className="container mt-5 mb-5">
      <h1 className="mb-4">Feature Flags Management</h1>

      {/* Alerts */}
      {error && <Alert variant="danger">{error}</Alert>}
      {stateError && <Alert variant="danger">State Error: {stateError}</Alert>}
      {trafficError && (
        <Alert variant="danger">Traffic Error: {trafficError}</Alert>
      )}
      {(stateSuccess || trafficSuccess) && (
        <Alert variant="success" dismissible onClose={() => {}}>
          Feature updated successfully!
        </Alert>
      )}

      {/* Filters */}
      <div className="row mb-4">
        <div className="col-md-6">
          <Form.Group>
            <Form.Label>Search Features</Form.Label>
            <Form.Control
              type="text"
              placeholder="Search by name, ID, or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </Form.Group>
        </div>
        <div className="col-md-6">
          <Form.Group>
            <Form.Label>Filter by Status</Form.Label>
            <Form.Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="Enabled">Enabled</option>
              <option value="Testing">Testing</option>
              <option value="Disabled">Disabled</option>
            </Form.Select>
          </Form.Group>
        </div>
      </div>

      {/* Summary */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="bg-success text-white p-3 rounded">
            <h5>Enabled</h5>
            <p className="mb-0">
              {features.filter((f) => f.status === 'Enabled').length}
            </p>
          </div>
        </div>
        <div className="col-md-3">
          <div className="bg-warning text-dark p-3 rounded">
            <h5>Testing</h5>
            <p className="mb-0">
              {features.filter((f) => f.status === 'Testing').length}
            </p>
          </div>
        </div>
        <div className="col-md-3">
          <div className="bg-danger text-white p-3 rounded">
            <h5>Disabled</h5>
            <p className="mb-0">
              {features.filter((f) => f.status === 'Disabled').length}
            </p>
          </div>
        </div>
        <div className="col-md-3">
          <div className="bg-info text-white p-3 rounded">
            <h5>Total</h5>
            <p className="mb-0">{features.length}</p>
          </div>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </div>
      )}

      {/* Features Table */}
      {!loading && filteredFeatures.length > 0 && (
        <div className="table-responsive">
          <Table striped bordered hover className="mb-0">
            <thead className="table-dark">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Status</th>
                <th>Traffic %</th>
                <th>Modified</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredFeatures.map((feature) => (
                <tr key={feature.feature_id}>
                  <td className="fw-bold">{feature.feature_id}</td>
                  <td>
                    <div>{feature.name}</div>
                    <small className="text-muted">{feature.description}</small>
                  </td>
                  <td>{getStatusBadge(feature.status)}</td>
                  <td>
                    <div
                      className={`bg-${getTrafficColor(
                        feature.traffic_percentage
                      )} text-white p-2 rounded text-center`}
                    >
                      {feature.traffic_percentage}%
                    </div>
                  </td>
                  <td>{feature.last_modified}</td>
                  <td>
                    <div className="btn-group btn-group-sm" role="group">
                      <Button
                        variant="outline-primary"
                        size="sm"
                        onClick={() =>
                          handleStateChange(
                            feature.feature_id,
                            feature.status === 'Disabled' ? 'Testing' : 'Disabled'
                          )
                        }
                        disabled={stateLoading}
                      >
                        Toggle
                      </Button>
                      {feature.status === 'Testing' && (
                        <Button
                          variant="outline-info"
                          size="sm"
                          onClick={() => handleTrafficChange(feature)}
                          disabled={trafficLoading}
                        >
                          Traffic
                        </Button>
                      )}
                      <Button
                        variant="outline-success"
                        size="sm"
                        onClick={() => handleStateChange(feature.feature_id, 'Enabled')}
                        disabled={feature.status === 'Enabled' || stateLoading}
                      >
                        Enable
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}

      {/* No results */}
      {!loading && filteredFeatures.length === 0 && (
        <Alert variant="info">
          No features found matching your criteria.
        </Alert>
      )}

      {/* Modal for state change confirmation */}
      <Modal show={showModal && editingFeature && !editingFeature.type} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Change Feature Status</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {editingFeature && (
            <p>
              Change status of <strong>{editingFeature.featureId}</strong> to{' '}
              <strong>{editingFeature.newState}</strong>?
            </p>
          )}
          {editingFeature?.newState === 'Testing' && (
            <Alert variant="info">
              When transitioning to Testing, traffic will be set to 10% by default.
            </Alert>
          )}
          {editingFeature?.newState === 'Enabled' && (
            <Alert variant="info">
              When transitioning to Enabled, traffic will be set to 100%.
            </Alert>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={confirmStateChange}
            disabled={stateLoading}
          >
            {stateLoading ? 'Updating...' : 'Confirm'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Modal for traffic adjustment */}
      <Modal
        show={showModal && editingFeature && editingFeature.type === 'traffic'}
        onHide={() => setShowModal(false)}
      >
        <Modal.Header closeButton>
          <Modal.Title>Adjust Traffic Percentage</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {editingFeature && (
            <>
              <p>
                Adjust traffic for <strong>{editingFeature.featureId}</strong>
              </p>
              <Form.Group>
                <Form.Label>Traffic Percentage ({trafficPercentage}%)</Form.Label>
                <Form.Range
                  min={0}
                  max={100}
                  step={5}
                  value={trafficPercentage}
                  onChange={(e) => setTrafficPercentage(e.target.value)}
                />
              </Form.Group>
              <Form.Group className="mt-3">
                <Form.Label>Or enter exact value:</Form.Label>
                <Form.Control
                  type="number"
                  min={0}
                  max={100}
                  value={trafficPercentage}
                  onChange={(e) => setTrafficPercentage(e.target.value)}
                />
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={confirmTrafficChange}
            disabled={trafficLoading}
          >
            {trafficLoading ? 'Updating...' : 'Confirm'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Last updated info */}
      <div className="mt-4 text-muted small">
        <p>Last updated: {new Date().toLocaleTimeString()}</p>
        <p>Auto-refreshing every 7 seconds</p>
      </div>
    </div>
  )
}

export default FeatureFlagsScreen
