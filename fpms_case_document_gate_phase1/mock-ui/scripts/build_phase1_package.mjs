import fs from "node:fs";
import path from "node:path";

const scriptDir = path.dirname(new URL(import.meta.url).pathname);
const mockDir = path.resolve(scriptDir, "..");
const rootDir = path.resolve(mockDir, "..");

const pages = [
  {
    id: "01",
    file: "01_01_case_dashboard.html",
    title: "案件工作台总览",
    short: "案件工作台",
    principle: "按案卷聚合今日风险：缺材料、待确认影响、未归档文件都回到案卷处理。",
    image: "01_01_case_dashboard",
    summary: "把文件风险、文书事件待确认、最终材料缺口并入案件工作台。",
    content: `
      <section class="hero">
        <div>
          <div class="eyebrow">今日工作台</div>
          <h1>案件工作台总览</h1>
          <p>主入口仍是案卷，但每个风险都能追溯到具体文件、文书事件和待执行动作。</p>
        </div>
        <button class="btn primary">处理最高风险</button>
      </section>
      <section class="metric-grid">
        <div class="metric"><b>18</b><span>有材料缺口案卷</span></div>
        <div class="metric warn"><b>6</b><span>影响预览待确认</span></div>
        <div class="metric danger"><b>2</b><span>递交硬阻止</span></div>
        <div class="metric ok"><b>31</b><span>今日可推进案卷</span></div>
      </section>
      <section class="grid two">
        <div class="card">
          <h2>文件驱动风险队列</h2>
          <table class="data-table">
            <thead><tr><th>案卷号</th><th>当前节点</th><th>风险来源</th><th>下一动作</th><th>负责人</th></tr></thead>
            <tbody>
              <tr><td>25F0411CN</td><td>撰写准备</td><td><span class="tag warn">委托书待补</span></td><td>生成补件任务</td><td>王律师</td></tr>
              <tr><td>25F0413CN</td><td>递交</td><td><span class="tag danger">最终外观图缺失</span></td><td>补齐最终稿</td><td>李流程</td></tr>
              <tr><td>25F0408CN</td><td>来文处理</td><td><span class="tag review">终止通知待确认</span></td><td>确认影响计划</td><td>赵律师</td></tr>
            </tbody>
          </table>
        </div>
        <div class="card">
          <h2>待确认影响计划</h2>
          <div class="stack">
            <div class="event-card">
              <b>第一次审查意见通知书</b>
              <span>将生成答复时限任务，状态从实审进入一通。</span>
              <em>来源文件已核验</em>
            </div>
            <div class="event-card">
              <b>专利权终止通知</b>
              <span>需要律师确认是否进入恢复决策流程。</span>
              <em>特殊规则</em>
            </div>
          </div>
        </div>
      </section>
      <section class="card">
        <h2>案卷与文件状态看板</h2>
        <div class="lane-board">
          <div><b>已收到未识别</b><span>4 个文件包</span></div>
          <div><b>已识别待核验</b><span>9 份文件</span></div>
          <div><b>已核验待事件化</b><span>5 份官方来文</span></div>
          <div><b>已形成文书事件</b><span>12 条今日新增</span></div>
        </div>
      </section>
    `,
  },
  {
    id: "02",
    file: "02_02_new_case_intake_files.html",
    title: "新建案卷 - 收案文件",
    short: "新建案卷·收案文件",
    principle: "先记录收案文件包，再拆分真实文件；建案只是文件包归入案卷的一个动作。",
    image: "02_02_new_case_intake_files",
    summary: "新案从客户邮件、委托文件和申请材料开始，先落文件包和文件状态。",
    content: `
      <section class="hero">
        <div>
          <div class="eyebrow">新建案卷 · 第 1 步</div>
          <h1>收案文件包</h1>
          <p>一封客户邮件或一个上传批次先作为文件包保存；文件识别和案卷归属可以在同一向导内完成。</p>
        </div>
        <button class="btn primary">继续核验材料</button>
      </section>
      <section class="grid two">
        <div class="card">
          <h2>收案来源</h2>
          <div class="form-grid">
            <label>来源类型<input value="客户邮件"></label>
            <label>收件日期<input value="2026-04-21"></label>
            <label>客户<input value="ABC科技有限公司"></label>
            <label>客户案号<input value="ABC-2026-001"></label>
            <label class="wide">主题<input value="高效电池管理方法新申请委托"></label>
            <label class="wide">处理备注<input value="客户要求尽快递交，委托书后补。"></label>
          </div>
        </div>
        <div class="card drop-card">
          <h2>上传申请文件</h2>
          <div class="drop-zone">
            <b>拖拽邮件、压缩包或单个文件到这里</b>
            <span>支持 PDF、DOCX、XML、EML、ZIP；系统先保存为不可变文件资产。</span>
            <button class="btn primary">选择文件</button>
          </div>
          <table class="data-table compact">
            <thead><tr><th>文件名</th><th>类型建议</th><th>文件状态</th><th>使用角色</th></tr></thead>
            <tbody>
              <tr><td>客户委托邮件.eml</td><td>客户指示</td><td><span class="tag ok">已识别</span></td><td>来源证据</td></tr>
              <tr><td>说明书.docx</td><td>说明书</td><td><span class="tag ok">已识别</span></td><td>收案稿</td></tr>
              <tr><td>权利要求书.docx</td><td>权利要求书</td><td><span class="tag ok">已识别</span></td><td>收案稿</td></tr>
              <tr><td>摘要.docx</td><td>摘要</td><td><span class="tag ok">已识别</span></td><td>收案稿</td></tr>
              <tr><td>附图.pdf</td><td>附图</td><td><span class="tag ok">已识别</span></td><td>收案稿</td></tr>
            </tbody>
          </table>
        </div>
      </section>
      <section class="notice warn"><b>材料完整度 5/7</b><span>缺委托书、费用减缴证明。允许建案，但递交前必须重新检查最终递交材料。</span></section>
    `,
  },
  {
    id: "03",
    file: "03_03_new_case_document_checklist.html",
    title: "新建案卷 - 文件核验清单",
    short: "文件核验清单",
    principle: "门禁检查的是要求项是否被合格文件满足，而不是简单统计上传数量。",
    image: "03_03_new_case_document_checklist",
    summary: "材料清单细化到要求项、文件角色、文件状态和后续动作。",
    content: `
      <section class="hero">
        <div>
          <div class="eyebrow">新建案卷 · 第 3 步</div>
          <h1>文件核验清单</h1>
          <p>清单由案件类型、专利类型、流向和流程节点共同决定；每一项都记录满足它的文件和核验状态。</p>
        </div>
        <button class="btn primary">保存核验结果</button>
      </section>
      <section class="card">
        <h2>收案节点要求</h2>
        <table class="data-table">
          <thead><tr><th>要求项</th><th>要求级别</th><th>匹配文件</th><th>文件状态</th><th>门禁结果</th><th>动作</th></tr></thead>
          <tbody>
            <tr><td>客户指示</td><td>必需</td><td>客户委托邮件.eml</td><td><span class="tag ok">已核验</span></td><td><span class="tag ok">通过</span></td><td>查看</td></tr>
            <tr><td>说明书</td><td>必需</td><td>说明书.docx</td><td><span class="tag ok">已核验</span></td><td><span class="tag ok">通过</span></td><td>查看版本</td></tr>
            <tr><td>权利要求书</td><td>必需</td><td>权利要求书.docx</td><td><span class="tag ok">已核验</span></td><td><span class="tag ok">通过</span></td><td>查看版本</td></tr>
            <tr><td>摘要</td><td>必需</td><td>摘要.docx</td><td><span class="tag ok">已核验</span></td><td><span class="tag ok">通过</span></td><td>查看</td></tr>
            <tr><td>附图</td><td>条件必需</td><td>附图.pdf</td><td><span class="tag ok">已核验</span></td><td><span class="tag ok">通过</span></td><td>查看</td></tr>
            <tr><td>委托书</td><td>递交前必需</td><td>未匹配</td><td><span class="tag warn">待补</span></td><td><span class="tag warn">软通过</span></td><td>生成补件任务</td></tr>
            <tr><td>费用减缴证明</td><td>可选</td><td>未匹配</td><td><span class="tag muted">未提供</span></td><td><span class="tag muted">不阻止</span></td><td>标记不申请</td></tr>
          </tbody>
        </table>
      </section>
      <section class="grid three">
        <div class="card small"><h3>门禁快照</h3><b>软通过</b><span>可创建案卷，不允许直接递交。</span></div>
        <div class="card small"><h3>缺失任务</h3><b>1 项</b><span>补交委托书，默认期限 2026-05-05。</span></div>
        <div class="card small"><h3>非闭合范围</h3><b>不生成递交稿</b><span>最终材料在递交节点重新核验。</span></div>
      </section>
    `,
  },
  {
    id: "04",
    file: "04_04_new_case_creation_preview.html",
    title: "新建案卷 - 事件提交预览",
    short: "创建预览",
    principle: "建案前展示一次事务会落哪些对象；状态、任务、费用都由影响计划驱动。",
    image: "04_04_new_case_creation_preview",
    summary: "把建案动作表达为一个可审计的客户收案文书事件。",
    content: `
      <section class="hero">
        <div>
          <div class="eyebrow">新建案卷 · 第 6 步</div>
          <h1>事件提交预览</h1>
          <p>提交后会创建案卷、客户收案文书事件、文件关联和缺失材料任务；不会生成递交稿或递交状态。</p>
        </div>
        <button class="btn primary">创建案卷并归档收案文件</button>
      </section>
      <section class="grid two">
        <div class="card">
          <h2>将创建的业务事实</h2>
          <div class="timeline">
            <div><b>案卷主档</b><span>25F0411CN · 发明 · 中国内申请</span></div>
            <div><b>文书事件</b><span>客户新申请委托，事件类型 CLIENT_INTAKE。</span></div>
            <div><b>文件链路</b><span>5 份收案文件作为来源文件和收案稿归档。</span></div>
            <div><b>门禁快照</b><span>收案节点软通过，记录缺失委托书。</span></div>
          </div>
        </div>
        <div class="card">
          <h2>影响计划</h2>
          <table class="data-table compact">
            <tbody>
              <tr><th>案卷流程阶段</th><td>收案 → 撰写准备</td></tr>
              <tr><th>法律状态</th><td>不改变，仍为未递交</td></tr>
              <tr><th>客户服务状态</th><td>收案处理中</td></tr>
              <tr><th>任务</th><td>生成“补交委托书”任务</td></tr>
              <tr><th>费用</th><td>不生成费用草单</td></tr>
            </tbody>
          </table>
          <div class="notice"><b>幂等键</b><span>CLIENT_INTAKE:25F0411CN:20260421，防止重复建案事件。</span></div>
        </div>
      </section>
      <section class="notice danger"><b>明确非闭合</b><span>本步骤不递交、不生成最终申请文件、不触发官费时限。</span></section>
    `,
  },
  {
    id: "05",
    file: "05_05_case_workflow_document_dock.html",
    title: "案件详情 - 工作流与文件材料区",
    short: "案件详情·文件材料区",
    principle: "右侧不是普通附件列表，而是当前节点所需文件、满足状态和可执行动作。",
    image: "05_05_case_workflow_document_dock",
    summary: "案件详情页同时展示流程阶段、文件要求、门禁结果和可推进动作。",
    content: `
      <section class="case-header">
        <div>
          <h1>25F0411CN · 一种高效电池管理方法</h1>
          <p>客户：ABC科技有限公司 · 代理人：王律师</p>
        </div>
        <div class="status-strip">
          <span>申请状态：未递交</span><span>客户状态：收案处理中</span><span>文件完整度：5/7</span><span>待办：1</span>
        </div>
      </section>
      <section class="workflow-shell">
        <aside class="workflow">
          <h2>案件工作流</h2>
          <div class="node done">收案</div>
          <div class="node active">撰写准备</div>
          <div class="node">客户确认</div>
          <div class="node">递交</div>
          <div class="node">等待受理</div>
          <div class="node">审查阶段</div>
          <div class="node">授权/结案</div>
        </aside>
        <main class="card main-action">
          <h2>当前节点：撰写准备</h2>
          <table class="data-table compact">
            <tbody>
              <tr><th>下一建议</th><td>补齐委托书，同时准备最终递交稿。</td></tr>
              <tr><th>允许动作</th><td>继续撰写、上传补充文件、生成缺失任务。</td></tr>
              <tr><th>阻止动作</th><td>不允许直接执行递交。</td></tr>
              <tr><th>原因</th><td>递交节点要求最终说明书、权利要求书、摘要、附图和委托书均已核验。</td></tr>
            </tbody>
          </table>
          <div class="toolbar"><button class="btn primary">上传补充文件</button><button class="btn">准备最终材料</button><button class="btn">生成补件任务</button></div>
        </main>
        <aside class="card file-dock">
          <h2>当前节点文件材料</h2>
          <h3>已满足</h3>
          <ul class="check-list">
            <li>客户指示 · 已核验</li>
            <li>说明书收案稿 · 已核验</li>
            <li>权利要求书收案稿 · 已核验</li>
            <li>摘要 · 已核验</li>
            <li>附图 · 已核验</li>
          </ul>
          <h3>缺失/待补</h3>
          <ul class="warn-list">
            <li>委托书 · 递交前必需</li>
            <li>费用减缴证明 · 可选</li>
          </ul>
          <div class="notice warn"><b>门禁结论</b><span>允许撰写；递交前需重新检查最终稿。</span></div>
        </aside>
      </section>
    `,
  },
  {
    id: "06",
    file: "06_06_case_dossier_timeline.html",
    title: "案件详情 - 卷宗事件账本",
    short: "卷宗事件账本",
    principle: "时间线以文书事件为中心，每条事件都显示来源文件、影响计划和已落账效果。",
    image: "06_06_case_dossier_timeline",
    summary: "用卷宗事件账本替代普通附件表，支持审计和回放。",
    content: `
      <section class="hero">
        <div>
          <div class="eyebrow">案卷详情</div>
          <h1>卷宗事件账本</h1>
          <p>文件不直接改案件；文件形成文书事件，文书事件确认后才落状态、任务、费用和文件状态。</p>
        </div>
        <button class="btn primary">登记新事件</button>
      </section>
      <section class="timeline ledger">
        <div>
          <b>客户新申请委托</b>
          <span>来源：客户委托邮件.eml、说明书.docx、权利要求书.docx。影响：客户状态变为收案处理中，生成补委托书任务。</span>
          <em>已落账 · 2026-04-21 · 幂等键 CLIENT_INTAKE:25F0411CN</em>
        </div>
        <div>
          <b>补交委托书</b>
          <span>来源：委托书签章版.pdf。影响：委托书要求项变为已满足，补件任务自动完成。</span>
          <em>待确认 · 来源文件已核验</em>
        </div>
        <div>
          <b>递交清单</b>
          <span>来源：最终递交材料包。影响：申请状态从未递交变为等待受理，生成申请费时限任务。</span>
          <em>未发生 · 等待递交门禁通过</em>
        </div>
      </section>
      <section class="grid two">
        <div class="card"><h2>关联文件状态</h2><table class="data-table compact"><tbody>
          <tr><td>说明书.docx</td><td>收案稿</td><td><span class="tag ok">已归档</span></td></tr>
          <tr><td>说明书-最终稿.docx</td><td>最终递交稿</td><td><span class="tag warn">待客户确认</span></td></tr>
          <tr><td>委托书签章版.pdf</td><td>递交前必需</td><td><span class="tag review">待确认</span></td></tr>
        </tbody></table></div>
        <div class="card"><h2>审计摘要</h2><div class="audit-list"><span>每次影响计划保留提交人、确认人、覆盖原因。</span><span>重复上传同一文件只新增文件状态，不重复生成任务。</span><span>特殊规则必须人工确认后落账。</span></div></div>
      </section>
    `,
  },
  {
    id: "07",
    file: "07_07_batch_filing_material_gate.html",
    title: "案件递交 - 最终材料门禁",
    short: "递交材料门禁",
    principle: "递交检查的是最终递交稿和签章材料，不是收案时上传过什么。",
    image: "07_07_batch_filing_material_gate",
    summary: "批量递交保留，但按最终材料门禁自动分组通过、警告和阻止。",
    content: `
      <section class="hero">
        <div>
          <div class="eyebrow">案件递交批处理</div>
          <h1>最终材料门禁</h1>
          <p>执行递交前检查最终稿、客户确认、委托书、附图/外观图等递交材料；阻止项不会进入本批次。</p>
        </div>
        <button class="btn primary">执行可递交案件</button>
      </section>
      <section class="card">
        <h2>递交候选案件</h2>
        <table class="data-table">
          <thead><tr><th>选择</th><th>案卷号</th><th>名称</th><th>最终材料</th><th>缺失项</th><th>门禁结论</th><th>处理</th></tr></thead>
          <tbody>
            <tr><td><input type="checkbox" checked></td><td>25F0411CN</td><td>一种高效电池管理方法</td><td>6/7</td><td>委托书</td><td><span class="tag warn">允许后补</span></td><td>查看材料</td></tr>
            <tr><td><input type="checkbox" checked></td><td>25F0412CN</td><td>图像识别装置</td><td>7/7</td><td>无</td><td><span class="tag ok">可递交</span></td><td>查看材料</td></tr>
            <tr><td><input type="checkbox" disabled></td><td>25F0413CN</td><td>外观设计 A</td><td>3/5</td><td>最终外观图</td><td><span class="tag danger">不可递交</span></td><td>补文件</td></tr>
            <tr><td><input type="checkbox" checked></td><td>25F0414CN</td><td>通信协议优化方法</td><td>6/6</td><td>无</td><td><span class="tag ok">可递交</span></td><td>查看材料</td></tr>
          </tbody>
        </table>
      </section>
      <section class="grid two">
        <div class="card"><h2>递交参数</h2><table class="data-table compact"><tbody>
          <tr><th>递交日期</th><td>2026-04-22</td></tr>
          <tr><th>同时提实审</th><td>是</td></tr>
          <tr><th>生成递交清单</th><td>是</td></tr>
          <tr><th>本批次</th><td>3 件可执行，其中 1 件带后补审计</td></tr>
        </tbody></table></div>
        <div class="card"><h2>执行预览</h2><div class="impact-list">
          <span>申请状态：未递交 → 等待受理</span>
          <span>生成：递交清单文书事件、申请费时限任务</span>
          <span class="danger-text">阻止：25F0413CN 缺最终外观图</span>
        </div></div>
      </section>
    `,
  },
  {
    id: "08",
    file: "08_08_case_document_registration.html",
    title: "案内登记来文 - 影响预览",
    short: "案内登记来文",
    principle: "官方来文必须绑定来源文件；提交前先形成影响计划，由用户确认后再落账。",
    image: "08_08_case_document_registration",
    summary: "中间文件登记从案卷进入，来源文件和影响预览成为提交门禁。",
    content: `
      <section class="hero">
        <div>
          <div class="eyebrow">案件内文书登记</div>
          <h1>官方来文影响预览</h1>
          <p>登记来文时必须绑定已核验来源文件，系统试跑规则并展示状态、任务、费用和文件状态影响。</p>
        </div>
        <button class="btn primary">确认并登记来文</button>
      </section>
      <section class="grid two">
        <div class="card">
          <h2>文书事件信息</h2>
          <div class="form-grid">
            <label>方向<input value="官方来文"></label>
            <label>文书类型<input value="第一次审查意见通知书"></label>
            <label>模板代码<input value="OA_NOTICE"></label>
            <label>发文日<input value="2026-03-01"></label>
            <label>官方绝限<input value="2026-07-01"></label>
            <label>来源文件<input value="第一次审查意见通知书.pdf"></label>
          </div>
          <div class="notice ok"><b>来源文件已核验</b><span>文件状态将从“已核验待事件化”变为“已形成文书事件”。</span></div>
        </div>
        <div class="card">
          <h2>影响计划</h2>
          <table class="data-table compact">
            <tbody>
              <tr><th>匹配规则</th><td>RULE-OA-NOTICE-01</td></tr>
              <tr><th>申请状态</th><td>实审 → 一通</td></tr>
              <tr><th>客户状态</th><td>实审 → 一通待转达</td></tr>
              <tr><th>任务</th><td>生成 OA 答复时限任务</td></tr>
              <tr><th>费用</th><td>不生成；答复提交时再计费</td></tr>
              <tr><th>确认要求</th><td>普通规则，流程人员可确认</td></tr>
            </tbody>
          </table>
        </div>
      </section>
      <section class="card">
        <h2>特殊规则提示</h2>
        <div class="lane-board">
          <div><b>专利证书</b><span>只改客户服务状态为领证，不重复生成授权费。</span></div>
          <div><b>专利权终止通知</b><span>必须律师确认，可能生成恢复决策任务。</span></div>
          <div><b>延长期限审批通知</b><span>只提示调整时限，不自动改案件状态。</span></div>
        </div>
      </section>
    `,
  },
  {
    id: "09",
    file: "09_09_unfiled_file_tray.html",
    title: "待归档文件 - 辅助队列",
    short: "待归档文件",
    principle: "待归档文件只负责把游离文件送回案卷动作，不成为第二条业务主线。",
    image: "09_09_unfiled_file_tray",
    summary: "未归档文件包按建议动作跳转到新建案卷、案内登记来文或补充材料。",
    content: `
      <section class="hero">
        <div>
          <div class="eyebrow">辅助队列</div>
          <h1>待归档文件</h1>
          <p>这里处理先上传、扫描批次、历史导入和未来邮件下载文件；所有处理动作都回到案卷流程。</p>
        </div>
        <button class="btn primary">批量识别</button>
      </section>
      <section class="card">
        <h2>游离文件包</h2>
        <table class="data-table">
          <thead><tr><th>来源</th><th>主题/批次</th><th>文件数</th><th>建议动作</th><th>可信度</th><th>入口</th></tr></thead>
          <tbody>
            <tr><td>客户邮件</td><td>高效电池管理方法新申请</td><td>5</td><td>创建新案卷</td><td><span class="tag ok">高</span></td><td>进入新建案卷</td></tr>
            <tr><td>扫描批次</td><td>官方通知书 20260422</td><td>12</td><td>案内登记来文</td><td><span class="tag warn">中</span></td><td>匹配案卷</td></tr>
            <tr><td>历史导入</td><td>授权证书补录</td><td>3</td><td>登记证书事件</td><td><span class="tag review">需复核</span></td><td>选择案卷</td></tr>
          </tbody>
        </table>
      </section>
      <section class="grid three">
        <div class="card small"><h3>允许动作</h3><span>创建案卷、案内登记来文、补充已有案卷材料。</span></div>
        <div class="card small"><h3>不允许动作</h3><span>不在此直接改状态、生成费用或关闭任务。</span></div>
        <div class="card small"><h3>审计要求</h3><span>每次匹配都保留来源文件包和操作者。</span></div>
      </section>
    `,
  },
  {
    id: "10",
    file: "10_10_doc_status_rule_matrix.html",
    title: "状态规则矩阵 - 试跑器",
    short: "规则矩阵",
    principle: "规则管理拆成匹配规则和效果项；管理员维护，普通用户只看到提交前试跑结果。",
    image: "10_10_doc_status_rule_matrix",
    summary: "状态规则矩阵增加试跑器，避免一行规则同时承担太多副作用。",
    content: `
      <section class="hero">
        <div>
          <div class="eyebrow">系统设置</div>
          <h1>状态规则矩阵与试跑器</h1>
          <p>文书事件先匹配规则，再展开状态效果、任务效果、费用效果和文件效果；每个效果都有幂等键。</p>
        </div>
        <button class="btn primary">新建规则</button>
      </section>
      <section class="card">
        <h2>规则列表</h2>
        <table class="data-table">
          <thead><tr><th>规则</th><th>文书事件</th><th>状态效果</th><th>任务效果</th><th>费用效果</th><th>确认</th></tr></thead>
          <tbody>
            <tr><td>RULE-OA-NOTICE-01</td><td>OA_NOTICE</td><td>申请状态 → 一通</td><td>OA 答复时限</td><td>无</td><td>否</td></tr>
            <tr><td>RULE-GRANT-NOTICE-01</td><td>GRANT_NOTICE</td><td>申请状态 → 待授权缴费</td><td>授权费时限</td><td>授权费草单</td><td>否</td></tr>
            <tr><td>RULE-CERT-CLIENT-01</td><td>PATENT_CERTIFICATE</td><td>客户状态 → 领证</td><td>证书转达</td><td>不重复</td><td>是</td></tr>
            <tr><td>RULE-RIGHT-TERM-01</td><td>RIGHT_TERMINATION_NOTICE</td><td>权利状态 → 终止</td><td>恢复决策</td><td>无</td><td>是</td></tr>
          </tbody>
        </table>
      </section>
      <section class="grid two">
        <div class="card">
          <h2>规则试跑</h2>
          <table class="data-table compact"><tbody>
            <tr><th>输入文件</th><td>专利证书.pdf</td></tr>
            <tr><th>当前状态</th><td>申请状态：授权；客户状态：授权；权利状态：有效</td></tr>
            <tr><th>匹配规则</th><td>RULE-CERT-CLIENT-01</td></tr>
          </tbody></table>
        </div>
        <div class="card">
          <h2>试跑结果</h2>
          <div class="impact-list">
            <span>申请状态保持授权</span>
            <span>客户状态变为领证</span>
            <span>生成证书转达任务</span>
            <span>不生成授权费草单</span>
            <span class="warn-text">需要人工确认</span>
          </div>
        </div>
      </section>
    `,
  },
];

