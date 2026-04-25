export class DbClient {
  constructor(private readonly dsn: string | undefined) {}

  enabled(): boolean {
    return Boolean(this.dsn);
  }

  async fetchOne(_sql: string, _params?: Record<string, unknown>): Promise<Record<string, unknown>> {
    throw new Error("请在项目落地时接入真实数据库客户端。");
  }

  async fetchAll(_sql: string, _params?: Record<string, unknown>): Promise<Record<string, unknown>[]> {
    throw new Error("请在项目落地时接入真实数据库客户端。");
  }
}
