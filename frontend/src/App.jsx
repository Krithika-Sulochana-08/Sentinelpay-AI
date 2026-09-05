import { useMemo, useState } from "react";
import axios from "axios";
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  CreditCard,
  Database,
  Gauge,
  GitBranch,
  LayoutDashboard,
  Loader2,
  Menu,
  Network,
  Search,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  UserCheck,
  WalletCards,
  XCircle,
} from "lucide-react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./index.css";

const API_URL = "http://127.0.0.1:8080/risk/analyze";

const FEEDBACK_URL = "http://127.0.0.1:8080/feedback/review";
const LOW_RISK_TRANSACTION = {
  transaction_id: "txn_demo_low_001",
  merchant_id: "merchant_demo",
  customer_id: "customer_101",
  amount: 1200,
  currency: "INR",
  payment_method: "card",
  timestamp: "2026-09-04T10:00:00",
  country: "IN",
  city: "Chennai",
  device_id: "device_demo_low",
  ip_address: "10.10.10.10",
  is_new_device: false,
  account_age_days: 700,
  transactions_last_1h: 1,
  transactions_last_24h: 3,
  avg_transaction_amount_30d: 1100,
  card_fingerprint: "card_demo_low",
  email_hash: "email_demo_low",
};

const HIGH_RISK_TRANSACTION = {
  transaction_id: "txn_demo_high_001",
  merchant_id: "merchant_demo",
  customer_id: "customer_999",
  amount: 50000,
  currency: "INR",
  payment_method: "card",
  timestamp: "2026-09-04T10:00:00",
  country: "IN",
  city: "Chennai",
  device_id: "device_demo_high",
  ip_address: "10.99.99.99",
  is_new_device: true,
  account_age_days: 2,
  transactions_last_1h: 10,
  transactions_last_24h: 20,
  avg_transaction_amount_30d: 2000,
  card_fingerprint: "card_demo_high",
  email_hash: "email_demo_high",
};

const FRAUD_RING_TRANSACTION = {
  transaction_id: "txn_graph_004",
  merchant_id: "merchant_demo",
  customer_id: "customer_D",
  amount: 1800,
  currency: "INR",
  payment_method: "card",
  timestamp: "2026-09-04T10:16:00",
  country: "IN",
  city: "Chennai",
  device_id: "device_ring_001",
  ip_address: "10.20.30.40",
  is_new_device: false,
  account_age_days: 180,
  transactions_last_1h: 1,
  transactions_last_24h: 2,
  avg_transaction_amount_30d: 1700,
  card_fingerprint: "card_ring_001",
  email_hash: "email_D",
};

function clampScore(value) {
  const n = Number(value || 0);
  return Math.max(0, Math.min(100, n));
}

function riskClass(level = "") {
  const value = String(level).toUpperCase();

  if (value.includes("HIGH")) return "risk-high";
  if (value.includes("MEDIUM")) return "risk-medium";
  return "risk-low";
}

function actionClass(action = "") {
  const value = String(action).toUpperCase();

  if (value.includes("REVIEW") || value.includes("BLOCK")) {
    return "action-review";
  }

  if (value.includes("CHALLENGE")) {
    return "action-challenge";
  }

  return "action-allow";
}

function formatProbability(value) {
  if (value === undefined || value === null) return "—";

  const number = Number(value);

  if (number <= 1) {
    return `${(number * 100).toFixed(1)}%`;
  }

  return `${number.toFixed(1)}%`;
}