const requirementRows = [
  ["NORMAL", "INV", "CN_DOMESTIC", "INTAKE", "REQ-INTAKE-CLIENT-INSTRUCTION", "CLIENT_INSTRUCTION", "SOURCE_FILE", "REQUIRED", "", "", "INTAKE_CREATE", "true", "false", "客户指示或客户委托邮件是建案事实来源。"],
  ["NORMAL", "INV", "CN_DOMESTIC", "INTAKE", "REQ-INTAKE-SPECIFICATION", "SPECIFICATION", "INTAKE_DRAFT", "REQUIRED", "", "", "INTAKE_CREATE", "true", "false", "建案时可为收案稿，递交前必须有最终稿。"],
  ["NORMAL", "INV", "CN_DOMESTIC", "INTAKE", "REQ-INTAKE-CLAIMS", "CLAIMS", "INTAKE_DRAFT", "REQUIRED", "", "", "INTAKE_CREATE", "true", "false", "建案时可为收案稿，递交前必须有最终稿。"],
  ["NORMAL", "INV", "CN_DOMESTIC", "INTAKE", "REQ-INTAKE-ABSTRACT", "ABSTRACT", "INTAKE_DRAFT", "REQUIRED", "", "", "INTAKE_CREATE", "true", "false", "摘要可在撰写阶段替换为最终稿。"],
  ["NORMAL", "INV", "CN_DOMESTIC", "INTAKE", "REQ-INTAKE-DRAWINGS", "DRAWINGS", "INTAKE_DRAFT", "CONDITIONAL", "has_drawings=true", "", "INTAKE_CREATE", "true", "false", "有附图时必须核验。"],
  ["NORMAL", "INV", "CN_DOMESTIC", "FILING", "REQ-FILING-SPECIFICATION-FINAL", "SPECIFICATION", "FINAL_FILING_COPY", "REQUIRED_BEFORE_ACTION", "", "", "BATCH_FILING", "false", "true", "递交门禁检查最终递交稿。"],
  ["NORMAL", "INV", "CN_DOMESTIC", "FILING", "REQ-FILING-CLAIMS-FINAL", "CLAIMS", "FINAL_FILING_COPY", "REQUIRED_BEFORE_ACTION", "", "", "BATCH_FILING", "false", "true", "递交门禁检查最终递交稿。"],
  ["NORMAL", "INV", "CN_DOMESTIC", "FILING", "REQ-FILING-POA", "POWER_OF_ATTORNEY", "SIGNED_AUTHORIZATION", "ALLOW_LATER", "", "SUPPLEMENT_POA", "BATCH_FILING", "false", "true", "允许后补时必须写审计原因。"],
  ["NORMAL", "DES", "CN_DOMESTIC", "FILING", "REQ-FILING-DESIGN-VIEWS", "DESIGN_DRAWINGS", "FINAL_FILING_COPY", "REQUIRED_BEFORE_ACTION", "", "", "BATCH_FILING", "false", "true", "外观设计最终视图缺失时硬阻止递交。"],
];

