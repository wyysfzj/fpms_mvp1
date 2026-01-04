# FPMS MVP1 Backend Enhancement Checklist

快速参考清单 - 按模块和优先级组织的增强项目

---

## 🚨 P0 - CRITICAL (必须完成才能发布MVP1)

### 认证与授权 (Authentication & RBAC) - 8 items
- [ ] BE-01-05: 实现 `app/core/security.py` (JWT + password hashing)
- [ ] BE-01-04: 实现 `T_RolePerm` 模型
- [ ] BE-01-10: 实现 `get_user_permissions()` 服务
- [ ] BE-01-11: 实现角色权限种子数据
- [ ] BE-01-12: 实现 `POST /auth/login` 端点
- [ ] BE-01-13: 实现 `GET /auth/me` 端点
- [ ] BE-01-15: 更新 `require_perm()` 为真实RBAC检查
- [ ] BE-01-16: 创建开发环境种子脚本 (admin用户)

### 核心基础设施 (Core Infrastructure) - 6 items
- [ ] BE-00-01: 实现 `app/core/errors.py` (BusinessError异常)
- [ ] BE-00-02: 在main.py注册异常处理器
- [ ] BE-00-03: 实现 `app/core/pagination.py` (PageParams, PageResult)
- [ ] BE-00-04: 实现 `app/db/mixins.py` (UUID + Audit字段)
- [ ] BE-00-06: 实现 `app/core/storage.py` (安全文件操作)
- [ ] 添加全局异常处理器到main.py

### 案卷模块 (Cases) - 10 items
- [ ] BE-03-00: 创建案卷枚举 (CaseType, FlowDir等)
- [ ] BE-03-02 to BE-03-04: 实现 T_CaseApplicant, T_CaseInventor, T_Priority 模型
- [ ] BE-03-05 to BE-03-12: 创建所有Pydantic schemas
- [ ] BE-03-13: 实现申请人验证服务
- [ ] BE-03-14 to BE-03-18: 实现服务层 (list/create/update等)
- [ ] 添加案卷号唯一性验证
- [ ] 实现优先权日期自动计算
- [ ] 强制执行有限编辑字段白名单
- [ ] 添加缺失的Case模型字段 (prio_date, description等)
- [ ] 将API层的直接DB访问移到服务层

### 账单模块 (Billing) - 10 items
- [ ] 为所有端点创建Pydantic schemas
- [ ] 实现账单生成服务层
- [ ] 添加单客户验证 (bills必须single client)
- [ ] 添加币种一致性验证
- [ ] 实现付款核销逻辑与余额更新
- [ ] 修复支付行概念 (per spec)
- [ ] 添加账单项验证
- [ ] 将API层业务逻辑移到服务层
- [ ] 实现账单状态转换
- [ ] 自动更新案卷收款汇总

### 文档模块 (Documents) -7 items
- [ ] BE-04-04, BE-04-05: 创建Pydantic schemas
- [ ] BE-04-06 to BE-04-08: 实现服务层
- [ ] 实现附件上传及文件验证
- [ ] 完善 T_DocAttachment 模型
- [ ] 实现文档-案卷关联
- [ ] 将API层直接DB访问移到服务层
- [ ] 创建storage.py用于安全文件处理

### 任务模块 (Tasks) - 5 items
- [ ] 创建所有Pydantic schemas
- [ ] 实现服务层
- [ ] 添加 T_TaskLog 模型用于审计追踪
- [ ] 实现今日提醒端点 GET /tasks/today
- [ ] 将API层业务逻辑移到服务层

### 费用模块 (Fees) - 5 items
- [ ] 创建所有Pydantic schemas
- [ ] 实现服务层
- [ ] 添加费用草案锁定机制
- [ ] 实现费用类型枚举 (GOV/SERVICE/MISC)
- [ ] 添加费用项CRUD

### 客户主数据 (Clients) - 4 items
- [ ] BE-02-04 to BE-02-06: 创建Pydantic schemas
- [ ] BE-02-07 to BE-02-10: 实现服务层
- [ ] 添加客户代码唯一性验证
- [ ] 将addresses/contacts改为proper schemas (非dict)

### 数据库 (Database) - 5 items
- [ ] 创建全面的初始Alembic migration
- [ ] 按规格添加数据库索引
- [ ] 添加外键约束
- [ ] 创建数据库种子脚本
- [ ] 添加UUID主键和审计字段mixins

**P0小计: 60项 | 预估工作量: 25-30天**

---

## ⚠️ P1 - HIGH (高优先级，MVP1强烈推荐)

### 案卷模块 (Cases) - 2 items
- [ ] BE-03-19: 修复CSV导出 (当前返回JSON)
- [ ] 添加案卷搜索/过滤增强

