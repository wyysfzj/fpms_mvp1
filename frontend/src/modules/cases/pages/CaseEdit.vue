<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">编辑案件</h1>
      </div>
      <div class="page-header-right">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存修改
        </el-button>
      </div>
    </div>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div v-if="loading" class="page-loading">
      <el-skeleton :rows="8" animated />
    </div>

    <div v-else class="form-card">
      <el-alert
        v-if="validationSummary.length"
        title="请先修正以下问题后再保存"
        type="error"
        show-icon
        :closable="false"
        class="validation-summary"
      >
        <ul class="validation-summary-list">
          <li v-for="item in validationSummary" :key="item.key">{{ item.message }}</li>
        </ul>
      </el-alert>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="case-form"
      >
        <div class="form-section">
          <h3 class="form-section-title">案件信息</h3>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="案号">
                <el-input :model-value="caseData?.case_no" disabled />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="案件类型">
                <el-input :model-value="caseTypeText" disabled />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="专利类别">
                <el-input :model-value="patentCategoryText" disabled />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="标题" prop="title" :error="fieldErrors.get('title')?.join('，')">
                <el-input v-model="form.title" placeholder="请输入案件标题" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="客户">
                <el-input :model-value="caseData?.client_name || caseData?.client_id || '未关联客户'" disabled />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="法律状态" prop="status" :error="fieldErrors.get('status')?.join('，')">
                <el-select v-model="form.status" placeholder="请选择法律状态" clearable class="full-width">
                  <el-option
                    v-for="option in statusOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                    :disabled="option.disabled"
                  />
                </el-select>
                <div v-if="showReadonlyStatusHint" class="field-hint">
                  当前状态由流程或文书联动生成，此处仅展示，不建议手工修改。
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="申请号" :error="fieldErrors.get('app_no')?.join('，')">
                <el-input v-model="form.app_no" placeholder="当状态进入受理/审查阶段时为必填" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <h3 class="form-section-title">日期信息</h3>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="申请日" prop="filing_date" :error="fieldErrors.get('filing_date')?.join('，')">
                <el-date-picker
                  v-model="form.filing_date"
                  type="date"
                  placeholder="请选择申请日"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  class="full-width"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <el-collapse v-model="expandedSections" class="case-extra-sections">
          <el-collapse-item title="申请人信息" name="applicant">
            <div class="section-toolbar">
              <div class="field-hint">支持从客户主数据回填申请人，并可在当前界面快速新建后回填。</div>
              <div class="section-actions">
                <el-button text type="primary" @click="addApplicant">新增申请人</el-button>
                <el-button text type="primary" @click="handleQuickApplicantCreate">快速新建申请人</el-button>
              </div>
            </div>
            <div v-if="fieldErrors.get('applicants')?.length" class="section-error">
              {{ fieldErrors.get('applicants')?.join('，') }}
            </div>
            <div v-if="!form.applicants?.length" class="field-hint">当前未维护申请人信息，可按需新增并回填。</div>
            <div
              v-for="(applicant, index) in form.applicants"
              :key="applicant.seq"
              class="priority-card"
            >
              <div class="priority-card-header">
                <span>申请人 {{ index + 1 }}</span>
                <div class="section-actions">
                  <el-checkbox v-model="applicant.is_first">第一申请人</el-checkbox>
                  <el-button text type="danger" @click="removeApplicant(index)">删除</el-button>
                </div>
              </div>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="从客户主数据回填">
                    <el-select
                      v-model="applicant.source_client_id"
                      filterable
                      clearable
                      class="full-width"
                      placeholder="选择客户后自动回填申请人信息"
                      @change="handleApplicantClientSelect(index, applicant.source_client_id)"
                    >
                      <el-option
                        v-for="client in clients"
                        :key="client.id"
                        :label="client.name"
                        :value="client.id"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12" class="applicant-actions">
                  <el-button plain @click="openQuickClientDialog('applicant', index)">快速新建并回填</el-button>
                </el-col>
              </el-row>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-input v-model="applicant.name_cn" placeholder="申请人中文名称" />
                </el-col>
                <el-col :span="12">
                  <el-input v-model="applicant.name_en" placeholder="申请人英文名称" />
                </el-col>
              </el-row>
              <el-row :gutter="16" class="applicant-address-row">
                <el-col :span="12">
                  <el-input v-model="applicant.address_cn" type="textarea" :rows="2" placeholder="申请人中文地址" />
                </el-col>
                <el-col :span="12">
                  <el-input v-model="applicant.address_en" type="textarea" :rows="2" placeholder="申请人英文地址" />
                </el-col>
              </el-row>
            </div>
          </el-collapse-item>

          <el-collapse-item v-if="!CONSULTING_CASE_TYPES.includes(caseData?.case_type || '')" title="涉外代理信息" name="foreign_agent">
            <div class="section-toolbar">
              <div class="field-hint">涉外流程方向下必须维护外方代理，可从客户主数据选择或快速新建后回填。</div>
              <el-button text type="primary" @click="openQuickClientDialog('foreign_agent')">快速新建外方代理</el-button>
            </div>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="外方代理" :error="fieldErrors.get('foreign_agent_id')?.join('，')">
                  <el-select
                    v-model="form.foreign_agent_id"
                    filterable
                    clearable
                    class="full-width"
                    placeholder="请选择外方代理"
                  >
                    <el-option
                      v-for="client in clients"
                      :key="client.id"
                      :label="client.name"
                      :value="client.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="外方案号">
                  <el-input v-model="form.foreign_ref" placeholder="请输入外方案号" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>

          <el-collapse-item v-if="showPrioritySection" title="优先权信息" name="priority">
            <div class="section-toolbar">
              <div class="field-hint">每条优先权必须完整填写国家/地区、号码和日期。</div>
              <el-button text type="primary" @click="addPriority">新增优先权</el-button>
            </div>
            <div v-if="fieldErrors.get('priorities')?.length" class="section-error">
              {{ fieldErrors.get('priorities')?.join('，') }}
            </div>
            <div v-if="!form.priorities?.length" class="field-hint">当前没有优先权记录。</div>
            <div
              v-for="(priority, index) in form.priorities"
              :key="priority.seq"
              class="priority-card"
            >
              <div class="priority-card-header">
                <span>优先权 {{ index + 1 }}</span>
                <el-button text type="danger" @click="removePriority(index)">删除</el-button>
              </div>
              <el-row :gutter="16">
                <el-col :span="8">
                  <el-input v-model="priority.country_code" placeholder="国家/地区代码，例如 CN" />
                </el-col>
                <el-col :span="8">
                  <el-input v-model="priority.prio_no" placeholder="优先权号" />
                </el-col>
                <el-col :span="8">
                  <el-date-picker
                    v-model="priority.prio_date"
                    type="date"
                    placeholder="优先权日"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    class="full-width"
                  />
                </el-col>
              </el-row>
            </div>
          </el-collapse-item>

          <el-collapse-item v-if="showBioDepositSection" title="菌种保藏" name="bio">
            <div class="section-toolbar">
              <div class="field-hint">支持维护 0..n 条菌种保藏记录；单条记录如填写则需完整。</div>
              <el-button text type="primary" @click="addBioDeposit">新增菌种保藏</el-button>
            </div>
            <div v-if="fieldErrors.get('bio_deposits')?.length" class="section-error">
              {{ fieldErrors.get('bio_deposits')?.join('，') }}
            </div>
            <div v-if="!form.bio_deposits?.length" class="field-hint">当前没有菌种保藏记录。</div>
            <div
              v-for="(bioDeposit, index) in form.bio_deposits"
              :key="bioDeposit.seq"
              class="priority-card"
            >
              <div class="priority-card-header">
                <span>菌种保藏 {{ index + 1 }}</span>
                <el-button text type="danger" @click="removeBioDeposit(index)">删除</el-button>
              </div>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-input v-model="bioDeposit.deposit_no" placeholder="保藏编号" />
                </el-col>
                <el-col :span="12">
                  <el-input v-model="bioDeposit.deposit_unit_name" placeholder="保藏单位" />
                </el-col>
              </el-row>
              <el-row :gutter="16" class="applicant-address-row">
                <el-col :span="12">
                  <el-date-picker
                    v-model="bioDeposit.deposit_date"
                    type="date"
                    placeholder="保藏日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    class="full-width"
                  />
                </el-col>
                <el-col :span="12">
                  <el-input v-model="bioDeposit.name" placeholder="菌种名称/分类命名" />
                </el-col>
              </el-row>
            </div>
          </el-collapse-item>

          <el-collapse-item v-if="isPctIntlCase || isPctNatlCase" title="PCT 信息" name="pct">
            <div v-if="fieldErrors.get('pct')?.length" class="section-error">
              {{ fieldErrors.get('pct')?.join('，') }}
            </div>
            <template v-if="isPctIntlCase">
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="国际申请号">
                    <el-input v-model="form.intl_app_no" placeholder="请输入国际申请号" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="国际申请日">
                    <el-date-picker
                      v-model="form.intl_app_date"
                      type="date"
                      placeholder="请选择国际申请日"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
                      class="full-width"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="16">
                <el-col :span="8"><el-form-item label="RO"><el-input v-model="form.ro" placeholder="受理局" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="ISA"><el-input v-model="form.isa" placeholder="国际检索单位" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="IPEA"><el-input v-model="form.ipea" placeholder="国际初审单位" /></el-form-item></el-col>
              </el-row>
              <el-row :gutter="16">
                <el-col :span="12"><el-form-item label="国际公开号"><el-input v-model="form.intl_pub_no" placeholder="请输入国际公开号" /></el-form-item></el-col>
                <el-col :span="12">
                  <el-form-item label="国际公开日">
                    <el-date-picker
                      v-model="form.intl_pub_date"
                      type="date"
                      placeholder="请选择国际公开日"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
                      class="full-width"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="16">
                <el-col :span="8"><el-form-item label="国际公开语言"><el-input v-model="form.intl_pub_lang" placeholder="例如 EN" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="需要 IPER"><el-switch v-model="form.need_iper" /></el-form-item></el-col>
                <el-col :span="8">
                  <el-form-item label="IPER 日期">
                    <el-date-picker
                      v-model="form.iper_date"
                      type="date"
                      placeholder="请选择 IPER 日期"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
                      class="full-width"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </template>
            <template v-if="isPctNatlCase">
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="国家阶段进入日">
                    <el-date-picker
                      v-model="form.pct_national_entry_date"
                      type="date"
                      placeholder="请选择国家阶段进入日"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
                      class="full-width"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </template>
          </el-collapse-item>

          <el-collapse-item v-if="isInvalidationCase" title="无效案件信息" name="invalidation">
            <div v-if="fieldErrors.get('invalidation')?.length" class="section-error">
              {{ fieldErrors.get('invalidation')?.join('，') }}
            </div>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="原案 ID">
                  <el-input v-model="form.original_case_id" placeholder="请输入被攻击原案的 Case ID" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="无效案件委托方">
                  <el-select
                    v-model="form.invalid_client_id"
                    filterable
                    clearable
                    class="full-width"
                    placeholder="请选择委托方"
                  >
                    <el-option
                      v-for="client in clients"
                      :key="client.id"
                      :label="client.name"
                      :value="client.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="12"><el-form-item label="专利权人"><el-input v-model="form.invalid_patentee" placeholder="请输入专利权人名称" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="请求人"><el-input v-model="form.invalid_requester" placeholder="请输入请求人名称" /></el-form-item></el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="我方角色">
                  <el-select v-model="form.invalid_role" clearable class="full-width" placeholder="请选择我方角色">
                    <el-option
                      v-for="option in INVALID_ROLE_OPTIONS"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>

          <el-collapse-item v-if="showPublicationSection" title="公告与授权" name="pub_grant">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="公告日">
                  <el-date-picker
                    v-model="form.pub_date"
                    type="date"
                    placeholder="请选择公告日"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    class="full-width"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="公告号">
                  <el-input v-model="form.pub_no" placeholder="请输入公告号" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="授权日">
                  <el-date-picker
                    v-model="form.grant_date"
                    type="date"
                    placeholder="请选择授权日"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    class="full-width"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="授权号">
                  <el-input v-model="form.grant_no" placeholder="请输入授权号" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="专利号">
                  <el-input v-model="form.patent_no" placeholder="请输入专利号" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="有效期至">
                  <el-date-picker
                    v-model="form.valid_until"
                    type="date"
                    placeholder="请选择有效期至"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    class="full-width"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>

          <el-collapse-item v-if="showSpecificationSection" title="说明书信息" name="spec">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="说明书页数">
                  <el-input-number
                    v-model="form.spec_pages"
                    :min="0"
                    controls-position="right"
                    placeholder="页数"
                    class="full-width"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="权利要求项数">
                  <el-input-number
                    v-model="form.claim_count"
                    :min="0"
                    controls-position="right"
                    placeholder="项数"
                    class="full-width"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="已提实审请求">
                  <el-switch v-model="form.has_exam_request" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>

          <el-collapse-item title="代理人分配" name="agent">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="主办代理人">
                  <el-input v-model="form.primary_agent_id" placeholder="请输入代理人 ID" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="辅办代理人">
                  <el-input v-model="form.second_agent_id" placeholder="请输入代理人 ID" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="撰写人">
                  <el-input v-model="form.draftor_id" placeholder="请输入撰写人 ID" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>

          <el-collapse-item v-if="showSpecificationSection" title="控制标记" name="flags">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="费用监控">
                  <el-switch v-model="form.is_fee_monitor" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="减免类型">
                  <el-select v-model="form.fee_reduction" placeholder="请选择" clearable class="full-width">
                    <el-option label="不减免" value="NONE" />
                    <el-option label="部分减免" value="PARTIAL" />
                    <el-option label="全额减免" value="FULL" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="申请人类型">
                  <el-select v-model="form.applicant_kind" placeholder="请选择" clearable class="full-width">
                    <el-option label="个人" value="INDIVIDUAL" />
                    <el-option label="企业" value="ENTITY" />
                    <el-option label="高校" value="UNIV" />
                    <el-option label="政府" value="GOV" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>
        </el-collapse>
      </el-form>
    </div>

    <el-dialog v-model="showQuickClientDialog" :title="quickClientDialogTitle" width="520px" destroy-on-close>
      <el-form label-position="top" class="quick-client-form">
        <el-form-item label="客户名称" required>
          <el-input v-model="quickClientForm.name" placeholder="请输入客户名称" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="客户代码">
              <el-input v-model="quickClientForm.client_code" placeholder="可选" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="英文名称">
              <el-input v-model="quickClientForm.name_en" placeholder="可选" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="客户类型">
              <el-input v-model="quickClientForm.client_type" placeholder="可选" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="quickClientForm.email" placeholder="可选" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="resetQuickClientDialog">取消</el-button>
        <el-button type="primary" :loading="creatingClient" @click="handleQuickClientSave">
          创建并回填
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getCase, updateCase } from '../../../api/cases'
import { createClient, getClients } from '../../../api/clients'
import type { Case, CaseApplicant, CasePriority, CaseUpdatePayload } from '../../../api/cases.types'
import type { Client, ClientCreatePayload } from '../../../api/clients.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { CASE_STATUS_TEXT } from '../../../constants/displayText'
import { mapValidationDetailsToFieldErrors } from '../../../utils/validation'