const statusRuleRows = [
  ["RULE-OA-NOTICE-01", "OFFICIAL_INCOMING", "OA_NOTICE", "OFFICIAL_NOTICE", "第一次审查意见通知书", "SET_EFFECTS", "APPLICATION_STATUS:SUB_EXAM>OA1|CLIENT_SERVICE_STATUS:SUB_EXAM>OA_PENDING_CLIENT_FORWARD", "CREATE_TASK:OA_REPLY_LIMIT", "NONE", "SOURCE_FILE:EVENTIZED", "DOC_EVENT:OA_NOTICE:{case_id}:{doc_date}", "false", "100", "true", "普通 OA 来文登记。"],
  ["RULE-GRANT-NOTICE-01", "OFFICIAL_INCOMING", "GRANT_NOTICE", "OFFICIAL_NOTICE", "授权通知书", "SET_EFFECTS", "APPLICATION_STATUS:SUB_EXAM>GRANT_PENDING|CLIENT_SERVICE_STATUS:SUB_EXAM>GRANT_NOTICE_RECEIVED", "CREATE_TASK:GRANT_FEE_LIMIT", "CREATE_FEE_DRAFT:GRANT_FEE", "SOURCE_FILE:EVENTIZED", "DOC_EVENT:GRANT_NOTICE:{case_id}:{doc_date}", "false", "90", "true", "授权通知会生成缴费相关动作。"],
  ["RULE-CERT-CLIENT-01", "OFFICIAL_INCOMING", "PATENT_CERTIFICATE", "CERTIFICATE", "专利证书", "SET_EFFECTS", "APPLICATION_STATUS:GRANTED>GRANTED|CLIENT_SERVICE_STATUS:GRANTED>CERTIFICATE_RECEIVED", "CREATE_TASK:CERTIFICATE_FORWARD_TASK", "NONE", "SOURCE_FILE:EVENTIZED", "DOC_EVENT:PATENT_CERTIFICATE:{case_id}:{file_hash}", "true", "80", "true", "证书只改变客户服务状态，不重复生成授权费。"],
  ["RULE-RIGHT-TERM-01", "OFFICIAL_INCOMING", "RIGHT_TERMINATION_NOTICE", "OFFICIAL_NOTICE", "专利权终止通知", "MANUAL_CONFIRM_REQUIRED", "RIGHTS_STATUS:ACTIVE>TERMINATED|CLIENT_SERVICE_STATUS:ACTIVE>TERMINATION_NOTICE_RECEIVED", "CREATE_TASK:RESTORE_DECISION_TASK", "NONE", "SOURCE_FILE:EVENTIZED", "DOC_EVENT:RIGHT_TERMINATION_NOTICE:{case_id}:{doc_date}", "true", "70", "true", "终止类文书必须律师确认。"],
  ["RULE-ANNUITY-NOTICE-01", "OFFICIAL_INCOMING", "ANNUITY_PAYMENT_NOTICE", "OFFICIAL_NOTICE", "年费缴费通知书", "SET_EFFECTS", "NO_STATUS_CHANGE", "LINK_TASK:ANNUITY_PAYMENT", "NONE", "SOURCE_FILE:EVENTIZED", "DOC_EVENT:ANNUITY_PAYMENT_NOTICE:{case_id}:{doc_date}", "false", "60", "true", "年费通知只关联年费任务。"],
  ["RULE-EXTENSION-APPROVAL-01", "OFFICIAL_INCOMING", "EXTENSION_APPROVAL", "OFFICIAL_NOTICE", "延长期限审批通知书", "REVIEW_ONLY", "NO_STATUS_CHANGE", "SUGGEST_TASK_UPDATE:DEADLINE", "NONE", "SOURCE_FILE:EVENTIZED", "DOC_EVENT:EXTENSION_APPROVAL:{case_id}:{doc_date}", "true", "50", "true", "只提示调整时限，不自动覆盖。"],
];

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function write(rel, content) {
  const filePath = path.join(rootDir, rel);
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, `${content.trim()}\n`, "utf8");
}