### 账单模块 (Billing) - 2 items
- [ ] 自动更新案卷收款汇总on offset
- [ ] 实现账单状态转换
- [ ] 修复模板路径处理 (多个fallback)

### 文档模块 (Documents) - 1 item
- [ ] 添加文档搜索/过滤

### 任务模块 (Tasks) - 3 items
- [ ] 实现close/reopen/assign端点
- [ ] 添加任务状态转换验证
- [ ] 状态变更时自动创建task log

### 费用模块 (Fees) - 2 items
- [ ] 实现lock/unlock端点
- [ ] 添加费用费率管理

### 系统与模板 (System & Templates) - 5 items
- [ ] 创建模板管理schemas
- [ ] 实现模板CRUD端点
- [ ] 添加LetterHead管理
- [ ] 实现SystemParam CRUD
- [ ] 添加模板渲染服务抽象

### 基础设施 (Infrastructure) - 2 items
- [ ] 添加结构化日志
- [ ] 添加请求/响应日志中间件

### 数据库 (Database) - 1 item
- [ ] 添加外键约束

### 测试 (Testing) - 6 items
- [ ] 设置pytest结构
- [ ] 创建测试fixtures (DB, auth, clients)
- [ ] 为服务层编写单元测试
- [ ] 为关键流程编写集成测试
- [ ] 添加测试覆盖率报告
- [ ] 为测试添加CI/CD pipeline

### 文档 (Documentation) - 5 items
- [ ] 为端点添加docstrings和示例
- [ ] 创建API使用指南
- [ ] 文档化环境变量
- [ ] 创建部署runbook
- [ ] 文档化错误码

**P1小计: 29项 | 预估工作量: 15-20天**

---

## 📋 P2 - MEDIUM (中优先级，后续优化)

### 基础设施 (Infrastructure) - 1 item
- [ ] 添加correlation ID用于请求追踪

### 测试 (Testing) - 1 item
- [ ] 添加性能测试

### 文档 (Documentation) - 1 item
- [ ] 创建数据库schema图

**P2小计: 3项 | 预估工作量: 2-3天**

---

## 📊 统计汇总

| 优先级 | 项目数 | 工作量估计 | 完成状态 |
|--------|--------|------------|----------|
| P0 (Critical) | 60 | 25-30天 | ☐ 0% |
| P1 (High) | 29 | 15-20天 | ☐ 0% |
| P2 (Medium) | 3 | 2-3天 | ☐ 0% |
| **总计** | **92** | **42-53天** | **☐ 0%** |

---

## 🎯 推荐行动计划

### 第1阶段: 关键基础 (10-12天)
**目标**: 完成P0项目以解锁MVP1

#### 第1周: 认证、RBAC、核心基础设施
- [ ] 所有BE-00-* 任务 (errors, pagination, storage, security)
- [ ] 所有BE-01-* 任务 (auth, RBAC, permissions)
- **交付物**: 工作中的认证系统、权限系统、错误处理

#### 第2周: 服务层与Schemas
- [ ] 所有模块: 创建Pydantic schemas
- [ ] 所有模块: 实现服务层
- [ ] 将业务逻辑从API层移出
- **交付物**: 分层架构完整、所有端点有schemas

### 第2阶段: 功能完成 (12-15天)
**目标**: 按scope文档完成MVP1功能集

#### 第3-4周: 业务逻辑与验证
- [ ] Cases: 申请人验证、优先权日期计算
- [ ] Billing: 核销逻辑、余额更新
- [ ] Tasks: 状态转换、日志记录
- [ ] Fees: 草案锁定
- **交付物**: 所有业务规则实现

### 第3阶段: 质量与部署 (8-10天)

#### 第5周: 测试与文档
- [ ] 所有服务的单元测试
- [ ] 关键流程的集成测试
- [ ] API文档
- **交付物**: >70%测试覆盖率、完整API文档

#### 第6周: 部署准备
- [ ] 数据库迁移
- [ ] 种子数据脚本
- [ ] 部署指南
- **交付物**: 生产就绪系统

---

## ⏱️ 时间线总结

```
当前状态: ~30% MVP1完成
P0完成后: ~75% MVP1完成 (可发布alpha)
P1完成后: ~95% MVP1完成 (生产就绪)
P2完成后: ~100% MVP1完成 (优化完成)

总估计: 6-8周全职开发
```

---

## 🔗 快速链接

- [详细审查报告](file:///Users/cfcc/.gemini/antigravity/brain/2a568481-c30f-4d1f-957f-274264d37156/mvp1_backend_review_report.md)
- [原子任务列表](file:///Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/backend_tasks_atomic.md)
- [MVP1范围](file:///Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/00_mvp1_scope.md)
- [后端架构](file:///Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/04_backend_architecture.md)

---

**最后更新**: 2026-01-03