interface ValidationItem {
  key: string
  message: string
  section?: string
}

const CASE_TYPE_TEXT: Record<string, string> = {
  NORMAL: '普通案件',
  PCT_INTL: 'PCT 国际阶段',
  PCT_NATL: 'PCT 国家阶段',
  INVALIDATION: '无效案件',
  PRIORITY: '优先权案件',
  CONSULTING: '顾问项目',
  SEARCH: '检索项目',
}

const PATENT_CATEGORY_TEXT: Record<string, string> = {
  INV: '发明',
  UM: '实用新型',
  DES: '外观设计',
}

const PRIORITY_CASE_TYPES = ['PRIORITY', 'PCT_INTL', 'PCT_NATL']
const CONSULTING_CASE_TYPES = ['CONSULTING', 'SEARCH']
const INVALID_ROLE_OPTIONS = [
  { label: '代表专利权人', value: 'PATENTEE' },
  { label: '代表请求人', value: 'REQUESTER' },
  { label: '双方均代表', value: 'BOTH' },
]
const EDITABLE_STATUS_VALUES = [
  'NOT_FILED',
  'PENDING',
  'WAITING_RECEIPT',
  'PRELIM_EXAM',
  'AMENDMENT',
  'PRELIM_PASS',
  'PUBLISHED',
  'SUB_EXAM',
  'OA1',
  'OA2',
  'REEXAM',
  'GRANTED',
  'REJECTED',
  'WITHDRAWN',
  'ABANDONED',
  'EXPIRED',
  'TERMINATED',
  'INVALIDATED',
  'INVALIDATED_PARTIAL',
]
const READONLY_STATUS_VALUES = ['ACCEPTED', 'GRANT_PENDING'] as const
const STATUSES_REQUIRING_APP_FIELDS = EDITABLE_STATUS_VALUES.filter((status) => status !== 'NOT_FILED')

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const error = ref<ApiError | null>(null)
const caseData = ref<Case | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const expandedSections = ref<string[]>([])
const validationSummary = ref<ValidationItem[]>([])
const clients = ref<Client[]>([])
const creatingClient = ref(false)
const showQuickClientDialog = ref(false)
const quickApplicantIndex = ref<number | null>(null)
const quickClientMode = ref<'applicant' | 'foreign_agent'>('applicant')

