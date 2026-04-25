export interface TestCase {
  id: string;
  wave: string;
  wave_title: string;
  context: string;
  priority: "P0" | "P1" | "P2";
  categories: string[];
  topic: string;
  stage_code: string | null;
  stage_name: string;
  coverage_ids: string[];
  requirement_ids: string[];
  validation_ids: string[];
  preconditions: string;
  steps_summary: string;
  expected: string;
  automation_recommendation: string;
  data_refs: string[];
  dynamic_refs: string[];
  tags: string[];
  status: string;
}

export interface BoundaryCase {
  id: string;
  object: string;
  boundary_point: string;
  test_values: string;
  expected: string;
  tags: string[];
}

export type ExecutionContext = Record<string, unknown>;
export type CaseHandler<T = TestCase | BoundaryCase> = (ctx: ExecutionContext, testCase: T) => Promise<void>;
