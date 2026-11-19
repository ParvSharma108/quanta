export interface Asset {
  id: string;
  name: string;
  asset_type?: string;
  cost: number;
  expected_return: number;
  risk: number;
  liquidity: number;
  volatility?: number;
}

export interface Liability {
  id: string;
  name: string;
  principal: number;
  amount?: number;
  interest_rate: number;
  maturity_months: number;
  maturity?: number;
  priority: number;
  is_mandatory_reserve: boolean;
}

export interface Constraint {
  id: string;
  constraint_type: string;
  description?: string;
  parameters: Record<string, any>;
  severity?: string;
}

export interface FinancialProblem {
  capital: number;
  step_size?: number;
  assets: Asset[];
  liabilities: Liability[];
  constraints: Constraint[];
  risk_tolerance: number;
  minimum_liquidity: number;
  objective: string;
  market_state?: string;
}

export interface OptimizationResult {
  method: string;
  status: string;
  allocation: Record<string, number>;
  objective_value: number;
  portfolio_return: number;
  portfolio_risk: number;
  liquidity: number;
  capital_used: number;
  feasible: boolean;
  constraint_violations: string[];
  runtime_ms: number;
  metadata?: Record<string, any>;
}

export interface OptimizationCompareResponse {
  problem_summary: Record<string, any>;
  results: Record<string, OptimizationResult>;
  summary_table: Array<{
    method: string;
    status: string;
    objective_value: number;
    portfolio_return: number;
    portfolio_risk: number;
    liquidity: number;
    capital_used: number;
    feasible: boolean;
    violations_count: number;
    runtime_ms: number;
  }>;
  best_classical_method: string;
  qaoa_approximation_ratio?: number;
  simulation_note?: string;
}

export interface BenchmarkLabResponse {
  instance_info: Record<string, any>;
  results: Record<string, OptimizationResult>;
  summary_table: any[];
  scientific_summary: Record<string, any>;
}

export interface StrategyGenerateResponse {
  strategy: {
    total_allocated: number;
    expected_return: number;
    risk_score: number;
    liquidity_ratio: number;
    objective_value: number;
    is_compliant: boolean;
    explanation: string;
    metadata?: Record<string, any>;
    actions: any[];
  };
  search_result: {
    algorithm: string;
    success: boolean;
    execution_time_ms: number;
    states_explored: number;
  };
  risk_breakdown: {
    composite_risk_score: number;
    weighted_asset_risk: number;
    concentration_index_hhi: number;
    concentration_penalty: number;
    liquidity_deficit_penalty: number;
    leverage_penalty: number;
    risk_tier: string;
  };
  constraint_audit: Array<{
    constraint_id: string;
    constraint_type: string;
    satisfied: boolean;
    actual: number;
    required: number;
    message: string;
    penalty: number;
  }>;
}

export interface DeliberationSummary {
  consensus_reached: boolean;
  recommended_strategy: {
    total_allocated: number;
    expected_return: number;
    risk_score: number;
    liquidity_ratio: number;
    explanation: string;
  };
  treasury_opinion: { is_acceptable: boolean; score: number; rationale: string };
  risk_opinion: { is_acceptable: boolean; score: number; rationale: string };
  compliance_opinion: { is_acceptable: boolean; score: number; rationale: string };
  decision_rationale: string;
}