const form = reactive<CaseUpdatePayload>({
  title: '',
  status: '',
  app_no: '',
  filing_date: '',
  applicants: [],
  priorities: [],
  bio_deposits: [],
  foreign_agent_id: '',
  foreign_ref: '',
  ro: '',
  isa: '',
  ipea: '',
  intl_app_no: '',
  intl_app_date: '',
  intl_pub_no: '',
  intl_pub_date: '',
  intl_pub_lang: '',
  need_iper: false,
  iper_date: '',
  pct_national_entry_date: '',
  original_case_id: '',
  invalid_client_id: '',
  invalid_patentee: '',
  invalid_requester: '',
  invalid_role: '',
})

const quickClientForm = reactive<ClientCreatePayload>({
  name: '',
  client_code: '',
  name_en: '',
  client_type: '',
  default_currency: 'CNY',
  email: '',
})

const rules: FormRules = {
  title: [{ max: 500, message: '标题不能超过 500 个字符', trigger: 'blur' }],
}

const caseTypeText = computed(() => {
  const value = caseData.value?.case_type || ''
  return CASE_TYPE_TEXT[value] || value || '未设置'
})

const patentCategoryText = computed(() => {
  const value = caseData.value?.patent_category || ''
  return PATENT_CATEGORY_TEXT[value] || value || '未设置'
})

