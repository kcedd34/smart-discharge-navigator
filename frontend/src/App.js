import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './index.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [patients, setPatients] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [riskAssessment, setRiskAssessment] = useState(null);
  const [dischargePlan, setDischargePlan] = useState(null);
  const [showRiskModal, setShowRiskModal] = useState(false);
  const [showPlanModal, setShowPlanModal] = useState(false);

  // AI Agent State
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'chat'
  const [aiStatus, setAiStatus] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatPatientId, setChatPatientId] = useState('');
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [showAiModal, setShowAiModal] = useState(false);
  const [aiAnalysisLoading, setAiAnalysisLoading] = useState(false);
  const [aiDischargePlan, setAiDischargePlan] = useState(null);
  const [showAiPlanModal, setShowAiPlanModal] = useState(false);
  const [aiPlanLoading, setAiPlanLoading] = useState(false);
  // Comparison state
  const [compareMode, setCompareMode] = useState(false);
  const [selectedForCompare, setSelectedForCompare] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [compareLoading, setCompareLoading] = useState(false);

  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchData();
    fetchAiStatus();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [patientsRes, statsRes] = await Promise.all([
        axios.get(`${API_URL}/api/v1/patients`),
        axios.get(`${API_URL}/api/v1/statistics`)
      ]);
      setPatients(patientsRes.data);
      setStatistics(statsRes.data);
    } catch (err) {
      setError('Failed to load data. Please ensure the backend is running.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAiStatus = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/v1/ai/status`);
      setAiStatus(res.data);
    } catch (err) {
      console.error('AI status check failed:', err);
      setAiStatus({ ai_available: false, mode: 'unavailable' });
    }
  };

  const viewRiskAssessment = async (patient) => {
    try {
      setSelectedPatient(patient);
      const response = await axios.get(
        `${API_URL}/api/v1/patients/${patient.id}/risk-assessment`
      );
      setRiskAssessment(response.data);
      setShowRiskModal(true);
    } catch (err) {
      alert('Failed to load risk assessment');
      console.error(err);
    }
  };

  const generateDischargePlan = async (patient) => {
    try {
      setSelectedPatient(patient);
      const response = await axios.post(
        `${API_URL}/api/v1/patients/${patient.id}/discharge-plan`
      );
      setDischargePlan(response.data);
      setShowPlanModal(true);
      fetchData();
    } catch (err) {
      alert('Failed to generate discharge plan');
      console.error(err);
    }
  };

  // ── AI Agent Functions ──

  const viewAiAnalysis = async (patient) => {
    try {
      setSelectedPatient(patient);
      setAiAnalysisLoading(true);
      setShowAiModal(true);
      const response = await axios.get(
        `${API_URL}/api/v1/patients/${patient.id}/ai-analysis`
      );
      setAiAnalysis(response.data);
    } catch (err) {
      alert('Failed to load AI analysis');
      console.error(err);
      setShowAiModal(false);
    } finally {
      setAiAnalysisLoading(false);
    }
  };

  const generateAiDischargePlan = async (patient) => {
    try {
      setSelectedPatient(patient);
      setAiPlanLoading(true);
      setShowAiPlanModal(true);
      const response = await axios.post(
        `${API_URL}/api/v1/patients/${patient.id}/ai-discharge-plan`
      );
      setAiDischargePlan(response.data);
    } catch (err) {
      alert('Failed to generate AI discharge plan');
      console.error(err);
      setShowAiPlanModal(false);
    } finally {
      setAiPlanLoading(false);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;
    const userMessage = chatInput.trim();
    setChatInput('');

    const newMessages = [...chatMessages, { role: 'user', content: userMessage, timestamp: new Date().toISOString() }];
    setChatMessages(newMessages);
    setChatLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/v1/ai/chat`, {
        message: userMessage,
        patient_id: chatPatientId || null,
        conversation_history: newMessages.slice(-10)
      });

      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        sources: response.data.sources,
        ai_powered: response.data.ai_powered,
        confidence: response.data.confidence
      }]);
    } catch (err) {
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: '❌ Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        ai_powered: false
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleCompareToggle = (patientId) => {
    setSelectedForCompare(prev =>
      prev.includes(patientId)
        ? prev.filter(id => id !== patientId)
        : [...prev, patientId]
    );
  };

  const runComparison = async () => {
    if (selectedForCompare.length < 2) {
      alert('Select at least 2 patients to compare');
      return;
    }
    setCompareLoading(true);
    setShowCompareModal(true);
    try {
      const response = await axios.post(`${API_URL}/api/v1/ai/compare-patients`, {
        patient_ids: selectedForCompare
      });
      setComparisonResult(response.data);
    } catch (err) {
      alert('Failed to compare patients');
      setShowCompareModal(false);
    } finally {
      setCompareLoading(false);
    }
  };

  const closeModals = () => {
    setShowRiskModal(false);
    setShowPlanModal(false);
    setShowAiModal(false);
    setShowAiPlanModal(false);
    setShowCompareModal(false);
    setSelectedPatient(null);
    setRiskAssessment(null);
    setDischargePlan(null);
    setAiAnalysis(null);
    setAiDischargePlan(null);
    setComparisonResult(null);
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'HIGH': return 'risk-high';
      case 'MODERATE': return 'risk-moderate';
      case 'LOW': return 'risk-low';
      default: return '';
    }
  };

  const getPriorityClass = (priority) => {
    switch (priority) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return '';
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div>
            <h1>🏥 Smart Discharge Navigator</h1>
            <p>AI Agent-Powered Hospital Readmission Risk Assessment & Discharge Planning</p>
          </div>
          {aiStatus && (
            <div className={`ai-status-badge ${aiStatus.ai_available ? 'ai-active' : 'ai-fallback'}`}>
              <span className="ai-dot"></span>
              {aiStatus.ai_available ? `🤖 AI Agent: ${aiStatus.model}` : '⚙️ Rule-Based Mode'}
            </div>
          )}
        </div>

        <nav className="tab-nav">
          <button
            className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Patient Dashboard
          </button>
          <button
            className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            💬 AI Agent Chat
          </button>
        </nav>
      </header>

      <main className="main-content">
        {loading && <div className="loading">Loading...</div>}
        {error && <div className="error">{error}</div>}

        {/* ════════════ DASHBOARD TAB ════════════ */}
        {activeTab === 'dashboard' && !loading && !error && statistics && (
          <>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Total Patients</h3>
                <div className="value">{statistics.total_patients}</div>
              </div>
              <div className="stat-card">
                <h3>High Risk</h3>
                <div className="value" style={{color: '#dc2626'}}>
                  {statistics.risk_distribution.high}
                </div>
              </div>
              <div className="stat-card">
                <h3>Moderate Risk</h3>
                <div className="value" style={{color: '#ea580c'}}>
                  {statistics.risk_distribution.moderate}
                </div>
              </div>
              <div className="stat-card">
                <h3>Low Risk</h3>
                <div className="value" style={{color: '#059669'}}>
                  {statistics.risk_distribution.low}
                </div>
              </div>
              <div className="stat-card">
                <h3>Avg Risk Score</h3>
                <div className="value">{statistics.average_risk_score.toFixed(2)}</div>
              </div>
              <div className="stat-card">
                <h3>With Discharge Plan</h3>
                <div className="value">
                  {statistics.discharge_plan_coverage.toFixed(0)}%
                </div>
              </div>
            </div>

            <div className="patient-list">
              <div className="patient-list-header">
                <h2>Patient Risk Dashboard</h2>
                <div className="compare-controls">
                  <button
                    className={`btn ${compareMode ? 'btn-warning' : 'btn-secondary'}`}
                    onClick={() => { setCompareMode(!compareMode); setSelectedForCompare([]); }}
                  >
                    {compareMode ? '✕ Cancel Compare' : '🔍 Compare Patients'}
                  </button>
                  {compareMode && selectedForCompare.length >= 2 && (
                    <button className="btn btn-ai" onClick={runComparison}>
                      🤖 AI Compare ({selectedForCompare.length})
                    </button>
                  )}
                </div>
              </div>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      {compareMode && <th>Select</th>}
                      <th>Patient Name</th>
                      <th>Age</th>
                      <th>Gender</th>
                      <th>Risk Score</th>
                      <th>Risk Level</th>
                      <th>Recent Admissions</th>
                      <th>Active Conditions</th>
                      <th>Discharge Plan</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {patients.map((patient) => (
                      <tr key={patient.id} className={selectedForCompare.includes(patient.id) ? 'row-selected' : ''}>
                        {compareMode && (
                          <td>
                            <input
                              type="checkbox"
                              checked={selectedForCompare.includes(patient.id)}
                              onChange={() => handleCompareToggle(patient.id)}
                            />
                          </td>
                        )}
                        <td>{patient.name}</td>
                        <td>{patient.age}</td>
                        <td>{patient.gender}</td>
                        <td>
                          <strong>{patient.risk_score.toFixed(2)}</strong>
                        </td>
                        <td>
                          <span className={`risk-badge ${getRiskColor(patient.risk_level)}`}>
                            {patient.risk_level}
                          </span>
                        </td>
                        <td>{patient.recent_admissions_count}</td>
                        <td>{patient.active_conditions_count}</td>
                        <td>{patient.has_discharge_plan ? '✓ Yes' : '✗ No'}</td>
                        <td className="actions-cell">
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => viewRiskAssessment(patient)}
                          >
                            View Risk
                          </button>
                          <button
                            className="btn btn-ai btn-sm"
                            onClick={() => viewAiAnalysis(patient)}
                            title="AI-Powered Analysis"
                          >
                            🤖 AI Analysis
                          </button>
                          <button
                            className="btn btn-primary btn-sm"
                            onClick={() => generateDischargePlan(patient)}
                          >
                            Generate Plan
                          </button>
                          <button
                            className="btn btn-ai-plan btn-sm"
                            onClick={() => generateAiDischargePlan(patient)}
                            title="AI-Powered Discharge Plan"
                          >
                            🤖 AI Plan
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* ════════════ AI CHAT TAB ════════════ */}
        {activeTab === 'chat' && (
          <div className="chat-container">
            <div className="chat-sidebar">
              <h3>🤖 AI Clinical Agent</h3>
              <p className="chat-description">
                Ask questions about patients, readmission risks, discharge planning, or clinical insights.
              </p>
              <div className="chat-context">
                <label>Patient Context (optional):</label>
                <select
                  value={chatPatientId}
                  onChange={(e) => setChatPatientId(e.target.value)}
                >
                  <option value="">All patients</option>
                  {patients.map(p => (
                    <option key={p.id} value={p.id}>{p.name} (ID: {p.id})</option>
                  ))}
                </select>
              </div>
              <div className="chat-suggestions">
                <h4>Suggested Questions:</h4>
                {[
                  'Which patients are at highest readmission risk?',
                  'What are the common risk factors across all patients?',
                  'Recommend a discharge plan for the highest-risk patient',
                  'Are there any drug interactions I should watch for?',
                  'Summarize the clinical profile of this patient'
                ].map((q, i) => (
                  <button key={i} className="suggestion-btn" onClick={() => { setChatInput(q); }}>
                    {q}
                  </button>
                ))}
              </div>
            </div>

            <div className="chat-main">
              <div className="chat-messages">
                {chatMessages.length === 0 && (
                  <div className="chat-welcome">
                    <div className="welcome-icon">🤖</div>
                    <h3>Smart Discharge Navigator AI Agent</h3>
                    <p>I'm your clinical AI assistant. I can analyze FHIR patient data, assess readmission risks, and help with discharge planning.</p>
                    <p className="welcome-hint">Type a question below or select a suggested question from the sidebar.</p>
                  </div>
                )}
                {chatMessages.map((msg, idx) => (
                  <div key={idx} className={`chat-message ${msg.role}`}>
                    <div className="message-avatar">
                      {msg.role === 'user' ? '👤' : '🤖'}
                    </div>
                    <div className="message-content">
                      <div className="message-header">
                        <span className="message-role">{msg.role === 'user' ? 'You' : 'AI Agent'}</span>
                        {msg.ai_powered !== undefined && (
                          <span className={`ai-badge-small ${msg.ai_powered ? 'badge-ai' : 'badge-rule'}`}>
                            {msg.ai_powered ? '🤖 AI-Powered' : '⚙️ Rule-Based'}
                          </span>
                        )}
                      </div>
                      <div className="message-text">{msg.content}</div>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="message-sources">
                          <strong>Sources:</strong> {msg.sources.join(' · ')}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="chat-message assistant">
                    <div className="message-avatar">🤖</div>
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span><span></span><span></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              <div className="chat-input-area">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendChatMessage()}
                  placeholder="Ask the AI Agent about patients, risks, discharge plans..."
                  disabled={chatLoading}
                  className="chat-input"
                />
                <button
                  onClick={sendChatMessage}
                  disabled={chatLoading || !chatInput.trim()}
                  className="btn btn-ai chat-send-btn"
                >
                  {chatLoading ? '⏳' : '➤'} Send
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ════════════ RISK ASSESSMENT MODAL ════════════ */}
        {showRiskModal && riskAssessment && (
          <div className="modal-overlay" onClick={closeModals}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Risk Assessment - {selectedPatient?.name}</h2>
                <span className="badge-rule-based">⚙️ Rule-Based</span>
                <button className="btn btn-secondary" onClick={closeModals}>Close</button>
              </div>
              <div className="modal-body">
                <div style={{marginBottom: '1.5rem'}}>
                  <h3>Overall Risk</h3>
                  <div style={{display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.5rem'}}>
                    <span className={`risk-badge ${getRiskColor(riskAssessment.risk_level)}`}>
                      {riskAssessment.risk_level}
                    </span>
                    <strong style={{fontSize: '1.5rem'}}>{riskAssessment.risk_score.toFixed(3)}</strong>
                  </div>
                </div>

                <div className="risk-factors">
                  <h3>Risk Factors Breakdown</h3>
                  {riskAssessment.risk_factors.map((factor, index) => (
                    <div key={index} className="risk-factor">
                      <div className="risk-factor-header">
                        <span className="risk-factor-name">{factor.name}</span>
                        <span className="risk-factor-score">
                          {(factor.value * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{width: `${factor.value * 100}%`}}
                        />
                      </div>
                      <div style={{fontSize: '0.85rem', color: '#6b7280', marginTop: '0.25rem'}}>
                        {factor.description}
                      </div>
                    </div>
                  ))}
                </div>

                {riskAssessment.recommendations.length > 0 && (
                  <div className="recommendations">
                    <h3>Clinical Recommendations</h3>
                    <ul>
                      {riskAssessment.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button className="btn btn-ai" onClick={() => { closeModals(); viewAiAnalysis(selectedPatient); }}>
                  🤖 Get AI Analysis
                </button>
                <button className="btn btn-primary" onClick={closeModals}>Close</button>
              </div>
            </div>
          </div>
        )}

        {/* ════════════ AI ANALYSIS MODAL ════════════ */}
        {showAiModal && (
          <div className="modal-overlay" onClick={closeModals}>
            <div className="modal modal-wide" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>🤖 AI Analysis - {selectedPatient?.name}</h2>
                <div className="modal-header-badges">
                  <span className="ai-powered-badge">🤖 AI-Powered</span>
                  <button className="btn btn-secondary" onClick={closeModals}>Close</button>
                </div>
              </div>
              <div className="modal-body">
                {aiAnalysisLoading ? (
                  <div className="ai-loading">
                    <div className="ai-loading-spinner"></div>
                    <p>AI Agent is analyzing FHIR data...</p>
                    <p className="ai-loading-detail">Fetching patient records from InterSystems IRIS and running clinical reasoning</p>
                  </div>
                ) : aiAnalysis && (
                  <>
                    {/* Score Comparison */}
                    <div className="score-comparison">
                      <div className="score-card rule-score">
                        <h4>⚙️ Rule-Based Score</h4>
                        <div className="score-value">{aiAnalysis.rule_based_score.toFixed(3)}</div>
                      </div>
                      <div className="score-vs">VS</div>
                      <div className="score-card ai-score">
                        <h4>🤖 AI Assessment</h4>
                        <div className={`score-value ${getRiskColor(aiAnalysis.ai_risk_level)}`}>
                          {aiAnalysis.ai_risk_level}
                        </div>
                        <div className="confidence-bar">
                          <span>Confidence: {(aiAnalysis.ai_confidence_score * 100).toFixed(0)}%</span>
                          <div className="progress-bar">
                            <div className="progress-fill ai-fill" style={{width: `${aiAnalysis.ai_confidence_score * 100}%`}} />
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* AI Insights */}
                    <div className="ai-section">
                      <h3>🔍 AI Insights</h3>
                      <ul className="ai-insights-list">
                        {aiAnalysis.ai_insights.map((insight, i) => (
                          <li key={i}>{insight}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Reasoning Steps */}
                    {aiAnalysis.reasoning_steps.length > 0 && (
                      <div className="ai-section">
                        <h3>🧠 AI Reasoning Steps</h3>
                        <div className="reasoning-steps">
                          {aiAnalysis.reasoning_steps.map((step, i) => (
                            <div key={i} className="reasoning-step">
                              <div className="step-number">Step {step.step}</div>
                              <div className="step-content">
                                <div className="step-action"><strong>Analyzed:</strong> {step.action}</div>
                                <div className="step-finding"><strong>Finding:</strong> {step.finding}</div>
                                <div className="step-relevance"><strong>Clinical Relevance:</strong> {step.clinical_relevance}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Risks Missed by Rules */}
                    {aiAnalysis.risks_missed_by_rules.length > 0 && (
                      <div className="ai-section missed-risks">
                        <h3>⚠️ Risks Identified by AI (Missed by Rules)</h3>
                        <ul>
                          {aiAnalysis.risks_missed_by_rules.map((risk, i) => (
                            <li key={i}>{risk}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Recommendations */}
                    <div className="ai-section">
                      <h3>📋 AI Recommendations</h3>
                      <ul>
                        {aiAnalysis.recommendations.map((rec, i) => (
                          <li key={i}>{rec}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="ai-model-info">
                      Model: {aiAnalysis.model_used} | Analysis time: {new Date(aiAnalysis.analysis_timestamp).toLocaleString()}
                    </div>
                  </>
                )}
              </div>
              <div className="modal-footer">
                <button className="btn btn-primary" onClick={closeModals}>Close</button>
              </div>
            </div>
          </div>
        )}

        {/* ════════════ AI DISCHARGE PLAN MODAL ════════════ */}
        {showAiPlanModal && (
          <div className="modal-overlay" onClick={closeModals}>
            <div className="modal modal-wide" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>🤖 AI Discharge Plan - {selectedPatient?.name}</h2>
                <div className="modal-header-badges">
                  <span className="ai-powered-badge">🤖 AI-Powered</span>
                  <button className="btn btn-secondary" onClick={closeModals}>Close</button>
                </div>
              </div>
              <div className="modal-body">
                {aiPlanLoading ? (
                  <div className="ai-loading">
                    <div className="ai-loading-spinner"></div>
                    <p>AI Agent is generating personalized discharge plan...</p>
                  </div>
                ) : aiDischargePlan && (
                  <div className="ai-discharge-plan-content">
                    {aiDischargePlan.ai_powered && (
                      <div className="ai-model-info" style={{marginBottom: '1rem'}}>
                        Model: {aiDischargePlan.model_used}
                      </div>
                    )}
                    <div className="instructions-box" style={{whiteSpace: 'pre-wrap'}}>
                      {aiDischargePlan.discharge_plan}
                    </div>
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button className="btn btn-primary" onClick={closeModals}>Close</button>
              </div>
            </div>
          </div>
        )}

        {/* ════════════ DISCHARGE PLAN MODAL (Rule-Based) ════════════ */}
        {showPlanModal && dischargePlan && (
          <div className="modal-overlay" onClick={closeModals}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>{dischargePlan.title}</h2>
                <span className="badge-rule-based">⚙️ Rule-Based</span>
                <button className="btn btn-secondary" onClick={closeModals}>Close</button>
              </div>
              <div className="modal-body">
                <p style={{color: '#6b7280', marginBottom: '1rem'}}>
                  {dischargePlan.description}
                </p>

                <div className="discharge-plan">
                  <h3>Discharge Tasks</h3>
                  <div className="task-list">
                    {dischargePlan.tasks.map((task, index) => (
                      <div key={index} className="task-item">
                        <div className="task-title">{task.title}</div>
                        <div style={{fontSize: '0.85rem', color: '#6b7280', margin: '0.5rem 0'}}>
                          {task.description}
                        </div>
                        <span className={`task-priority ${getPriorityClass(task.priority)}`}>
                          {task.priority}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {dischargePlan.medications.length > 0 && (
                  <div style={{marginTop: '1.5rem'}}>
                    <h3>Discharge Medications</h3>
                    <ul>
                      {dischargePlan.medications.map((med, index) => (
                        <li key={index}>{med}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {dischargePlan.follow_up_appointments.length > 0 && (
                  <div style={{marginTop: '1.5rem'}}>
                    <h3>Follow-up Appointments</h3>
                    <ul>
                      {dischargePlan.follow_up_appointments.map((appt, index) => (
                        <li key={index}>{appt}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div style={{marginTop: '1.5rem'}}>
                  <h3>Patient Instructions</h3>
                  <div className="instructions-box">
                    {dischargePlan.patient_instructions}
                  </div>
                </div>

                {dischargePlan.care_plan_id && (
                  <div style={{marginTop: '1rem', padding: '0.75rem', backgroundColor: '#d1fae5', borderRadius: '6px'}}>
                    <strong style={{color: '#065f46'}}>✓ CarePlan Created:</strong>
                    <span style={{color: '#059669', marginLeft: '0.5rem'}}>
                      FHIR CarePlan/{dischargePlan.care_plan_id}
                    </span>
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button className="btn btn-ai" onClick={() => { closeModals(); generateAiDischargePlan(selectedPatient); }}>
                  🤖 Get AI Plan
                </button>
                <button className="btn btn-primary" onClick={closeModals}>Close</button>
              </div>
            </div>
          </div>
        )}

        {/* ════════════ COMPARISON MODAL ════════════ */}
        {showCompareModal && (
          <div className="modal-overlay" onClick={closeModals}>
            <div className="modal modal-wide" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>🤖 AI Patient Comparison</h2>
                <div className="modal-header-badges">
                  <span className="ai-powered-badge">🤖 AI-Powered</span>
                  <button className="btn btn-secondary" onClick={closeModals}>Close</button>
                </div>
              </div>
              <div className="modal-body">
                {compareLoading ? (
                  <div className="ai-loading">
                    <div className="ai-loading-spinner"></div>
                    <p>AI Agent is comparing patients...</p>
                  </div>
                ) : comparisonResult && (
                  <>
                    <div className="ai-section">
                      <h3>📊 Comparison Summary</h3>
                      <p>{comparisonResult.comparison_summary}</p>
                    </div>

                    {comparisonResult.risk_ranking.length > 0 && (
                      <div className="ai-section">
                        <h3>🏥 Risk Ranking</h3>
                        <div className="ranking-list">
                          {comparisonResult.risk_ranking.map((item, i) => (
                            <div key={i} className="ranking-item">
                              <span className="ranking-number">#{i + 1}</span>
                              <div className="ranking-detail">
                                <strong>{item.patient_name || item.patient_id}</strong>
                                {item.risk_level && (
                                  <span className={`risk-badge ${getRiskColor(item.risk_level)}`}>
                                    {item.risk_level}
                                  </span>
                                )}
                                {item.key_concern && <p>{item.key_concern}</p>}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {comparisonResult.common_risk_factors.length > 0 && (
                      <div className="ai-section">
                        <h3>🔗 Common Risk Factors</h3>
                        <ul>
                          {comparisonResult.common_risk_factors.map((f, i) => (
                            <li key={i}>{f}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="ai-section triage-rec">
                      <h3>🚨 Triage Recommendation</h3>
                      <p>{comparisonResult.triage_recommendation}</p>
                    </div>
                  </>
                )}
              </div>
              <div className="modal-footer">
                <button className="btn btn-primary" onClick={closeModals}>Close</button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