function csvEscape(value) {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function toCsv(headers, rows) {
  return [headers.join(","), ...rows.map((row) => row.map(csvEscape).join(","))].join("\n");
}

const nav = pages
  .map((page) => `<a href="${page.file}" class="{{ACTIVE_${page.id}}}">${page.id} ${page.short}</a>`)
  .join("\n");

function pageHtml(page) {
  const activeNav = nav.replace(`{{ACTIVE_${page.id}}}`, "active").replace(/\{\{ACTIVE_\d+\}\}/g, "");
  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${page.id} ${page.title}</title>
<link rel="stylesheet" href="../assets/styles.css">
</head>
<body>
<div class="app">
  <aside class="side">
    <div class="logo">FPMS</div>
    <div class="logo-sub">案卷主线 + 文件门禁</div>
    <nav class="nav">${activeNav}</nav>
    <div class="principle"><b>页面定位</b>${page.principle}</div>
  </aside>
  <main class="main">${page.content}</main>
</div>
</body>
</html>`;
}

function indexHtml(prefix = "") {
  const cardHtml = pages
    .map(
      (page) => `<section id="s${page.id}" class="screen-card">
  <h2>${page.id} ${page.title}<span class="badge">原型 ${page.id}</span></h2>
  <p>${page.summary}</p>
  <a href="${prefix}mock-ui/pages/${page.file}"><img src="${prefix}mock-ui/screens/${page.image}.png" alt="${page.id} ${page.title}"></a>
</section>`,
    )
    .join("\n\n");
  const toc = pages.map((page) => `<a href="#s${page.id}">${page.id} ${page.title}</a>`).join("\n");
  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FPMS 案卷主线 + 文件门禁原型</title>
<link rel="stylesheet" href="${prefix}mock-ui/assets/styles.css">
</head>
<body>
<div class="app">
  <aside class="side">
    <div class="logo">FPMS</div>
    <div class="logo-sub">案卷主线 + 文件门禁</div>
    <nav class="nav">${toc}</nav>
    <div class="principle"><b>核心定位</b>文件不是另一个主流程，而是案卷动作的输入、证据、门禁和审计线索。</div>
  </aside>
  <main class="main">
    <section class="hero">
      <div>
        <div class="eyebrow">第一阶段设计包</div>
        <h1>案卷主线 + 文件门禁</h1>
        <p>本版把文件驱动落到文书事件、门禁快照、影响计划和效果账本，避免只在案件工作流上贴一层附件检查。</p>
      </div>
      <a class="btn primary" href="${prefix}FPMS_案卷主线_文件门禁增强方案_Phase1.md">查看方案</a>
    </section>
    <div class="index-grid">
      <div>${cardHtml}</div>
      <aside class="toc">
        <h3>页面目录</h3>
        ${toc}
        <div class="note">
          <h3>推荐评审顺序</h3>
          02 → 03 → 04 → 05 → 08 → 06 → 07 → 09 → 10。先看收案如何形成文件资产，再看文书事件如何驱动状态、任务和费用。
        </div>
      </aside>
    </div>
  </main>
</div>
</body>
</html>`;
}

const styles = `
:root {
  --bg: #f5f7fb;
  --panel: #ffffff;
  --text: #0f172a;
  --muted: #667085;
  --line: #d7dee9;
  --nav: #111827;
  --primary: #1f5eff;
  --primary-soft: #e8efff;
  --ok: #14945d;
  --ok-bg: #e7f7ef;
  --warn: #b7791f;
  --warn-bg: #fff4cf;
  --danger: #c2413a;
  --danger-bg: #ffe6e4;
  --review: #6d5bd0;
  --review-bg: #eeeaff;
  --shadow: 0 14px 36px rgba(15, 23, 42, 0.08);
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Noto Sans CJK SC", "Microsoft YaHei", Arial, sans-serif; }
a { color: inherit; text-decoration: none; }
.app { display: grid; grid-template-columns: 236px 1fr; min-height: 100vh; }
.side { position: sticky; top: 0; height: 100vh; padding: 28px 14px 20px; background: var(--nav); color: #e5e7eb; }
.logo { padding: 0 10px; font-size: 30px; font-weight: 800; letter-spacing: 0; color: #fff; }
.logo-sub { padding: 0 10px; margin-top: 4px; color: #bdd7ff; font-size: 14px; }
.nav { display: grid; gap: 4px; margin-top: 28px; }
.nav a { padding: 10px 12px; border-radius: 8px; color: #d1d5db; font-size: 14px; line-height: 1.25; }
.nav a.active, .nav a:hover { color: #fff; background: #2254d6; }
.principle { position: absolute; left: 14px; right: 14px; bottom: 20px; padding: 14px; border: 1px solid #2857b8; border-radius: 8px; background: #182554; color: #c7d7ff; font-size: 13px; line-height: 1.55; }
.principle b { display: block; margin-bottom: 6px; color: #fff; }
.main { padding: 24px; min-width: 0; }
.hero, .case-header, .card, .screen-card, .toc, .notice, .metric, .node, .lane-board > div { border: 1px solid var(--line); border-radius: 8px; background: var(--panel); box-shadow: var(--shadow); }
.hero { display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 22px 24px; margin-bottom: 20px; }
.hero h1, .case-header h1 { margin: 2px 0 8px; font-size: 28px; line-height: 1.2; }
.hero p, .case-header p, .screen-card p { margin: 0; color: var(--muted); line-height: 1.7; }
.eyebrow { color: var(--primary); font-size: 13px; font-weight: 700; }
.btn { display: inline-flex; align-items: center; justify-content: center; min-height: 38px; padding: 9px 14px; border: 1px solid #c5cfdd; border-radius: 8px; background: #fff; color: #243247; font-weight: 700; white-space: nowrap; }
.btn.primary { border-color: var(--primary); background: var(--primary); color: #fff; }
.toolbar { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 18px; }
.grid { display: grid; gap: 20px; align-items: start; }
.grid.two { grid-template-columns: 1fr 1fr; }
.grid.three, .metric-grid { grid-template-columns: repeat(3, 1fr); }
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.metric { padding: 18px; box-shadow: none; }
.metric b { display: block; margin-bottom: 4px; font-size: 30px; }
.metric span { color: var(--muted); }
.metric.ok b { color: var(--ok); }
.metric.warn b { color: var(--warn); }
.metric.danger b { color: var(--danger); }
.card { padding: 20px; }
.card h2 { margin: 0 0 14px; font-size: 20px; }
.card h3 { margin: 14px 0 8px; font-size: 15px; }
.card.small { min-height: 122px; }
.card.small b { display: block; margin: 10px 0 6px; font-size: 24px; }
.card.small span { color: var(--muted); line-height: 1.6; }
.data-table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 14px; }
.data-table th { color: #334155; background: #f3f6fa; text-align: left; font-weight: 700; }
.data-table th, .data-table td { padding: 12px 10px; border-bottom: 1px solid #e2e8f0; vertical-align: top; overflow-wrap: anywhere; }
.data-table.compact th, .data-table.compact td { padding: 10px; }
.tag { display: inline-flex; align-items: center; min-height: 24px; padding: 3px 8px; border-radius: 999px; background: #eef2f7; color: #445066; font-weight: 700; font-size: 12px; }
.tag.ok { color: var(--ok); background: var(--ok-bg); }
.tag.warn { color: var(--warn); background: var(--warn-bg); }
.tag.danger { color: var(--danger); background: var(--danger-bg); }
.tag.review { color: var(--review); background: var(--review-bg); }
.tag.muted { color: #667085; background: #eef2f7; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-grid label { display: grid; gap: 6px; color: #52627a; font-size: 13px; font-weight: 700; }
.form-grid label.wide { grid-column: 1 / -1; }
input { width: 100%; height: 38px; padding: 0 12px; border: 1px solid #cbd5e1; border-radius: 8px; background: #f8fafc; color: #182338; font: inherit; }
.drop-zone { display: grid; gap: 10px; place-items: center; min-height: 138px; margin-bottom: 18px; border: 2px dashed var(--primary); border-radius: 8px; background: var(--primary-soft); text-align: center; }
.drop-zone span { color: var(--muted); }
.notice { display: flex; gap: 12px; align-items: flex-start; padding: 14px 16px; margin-top: 18px; box-shadow: none; }
.notice b { min-width: 96px; }
.notice span { color: #344054; line-height: 1.6; }
.notice.warn { border-color: #f6d77b; background: var(--warn-bg); }
.notice.danger { border-color: #ffbbb7; background: var(--danger-bg); }
.notice.ok { border-color: #a7e4c4; background: var(--ok-bg); }
.stack { display: grid; gap: 12px; }
.event-card { display: grid; gap: 5px; padding: 14px; border: 1px solid #e2e8f0; border-radius: 8px; background: #f8fafc; }
.event-card span, .event-card em { color: var(--muted); font-style: normal; line-height: 1.55; }
.event-card em { color: var(--primary); font-weight: 700; }
.lane-board { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.lane-board > div { padding: 14px; box-shadow: none; background: #f8fafc; }
.lane-board b { display: block; margin-bottom: 6px; }
.lane-board span { color: var(--muted); line-height: 1.55; }
.case-header { display: grid; gap: 14px; padding: 22px 24px; margin-bottom: 20px; }
.status-strip { display: flex; flex-wrap: wrap; gap: 10px; }
.status-strip span { padding: 7px 10px; border-radius: 999px; background: #edf2f7; color: #344054; font-weight: 700; font-size: 13px; }
.workflow-shell { display: grid; grid-template-columns: 300px 1fr 312px; gap: 20px; align-items: stretch; }
.workflow { display: grid; gap: 10px; padding: 20px; border: 1px solid var(--line); border-radius: 8px; background: #fff; box-shadow: var(--shadow); }
.workflow h2 { margin: 0 0 8px; font-size: 20px; }
.node { position: relative; padding: 10px 12px; box-shadow: none; color: #52627a; }
.node.done { color: var(--ok); background: var(--ok-bg); }
.node.active { color: var(--primary); background: var(--primary-soft); font-weight: 800; }
.main-action { min-height: 480px; }
.file-dock { min-height: 480px; }
.check-list, .warn-list { margin: 0 0 12px; padding-left: 20px; line-height: 1.85; }
.check-list li::marker { color: var(--ok); }
.warn-list li::marker { color: var(--warn); }
.timeline { display: grid; gap: 14px; }
.timeline > div { position: relative; display: grid; gap: 6px; padding: 16px 18px; border: 1px solid #e2e8f0; border-radius: 8px; background: #fff; }
.timeline > div b { font-size: 17px; }
.timeline > div span { color: #344054; line-height: 1.65; }
.timeline > div em { color: var(--muted); font-style: normal; font-weight: 700; }
.ledger { margin-bottom: 20px; }
.audit-list, .impact-list { display: grid; gap: 10px; color: #344054; line-height: 1.65; }
.danger-text { color: var(--danger); font-weight: 800; }
.warn-text { color: var(--warn); font-weight: 800; }
.index-grid { display: grid; grid-template-columns: 1fr 320px; gap: 22px; align-items: start; }
.screen-card { padding: 16px; margin-bottom: 20px; }
.screen-card h2 { margin: 0 0 8px; font-size: 20px; }
.screen-card img { display: block; width: 100%; margin-top: 14px; border: 1px solid #dfe6f0; border-radius: 8px; background: #fff; }
.badge { display: inline-flex; margin-left: 8px; padding: 4px 8px; border-radius: 999px; background: var(--primary-soft); color: var(--primary); font-size: 12px; }
.toc { position: sticky; top: 20px; padding: 16px; }
.toc h3, .note h3 { margin: 0 0 10px; }
.toc a { display: block; padding: 7px 0; border-bottom: 1px solid #eef2f7; color: #52627a; font-size: 14px; }
.note { margin-top: 16px; padding: 14px; color: #52627a; line-height: 1.65; box-shadow: none; }
@media (max-width: 1100px) {
  .app, .index-grid, .workflow-shell, .grid.two, .grid.three, .metric-grid, .lane-board { grid-template-columns: 1fr; }
  .side { position: relative; height: auto; }
  .principle { position: relative; left: auto; right: auto; bottom: auto; margin-top: 20px; }
}
`;

const designDoc = `
# FPMS Phase 1 增强方案：案卷主线 + 文件门禁

版本：Phase 1 修订版
目标：把“文件驱动”从口号落到案卷动作的输入、证据、门禁、影响计划和效果账本，同时保留 FPMS 既有案卷主线。

## Story Shape Classification

| 指标 | 结论 |
|---|---|
| shared_file_density | 高。会涉及案件、文书、任务、费用、权限、前端路由和设置页。 |
| prereq_dependency_density | 高。必须先冻结文件资产、文书事件、门禁快照、影响计划、效果账本的数据合同。 |
| be_fe_coupling | 高。前端每个关键页面都依赖后端预览和门禁结果。 |
| evidence_cost | 高。需要证明状态、任务、费用不会重复落账，并证明缺材料时阻止或审计放行。 |

chosen_runbook：P0-prereq-heavy-story。

执行原则：先做模型和 API 合同，再分波次做收案、递交、来文登记、卷宗账本和规则后台。不得把十个页面一次性当成一个实现任务。

## 1. 产品定位

本阶段不建设独立的文件主流程。用户仍然围绕案卷工作：

- 新建案卷
- 案件详情
- 案件递交
- 案内登记来文
- OA 答复
- 授权、证书、年费

变化是：每个动作都必须说明它依据哪些文件、满足哪些门禁、会产生哪些状态/任务/费用影响，并留下可审计账本。

一句话定义：

案卷是主工作对象；文件是案卷动作的证据；文书事件是状态、任务、费用变化的驱动单元。

## 2. 修订后的核心原则

### 2.1 文件不直接改案件

文件只能先形成文书事件或明确的案卷动作。状态、任务、费用由文书事件的影响计划确认后落账。

错误链路：上传文件 → 自动改案件状态。

正确链路：上传文件 → 文件资产 → 文件核验 → 文书事件 → 影响计划 → 用户确认 → 效果账本。

### 2.2 新建案卷必须有真实收案文件，但递交必须检查最终文件

建案检查的是收案事实：

- 客户指示或委托邮件
- 说明书收案稿
- 权利要求书收案稿
- 摘要
- 附图或外观图

递交检查的是最终递交材料：

- 最终说明书
- 最终权利要求书
- 最终摘要
- 最终附图或外观图
- 申请书/请求书
- 委托书或后补审计
- 费用减缴材料或不申请费减说明
- 客户确认记录

所以“收案材料完整”不等于“可递交”。

### 2.3 门禁结果必须可解释

每次门禁要记录：

- 检查场景：建案、撰写、客户确认、递交、来文登记
- 要求项
- 满足该要求的文件
- 文件角色：来源文件、收案稿、最终递交稿、签章件、生成件
- 文件状态：已收到、已识别、已核验、已替换、已事件化、已用于递交、已作废
- 结论：通过、软通过、硬阻止、需人工覆盖
- 覆盖人和覆盖原因

### 2.4 状态要拆维度

单一案件状态不足以表达代理所业务。建议拆为四个维度：

| 维度 | 作用 | 示例 |
|---|---|---|
| ApplicationStatus | 官方/法律程序状态 | 未递交、等待受理、实审、一通、授权、驳回、撤回 |
| AgencyWorkflowStage | 所内作业阶段 | 收案、撰写准备、客户确认、递交、来文处理、答复中 |
| ClientServiceStatus | 客户服务状态 | 待客户材料、待客户确认、已转达、领证待转交 |
| RightsStatus | 权利维护状态 | 未授权、有效、终止、恢复中、无效、届满 |

兼容策略：现有 T_Case.status 在第一阶段保留，可作为 ApplicationStatus 的兼容投影；新设计不得继续把客户服务状态和权利状态塞回同一个字段。

### 2.5 规则矩阵拆成匹配规则和效果项

文书状态规则不应一行同时承担所有副作用。建议结构：

- 规则头：匹配什么文书事件和文件类型。
- 状态效果项：改哪个状态维度。
- 任务效果项：创建、完成或建议更新哪个任务。
- 费用效果项：创建费用草单或明确不生成。
- 文件效果项：文件状态从已核验变为已事件化，或被标记为递交使用。
- 幂等键：防止重复生成任务、费用和状态历史。

## 3. 核心数据模型

### 3.1 FilePackage

一次导入或上传批次，例如客户邮件、扫描批次、CNIPA 下载包。

关键字段：

- id
- source_channel
- source_ref
- subject
- sender_name
- received_at
- intake_status
- suggested_case_id
- suggested_action
- created_by / created_at

### 3.2 FileAsset

单个不可变文件。替换文件时新增版本或新资产，不覆盖旧文件。

关键字段：

- id
- package_id
- original_file_name
- mime_type
- file_size
- storage_key
- sha256_hash
- file_kind
- file_role
- file_status
- version_no
- replaces_file_id
- parse_status
- extracted_metadata
- uploaded_by / uploaded_at

建议 file_status：

- RECEIVED
- IDENTIFIED
- VERIFIED
- EVENTIZED
- USED_FOR_FILING
- REPLACED
- VOIDED

### 3.3 DocumentEvent

有业务意义的文书事件。它不是普通附件，也不是文件本身。

示例：

- CLIENT_INTAKE：客户新申请委托
- OA_NOTICE：审查意见通知书
- GRANT_NOTICE：授权通知书
- PATENT_CERTIFICATE：专利证书
- RIGHT_TERMINATION_NOTICE：专利权终止通知
- FILING_PACKAGE：递交材料包

关键字段：

- id
- case_id
- event_type
- doc_template_id
- direction
- event_date
- title
- source
- status: DRAFT / PREVIEWED / CONFIRMED / CANCELLED
- idempotency_key
- created_by / created_at

### 3.4 FileLink

把文件资产连接到案卷、文书事件、任务、费用草单。

关键字段：

- id
- file_id
- target_type: CASE / DOCUMENT_EVENT / TASK / FEE_DRAFT
- target_id
- link_role: SOURCE_FILE / INTAKE_DRAFT / FINAL_FILING_COPY / SIGNED_AUTHORIZATION / GENERATED_OUTPUT / SUPPORTING_EVIDENCE
- created_by / created_at

### 3.5 GateEvaluation

一次门禁检查快照，必须可回放。

关键字段：

- id
- case_id
- gate_scope: INTAKE_CREATE / DRAFTING / CLIENT_CONFIRM / BATCH_FILING / DOCUMENT_EVENT_REGISTER
- result: PASS / SOFT_PASS / HARD_BLOCK / OVERRIDE_REQUIRED / OVERRIDDEN
- evaluated_at
- evaluated_by
- override_reason
- items_json

### 3.6 ImpactPlan

提交前影响预览。用户看到的是它，不是后台直接改状态。

关键字段：

- id
- case_id
- document_event_id
- matched_rule_id
- status_effects_json
- task_effects_json
- fee_effects_json
- file_effects_json
- requires_manual_confirm
- confirmed_by / confirmed_at

### 3.7 EffectLedger

落账记录。用于审计和防重复。

关键字段：

- id
- impact_plan_id
- effect_type: STATUS / TASK / FEE / FILE
- target_type
- target_id
- from_value
- to_value
- idempotency_key
- applied_by / applied_at

## 4. 关键流程

### 4.1 新建案卷

步骤：

1. 收案文件包：上传客户邮件、申请材料、压缩包或扫描件。
2. 文件识别：系统建议文件类型和文件角色，流程人员核验。
3. 案件信息：填写客户、案名、类型、发明人、申请人等。
4. 文件核验清单：检查收案节点要求。
5. 缺失任务：对可后补材料生成任务。
6. 创建预览：展示将创建的案卷、客户收案文书事件、文件链路、门禁快照和任务。

创建成功后：

- 创建 T_Case。
- 创建 CLIENT_INTAKE 类型 DocumentEvent。
- 将收案文件通过 FileLink 连接到 Case 和 DocumentEvent。
- 保存 GateEvaluation。
- 生成缺失材料任务。
- 不触发递交、不生成最终稿、不生成官费时限。

### 4.2 案件详情

详情页不应只是字段表。建议固定三块：

- 左侧：所内工作流阶段。
- 中间：当前节点推荐动作和阻止原因。
- 右侧：文件材料区，显示当前节点要求项、满足文件、缺失项和门禁结果。

### 4.3 案件递交

批量递交保留，但检查对象必须是最终递交材料。

执行前分组：

- 可递交：所有硬要求满足。
- 可后补递交：只有允许后补项缺失，必须写审计。
- 不可递交：缺最终说明书、权利要求书、外观图等核心材料。

被硬阻止的案件不得进入同一递交事务。

### 4.4 案内登记来文

官方来文必须绑定来源文件。

流程：

1. 选择案卷。
2. 上传或选择已核验来源文件。
3. 选择文书事件类型和模板。
4. 系统生成 ImpactPlan。
5. 普通规则由流程人员确认；特殊规则由律师或管理员确认。
6. 确认后落 EffectLedger，并更新状态、任务、费用和文件状态。

### 4.5 待归档文件

待归档文件只是辅助队列。它只能把游离文件送回主流程：

- 创建新案卷。
- 案内登记来文。
- 补充已有案卷材料。
- 登记证书、年费通知或终止通知。

不得在待归档文件页直接改案件状态、生成费用或关闭任务。

## 5. API 合同建议

第一阶段 API 不应一次性做全量。建议按竖切推进。

### 5.1 上传文件资产

POST /file-assets/upload

返回 file_id、file_kind 建议、file_status、sha256_hash、parse_status。

### 5.2 收案门禁预览

POST /cases/intake-gate/preview

输入案件类型、专利类型、流向、文件列表。返回 GateEvaluation 草案。

### 5.3 创建案卷并归档收案文件

POST /cases/from-intake-files

创建案卷、CLIENT_INTAKE 文书事件、文件链路、缺失任务和门禁快照。

### 5.4 递交门禁预览

POST /cases/batch-filing/gate-preview

返回每个候选案件的最终材料门禁结果。

### 5.5 文书事件影响预览

POST /document-events/impact-preview

只预览，不落账。

### 5.6 确认文书事件影响

POST /document-events/{event_id}/confirm-impact

确认后落状态、任务、费用和文件状态效果。

## 6. 第一阶段范围修订

建议不要把所有页面一次实现。按以下竖切拆分：

| Phase | 闭合切片 | 非闭合 |
|---|---|---|
| 1A | 新建案卷绑定收案文件，创建 CLIENT_INTAKE 事件和缺失任务 | 不做递交门禁、不做 OA 规则 |
| 1B | 递交前最终材料门禁 | 不做来文登记规则后台 |
| 1C | 官方来文登记影响预览，覆盖 OA、授权、证书、终止通知 | 不做邮件自动拉取 |
| 1D | 卷宗事件账本和文件状态列表 | 不做全文 OCR |
| 1E | 待归档文件队列和规则试跑器 | 不做自动 CNIPA 下载 |

## 7. 种子规则修订

本包的数据种子已改为与现有枚举兼容：

- CaseType 使用 NORMAL。
- PatentCategory 使用 INV、UM、DES。
- FlowDir 使用 CN_DOMESTIC、CN_OUTBOUND、FOREIGN_INBOUND。
- 递交规则明确区分收案稿和最终递交稿。

## 8. 原型页面

1. 案件工作台总览
2. 新建案卷 - 收案文件
3. 新建案卷 - 文件核验清单
4. 新建案卷 - 事件提交预览
5. 案件详情 - 工作流与文件材料区
6. 案件详情 - 卷宗事件账本
7. 案件递交 - 最终材料门禁
8. 案内登记来文 - 影响预览
9. 待归档文件 - 辅助队列
10. 状态规则矩阵 - 试跑器

## 9. 验收标准

### 新建案卷

Given 用户上传客户申请材料。
When 完成案卷信息和文件核验。
Then 系统创建案卷、CLIENT_INTAKE 文书事件、文件链路、门禁快照和缺失材料任务。
And 系统不生成递交事件、不生成官费时限。

### 递交门禁

Given 某案只有收案说明书但没有最终说明书。
When 用户进入批量递交。
Then 系统显示最终材料缺失。
And 阻止该案进入递交事务。

### 登记 OA 通知

Given 案件处于实审阶段，且来源文件已核验。
When 用户登记 OA_NOTICE。
Then 系统先展示影响计划。
And 用户确认后生成 OA 答复时限任务、写入效果账本和状态历史。

### 登记专利证书

Given 案件已授权。
When 用户登记专利证书。
Then 申请状态保持授权，客户服务状态变为领证。
And 不重复生成授权费。
And 要求人工确认。

## 10. 最终判断

本修订版保留案卷主线，但把“文件驱动”落到了可执行对象：

- 文件资产记录真实文件。
- 文书事件表达业务事实。
- 门禁快照解释能不能推进。
- 影响计划先预览再确认。
- 效果账本保证可审计和不重复。

这比只在案件工作流中增加附件检查更稳，也更接近中国专利代理事务所围绕来文、去文、客户指示和官方通知推进工作的实际方式。
`;

const packageReadme = `
# FPMS 案卷主线 + 文件门禁交付包

本包已按“文书事件驱动”的 approach 重写。

核心变化：

- 保留案卷主线，不建立独立文件主流程。
- 引入文件资产、文书事件、门禁快照、影响计划、效果账本。
- 新建案卷检查收案文件；递交检查最终递交材料。
- 原型页面已从旧截图壳改为真实静态页面，可重新截图。
- 种子规则已调整为与现有 CaseType、PatentCategory、FlowDir 枚举兼容。

## 内容

- FPMS_案卷主线_文件门禁增强方案_Phase1.md：修订后的业务架构方案。
- mock-ui/index.html：可浏览 10 个 mock 页面截图的总览。
- mock-ui/pages/*.html：10 个静态 mock 页面。
- mock-ui/screens/*.png：页面截图。
- mock-ui/screens/*.svg：嵌入对应 PNG 的 SVG 包装图。
- data/case_document_requirements_seed.*：材料要求规则种子。
- data/doc_status_rules_seed.*：文书事件状态/任务/费用效果规则种子。

## 推荐评审顺序

02 → 03 → 04 → 05 → 08 → 06 → 07 → 09 → 10

这个顺序可以说明：

- 收案文件如何形成文件资产。
- 文件如何满足建案门禁。
- 建案如何形成 CLIENT_INTAKE 文书事件。
- 案件详情如何展示当前节点文件材料区。
- 来文如何先预览影响再落账。
- 递交为什么必须检查最终递交材料。
`;

const mockReadme = `
# 原型界面使用说明

打开 index.html 可浏览全部 10 个页面。

本版原型的重点：

- 所有可见 UI 文案使用简体中文。
- 不再使用旧英文界面词，改为“文件材料区”。
- 页面展示文书事件、门禁快照、影响计划、效果账本。
- 递交页明确检查最终递交材料，不把收案材料等同于递交材料。
- 规则矩阵增加试跑器，用于验证特殊文书的影响。
`;

write("README.md", packageReadme);
write("mock-ui/README.md", mockReadme);
write("FPMS_案卷主线_文件门禁增强方案_Phase1.md", designDoc);
write("mock-ui/assets/styles.css", styles);
write("mock-ui/index.html", indexHtml("../"));
write("fpms_case_document_gate_mock_ui_index.html", indexHtml(""));

for (const page of pages) {
  write(`mock-ui/pages/${page.file}`, pageHtml(page));
}

const requirementHeaders = [
  "CaseType",
  "PatentCategory",
  "FlowDir",
  "StageCode",
  "RequirementCode",
  "RequiredFileKind",
  "RequiredEvidenceRole",
  "RequirementLevel",
  "ConditionExpr",
  "DefaultMissingTaskTemplateCode",
  "GateScope",
  "AcceptsDraft",
  "AcceptsFinal",
  "Notes",
];

const ruleHeaders = [
  "RuleCode",
  "DocumentEventType",
  "TemplateCode",
  "SourceFileKind",
  "FileNameAlias",
  "EffectPolicy",
  "StatusEffects",
  "TaskEffects",
  "FeeEffects",
  "FileEffects",
  "IdempotencyKey",
  "RequiresManualConfirm",
  "Priority",
  "Enabled",
  "Notes",
];

write("data/case_document_requirements_seed.csv", toCsv(requirementHeaders, requirementRows));
write(
  "data/case_document_requirements_seed.json",
  JSON.stringify(
    requirementRows.map((row) => Object.fromEntries(requirementHeaders.map((key, index) => [key, row[index]]))),
    null,
    2,
  ),
);
write("data/doc_status_rules_seed.csv", toCsv(ruleHeaders, statusRuleRows));
write(
  "data/doc_status_rules_seed.json",
  JSON.stringify(
    statusRuleRows.map((row) => Object.fromEntries(ruleHeaders.map((key, index) => [key, row[index]]))),
    null,
    2,
  ),
);

console.log(`Updated ${pages.length} mock pages and package documents.`);