const showPrioritySection = computed(() => PRIORITY_CASE_TYPES.includes(caseData.value?.case_type || ''))
const showPublicationSection = computed(() => !CONSULTING_CASE_TYPES.includes(caseData.value?.case_type || ''))
const showSpecificationSection = computed(() => !CONSULTING_CASE_TYPES.includes(caseData.value?.case_type || ''))
const showBioDepositSection = computed(() => !CONSULTING_CASE_TYPES.includes(caseData.value?.case_type || ''))
const isForeignFlow = computed(() => (caseData.value?.flow_dir || 'CN_DOMESTIC') !== 'CN_DOMESTIC')
const isPctIntlCase = computed(() => caseData.value?.case_type === 'PCT_INTL')
const isPctNatlCase = computed(() => caseData.value?.case_type === 'PCT_NATL')
const isInvalidationCase = computed(() => caseData.value?.case_type === 'INVALIDATION')
const quickClientDialogTitle = computed(() =>
  quickClientMode.value === 'foreign_agent' ? '快速新建外方代理' : '快速新建申请人主数据'
)

const statusOptions = computed(() => {
  const editableOptions = EDITABLE_STATUS_VALUES.map((value) => ({
    value,
    label: CASE_STATUS_TEXT[value] || value,
    disabled: false,
  }))

  const currentStatus = form.status?.trim()
  if (currentStatus && READONLY_STATUS_VALUES.includes(currentStatus as typeof READONLY_STATUS_VALUES[number])) {
    return [
      {
        value: currentStatus,
        label: `${CASE_STATUS_TEXT[currentStatus] || currentStatus}（流程状态，只读）`,
        disabled: true,
      },
      ...editableOptions,
    ]
  }

  return editableOptions
})