function Sidebar({ activePage, setActivePage, collapsed, setCollapsed }) {
  const items = [
    {
      id: "dashboard",
      label: "Risk Command Center",
      icon: LayoutDashboard,
    },
    {
      id: "transactions",
      label: "Transactions",
      icon: CreditCard,
    },
    {
      id: "reviews",
      label: "Review Queue",
      icon: UserCheck,
    },
  ];

  return (
    <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      <div className="brand">
        <div className="brand-icon">
          <Shield size={24} />
        </div>

        {!collapsed && (
          <div>
            <div className="brand-name">SentinelPay</div>
            <div className="brand-subtitle">AI Risk Intelligence</div>
          </div>
        )}
      </div>

      <nav className="nav-menu">
        {items.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.id}
              className={`nav-item ${
                activePage === item.id ? "active" : ""
              }`}
              onClick={() => setActivePage(item.id)}
            >
              <Icon size={20} />
              {!collapsed && <span>{item.label}</span>}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-spacer" />

      {!collapsed && (
        <div className="system-card">
          <div className="system-indicator">
            <span className="pulse-dot" />
            System Online
          </div>

          <div className="system-copy">
            Risk engine, ML model and payment intelligence operational.
          </div>
        </div>
      )}

      <button
        className="collapse-button"
        onClick={() => setCollapsed(!collapsed)}
      >
        <Menu size={19} />
        {!collapsed && <span>Collapse</span>}
      </button>
    </aside>
  );
}

function Topbar({ activePage }) {
  const titles = {
    dashboard: "Risk Command Center",
    transactions: "Transaction Intelligence",
    reviews: "Human Review Queue",
    investigation: "Analyst Investigation",
  };

  return (
    <header className="topbar">
      <div>
        <div className="eyebrow">SENTINELPAY AI</div>
        <h1>{titles[activePage]}</h1>
      </div>

      <div className="topbar-actions">
        <div className="search-box">
          <Search size={17} />
          <span>Search intelligence</span>
        </div>

        <div className="online-badge">
          <span className="pulse-dot" />
          Live
        </div>
      </div>
    </header>
  );
}

function MetricCard({
  title,
  value,
  helper,
  icon: Icon,
  className = "",
}) {
  return (
    <div className={`metric-card ${className}`}>
      <div className="metric-card-top">
        <span>{title}</span>

        {Icon && (
          <div className="metric-icon">
            <Icon size={19} />
          </div>
        )}
      </div>

      <div className="metric-value">{value}</div>

      {helper && <div className="metric-helper">{helper}</div>}
    </div>
  );
}

function SignalRow({ label, value, icon: Icon }) {
  const score = clampScore(value);

  return (
    <div className="signal-row">
      <div className="signal-name">
        <div className="signal-icon">
          <Icon size={17} />
        </div>

        <span>{label}</span>
      </div>

      <div className="signal-track">
        <div
          className="signal-fill"
          style={{ width: `${score}%` }}
        />
      </div>

      <div className="signal-score">{score.toFixed(0)}</div>
    </div>
  );
}

function EmptyState({ onAnalyze }) {
  return (
    <div className="empty-analysis">
      <div className="empty-icon">
        <BrainCircuit size={32} />
      </div>

      <h3>Risk engine ready</h3>

      <p>
        Select a scenario and analyze the transaction to generate
        multi-signal fraud intelligence.
      </p>

      <button className="secondary-button" onClick={onAnalyze}>
        Run Demo Analysis
        <ChevronRight size={17} />
      </button>
    </div>
  );
}

