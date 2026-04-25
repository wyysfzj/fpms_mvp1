你现在在一个真实业务仓库的根目录工作，仓库中已经放入：

- `FPMS_Automation_Skeleton_Pack/`
- 真实业务前后端代码
- 真实数据库接入代码或 ORM 模块

本次任务只做**分析和计划**，不要修改任何代码。

## 你的目标

把 `FPMS_Automation_Skeleton_Pack/` 映射到真实项目，找出自动化落地路径。

## 你必须先阅读的文件

### 测试资产
- `FPMS_Automation_Skeleton_Pack/README.md`
- `FPMS_Automation_Skeleton_Pack/docs/source/FPMS_SPEC_2_0.md`
- `FPMS_Automation_Skeleton_Pack/docs/source/FPMS_SPEC2_0_Test_Cases_E2E.md`
- `FPMS_Automation_Skeleton_Pack/data/manifests/smoke_p0.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/wave_manifest.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/reference_resolution.yaml`
- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/router.py`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/router.ts`

### 真实项目代码
请自行查找并阅读与以下领域相关的代码：
- 登录 / 鉴权
- 案卷维护
- 中间文件
- 时限
- 费用
- 账单 / 收款 / 催款 / 坏账
- 查询 / 报表
- 数据库访问层
- 前端路由与页面对象可落点

## 你要输出的结果

请只输出以下内容，不要改代码：

1. **模块映射表**
   - skeleton pack 中每个 wave 对应到真实项目的哪些模块、路由、API、DB 表
2. **技术落地清单**
   - pytest 需要补哪些 client / helper / db assert
   - Playwright 需要补哪些 page object / selector / fixture
3. **高风险项**
   - 登录方式
   - 动态数据冲突
   - 数据 seed 缺口
   - warning vs blocking 差异
   - 选择器不稳定
   - 缺少 DB 只读权限
4. **首批建议实现范围**
   - 只建议 `W0 + A` 的 P0 主链路
   - 按具体 testcase ID 列出来
5. **拟改文件清单**
   - 仅列文件，不动代码
6. **建议执行命令**
   - 计划中的 validate / pytest / playwright 命令

## 严格约束

- 不要修改任何代码
- 不要修改任何 YAML/JSON/schema
- 不要重命名 handler / testcase id
- 输出必须清楚地区分“已确认映射”和“待确认假设”
