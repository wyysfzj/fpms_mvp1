<template>
  <div class="page-container document-wizard-page">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">中间文件向导</h1>
        <span class="page-subtitle">五步完成批量登记</span>
      </div>
      <div class="page-header-right">
        <el-button @click="handleReturn">返回文书列表</el-button>
      </div>
    </div>

    <el-card class="wizard-card" shadow="never">
      <el-steps :active="activeStepIndex" align-center finish-status="success">
        <el-step title="解析案件" description="录入案件清单" />
        <el-step title="编辑并提交" description="核对批量内容" />
        <el-step title="时限联动" description="预留任务步骤" />
        <el-step title="费用联动" description="预留费用步骤" />
        <el-step title="附件生成" description="预览附件候选" />
      </el-steps>
    </el-card>

    <el-card class="wizard-card wizard-body" shadow="never">
      <div v-if="isStep1" class="wizard-step">
        <el-alert
          title="每行输入一个案卷号或申请号，点击“拆分为逐行列表”后可逐条解析。至少解析出 1 条有效案件后，才能进入下一步。"
          type="info"
          :closable="false"
          show-icon
        />

        <div class="step-panel">
          <div class="step-panel-header">
            <div>
              <div class="section-title">共享默认值</div>
              <div class="section-hint">Step 1 先确认文书方向、模板和发文日期，下一步将带入这些默认值。</div>
            </div>
          </div>

          <div class="defaults-grid">
            <div class="defaults-field">
              <div class="defaults-field-label">文书方向</div>
              <el-radio-group v-model="documentWizardState.defaults.direction">
                <el-radio-button value="IN">收文</el-radio-button>
                <el-radio-button value="OUT">发文</el-radio-button>
              </el-radio-group>
              <div class="section-hint">当前合同只支持 `IN/OUT`，这里用方向映射 `DocType`。</div>
            </div>

            <div class="defaults-field">
              <div class="defaults-field-label">文书模板</div>
              <el-select
                v-model="documentWizardState.defaults.doc_template_id"
                class="full-width"
                clearable
                filterable
                :loading="templatesLoading"
                placeholder="请选择文书模板"
              >
                <el-option
                  v-for="template in filteredTemplates"
                  :key="template.id"
                  :label="formatTemplateLabel(template)"
                  :value="template.id"
                />
              </el-select>
              <div v-if="templatesError" class="defaults-error">{{ templatesError }}</div>
              <div v-else class="section-hint">
                {{ filteredTemplates.length ? '仅展示与当前方向一致的已启用模板。' : '当前方向下暂无可用模板。' }}
              </div>
            </div>

            <div class="defaults-field">
              <div class="defaults-field-label">发文日期</div>
              <el-date-picker
                v-model="documentWizardState.defaults.doc_date"
                type="date"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                placeholder="请选择发文日期"
                class="full-width"
              />
              <div class="section-hint">解析成功的案件进入下一步后，会默认带入这个日期。</div>
            </div>
          </div>

          <el-descriptions :column="3" border>
            <el-descriptions-item label="当前方向">{{ directionLabel }}</el-descriptions-item>
            <el-descriptions-item label="当前模板">{{ templateLabel }}</el-descriptions-item>
            <el-descriptions-item label="当前日期">{{ documentWizardState.defaults.doc_date }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="step-panel">
          <div class="step-panel-header">
            <div>
              <div class="section-title">案件逐行输入</div>
              <div class="section-hint">支持直接粘贴多行文本，空行会自动忽略。</div>
            </div>
            <div class="step-panel-actions">
              <el-button @click="clearDraft">清空</el-button>
              <el-button type="primary" @click="splitRowsFromDraft">拆分为逐行列表</el-button>
            </div>
          </div>

          <el-input
            v-model="draftText"
            type="textarea"
            :rows="6"
            resize="vertical"
            placeholder="请输入案卷号或申请号，每行一条，例如：&#10;P2024-001&#10;202400123456.7"
          />
        </div>

        <div class="step-summary">
          <el-descriptions :column="3" border>
            <el-descriptions-item label="待解析行数">{{ draftLineCount }}</el-descriptions-item>
            <el-descriptions-item label="有效案件数">{{ parsedCaseCount }}</el-descriptions-item>
            <el-descriptions-item label="失败行数">{{ failedRowCount }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="step-panel">
          <div class="step-panel-header">
            <div>
              <div class="section-title">逐行解析</div>
              <div class="section-hint">每行可单独解析，也可以一次性解析全部。</div>
            </div>
            <div class="step-panel-actions">
              <el-button :disabled="!rows.length || parseAllLoading" :loading="parseAllLoading" @click="parseAllRows">
                解析全部
              </el-button>
            </div>
          </div>

          <el-empty v-if="!rows.length" description="请先录入案件后拆分为逐行列表" />

          <div v-else class="row-list">
            <div v-for="(row, index) in rows" :key="row.id" class="row-item">
              <div class="row-item-index">第 {{ index + 1 }} 行</div>
              <el-input
                v-model="row.input"
                class="row-item-input"
                placeholder="请输入案卷号或申请号"
                @input="markRowDirty(row)"
              />
              <el-button
                type="primary"
                :loading="row.status === 'loading'"
                :disabled="!row.input.trim()"
                @click="parseSingleRow(row)"
              >
                解析
              </el-button>
              <div class="row-item-status">
                <el-tag v-if="row.status === 'success'" type="success" effect="light">已解析</el-tag>
                <el-tag v-else-if="row.status === 'error'" type="danger" effect="light">解析失败</el-tag>
                <el-tag v-else-if="row.status === 'loading'" type="warning" effect="light">解析中</el-tag>
                <el-tag v-else type="info" effect="light">待解析</el-tag>
              </div>
            </div>
          </div>
        </div>

        <div class="step-grid">
          <div class="step-panel">
            <div class="step-panel-header">
              <div>
                <div class="section-title">有效案件</div>
                <div class="section-hint">这些案件可以进入下一步编辑。</div>
              </div>
            </div>

            <el-table v-if="parsedCases.length" :data="parsedCases" border stripe size="small">
              <el-table-column prop="line_no" label="行号" width="80" />
              <el-table-column prop="input" label="输入值" min-width="180" />
              <el-table-column prop="case_no" label="案卷号" min-width="160" />
              <el-table-column prop="app_no" label="申请号" min-width="180">
                <template #default="{ row }">
                  {{ row.app_no || '—' }}
                </template>
              </el-table-column>
              <el-table-column prop="title" label="案件标题" min-width="220">
                <template #default="{ row }">
                  {{ row.title || '—' }}
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-else description="暂无有效案件" />
          </div>

          <div class="step-panel">
            <div class="step-panel-header">
              <div>
                <div class="section-title">失败行</div>
                <div class="section-hint">错误原因会保留在行级结果中，方便逐条修正后重试。</div>
              </div>
            </div>

            <el-table v-if="failedRows.length" :data="failedRows" border stripe size="small">
              <el-table-column prop="line_no" label="行号" width="80" />
              <el-table-column prop="input" label="输入值" min-width="180" />
              <el-table-column prop="error_message" label="错误原因" min-width="240">
                <template #default="{ row }">
                  {{ row.error_message }}
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-else description="暂无失败行" />
          </div>
        </div>
      </div>

      <div v-else-if="isStep2" class="wizard-step">
        <el-alert
          title="请逐案补录标题、文书日期、内部文号、是否需要回复、回复来源文件 ID 和补充说明，然后一次性批量提交。"
          type="info"
          :closable="false"
          show-icon
        />

        <el-alert
          v-if="submitError"
          :title="submitError"
          type="error"
          :closable="false"
          show-icon
        />

        <div class="step-panel">
          <div class="step-panel-header">
            <div>
              <div class="section-title">逐案编辑</div>
              <div class="section-hint">当前只开放标题、文书日期、内部文号、需要回复、回复来源文件 ID 和补充说明。</div>
            </div>
            <div class="step-panel-actions">
              <el-button @click="reloadStep2Rows">重新载入当前解析结果</el-button>
            </div>
          </div>

          <el-empty v-if="!step2Rows.length" description="请先返回上一步并至少解析出 1 条有效案件" />

          <div v-else class="wizard-row-stack">
            <div v-for="(row, index) in step2Rows" :key="row.id" class="step2-row-card">
              <div class="step2-row-header">
                <div>
                  <div class="step2-row-title">第 {{ index + 1 }} 条</div>
                  <div class="step2-row-subtitle">
                    {{ row.case_no }}
                    <span v-if="row.app_no">· {{ row.app_no }}</span>
                  </div>
                </div>
                <el-tag type="info" effect="light">待提交</el-tag>
              </div>

              <div class="step2-row-case">
                {{ row.source_title || '暂无案件标题' }}
              </div>

              <div class="step2-field-grid">
                <div class="step2-field">
                  <div class="step2-field-label">标题</div>
                  <el-input
                    v-model="row.title"
                    placeholder="请输入文书标题"
                    @input="markStep2RowDirty(row)"
                  />
                </div>

                <div class="step2-field">
                  <div class="step2-field-label">文书日期</div>
                  <el-date-picker
                    v-model="row.doc_date"
                    type="date"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    placeholder="请选择日期"
                    class="full-width"
                    @change="markStep2RowDirty(row)"
                  />
                </div>

                <div class="step2-field">
                  <div class="step2-field-label">内部文号</div>
                  <el-input
                    v-model="row.ref_no"
                    placeholder="可选"
                    @input="markStep2RowDirty(row)"
                  />
                </div>

                <div class="step2-field">
                  <div class="step2-field-label">需要回复</div>
                  <el-switch
                    v-model="row.need_reply"
                    inline-prompt
                    active-text="是"
                    inactive-text="否"
                    @change="markStep2RowDirty(row)"
                  />
                </div>

                <div class="step2-field">
                  <div class="step2-field-label">回复来源文件 ID</div>
                  <el-input
                    v-model="row.reply_to_id"
                    placeholder="可选"
                    @input="markStep2RowDirty(row)"
                  />
                </div>

                <div class="step2-field step2-field--full">
                  <div class="step2-field-label">补充说明</div>
                  <el-input
                    v-model="row.extra_data"
                    type="textarea"
                    :rows="3"
                    resize="vertical"
                    placeholder="可填写摘要、备注或其他补充信息"
                    @input="markStep2RowDirty(row)"
                  />
                </div>
              </div>

              <div v-if="row.error_message" class="step2-row-error">
                {{ row.error_message }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="isStep3" class="wizard-step">
        <el-alert
          title="当前步骤会根据第二步的文书草案预览相关时限任务候选。你可以调整允许编辑的字段，但这些修改目前只保存在页面内存中。"
          type="info"
          :closable="false"
          show-icon
        />

        <el-alert
          v-if="step3Error"
          :title="step3Error"
          type="error"
          :closable="false"
          show-icon
        />

        <div class="step-panel">
          <div class="step-panel-header">
            <div>
              <div class="section-title">任务候选预览</div>
              <div class="section-hint">仅显示当前草案中适用时限联动的文书。当前不会写入真实任务。</div>
            </div>
            <div class="step-panel-actions">
              <el-button :loading="step3Loading" @click="reloadStep3Preview">重新生成预览</el-button>
            </div>
          </div>

          <el-descriptions :column="3" border>
            <el-descriptions-item label="草案行数">{{ step2RowCount }}</el-descriptions-item>
            <el-descriptions-item label="任务候选">{{ step3PreviewCount }}</el-descriptions-item>
            <el-descriptions-item label="当前模板">{{ templateLabel }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <el-empty
          v-if="!step2Rows.length"
          description="请先完成第二步的逐案编辑后再查看任务候选预览"
        />

        <el-empty
          v-else-if="!step3Loading && !step3PreviewRows.length"
          description="当前草案没有可生成的时限任务候选"
        />

        <div v-else class="wizard-row-stack">
          <div v-for="(row, index) in step3PreviewRows" :key="row.id" class="step3-row-card">
            <div class="step2-row-header">
              <div>
                <div class="step2-row-title">任务候选 {{ index + 1 }}</div>
                <div class="step2-row-subtitle">
                  {{ row.case_no || '未关联案卷号' }}
                  <span v-if="row.task_template_name">· {{ row.task_template_name }}</span>
                </div>
              </div>
              <el-tag type="warning" effect="light">预览中</el-tag>
            </div>

            <div class="step2-row-case">
              {{ row.source_title || row.document_title || '暂无案件标题' }}
            </div>

            <div class="step3-meta-grid">
              <div class="step3-meta-item">
                <div class="step2-field-label">任务模板代码</div>
                <div class="step3-meta-value">{{ row.task_template_code }}</div>
              </div>
              <div class="step3-meta-item">
                <div class="step2-field-label">基准日期</div>
                <div class="step3-meta-value">{{ row.base_date || '—' }}</div>
              </div>
              <div class="step3-meta-item">
                <div class="step2-field-label">法定期限</div>
                <div class="step3-meta-value">{{ row.due_date || '—' }}</div>
              </div>
              <div class="step3-meta-item">
                <div class="step2-field-label">日提醒起始</div>
                <div class="step3-meta-value">{{ row.daily_remind_from || '—' }}</div>
              </div>
            </div>

            <div class="step2-field-grid">
              <div class="step2-field">
                <div class="step2-field-label">任务标题</div>
                <el-input v-model="row.title" placeholder="请输入任务标题" />
              </div>

              <div class="step2-field">
                <div class="step2-field-label">内部期限</div>
                <el-date-picker
                  v-model="row.internal_due_date"
                  type="date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  placeholder="请选择内部期限"
                  class="full-width"
                />
              </div>

              <div class="step2-field">
                <div class="step2-field-label">提醒 1</div>
                <el-date-picker
                  v-model="row.remind1"
                  type="date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  placeholder="请选择提醒日期"
                  class="full-width"
                />
              </div>

              <div class="step2-field">
                <div class="step2-field-label">提醒 2</div>
                <el-date-picker
                  v-model="row.remind2"
                  type="date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  placeholder="请选择提醒日期"
                  class="full-width"
                />
              </div>

              <div class="step2-field">
                <div class="step2-field-label">提醒 3</div>
                <el-date-picker
                  v-model="row.remind3"
                  type="date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  placeholder="请选择提醒日期"
                  class="full-width"
                />
              </div>

              <div class="step2-field">
                <div class="step2-field-label">每日提醒</div>
                <div class="step3-meta-value">{{ row.daily_remind ? '启用' : '未启用' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="isStep4" class="wizard-step">
        <el-alert
          title="当前步骤会根据第二步的文书草案预览费用候选。你可以调整允许编辑的字段，但这些修改目前只保存在页面内存中。"
          type="info"
          :closable="false"
          show-icon
        />

        <el-alert
          v-if="step4Error"
          :title="step4Error"
          type="error"
          :closable="false"
          show-icon
        />

        <div class="step-panel">
          <div class="step-panel-header">
            <div>
              <div class="section-title">费用候选预览</div>
              <div class="section-hint">仅显示当前草案中适用费用联动的文书。当前不会写入真实费用草稿。</div>
            </div>
            <div class="step-panel-actions">
              <el-button :loading="step4Loading" @click="reloadStep4Preview">重新生成预览</el-button>
            </div>
          </div>

          <el-descriptions :column="3" border>
            <el-descriptions-item label="草案行数">{{ step2RowCount }}</el-descriptions-item>
            <el-descriptions-item label="费用候选">{{ step4PreviewCount }}</el-descriptions-item>
            <el-descriptions-item label="当前模板">{{ templateLabel }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <el-empty
          v-if="!step2Rows.length"
          description="请先完成第二步的逐案编辑后再查看费用候选预览"
        />

        <el-empty
          v-else-if="!step4Loading && !step4PreviewRows.length"
          description="当前草案没有可生成的费用候选"
        />

        <div v-else class="wizard-row-stack">
          <div v-for="(row, index) in step4PreviewRows" :key="row.id" class="step4-row-card">
            <div class="step2-row-header">
              <div>
                <div class="step2-row-title">费用候选 {{ index + 1 }}</div>
                <div class="step2-row-subtitle">
                  {{ row.case_no || '未关联案卷号' }}
                  <span>· {{ row.fee_draft_type }}</span>
                </div>
              </div>
              <el-tag type="warning" effect="light">预览中</el-tag>
            </div>

            <div class="step2-row-case">
              {{ row.source_title || row.document_title || '暂无案件标题' }}
            </div>

            <div class="step3-meta-grid">
              <div class="step3-meta-item">
                <div class="step2-field-label">费用草稿类型</div>
                <div class="step3-meta-value">{{ row.fee_draft_type }}</div>
              </div>
              <div class="step3-meta-item">
                <div class="step2-field-label">候选项目数</div>
                <div class="step3-meta-value">{{ row.fee_items.length }}</div>
              </div>
            </div>

            <div class="step2-field">
              <div class="step2-field-label">跳过本候选</div>
              <el-switch
                v-model="row.skip_this_candidate"
                inline-prompt
                active-text="是"
                inactive-text="否"
              />
            </div>

            <div class="step4-fee-list">
              <div v-for="(item, feeIndex) in row.fee_items" :key="item.id" class="step4-fee-item">
                <div class="step4-fee-item-title">费用项 {{ feeIndex + 1 }}</div>

                <div class="step3-meta-grid">
                  <div class="step3-meta-item">
                    <div class="step2-field-label">费用代码</div>
                    <div class="step3-meta-value">{{ item.fee_code || '—' }}</div>
                  </div>
                  <div class="step3-meta-item">
                    <div class="step2-field-label">费用类型</div>
                    <div class="step3-meta-value">{{ item.fee_type }}</div>
                  </div>
                </div>

                <div class="step2-field-grid">
                  <div class="step2-field">
                    <div class="step2-field-label">费用名称</div>
                    <el-input v-model="item.fee_name" placeholder="请输入费用名称" />
                  </div>

                  <div class="step2-field">
                    <div class="step2-field-label">金额</div>
                    <el-input v-model="item.amount" placeholder="请输入金额" />
                  </div>

                  <div class="step2-field">
                    <div class="step2-field-label">数量</div>
                    <el-input v-model="item.quantity" placeholder="可选" />
                  </div>

                  <div class="step2-field">
                    <div class="step2-field-label">单价</div>
                    <el-input v-model="item.unit_price" placeholder="可选" />
                  </div>

                  <div class="step2-field step2-field--full">
                    <div class="step2-field-label">说明</div>
                    <el-input
                      v-model="item.remark"
                      type="textarea"
                      :rows="2"
                      resize="vertical"
                      placeholder="可填写费用项说明"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="wizard-step">
        <el-alert
          title="当前步骤会根据第二步的文书草案预览附件与模板候选。你可以调整允许编辑的字段，但这些修改目前只保存在页面内存中。"
          type="info"
          :closable="false"
          show-icon
        />

        <el-alert
          v-if="step5Error"
          :title="step5Error"
          type="error"
          :closable="false"
          show-icon
        />

        <div class="step-panel">
          <div class="step-panel-header">
            <div>
              <div class="section-title">附件候选预览</div>
              <div class="section-hint">仅显示当前草案中适用模板生成的文书。当前不会写入真实附件。</div>
            </div>
            <div class="step-panel-actions">
              <el-button :loading="step5Loading" @click="reloadStep5Preview">重新生成预览</el-button>
            </div>
          </div>

          <el-descriptions :column="3" border>
            <el-descriptions-item label="草案行数">{{ step2RowCount }}</el-descriptions-item>
            <el-descriptions-item label="附件候选">{{ step5PreviewCount }}</el-descriptions-item>
            <el-descriptions-item label="当前模板">{{ templateLabel }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <el-empty
          v-if="!step2Rows.length"
          description="请先完成第二步的逐案编辑后再查看附件候选预览"
        />

        <el-empty
          v-else-if="!step5Loading && !step5PreviewRows.length"
          description="当前草案没有可生成的附件候选"
        />

        <div v-else class="wizard-row-stack">
          <div v-for="(row, index) in step5PreviewRows" :key="row.id" class="step4-row-card">
            <div class="step2-row-header">
              <div>
                <div class="step2-row-title">附件候选 {{ index + 1 }}</div>
                <div class="step2-row-subtitle">
                  {{ row.case_no || '未关联案卷号' }}
                  <span v-if="row.template_name">· {{ row.template_name }}</span>
                </div>
              </div>
              <el-tag type="warning" effect="light">预览中</el-tag>
            </div>

            <div class="step2-row-case">
              {{ row.source_title || row.document_title || '暂无案件标题' }}
            </div>

            <div class="step3-meta-grid">
              <div class="step3-meta-item">
                <div class="step2-field-label">模板代码</div>
                <div class="step3-meta-value">{{ row.template_code }}</div>
              </div>
              <div class="step3-meta-item">
                <div class="step2-field-label">输出格式</div>
                <div class="step3-meta-value">{{ row.output_format }}</div>
              </div>
              <div class="step3-meta-item">
                <div class="step2-field-label">候选来源</div>
                <div class="step3-meta-value">{{ row.candidate_source_kind }}</div>
              </div>
              <div class="step3-meta-item">
                <div class="step2-field-label">预览文件名</div>
                <div class="step3-meta-value">{{ row.output_file_name }}</div>
              </div>
            </div>

            <div class="step2-field-grid">
              <div class="step2-field">
                <div class="step2-field-label">生成本候选</div>
                <el-switch
                  v-model="row.generate_this_candidate"
                  inline-prompt
                  active-text="是"
                  inactive-text="否"
                />
              </div>

              <div class="step2-field">
                <div class="step2-field-label">输出名称</div>
                <el-input v-model="row.output_name" placeholder="请输入输出名称" />
              </div>

              <div class="step2-field step2-field--full">
                <div class="step2-field-label">备注</div>
                <el-input
                  v-model="row.remark"
                  type="textarea"
                  :rows="2"
                  resize="vertical"
                  placeholder="可填写附件候选说明"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <div class="wizard-actions">
      <el-button :disabled="isStep1" @click="goBack">上一步</el-button>
      <el-button v-if="isStep1" type="primary" :disabled="!canEnterStep2" @click="goNext">下一步</el-button>
      <template v-else-if="isStep2">
        <el-button @click="goNext">查看后续步骤壳层</el-button>
        <el-button
          type="primary"
          :loading="submitLoading"
          :disabled="!canSubmitStep2"
          @click="submitStep2Batch"
        >
          批量提交
        </el-button>
      </template>
      <el-button v-else-if="!isStep5" type="primary" @click="goNext">下一步</el-button>
      <el-button
        v-else
        type="primary"
        @click="returnToStep2"
      >
        返回第二步提交
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getCases } from '../../../api/cases'
import {
  createDocumentWizardAttachmentPreview,
  createDocumentWizardBatch,
  createDocumentWizardFeePreview,
  createDocumentWizardTaskPreview,
  documentWizardState,
  getDocTemplates,
  resetDocumentWizardState,
} from '../../../api/documents'
import type { ApiError } from '../../../api/types'
import type {
  DocTemplate,
  DocumentWizardAttachmentPreviewItem,
  DocumentWizardBatchCreatePayload,
  DocumentWizardBatchRowError,
  DocumentWizardCaseRow,
  DocumentWizardFeeFinalRowDraft,
  DocumentWizardFeePreviewFeeItem,
  DocumentWizardFeePreviewItem,
  DocumentWizardParsedCase,
  DocumentWizardTaskFinalRowDraft,
  DocumentWizardTaskPreviewItem,
} from '../../../api/documents.types'

const router = useRouter()
const TOTAL_STEPS = 5

interface ParsedCaseRowView {
  line_no: number
  input: string
  case_id: string
  case_no: string
  app_no?: string
  title?: string
}

interface FailedCaseRowView {
  line_no: number
  input: string
  error_message: string
}

interface Step2CaseRowView {
  id: string
  case_id: string
  case_no: string
  app_no?: string
  source_title?: string
  title: string
  doc_date: string
  ref_no: string
  need_reply: boolean
  reply_to_id: string
  extra_data: string
  error_message?: string
}

interface Step3PreviewRowView extends DocumentWizardTaskPreviewItem {
  id: string
}

interface Step4PreviewFeeItemView extends DocumentWizardFeePreviewFeeItem {
  id: string
}

interface Step4PreviewRowView extends Omit<DocumentWizardFeePreviewItem, 'fee_items'> {
  id: string
  fee_items: Step4PreviewFeeItemView[]
}

interface Step5PreviewRowView extends DocumentWizardAttachmentPreviewItem {
  id: string
}

const activeStepIndex = computed(() => documentWizardState.activeStep - 1)
const isStep1 = computed(() => documentWizardState.activeStep === 1)
const isStep2 = computed(() => documentWizardState.activeStep === 2)
const isStep3 = computed(() => documentWizardState.activeStep === 3)
const isStep4 = computed(() => documentWizardState.activeStep === 4)
const isStep5 = computed(() => documentWizardState.activeStep === 5)
const directionLabel = computed(() => (documentWizardState.defaults.direction === 'IN' ? '收文' : '发文'))
const docTemplates = ref<DocTemplate[]>([])
const templatesLoading = ref(false)
const templatesError = ref('')
const rows = computed(() => documentWizardState.step1.rows)
const draftText = ref('')
const parseAllLoading = ref(false)
const step2Rows = ref<Step2CaseRowView[]>([])
const step3PreviewRows = ref<Step3PreviewRowView[]>([])
const step3Loading = ref(false)
const step3Error = ref<string | null>(null)
const step4PreviewRows = ref<Step4PreviewRowView[]>([])
const step4Loading = ref(false)
const step4Error = ref<string | null>(null)
const step5PreviewRows = ref<Step5PreviewRowView[]>([])
const step5Loading = ref(false)
const step5Error = ref<string | null>(null)
const step2SourceSignature = ref('')
const submitLoading = ref(false)
const submitError = ref<string | null>(null)
const filteredTemplates = computed(() =>
  docTemplates.value.filter((template) =>
    template.enabled && template.direction === documentWizardState.defaults.direction
  )
)
const templateLabel = computed(() => {
  if (!documentWizardState.defaults.doc_template_id) {
    return '未选择'
  }

  const matchedTemplate = docTemplates.value.find(
    (template) => template.id === documentWizardState.defaults.doc_template_id
  )
  return matchedTemplate ? formatTemplateLabel(matchedTemplate) : documentWizardState.defaults.doc_template_id
})

const parsedCases = computed<ParsedCaseRowView[]>(() =>
  documentWizardState.step1.rows.flatMap((row, index) => {
    if (row.status !== 'success' || !row.matched_case) {
      return []
    }

    return [{
      line_no: index + 1,
      input: row.input,
      case_id: row.matched_case.id,
      case_no: row.matched_case.case_no,
      app_no: row.matched_case.app_no,
      title: row.matched_case.title,
    }]
  })
)

const failedRows = computed<FailedCaseRowView[]>(() =>
  documentWizardState.step1.rows.flatMap((row, index) => {
    if (row.status !== 'error') {
      return []
    }

    return [{
      line_no: index + 1,
      input: row.input,
      error_message: row.error_message || '解析失败。',
    }]
  })
)

const parsedCaseCount = computed(() => parsedCases.value.length)
const step2RowCount = computed(() => step2Rows.value.length)
const step3PreviewCount = computed(() => step3PreviewRows.value.length)
const step4PreviewCount = computed(() => step4PreviewRows.value.length)
const step5PreviewCount = computed(() => step5PreviewRows.value.length)
const failedRowCount = computed(() => failedRows.value.length)
const draftLineCount = computed(() => splitDraftLines(draftText.value).length)
const canEnterStep2 = computed(() => parsedCaseCount.value > 0)
const canSubmitStep2 = computed(() => step2RowCount.value > 0 && !submitLoading.value)

function goBack() {
  if (!isStep1.value) {
    documentWizardState.activeStep -= 1
    submitError.value = null
  }
}

async function goNext() {
  if (isStep1.value && !canEnterStep2.value) {
    ElMessage.warning('请至少解析出 1 条有效案件后再进入下一步。')
    return
  }

  if (isStep1.value) {
    reloadStep2Rows()
  }

  if (isStep2.value) {
    await reloadStep3Preview()
  }

  if (isStep3.value) {
    await reloadStep4Preview()
  }

  if (isStep4.value) {
    await reloadStep5Preview()
  }

  if (documentWizardState.activeStep < TOTAL_STEPS) {
    documentWizardState.activeStep += 1
  }
}

function returnToStep2(): void {
  documentWizardState.activeStep = 2
  submitError.value = null
}

function handleReturn() {
  router.push('/documents')
}

function formatTemplateLabel(template: DocTemplate): string {
  return `${template.code} - ${template.name}`
}

function createRow(input: string): DocumentWizardCaseRow {
  return {
    id: typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`,
    input,
    status: 'idle',
  }
}

function splitDraftLines(text: string): string[] {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
}

function rebuildRowsFromDraft(): void {
  documentWizardState.step1.rows = splitDraftLines(draftText.value).map((line) => createRow(line))
}

function syncDraftFromRows(): void {
  draftText.value = documentWizardState.step1.rows.map((row) => row.input).join('\n')
}

function splitRowsFromDraft(): void {
  rebuildRowsFromDraft()
  syncDraftFromRows()
  if (!documentWizardState.step1.rows.length) {
    ElMessage.warning('请先输入至少 1 行案件信息。')
  }
}

function clearDraft(): void {
  draftText.value = ''
  documentWizardState.step1.rows = []
}

function markRowDirty(row: DocumentWizardCaseRow): void {
  row.status = 'idle'
  row.matched_case = undefined
  row.error_message = undefined
  syncDraftFromRows()
}

function toParsedCase(caseItem: Awaited<ReturnType<typeof getCases>>['items'][number]): DocumentWizardParsedCase {
  return {
    id: caseItem.id,
    case_no: caseItem.case_no,
    app_no: caseItem.app_no,
    title: caseItem.title,
  }
}

function createStep2RowId(): string {
  return typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

function createStep3PreviewRow(item: DocumentWizardTaskPreviewItem): Step3PreviewRowView {
  return {
    id: createStep2RowId(),
    ...item,
  }
}

function createStep4FeeItem(item: DocumentWizardFeePreviewFeeItem): Step4PreviewFeeItemView {
  return {
    id: createStep2RowId(),
    ...item,
  }
}

function createStep4PreviewRow(item: DocumentWizardFeePreviewItem): Step4PreviewRowView {
  return {
    id: createStep2RowId(),
    ...item,
    fee_items: item.fee_items.map((feeItem) => createStep4FeeItem(feeItem)),
  }
}

function createStep5PreviewRow(item: DocumentWizardAttachmentPreviewItem): Step5PreviewRowView {
  return {
    id: createStep2RowId(),
    ...item,
  }
}

function createStep2Row(parsedCase: ParsedCaseRowView): Step2CaseRowView {
  return {
    id: createStep2RowId(),
    case_id: parsedCase.case_id,
    case_no: parsedCase.case_no,
    app_no: parsedCase.app_no,
    source_title: parsedCase.title,
    title: parsedCase.title || '',
    doc_date: documentWizardState.defaults.doc_date,
    ref_no: '',
    need_reply: false,
    reply_to_id: '',
    extra_data: '',
  }
}

function clearStep2RowErrors(): void {
  step2Rows.value.forEach((row) => {
    row.error_message = undefined
  })
}

function markStep2RowDirty(row: Step2CaseRowView): void {
  if (row.error_message) {
    row.error_message = undefined
  }
  submitError.value = null
}

function reloadStep2Rows(): void {
  if (!parsedCases.value.length) {
    step2Rows.value = []
    step3PreviewRows.value = []
    step3Error.value = null
    step4PreviewRows.value = []
    step4Error.value = null
    step5PreviewRows.value = []
    step5Error.value = null
    step2SourceSignature.value = ''
    return
  }

  const signature = [
    parsedCases.value.map((item) => item.case_id).join('|'),
    documentWizardState.defaults.direction,
    documentWizardState.defaults.doc_template_id || '',
    documentWizardState.defaults.doc_date,
  ].join('::')

  if (step2Rows.value.length > 0 && step2SourceSignature.value === signature) {
    return
  }

  step2Rows.value = parsedCases.value.map((item) => createStep2Row(item))
  step3PreviewRows.value = []
  step3Error.value = null
  step4PreviewRows.value = []
  step4Error.value = null
  step5PreviewRows.value = []
  step5Error.value = null
  step2SourceSignature.value = signature
  submitError.value = null
}

watch(() => documentWizardState.activeStep, (step) => {
  if (step === 2) {
    reloadStep2Rows()
  } else {
    submitError.value = null
  }
})

watch(() => documentWizardState.defaults.direction, (direction) => {
  const selectedTemplate = docTemplates.value.find(
    (template) => template.id === documentWizardState.defaults.doc_template_id
  )

  if (selectedTemplate && selectedTemplate.direction !== direction) {
    documentWizardState.defaults.doc_template_id = null
  }
})

async function loadDocTemplates(): Promise<void> {
  templatesLoading.value = true
  templatesError.value = ''

  try {
    const result = await getDocTemplates({
      page: 1,
      page_size: 200,
      enabled: true,
    })
    docTemplates.value = result.items
  } catch {
    docTemplates.value = []
    templatesError.value = '模板列表加载失败，请稍后重试。'
  } finally {
    templatesLoading.value = false
  }
}

async function lookupCase(input: string): Promise<DocumentWizardParsedCase | null> {
  const query = input.trim()
  if (!query) {
    return null
  }

  const caseNoResult = await getCases({
    page: 1,
    page_size: 1,
    case_no: query,
  } as Parameters<typeof getCases>[0])

  if (caseNoResult.items.length > 0) {
    return toParsedCase(caseNoResult.items[0])
  }

  const appNoResult = await getCases({
    page: 1,
    page_size: 1,
    app_no: query,
  } as Parameters<typeof getCases>[0])

  if (appNoResult.items.length > 0) {
    return toParsedCase(appNoResult.items[0])
  }

  return null
}

async function parseSingleRow(row: DocumentWizardCaseRow): Promise<void> {
  const query = row.input.trim()
  if (!query) {
    row.status = 'error'
    row.matched_case = undefined
    row.error_message = '当前行为空，请填写案卷号或申请号。'
    return
  }

  row.status = 'loading'
  row.error_message = undefined
  row.matched_case = undefined

  try {
    const resolvedCase = await lookupCase(query)
    if (!resolvedCase) {
      row.status = 'error'
      row.error_message = '未找到匹配案件，请检查案卷号或申请号后重试。'
      return
    }

    row.status = 'success'
    row.matched_case = resolvedCase
    row.error_message = undefined
    syncDraftFromRows()
  } catch {
    row.status = 'error'
    row.error_message = '案件解析失败，请稍后重试。'
    row.matched_case = undefined
  }
}

async function parseAllRows(): Promise<void> {
  if (!documentWizardState.step1.rows.length) {
    ElMessage.warning('请先录入案件后再解析。')
    return
  }

  parseAllLoading.value = true
  try {
    for (const row of documentWizardState.step1.rows) {
      await parseSingleRow(row)
    }
  } finally {
    parseAllLoading.value = false
  }
}

function buildStep2Payload(): DocumentWizardBatchCreatePayload {
  return {
    defaults: {
      doc_template_id: documentWizardState.defaults.doc_template_id,
      direction: documentWizardState.defaults.direction,
      doc_date: documentWizardState.defaults.doc_date,
    },
    rows: step2Rows.value.map((row) => ({
      case_id: row.case_id,
      title: row.title.trim() || undefined,
      doc_date: row.doc_date.trim() || undefined,
      ref_no: row.ref_no.trim() || undefined,
      need_reply: row.need_reply,
      reply_to_id: row.reply_to_id.trim() || undefined,
      extra_data: row.extra_data.trim() || undefined,
    })),
  }
}

function buildStep3TaskRows(): DocumentWizardTaskFinalRowDraft[] {
  return step3PreviewRows.value.map((row) => ({
    row_index: row.row_index,
    case_id: row.case_id,
    task_template_code: row.task_template_code,
    title: row.title || undefined,
    base_date: row.base_date || undefined,
    due_date: row.due_date || undefined,
    internal_due_date: row.internal_due_date || undefined,
    remind1: row.remind1 || undefined,
    remind2: row.remind2 || undefined,
    remind3: row.remind3 || undefined,
    daily_remind_from: row.daily_remind_from || undefined,
    daily_remind: row.daily_remind,
  }))
}

function buildFinalSubmitPayload(): DocumentWizardBatchCreatePayload {
  return {
    ...buildStep2Payload(),
    task_rows: buildStep3TaskRows(),
    fee_rows: buildStep4FeeRows(),
  }
}

function buildStep4FeeRows(): DocumentWizardFeeFinalRowDraft[] {
  return step4PreviewRows.value
    .filter((row) => !row.skip_this_candidate)
    .map((row) => ({
      row_index: row.row_index,
      case_id: row.case_id,
      fee_draft_type: row.fee_draft_type,
      skip_this_candidate: row.skip_this_candidate,
      fee_items: row.fee_items.map((item) => ({
        fee_code: item.fee_code,
        fee_name: item.fee_name,
        fee_type: item.fee_type,
        quantity: item.quantity,
        unit_price: item.unit_price,
        amount: item.amount,
        remark: item.remark,
      })),
    }))
}

async function reloadStep3Preview(): Promise<void> {
  if (!step2Rows.value.length || !documentWizardState.defaults.doc_template_id) {
    step3PreviewRows.value = []
    step3Error.value = null
    return
  }

  step3Loading.value = true
  step3Error.value = null

  try {
    const result = await createDocumentWizardTaskPreview(buildStep2Payload())
    step3PreviewRows.value = result.items.map((item) => createStep3PreviewRow(item))
  } catch {
    step3PreviewRows.value = []
    step3Error.value = '任务候选预览加载失败，请稍后重试。'
  } finally {
    step3Loading.value = false
  }
}

async function reloadStep4Preview(): Promise<void> {
  if (!step2Rows.value.length || !documentWizardState.defaults.doc_template_id) {
    step4PreviewRows.value = []
    step4Error.value = null
    return
  }

  step4Loading.value = true
  step4Error.value = null

  try {
    const result = await createDocumentWizardFeePreview(buildStep2Payload())
    step4PreviewRows.value = result.items.map((item) => createStep4PreviewRow(item))
  } catch {
    step4PreviewRows.value = []
    step4Error.value = '费用候选预览加载失败，请稍后重试。'
  } finally {
    step4Loading.value = false
  }
}

async function reloadStep5Preview(): Promise<void> {
  if (!step2Rows.value.length || !documentWizardState.defaults.doc_template_id) {
    step5PreviewRows.value = []
    step5Error.value = null
    return
  }

  step5Loading.value = true
  step5Error.value = null

  try {
    const result = await createDocumentWizardAttachmentPreview(buildStep2Payload())
    step5PreviewRows.value = result.items.map((item) => createStep5PreviewRow(item))
  } catch {
    step5PreviewRows.value = []
    step5Error.value = '附件候选预览加载失败，请稍后重试。'
  } finally {
    step5Loading.value = false
  }
}

function localizeWizardRowError(error: DocumentWizardBatchRowError): string {
  switch (error.code) {
    case 'CASE_ID_REQUIRED':
      return '案件编号不能为空。'
    case 'CASE_ID_DUPLICATE':
      return '同一批次中不能重复登记同一案件。'
    case 'CASE_NOT_FOUND':
      return '案件不存在，请返回上一步重新解析。'
    default:
      return '该行校验失败，请检查后重试。'
  }
}

function applyWizardRowErrors(rowErrors: DocumentWizardBatchRowError[]): void {
  clearStep2RowErrors()

  rowErrors.forEach((error) => {
    const row = step2Rows.value[error.row_index - 1]
    if (row) {
      row.error_message = localizeWizardRowError(error)
    }
  })
}

function getWizardSubmitError(apiError: ApiError): string {
  switch (apiError.code) {
    case 'DOCUMENT_WIZARD_BATCH_INVALID':
      return '批量提交失败，请检查标红项目后重试。'
    case 'DOC_TEMPLATE_NOT_FOUND':
      return '所选模板不存在，请返回上一步重新确认。'
    case 'CASE_NOT_FOUND':
      return '部分案件已失效，请返回上一步重新解析。'
    case 'REPLY_TO_DOC_NOT_FOUND':
      return '回复来源文件不存在，请检查后重试。'
    default:
      return '批量提交失败，请稍后重试。'
  }
}

async function submitStep2Batch(): Promise<void> {
  if (!documentWizardState.defaults.doc_template_id) {
    submitError.value = '请先带入文书模板后再提交。'
    ElMessage.warning(submitError.value)
    return
  }

  if (!step2Rows.value.length) {
    submitError.value = '请至少解析出 1 条有效案件后再提交。'
    ElMessage.warning(submitError.value)
    return
  }

  submitLoading.value = true
  submitError.value = null

  try {
    const result = await createDocumentWizardBatch(buildFinalSubmitPayload())
    ElMessage.success(`已成功批量创建 ${result.created} 份文书。`)
    resetDocumentWizardState()
    step2Rows.value = []
    step3PreviewRows.value = []
    step4PreviewRows.value = []
    step5PreviewRows.value = []
    step2SourceSignature.value = ''
    router.push('/documents')
  } catch (err) {
    const apiError = err as ApiError
    if (apiError.status === 400 && apiError.code === 'DOCUMENT_WIZARD_BATCH_INVALID') {
      const rowErrors = Array.isArray(apiError.details?.row_errors)
        ? apiError.details?.row_errors as DocumentWizardBatchRowError[]
        : []
      applyWizardRowErrors(rowErrors)
      submitError.value = getWizardSubmitError(apiError)
    } else {
      submitError.value = getWizardSubmitError(apiError)
    }

    ElMessage.error(submitError.value)
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  resetDocumentWizardState()
  draftText.value = ''
  step2Rows.value = []
  step3PreviewRows.value = []
  step3Loading.value = false
  step3Error.value = null
  step4PreviewRows.value = []
  step4Loading.value = false
  step4Error.value = null
  step5PreviewRows.value = []
  step5Loading.value = false
  step5Error.value = null
  step2SourceSignature.value = ''
  submitLoading.value = false
  submitError.value = null
  void loadDocTemplates()
})
</script>

<style scoped>
.document-wizard-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--text-sub);
  margin-top: 4px;
}

.wizard-card {
  border-radius: 10px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 12px;
}

.wizard-body {
  min-height: 240px;
}

.wizard-step,
.wizard-placeholder {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px 2px;
}

.wizard-placeholder-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
}

.wizard-placeholder-text {
  color: var(--text-sub);
  line-height: 1.7;
  margin-bottom: 8px;
}

.wizard-row-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.defaults-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.defaults-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.defaults-field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-main);
}

.defaults-error {
  color: #f56c6c;
  font-size: 12px;
  line-height: 1.6;
}

.step2-row-card {
  padding: 16px;
  border: 1px solid var(--border-color, #ebeef5);
  border-radius: 12px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.92), #ffffff);
}

.step2-row-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 10px;
}

.step2-row-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
}

.step2-row-subtitle {
  margin-top: 4px;
  color: var(--text-sub);
  font-size: 12px;
}

.step2-row-case {
  margin-bottom: 14px;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(59, 130, 246, 0.06);
  color: var(--text-main);
  line-height: 1.6;
}

.step2-field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 16px;
}

.step2-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step2-field--full {
  grid-column: 1 / -1;
}

.step2-field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-main);
}

.step2-row-error {
  margin-top: 10px;
  color: #f56c6c;
  font-size: 12px;
  line-height: 1.6;
}

.step3-row-card {
  padding: 16px;
  border: 1px solid var(--border-color, #ebeef5);
  border-radius: 12px;
  background: linear-gradient(180deg, rgba(255, 251, 235, 0.85), #ffffff);
}

.step4-row-card {
  padding: 16px;
  border: 1px solid var(--border-color, #ebeef5);
  border-radius: 12px;
  background: linear-gradient(180deg, rgba(236, 253, 245, 0.92), #ffffff);
}

.step4-fee-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.step4-fee-item {
  padding: 14px;
  border: 1px solid rgba(16, 185, 129, 0.18);
  border-radius: 10px;
  background: rgba(240, 253, 250, 0.9);
}

.step4-fee-item-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 12px;
}

.step3-meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 16px;
  margin-bottom: 14px;
}

.step3-meta-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.step3-meta-value {
  min-height: 22px;
  color: var(--text-main);
  line-height: 1.6;
}

.full-width {
  width: 100%;
}

.step-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--border-color, #ebeef5);
  border-radius: 10px;
  background: #fff;
}

.step-panel-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.step-panel-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.section-hint {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-sub);
}

.step-summary {
  margin-top: 4px;
}

.step-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.row-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.row-item {
  display: grid;
  grid-template-columns: 84px minmax(0, 1fr) auto auto;
  gap: 10px;
  align-items: center;
}

.row-item-index {
  font-size: 13px;
  color: var(--text-sub);
}

.row-item-status {
  min-width: 84px;
  display: flex;
  justify-content: flex-end;
}

.row-item-input {
  width: 100%;
}

.wizard-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 960px) {
  .defaults-grid {
    grid-template-columns: 1fr;
  }

  .step-grid {
    grid-template-columns: 1fr;
  }

  .step2-field-grid {
    grid-template-columns: 1fr;
  }

  .step3-meta-grid {
    grid-template-columns: 1fr;
  }

  .row-item {
    grid-template-columns: 1fr;
  }

  .row-item-status {
    justify-content: flex-start;
  }
}
</style>