const showReadonlyStatusHint = computed(() =>
  READONLY_STATUS_VALUES.includes((form.status || '').trim() as typeof READONLY_STATUS_VALUES[number])
)

function createEmptyPriority(seq: number): CasePriority {
  return {
    seq,
    country_code: '',
    prio_no: '',
    prio_date: '',
  }
}

function createEmptyApplicant(seq: number): CaseApplicant {
  return {
    seq,
    is_first: seq === 1,
    source_client_id: '',
    name_cn: '',
    name_en: '',
    address_cn: '',
    address_en: '',
  }
}

function createEmptyBioDeposit(seq: number) {
  return {
    seq,
    deposit_no: '',
    deposit_unit_name: '',
    deposit_date: '',
    name: '',
  }
}

async function fetchClients() {
  try {
    const result = await getClients({ page: 1, page_size: 100 })
    clients.value = result.items
  } catch (err) {
    error.value = err as ApiError
  }
}

async function fetchCase() {
  const id = String(route.params.id || '').trim()
  if (!id) return

  loading.value = true
  error.value = null

  try {
    caseData.value = await getCase(id)
    form.title = caseData.value.title || ''
    form.status = caseData.value.status || ''
    form.app_no = caseData.value.app_no || ''
    form.filing_date = caseData.value.filing_date || ''
    form.applicants = (caseData.value.applicants || []).map((applicant, index) => ({
      seq: index + 1,
      is_first: applicant.is_first ?? index === 0,
      source_client_id: '',
      name_cn: applicant.name_cn || '',
      name_en: applicant.name_en || '',
      address_cn: applicant.address_cn || '',
      address_en: applicant.address_en || '',
    }))
    form.priorities = (caseData.value.priorities || []).map((priority, index) => ({
      seq: index + 1,
      country_code: priority.country_code || '',
      prio_no: priority.prio_no || '',
      prio_date: priority.prio_date || '',
    }))
    form.bio_deposits = (caseData.value.bio_deposits || []).map((bioDeposit, index) => ({
      seq: index + 1,
      deposit_no: bioDeposit.deposit_no || '',
      deposit_unit_name: bioDeposit.deposit_unit_name || '',
      deposit_date: bioDeposit.deposit_date || '',
      name: bioDeposit.name || '',
    }))
    form.foreign_agent_id = caseData.value.foreign_agent_id || ''
    form.foreign_ref = caseData.value.foreign_ref || ''
    form.ro = caseData.value.ro || ''
    form.isa = caseData.value.isa || ''
    form.ipea = caseData.value.ipea || ''
    form.intl_app_no = caseData.value.intl_app_no || ''
    form.intl_app_date = caseData.value.intl_app_date || ''
    form.intl_pub_no = caseData.value.intl_pub_no || ''
    form.intl_pub_date = caseData.value.intl_pub_date || ''
    form.intl_pub_lang = caseData.value.intl_pub_lang || ''
    form.need_iper = caseData.value.need_iper ?? false
    form.iper_date = caseData.value.iper_date || ''
    form.pct_national_entry_date = caseData.value.pct_national_entry_date || ''
    form.original_case_id = caseData.value.original_case_id || ''
    form.invalid_client_id = caseData.value.invalid_client_id || ''
    form.invalid_patentee = caseData.value.invalid_patentee || ''
    form.invalid_requester = caseData.value.invalid_requester || ''
    form.invalid_role = caseData.value.invalid_role || ''
    form.pub_date = caseData.value.pub_date || ''
    form.pub_no = caseData.value.pub_no || ''
    form.grant_date = caseData.value.grant_date || ''
    form.grant_no = caseData.value.grant_no || ''
    form.patent_no = caseData.value.patent_no || ''
    form.valid_until = caseData.value.valid_until || ''
    form.spec_pages = caseData.value.spec_pages ?? undefined
    form.claim_count = caseData.value.claim_count ?? undefined
    form.has_exam_request = caseData.value.has_exam_request ?? undefined
    form.primary_agent_id = caseData.value.primary_agent_id || ''
    form.second_agent_id = caseData.value.second_agent_id || ''
    form.draftor_id = caseData.value.draftor_id || ''
    form.is_fee_monitor = caseData.value.is_fee_monitor ?? undefined
    form.fee_reduction = caseData.value.fee_reduction || ''
    form.applicant_kind = caseData.value.applicant_kind || ''
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function addPriority() {
  const nextSeq = (form.priorities?.length || 0) + 1
  form.priorities = [...(form.priorities || []), createEmptyPriority(nextSeq)]
}

function addApplicant() {
  const nextSeq = (form.applicants?.length || 0) + 1
  form.applicants = [...(form.applicants || []), createEmptyApplicant(nextSeq)]
  expandedSections.value = Array.from(new Set([...expandedSections.value, 'applicant']))
}

function addBioDeposit() {
  const nextSeq = (form.bio_deposits?.length || 0) + 1
  form.bio_deposits = [...(form.bio_deposits || []), createEmptyBioDeposit(nextSeq)]
  expandedSections.value = Array.from(new Set([...expandedSections.value, 'bio']))
}

function removeBioDeposit(index: number) {
  const nextDeposits = [...(form.bio_deposits || [])]
  nextDeposits.splice(index, 1)
  form.bio_deposits = nextDeposits.map((bioDeposit, seq) => ({ ...bioDeposit, seq: seq + 1 }))
}

function removeApplicant(index: number) {
  const nextApplicants = [...(form.applicants || [])]
  nextApplicants.splice(index, 1)
  form.applicants = nextApplicants.map((applicant, seq) => ({
    ...applicant,
    seq: seq + 1,
    is_first: nextApplicants.length === 1 ? true : applicant.is_first,
  }))
  if ((form.applicants || []).length === 1) {
    form.applicants[0].is_first = true
  }
}

function applyClientToApplicant(index: number, client: Client) {
  const nextApplicants = [...(form.applicants || [])]
  const current = nextApplicants[index] || createEmptyApplicant(index + 1)
  nextApplicants[index] = {
    ...current,
    seq: index + 1,
    source_client_id: client.id,
    name_cn: client.name_cn || client.name || current.name_cn || '',
    name_en: client.name_en || current.name_en || '',
  }
  form.applicants = nextApplicants
  fieldErrors.value.delete('applicants')
  validationSummary.value = validationSummary.value.filter((item) => item.key !== 'applicants')
}

function handleApplicantClientSelect(index: number, clientId: string | number | null | undefined) {
  const normalizedId = String(clientId || '').trim()
  if (!normalizedId) return
  const selected = clients.value.find((client) => client.id === normalizedId)
  if (!selected) return
  applyClientToApplicant(index, selected)
}

function openQuickClientDialog(mode: 'applicant' | 'foreign_agent', applicantIndex?: number) {
  quickClientMode.value = mode
  quickApplicantIndex.value = mode === 'applicant' ? applicantIndex ?? null : null
  if (mode === 'foreign_agent') {
    quickClientForm.client_type = 'AGENT'
  }
  showQuickClientDialog.value = true
}

function handleQuickApplicantCreate() {
  if (!form.applicants?.length) {
    addApplicant()
    openQuickClientDialog('applicant', 0)
    return
  }
  openQuickClientDialog('applicant', (form.applicants?.length || 1) - 1)
}

function removePriority(index: number) {
  const nextPriorities = [...(form.priorities || [])]
  nextPriorities.splice(index, 1)
  form.priorities = nextPriorities.map((priority, seq) => ({ ...priority, seq: seq + 1 }))
}

function runCustomValidation(): ValidationItem[] {
  const items: ValidationItem[] = []
  const seen = new Set<string>()
  const add = (key: string, message: string, section?: string) => {
    const token = `${key}:${message}`
    if (seen.has(token)) return
    seen.add(token)
    items.push({ key, message, section })
  }

  const status = (form.status || '').trim()
  if (status && STATUSES_REQUIRING_APP_FIELDS.includes(status)) {
    if (!String(form.app_no || '').trim()) {
      add('app_no', '当前法律状态要求填写申请号。', 'pub_grant')
    }
    if (!String(form.filing_date || '').trim()) {
      add('filing_date', '当前法律状态要求填写申请日。', 'pub_grant')
    }
  }

  ;(form.priorities || []).forEach((priority, index) => {
    const hasAnyValue = [priority.country_code, priority.prio_no, priority.prio_date].some((value) => String(value || '').trim())
    const hasAllValues = [priority.country_code, priority.prio_no, priority.prio_date].every((value) => String(value || '').trim())
    if (hasAnyValue && !hasAllValues) {
      add('priorities', `优先权 ${index + 1} 需要同时填写国家/地区、号码和日期。`, 'priority')
    }
  })

  const filledApplicants = (form.applicants || []).filter((applicant) =>
    [applicant.name_cn, applicant.name_en, applicant.address_cn, applicant.address_en].some((value) => String(value || '').trim())
  )
  if (filledApplicants.length) {
    const firstCount = filledApplicants.filter((applicant) => applicant.is_first).length
    if (firstCount !== 1) {
      add('applicants', '申请人信息必须且只能指定一名第一申请人。', 'applicant')
    }
    filledApplicants.forEach((applicant, index) => {
      if (![applicant.name_cn, applicant.name_en].some((value) => String(value || '').trim())) {
        add('applicants', `申请人 ${index + 1} 至少填写中文名或英文名。`, 'applicant')
      }
    })
  }

  if (isForeignFlow.value && !String(form.foreign_agent_id || '').trim()) {
    add('foreign_agent_id', '涉外流程方向下必须选择外方代理。', 'foreign_agent')
  }

  ;(form.bio_deposits || []).forEach((bioDeposit, index) => {
    const hasAnyValue = [bioDeposit.deposit_no, bioDeposit.deposit_unit_name, bioDeposit.deposit_date, bioDeposit.name].some(
      (value) => String(value || '').trim()
    )
    const hasAllValues = [bioDeposit.deposit_no, bioDeposit.deposit_unit_name, bioDeposit.deposit_date, bioDeposit.name].every(
      (value) => String(value || '').trim()
    )
    if (hasAnyValue && !hasAllValues) {
      add('bio_deposits', `菌种保藏 ${index + 1} 需要同时填写保藏编号、保藏单位、保藏日期和菌种名称。`, 'bio')
    }
  })

  const bioSeqs = (form.bio_deposits || []).map((bioDeposit) => bioDeposit.seq)
  if (bioSeqs.length !== new Set(bioSeqs).size) {
    add('bio_deposits', '菌种保藏序号不能重复。', 'bio')
  }

  if (isPctIntlCase.value) {
    if (!String(form.intl_app_no || '').trim() || !String(form.intl_app_date || '').trim()) {
      add('pct', 'PCT 国际阶段案件必须填写国际申请号和国际申请日。', 'pct')
    }
  }

  if (isPctNatlCase.value && !String(form.pct_national_entry_date || '').trim()) {
    add('pct', 'PCT 国家阶段案件必须填写国家阶段进入日。', 'pct')
  }

  if (isInvalidationCase.value) {
    if (!String(form.invalid_client_id || '').trim() || !String(form.invalid_role || '').trim()) {
      add('invalidation', '无效案件必须填写委托方和我方角色。', 'invalidation')
    }
    if (!String(form.invalid_patentee || '').trim() && !String(form.invalid_requester || '').trim()) {
      add('invalidation', '无效案件至少填写专利权人或请求人之一。', 'invalidation')
    }
  }

  return items
}

function mergeFieldErrors(items: ValidationItem[]) {
  const next = new Map<string, string[]>(fieldErrors.value)
  for (const item of items) {
    const current = next.get(item.key) || []
    current.push(item.message)
    next.set(item.key, current)
  }
  fieldErrors.value = next
}

async function handleSave() {
  const id = String(route.params.id || '').trim()
  if (!id) return

  fieldErrors.value = new Map()
  validationSummary.value = []

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) {
    validationSummary.value = [{ key: 'form', message: '请先修正表单基础字段。' }]
    return
  }

  const customErrors = runCustomValidation()
  if (customErrors.length) {
    validationSummary.value = customErrors
    mergeFieldErrors(customErrors)
    expandedSections.value = Array.from(
      new Set([...expandedSections.value, ...customErrors.map((item) => item.section).filter(Boolean) as string[]])
    )
    return
  }

  saving.value = true
  error.value = null

  try {
    const payload: CaseUpdatePayload = {
      ...form,
      applicants: form.applicants
        ?.filter((applicant) =>
          [applicant.name_cn, applicant.name_en, applicant.address_cn, applicant.address_en].some((value) => String(value || '').trim())
        )
        .map((applicant, index) => ({
          ...applicant,
          seq: index + 1,
        })),
      priorities: form.priorities?.filter((priority) =>
        [priority.country_code, priority.prio_no, priority.prio_date].some((value) => String(value || '').trim())
      ),
      bio_deposits: form.bio_deposits?.filter((bioDeposit) =>
        [bioDeposit.deposit_no, bioDeposit.deposit_unit_name, bioDeposit.deposit_date, bioDeposit.name].some((value) => String(value || '').trim())
      ),
    }

    if (READONLY_STATUS_VALUES.includes((payload.status || '').trim() as typeof READONLY_STATUS_VALUES[number])) {
      delete payload.status
    }

    await updateCase(id, payload)
    ElMessage.success('案件更新成功')
    router.push(`/cases/${id}`)
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError

    if (apiError.status === 422 && apiError.details) {
      fieldErrors.value = mapValidationDetailsToFieldErrors(apiError.details)
      validationSummary.value = [{ key: 'api', message: '后端校验未通过，请检查表单字段。' }]
    }
  } finally {
    saving.value = false
  }
}

function handleCancel() {
  const id = route.params.id
  router.push(`/cases/${id}`)
}

function resetQuickClientDialog() {
  showQuickClientDialog.value = false
  quickApplicantIndex.value = null
  quickClientMode.value = 'applicant'
  quickClientForm.name = ''
  quickClientForm.client_code = ''
  quickClientForm.name_en = ''
  quickClientForm.client_type = ''
  quickClientForm.default_currency = 'CNY'
  quickClientForm.email = ''
}

async function handleQuickClientSave() {
  if (!quickClientForm.name.trim()) {
    ElMessage.warning('请先填写客户名称')
    return
  }

  creatingClient.value = true
  try {
    const created = await createClient({
      ...quickClientForm,
      name: quickClientForm.name.trim(),
      client_code: quickClientForm.client_code?.trim(),
      name_en: quickClientForm.name_en?.trim(),
      client_type: quickClientForm.client_type?.trim(),
      email: quickClientForm.email?.trim(),
    })
    await fetchClients()
    if (quickClientMode.value === 'foreign_agent') {
      form.foreign_agent_id = created.id
      ElMessage.success('外方代理已创建并回填')
    } else {
      const applicantIndex = quickApplicantIndex.value ?? form.applicants?.length ?? 0
      if (!form.applicants?.[applicantIndex]) {
        addApplicant()
      }
      applyClientToApplicant(applicantIndex, created)
      ElMessage.success('申请人主数据已创建并回填')
    }
    resetQuickClientDialog()
  } catch (err) {
    error.value = err as ApiError
  } finally {
    creatingClient.value = false
  }
}

onMounted(() => {
  fetchClients()
  fetchCase()
})
</script>

<style scoped>
.full-width {
  width: 100%;
}

.validation-summary {
  margin-bottom: 20px;
}

.validation-summary-list {
  margin: 8px 0 0;
  padding-left: 18px;
}

.field-hint {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 4px;
}

.section-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.section-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.applicant-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.applicant-address-row {
  margin-top: 12px;
}

.section-error {
  margin-bottom: 12px;
  color: var(--el-color-danger);
  font-size: 13px;
}

.priority-card {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  background: var(--color-bg-card);
}

.priority-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
}
</style>
