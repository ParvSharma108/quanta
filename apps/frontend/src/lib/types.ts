export interface UserRecord {
  id: string;
  email: string;
  full_name?: string;
  role: 'admin' | 'analyst' | 'viewer';
  created_at?: string;
  updated_at?: string;
}

export interface AuthResponse {
  token: string;
  user: UserRecord;
}

export interface UsersListResponse {
  data: UserRecord[];
  total?: number;
}

export interface UpdateRoleInput {
  role: 'admin' | 'analyst' | 'viewer';
}

export interface Asset {
  id: string;
  name: string;
  asset_class?: string;
  expected_return: number;
  risk_variance: number;
  liquidity_tier?: number;
  ticket_cost?: number;
}

export interface Liability {
  id: string;
  name: string;
  amount: number;
  due_horizon_days: number;
}

export interface ConstraintAuditItem {
  name: string;
  passed: boolean;
  actual_value: number;
  limit_value: number;
  description?: string;
}

export interface Treasury {
  id: string;
  name: string;
  base_currency: string;
  total_capital: number;
  risk_tolerance: number;
  min_liquidity_ratio: number;
  owner_id?: string;
  assets?: Asset[];
  liabilities?: Liability[];
  created_at?: string;
  updated_at?: string;
}

export interface CreateTreasuryInput {
  name: string;
  base_currency: string;
  total_capital: number;
  risk_tolerance: number;
  min_liquidity_ratio: number;
  assets?: Asset[];
  liabilities?: Liability[];
}

export interface TreasuriesListResponse {
  data: Treasury[];
  total?: number;
}

export interface StrategyExecutionLog {
  id: string;
  treasury_id: string;
  algorithm: string;
  status: string;
  allocations: Record<string, number> | string;
  expected_return?: number;
  total_risk?: number;
  objective_value?: number;
  runtime_ms?: number;
  comparison_metrics?: Record<string, any>;
  created_at: string;
}

export interface StrategiesListResponse {
  data: StrategyExecutionLog[];
  total?: number;
}

export interface GenerateStrategyInput {
  algorithm: string;
  include_comparison?: boolean;
  step_size?: number;
  min_liquidity?: number;
}

export interface OrchestrateAllocationResponse {
  allocations: Record<string, number>;
  objective_value: number;
  expected_return: number;
  risk_penalty: number;
  liquidity_satisfied: boolean;
  runtime_ms: number;
  solver: string;
  quantum_metadata?: {
    circuit_depth_p?: number;
    qubit_count?: number;
    approximation_ratio?: number;
    shots?: number;
  };
}

export interface BayesianEvidence {
  feature: string;
  likelihood_ratio: number;
  interpretation: string;
}

export interface AIRiskAnalyzeResponse {
  risk_tier: 'Low' | 'Medium' | 'High' | 'Critical';
  risk_score: number;
  liquidity_buffer_ratio: number;
  evidence: BayesianEvidence[];
  recommended_actions: string[];
}

export interface TreasuryStressTestResponse {
  scenario: string;
  baseline_value: number;
  stressed_value: number;
  drawdown_percent: number;
  liquidity_surplus_deficit: number;
  is_solvent: boolean;
  mitigation_strategy: string;
}

export interface AnalyzeTreasuryRiskInput {
  risk_tolerance?: number;
  horizon_days?: number;
}

export interface AdversarialStressTestInput {
  shock_scenario?: 'liquidity_freeze' | 'market_crash' | 'counterparty_default' | 'rate_spike';
  stress_intensity?: number;
}

export interface AuditLogRecord {
  id: string;
  user_id: string;
  user_email?: string;
  action: string;
  entity_type: string;
  entity_id: string;
  ip_address?: string;
  created_at: string;
}

export interface AuditLogsListResponse {
  data: AuditLogRecord[];
  total?: number;
}

export interface OptimizationResult {
  allocations: Record<string, number>;
  objective_value: number;
  expected_return: number;
  risk_penalty: number;
  liquidity_satisfied: boolean;
  runtime_ms: number;
  solver: string;
  feasible?: boolean;
  metadata?: Record<string, any>;
}

export interface OptimizationCompareResponse {
  qaoa?: OptimizationResult;
  simulated_annealing?: OptimizationResult;
  greedy?: OptimizationResult;
  exact?: OptimizationResult;
  slsqp?: OptimizationResult;
  highs_milp?: OptimizationResult;
}

export interface BenchmarkLabResponse {
  optimal_found: boolean;
  sample_distribution: Record<string, number>;
  energy_history: number[];
  approximation_ratio: number;
}

export interface FinancialProblem {
  capital_base: number;
  assets: Asset[];
  liabilities: Liability[];
  risk_aversion: number;
  min_liquidity_ratio: number;
}

export interface StrategyGenerateResponse {
  algorithm: string;
  allocations: Record<string, number>;
  nodes_expanded: number;
  runtime_ms: number;
  objective_value: number;
  expected_return: number;
  trajectory: Array<{ step: number; state: string; action: string; g_score: number; h_score: number }>;
}

export interface AgentDeliberationOpinion {
  agent_name: string;
  vote: 'APPROVE' | 'REJECT' | 'CONDITIONAL';
  confidence: number;
  rationale: string;
}

export interface DeliberationSummary {
  consensus_reached: boolean;
  final_decision: string;
  votes: AgentDeliberationOpinion[];
  summary: string;
}