function Dashboard({
  result,
  loading,
  error,
  scenario,
  setScenario,
  analyzeTransaction,
}) {
  const chartData = useMemo(() => {
    if (!result) return [];

    return [
      {
        name: "Rule",
        score: clampScore(result.risk_score),
      },
      {
        name: "Behavior",
        score: clampScore(result.behavior_anomaly_score),
      },
      {
        name: "Graph",
        score: clampScore(result.graph_risk_score),
      },
      {
        name: "Merchant",
        score: clampScore(result.merchant_context_score),
      },
    ];
  }, [result]);

  return (
    <main className="page-content">
      <section className="hero-panel">
        <div>
          <div className="section-tag">
            <Sparkles size={15} />
            Real-time decision intelligence
          </div>

          <h2>
            Explainable payment risk,
            <span> before money moves.</span>
          </h2>

          <p>
            SentinelPay combines rule risk, behavioral anomalies,
            graph relationships, merchant context, machine learning,
            policy and expected-cost reasoning into one authoritative
            payment decision.
          </p>
        </div>

        <div className="hero-status">
          <ShieldCheck size={36} />
          <div>
            <strong>Protection Active</strong>
            <span>Risk pipeline operational</span>
          </div>
        </div>
      </section>

      <section className="scenario-panel">
        <div>
          <div className="panel-label">DEMO SCENARIO</div>
          <div className="scenario-title">
            Choose transaction profile
          </div>
        </div>

        <div className="scenario-actions">
          <button
            className={`scenario-option ${
              scenario === "low" ? "selected-low" : ""
            }`}
            onClick={() => setScenario("low")}
          >
            <ShieldCheck size={18} />
            Low Risk
          </button>

          <button
            className={`scenario-option ${
              scenario === "high" ? "selected-high" : ""
            }`}
            onClick={() => setScenario("high")}
          >
            <ShieldAlert size={18} />
            High Risk
          </button>

          <button
            className={`scenario-option ${
              scenario === "ring" ? "selected-ring" : ""
            }`}
            onClick={() => setScenario("ring")}
          >
            <Network size={18} />
            Fraud Ring
          </button>
          <button
            className="analyze-button"
            onClick={analyzeTransaction}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="spin" size={18} />
                Analyzing
              </>
            ) : (
              <>
                <Activity size={18} />
                Analyze Transaction
              </>
            )}
          </button>
        </div>
      </section>

      {error && (
        <div className="error-banner">
          <XCircle size={18} />
          <div>
            <strong>Backend connection failed</strong>
            <span>{error}</span>
          </div>
        </div>
      )}

      {!result && !loading && (
        <EmptyState onAnalyze={analyzeTransaction} />
      )}

      {result && (
        <>
          <section className="primary-metrics">
            <MetricCard
              title="Fused Risk Score"
              value={`${Number(
                result.fused_risk_score || 0
              ).toFixed(1)}/100`}
              helper="Unified multi-signal score"
              icon={Gauge}
            />

            <MetricCard
              title="Final Risk Level"
              value={result.final_risk_level || "—"}
              helper="Policy-grade classification"
              icon={AlertTriangle}
              className={riskClass(result.final_risk_level)}
            />

            <MetricCard
              title="Authoritative Action"
              value={result.authoritative_action || "—"}
              helper="Final enforceable decision"
              icon={Shield}
              className={actionClass(
                result.authoritative_action
              )}
            />

            <MetricCard
              title="Decision Confidence"
              value={result.decision_confidence || "—"}
              helper={`Agreement: ${
                result.signal_agreement || "—"
              } • Uncertainty: ${
                result.uncertainty_score ?? "—"
              }/100`}
              icon={BrainCircuit}
            />
          </section>

          <section className="dashboard-grid">
            <div className="panel signal-panel">
              <div className="panel-header">
                <div>
                  <div className="panel-label">
                    MULTI-SIGNAL INTELLIGENCE
                  </div>
                  <h3>Risk decomposition</h3>
                </div>

                <Activity size={20} />
              </div>

              <SignalRow
                label="Transaction Risk"
                value={result.risk_score}
                icon={CreditCard}
              />

              <SignalRow
                label="Behavior Risk"
                value={result.behavior_anomaly_score}
                icon={Activity}
              />

              <SignalRow
                label="Graph Risk"
                value={result.graph_risk_score}
                icon={Network}
              />

              <SignalRow
                label="Merchant Risk"
                value={result.merchant_context_score}
                icon={WalletCards}
              />
            </div>

            <div className="panel ml-panel">
              <div className="panel-header">
                <div>
                  <div className="panel-label">
                    MACHINE LEARNING
                  </div>
                  <h3>Fraud probability</h3>
                </div>

                <BrainCircuit size={20} />
              </div>

              <div className="probability-value">
                {formatProbability(
                  result.ml_fraud_probability
                )}
              </div>

              <div className="probability-track">
                <div
                  className="probability-fill"
                  style={{
                    width: `${
                      Number(
                        result.ml_fraud_probability || 0
                      ) <= 1
                        ? Number(
                            result.ml_fraud_probability || 0
                          ) * 100
                        : Number(
                            result.ml_fraud_probability || 0
                          )
                    }%`,
                  }}
                />
              </div>

              <div className="ml-details">
                <div>
                  <span>Prediction</span>
                  <strong>
                    {String(
                      result.ml_predicted_label ??
                        "Unavailable"
                    )}
                  </strong>
                </div>

                <div>
                  <span>Threshold</span>
                  <strong>
                    {result.ml_threshold ?? "—"}
                  </strong>
                </div>
              </div>
            </div>
          </section>

          <section className="dashboard-grid lower-grid">
            <div className="panel chart-panel">
              <div className="panel-header">
                <div>
                  <div className="panel-label">
                    SIGNAL COMPARISON
                  </div>
                  <h3>Risk profile</h3>
                </div>

                <GitBranch size={20} />
              </div>

              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                      stroke="rgba(148, 163, 184, 0.1)"
                    />

                    <XAxis
                      dataKey="name"
                      axisLine={false}
                      tickLine={false}
                      tick={{
                        fill: "#8191ad",
                        fontSize: 12,
                      }}
                    />

                    <YAxis
                      domain={[0, 100]}
                      axisLine={false}
                      tickLine={false}
                      tick={{
                        fill: "#8191ad",
                        fontSize: 11,
                      }}
                    />

                    <Tooltip
                      cursor={{
                        fill: "rgba(255,255,255,0.025)",
                      }}
                      contentStyle={{
                        background: "#111827",
                        border:
                          "1px solid rgba(148,163,184,.15)",
                        borderRadius: "12px",
                      }}
                    />

                    <Bar
                      dataKey="score"
                      fill="#39bdf8"
                      radius={[7, 7, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="panel evidence-panel">
              <div className="panel-header">
                <div>
                  <div className="panel-label">
                    EXPLAINABLE AI
                  </div>
                  <h3>Why SentinelPay flagged it</h3>
                </div>

                <Sparkles size={20} />
              </div>

              <div className="decision-summary">
                {result.decision_summary ||
                  "Decision explanation unavailable."}
              </div>

              <div className="evidence-list">
                {(result.top_evidence || []).length > 0 ? (
                  result.top_evidence.map((item, index) => (
                    <div
                      className="evidence-item"
                      key={`${item.evidence}-${index}`}
                  >
                    <div className="evidence-number">
                      {index + 1}
                    </div>

                    <div className="evidence-content">
                      <span className="evidence-source">
                        {item.source
                          ?.replaceAll("_", " ")
                          .toUpperCase()}
                      </span>

                      <span>
                        {item.evidence}
                      </span>
                    </div>
                  </div>
              ))
            ) : (
                  <div className="muted-copy">
                    No additional risk evidence returned.
                  </div>
                )}
              </div>
            </div>
          </section>

          <section className="dashboard-grid lower-grid">
            <div className="panel decision-panel">
              <div className="panel-header">
                <div>
                  <div className="panel-label">
                    POLICY ENGINE
                  </div>
                  <h3>Decision resolution</h3>
                </div>

                <Shield size={20} />
              </div>

              <div className="decision-row">
                <span>Risk recommendation</span>
                <strong>
                  {result.risk_recommended_action || "—"}
                </strong>
              </div>

              <div className="decision-row">
                <span>Cost recommendation</span>
                <strong>
                  {result.cost_recommended_action || "—"}
                </strong>
              </div>

              <div className="decision-row highlighted">
                <span>Authoritative action</span>
                <strong>
                  {result.authoritative_action || "—"}
                </strong>
              </div>

              <div className="policy-reason">
                {result.policy_resolution_reason ||
                  "No policy explanation returned."}
              </div>
            </div>

            <div className="panel cost-panel">
              <div className="panel-header">
                <div>
                  <div className="panel-label">
                    COST-AWARE DECISIONING
                  </div>
                  <h3>Expected business impact</h3>
                </div>

                <CircleDollarSign size={20} />
              </div>

              <div className="cost-action">
                <span>Optimal Action</span>
                <strong>
                  {result.cost_optimized_action || "—"}
                </strong>
              </div>

              <div className="minimum-cost">
                <span>Minimum Expected Cost</span>
                <strong>
                  {result.minimum_expected_cost ?? "—"}
                </strong>
              </div>

              <div
                className={`review-callout ${
                  result.human_review_recommended
                    ? "review-needed"
                    : "review-clear"
                }`}
              >
                {result.human_review_recommended ? (
                  <AlertTriangle size={20} />
                ) : (
                  <CheckCircle2 size={20} />
                )}

                <div>
                  <strong>
                    {result.human_review_recommended
                      ? "Human review recommended"
                      : "Automation confidence sufficient"}
                  </strong>

                  <span>
                    {result.human_review_recommended
                      ? "Transaction should enter analyst review before final settlement."
                      : "Risk signals support automated processing."}
                  </span>
                </div>
              </div>
            </div>
          </section>

          <section className="transaction-footer">
            <div>
              <span>TRANSACTION</span>
              <strong>{result.transaction_id}</strong>
            </div>

            <div>
              <span>MERCHANT</span>
              <strong>{result.merchant_id}</strong>
            </div>

            <div>
              <span>DRIFT STATUS</span>
              <strong>{result.drift_status || "—"}</strong>
            </div>

            <div>
              <span>FRAUD SPIKE</span>
              <strong>
                {result.fraud_spike_detected ? "DETECTED" : "NONE"}
              </strong>
            </div>
          </section>
        </>
      )}
    </main>
  );
}

function Transactions({ history }) {
  return (
    <main className="page-content">
      <section className="page-heading">
        <div>
          <div className="section-tag">
            <Database size={15} />
            Transaction Intelligence
          </div>

          <h2>Recent risk decisions</h2>

          <p>
            Every analyzed transaction is presented with its fused
            score and final authoritative action.
          </p>
        </div>
      </section>

      <div className="panel table-panel">
        {history.length === 0 ? (
          <div className="table-empty">
            <CreditCard size={28} />
            <h3>No analyzed transactions yet</h3>
            <p>
              Return to the Risk Command Center and run a demo
              transaction.
            </p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Transaction</th>
                  <th>Merchant</th>
                  <th>Risk Score</th>
                  <th>Risk Level</th>
                  <th>ML Probability</th>
                  <th>Final Action</th>
                </tr>
              </thead>

              <tbody>
                {history.map((item, index) => (
                  <tr key={`${item.transaction_id}-${index}`}>
                    <td>
                      <span className="transaction-id">
                        {item.transaction_id}
                      </span>
                    </td>

                    <td>{item.merchant_id}</td>

                    <td>
                      {Number(
                        item.fused_risk_score || 0
                      ).toFixed(1)}
                    </td>

                    <td>
                      <span
                        className={`table-badge ${riskClass(
                          item.final_risk_level
                        )}`}
                      >
                        {item.final_risk_level}
                      </span>
                    </td>

                    <td>
                      {formatProbability(
                        item.ml_fraud_probability
                      )}
                    </td>

                    <td>
                      <span
                        className={`table-badge ${actionClass(
                          item.authoritative_action
                        )}`}
                      >
                        {item.authoritative_action}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}

function ReviewQueue({
  history,
  setSelectedReview,
  setActivePage,
}) {
  const reviews = history.filter(
    (item) =>
      !item.analyst_reviewed &&
      (
        item.human_review_recommended ||
        String(item.authoritative_action)
          .toUpperCase()
          .includes("REVIEW")
      )
  );

  return (
    <main className="page-content">
      <section className="page-heading">
        <div>
          <div className="section-tag">
            <UserCheck size={15} />
            Human Oversight
          </div>

          <h2>Analyst review queue</h2>

          <p>
            Transactions where SentinelPay recommends human
            intervention appear here.
          </p>
        </div>

        <div className="queue-count">
          <span>{reviews.length}</span>
          pending
        </div>
      </section>

      {reviews.length === 0 ? (
        <div className="panel review-empty">
          <ShieldCheck size={38} />

          <h3>No transactions awaiting review</h3>

          <p>
            High-risk or uncertain transactions will appear here
            automatically.
          </p>
        </div>
      ) : (
        <div className="review-grid">
          {reviews.map((item, index) => (
            <div
              className="review-card"
              key={`${item.transaction_id}-${index}`}
            >
              <div className="review-card-header">
                <div>
                  <div className="panel-label">
                    TRANSACTION
                  </div>
                  <strong>{item.transaction_id}</strong>
                </div>

                <span
                  className={`table-badge ${riskClass(
                    item.final_risk_level
                  )}`}
                >
                  {item.final_risk_level}
                </span>
              </div>

              <div className="review-score">
                <span>Fused Risk</span>
                <strong>
                  {Number(
                    item.fused_risk_score || 0
                  ).toFixed(1)}
                </strong>
              </div>

              <div className="review-summary">
                {item.decision_summary}
              </div>

              <button
                className="review-button"
                onClick={() => {
                  setSelectedReview(item);
                  setActivePage("investigation");
                }}
              >
                Open Investigation
                <ChevronRight size={17} />
              </button>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

function Investigation({
  transaction,
  setActivePage,
  setHistory,
}) {
  if (!transaction) {
    return (
      <main className="page-content">
        <div className="panel review-empty">
          <ShieldCheck size={38} />
          <h3>No transaction selected</h3>
          <p>
            Return to the Review Queue and open a transaction.
          </p>

          <button
            className="secondary-button"
            onClick={() => setActivePage("reviews")}
          >
            Back to Review Queue
          </button>
        </div>
      </main>
    );
  }

  const [submitting, setSubmitting] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState("");

  async function submitReview(outcome) {
    setSubmitting(true);
    setFeedbackMessage("");

    try {
      await axios.post(
        FEEDBACK_URL,
        {
          transaction_id: transaction.transaction_id,
          review_outcome: outcome,
          reviewer_note:
            outcome === "FRAUD"
              ? "Analyst confirmed fraudulent activity."
              : "Analyst confirmed transaction as legitimate.",
        },
        {
          timeout: 15000,
        }
      );

      setHistory((previous) =>
        previous.map((item) =>
          item.transaction_id === transaction.transaction_id
            ? {
                ...item,
                human_review_recommended: false,
                analyst_review_outcome: outcome,
                analyst_reviewed: true,
              }
            : item
        )
      );

      setFeedbackMessage(
        outcome === "FRAUD"
          ? "Transaction confirmed as fraud."
          : "Transaction approved as legitimate."
      );

      setTimeout(() => {
        setActivePage("reviews");
      }, 900);
    } catch (error) {
      setFeedbackMessage(
        error?.response?.data?.detail
          ? JSON.stringify(error.response.data.detail)
          : "Failed to submit analyst decision."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="page-content">
      <section className="page-heading">
        <div>
          <div className="section-tag">
            <UserCheck size={15} />
            Analyst Investigation
          </div>

          <h2>{transaction.transaction_id}</h2>

          <p>
            Review SentinelPay&apos;s evidence before making the
            final human decision.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() => setActivePage("reviews")}
        >
          Back to Queue
        </button>
      </section>

      <section className="primary-metrics">
        <MetricCard
          title="Fused Risk"
          value={`${Number(
            transaction.fused_risk_score || 0
          ).toFixed(1)}/100`}
          helper="Unified multi-signal score"
          icon={Gauge}
        />

        <MetricCard
          title="Risk Level"
          value={transaction.final_risk_level || "—"}
          helper="Policy-grade classification"
          icon={AlertTriangle}
          className={riskClass(
            transaction.final_risk_level
          )}
        />

        <MetricCard
          title="Recommended Action"
          value={transaction.authoritative_action || "—"}
          helper="SentinelPay recommendation"
          icon={Shield}
          className={actionClass(
            transaction.authoritative_action
          )}
        />

        <MetricCard
          title="Decision Confidence"
          value={transaction.decision_confidence || "—"}
          helper={`Agreement: ${
            transaction.signal_agreement || "—"
          } • Uncertainty: ${
            transaction.uncertainty_score ?? "—"
          }/100`}
          icon={BrainCircuit}
        />
      </section>

      <section className="dashboard-grid lower-grid">
        <div className="panel evidence-panel">
          <div className="panel-header">
            <div>
              <div className="panel-label">
                EXPLAINABLE EVIDENCE
              </div>
              <h3>Why this transaction was flagged</h3>
            </div>

            <Sparkles size={20} />
          </div>

          <div className="decision-summary">
            {transaction.decision_summary ||
              "Decision explanation unavailable."}
          </div>

          <div className="evidence-list">
            {(transaction.top_evidence || []).length > 0 ? (
              transaction.top_evidence.map(
                (item, index) => (
                  <div
                    className="evidence-item"
                    key={`${item.evidence}-${index}`}
                  >
                    <div className="evidence-number">
                      {index + 1}
                    </div>

                    <div className="evidence-content">
                      <span className="evidence-source">
                        {item.source
                          ?.replaceAll("_", " ")
                          .toUpperCase()}
                      </span>

                      <span>{item.evidence}</span>
                    </div>
                  </div>
                )
              )
            ) : (
              <div className="muted-copy">
                No additional risk evidence returned.
              </div>
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <div className="panel-label">
                ANALYST DECISION
              </div>
              <h3>Final human action</h3>
            </div>

            <UserCheck size={20} />
          </div>

          <div className="decision-row">
            <span>Transaction</span>
            <strong>{transaction.transaction_id}</strong>
          </div>

          <div className="decision-row">
            <span>Merchant</span>
            <strong>{transaction.merchant_id}</strong>
          </div>

          <div className="decision-row">
            <span>ML Fraud Probability</span>
            <strong>
              {formatProbability(
                transaction.ml_fraud_probability
              )}
            </strong>
          </div>

          <div className="decision-row highlighted">
            <span>SentinelPay Recommendation</span>
            <strong>
              {transaction.authoritative_action || "—"}
            </strong>
          </div>

          <div className="analyst-actions">
            <button
              className="approve-button"
              disabled={submitting}
              onClick={() => submitReview("LEGITIMATE")}
            >
              <CheckCircle2 size={18} />
              {submitting
                ? "Submitting..."
                : "Approve Transaction"}
            </button>

            <button
              className="block-button"
              disabled={submitting}
              onClick={() => submitReview("FRAUD")}
            >
              <XCircle size={18} />
              {submitting
                ? "Submitting..."
                : "Block Transaction"}
            </button>
          </div>

          {feedbackMessage && (
            <div className="review-feedback-message">
              {feedbackMessage}
            </div>
          )}

          <div className="policy-reason">
            Analyst decisions are submitted to SentinelPay&apos;s
            review-feedback endpoint and retained with the
            transaction history.
          </div>
        </div>
      </section>
    </main>
  );
}

function App() {
  const [activePage, setActivePage] =
    useState("dashboard");

  const [sidebarCollapsed, setSidebarCollapsed] =
    useState(false);

  const [scenario, setScenario] = useState("high");

  const [result, setResult] = useState(null);

  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [selectedReview, setSelectedReview] =
    useState(null);

  async function analyzeTransaction() {
    setLoading(true);
    setError("");

    let transaction;

    if (scenario === "high") {
      transaction = HIGH_RISK_TRANSACTION;
    } else if (scenario === "ring") {
      transaction = FRAUD_RING_TRANSACTION;
    } else {
      transaction = LOW_RISK_TRANSACTION;
    }

    try {
      const response = await axios.post(
        API_URL,
        transaction,
        {
          timeout: 15000,
        }
      );

      const data = response.data;

      setResult(data);

      setHistory((previous) => [
        data,
        ...previous.filter(
          (item) =>
            item.transaction_id !== data.transaction_id
        ),
      ]);
    } catch (requestError) {
      const message =
        requestError?.response?.data?.detail
          ? JSON.stringify(
              requestError.response.data.detail
            )
          : requestError.message;

      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
      />

      <div className="main-shell">
        <Topbar activePage={activePage} />

        {activePage === "dashboard" && (
          <Dashboard
            result={result}
            loading={loading}
            error={error}
            scenario={scenario}
            setScenario={setScenario}
            analyzeTransaction={analyzeTransaction}
          />
        )}

        {activePage === "transactions" && (
          <Transactions history={history} />
        )}

        {activePage === "reviews" && (
          <ReviewQueue
            history={history}
            setSelectedReview={setSelectedReview}
            setActivePage={setActivePage}
          />
        )}

        {activePage === "investigation" && (
          <Investigation
            transaction={selectedReview}
            setActivePage={setActivePage}
            setHistory={setHistory}
          />
        )}
      </div>
    </div>
  );
}

export default App;