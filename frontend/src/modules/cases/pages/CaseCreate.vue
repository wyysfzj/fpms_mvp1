<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">新建案件</h1>
      </div>
      <div class="page-header-right">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          创建案件
        </el-button>
      </div>
    </div>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div v-if="loadingClients" class="page-loading">
      <el-skeleton :rows="6" animated />
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
          <li v-for="item in validationSummary" :key="item.key">
            {{ item.message }}
          </li>
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
          <h3 class="form-section-title">基础信息</h3>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="案号" prop="case_no" :error="fieldErrors.get('case_no')?.join('，')">
                <el-input v-model="form.case_no" placeholder="请输入案号（例如：P2024-001）" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="案件类型" prop="case_type" :error="fieldErrors.get('case_type')?.join('，')">
                <el-select v-model="form.case_type" class="full-width" placeholder="请选择案件类型">
                  <el-option
                    v-for="option in CASE_TYPE_OPTIONS"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="专利类别" prop="patent_category" :error="fieldErrors.get('patent_category')?.join('，')">
                <el-select
                  v-model="form.patent_category"
                  class="full-width"
                  placeholder="请选择专利类别"
                  :disabled="isConsultingCase"
                >
                  <el-option
                    v-for="option in PATENT_CATEGORY_OPTIONS"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
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
              <el-form-item label="流程方向" prop="flow_dir" :error="fieldErrors.get('flow_dir')?.join('，')">
                <el-select v-model="form.flow_dir" class="full-width" placeholder="请选择流程方向">
                  <el-option
                    v-for="option in FLOW_DIR_OPTIONS"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="客户" prop="client_id" :error="fieldErrors.get('client_id')?.join('，')">
            <div class="client-field">
              <el-select
                v-model="form.client_id"
                placeholder="请选择客户"
                :loading="loadingClients"
                filterable
                class="full-width"
              >
                <el-option
                  v-for="client in clients"
                  :key="client.id"
                  :label="client.name"
                  :value="client.id"
                />
              </el-select>
              <el-button plain @click="openQuickClientDialog('client')">快速新建客户</el-button>
            </div>
            <div v-if="clientsTotal > clients.length" class="field-hint">
              当前显示 {{ clients.length }} / {{ clientsTotal }} 位客户
            </div>
          </el-form-item>
        </div>

        <div class="form-section" v-if="!isConsultingCase">
          <h3 class="form-section-title">补充字段</h3>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="收文日" :error="fieldErrors.get('recv_date')?.join('，')">
                <el-date-picker v-model="form.recv_date" type="date" placeholder="请选择收文日" format="YYYY-MM-DD" value-format="YYYY-MM-DD" class="full-width" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="发证日" :error="fieldErrors.get('issue_date')?.join('，')">
                <el-date-picker v-model="form.issue_date" type="date" placeholder="请选择发证日" format="YYYY-MM-DD" value-format="YYYY-MM-DD" class="full-width" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="首年年费年度" :error="fieldErrors.get('first_annuity_year')?.join('，')">
                <el-input-number v-model="form.first_annuity_year" :min="1" controls-position="right" placeholder="请输入首年年费年度" class="full-width" />
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

          <el-collapse-item v-if="!isConsultingCase" title="涉外代理信息" name="foreign_agent">
            <div class="section-toolbar">
              <div class="field-hint">涉外流程方向下必须维护外方代理，可直接从客户主数据选择或快速新建后回填。</div>
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
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="来源国家/地区" :error="fieldErrors.get('from_country')?.join('，')">
                  <el-input v-model="form.from_country" placeholder="请输入来源国家/地区代码" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="目标国家/地区" :error="fieldErrors.get('to_country')?.join('，')">
                  <el-input v-model="form.to_country" placeholder="请输入目标国家/地区代码" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="公文地址" :error="fieldErrors.get('doc_address_id')?.join('，')">
                  <el-input v-model="form.doc_address_id" placeholder="请输入客户地址主数据" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="账单地址" :error="fieldErrors.get('bill_address_id')?.join('，')">
                  <el-input v-model="form.bill_address_id" placeholder="请输入客户地址主数据" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>

          <el-collapse-item v-if="showPrioritySection" title="优先权信息" name="priority">
            <div class="section-toolbar">
              <div class="field-hint">当存在优先权时，每条记录都必须完整填写国家/地区、号码和日期。</div>
              <el-button text type="primary" @click="addPriority">新增优先权</el-button>
            </div>
            <div v-if="fieldErrors.get('priorities')?.length" class="section-error">
              {{ fieldErrors.get('priorities')?.join('，') }}
            </div>
            <div v-if="!form.priorities?.length" class="field-hint">当前案件类型建议补充优先权记录；如不适用，可留空。</div>
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
                  <el-input v-model="priority.country_code" placeholder="国家/地区代码" />
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
                <el-col :span="8">
                  <el-form-item label="RO">
                    <el-input v-model="form.ro" placeholder="受理局" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="ISA">
                    <el-input v-model="form.isa" placeholder="国际检索单位" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="IPEA">
                    <el-input v-model="form.ipea" placeholder="国际初审单位" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="国际公开号">
                    <el-input v-model="form.intl_pub_no" placeholder="请输入国际公开号" />
                  </el-form-item>
                </el-col>
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
                <el-col :span="8">
                  <el-form-item label="国际公开语言">
                    <el-input v-model="form.intl_pub_lang" placeholder="请输入国际公开语言代码" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="需要 IPER">
                    <el-switch v-model="form.need_iper" />
                  </el-form-item>
                </el-col>
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
                <el-form-item label="原案">
                  <el-input v-model="form.original_case_id" placeholder="请输入被攻击原案" />
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
              <el-col :span="12">
                <el-form-item label="专利权人">
                  <el-input v-model="form.invalid_patentee" placeholder="请输入专利权人名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="请求人">
                  <el-input v-model="form.invalid_requester" placeholder="请输入请求人名称" />
                </el-form-item>
              </el-col>
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
                <el-form-item label="申请号" :error="fieldErrors.get('app_no')?.join('，')">
                  <el-input v-model="form.app_no" placeholder="用于后续状态联动校验" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="发证日" :error="fieldErrors.get('issue_date')?.join('，')">
                  <el-date-picker v-model="form.issue_date" type="date" placeholder="请选择发证日" format="YYYY-MM-DD" value-format="YYYY-MM-DD" class="full-width" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="证书号" :error="fieldErrors.get('cert_no')?.join('，')">
                  <el-input v-model="form.cert_no" placeholder="请输入证书号" />
                </el-form-item>
              </el-col>
            </el-row>
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
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="附图页数" :error="fieldErrors.get('draw_pages')?.join('，')">
                  <el-input-number v-model="form.draw_pages" :min="0" controls-position="right" placeholder="页数" class="full-width" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="权利要求页数" :error="fieldErrors.get('claim_pages')?.join('，')">
                  <el-input-number v-model="form.claim_pages" :min="0" controls-position="right" placeholder="页数" class="full-width" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="说明书字数" :error="fieldErrors.get('manuscript_words')?.join('，')">
                  <el-input-number v-model="form.manuscript_words" :min="0" controls-position="right" placeholder="字数" class="full-width" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>

          <el-collapse-item title="代理人分配" name="agent">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="主办代理人">
                  <el-input v-model="form.primary_agent_id" placeholder="请输入代理人" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="辅办代理人">
                  <el-input v-model="form.second_agent_id" placeholder="请输入代理人" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="撰写人">
                  <el-input v-model="form.draftor_id" placeholder="请输入撰写人" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>

          <el-collapse-item title="代理人分摊" name="agent_split">
            <div class="section-toolbar">
              <div class="field-hint">当前仅支持“代理人”角色。每行填写代理人、角色和分摊比例，比例总和必须等于 100。</div>
            </div>
            <div v-if="agentSplitErrorItems.length" class="section-error">
              <div>代理人分摊校验未通过：</div>
              <ul class="validation-summary-list">
                <li v-for="item in agentSplitErrorItems" :key="item.key + item.message">{{ item.message }}</li>
              </ul>
            </div>
            <CaseAgentSplitEditor v-model="form.agent_splits" :row-errors="agentSplitRowErrors" />
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
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="减免比例" :error="fieldErrors.get('discount_rate')?.join('，')">
                  <el-input v-model="form.discount_rate" placeholder="请输入 0 到 1 之间的小数" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="无委托书">
                  <el-switch v-model="form.no_power" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="无优先权文本">
                  <el-switch v-model="form.no_prio_text" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="要求港澳台">
                  <el-switch v-model="form.require_hk" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>
        </el-collapse>

        <div class="form-section intake-gate-section">
          <div class="intake-gate-header">
            <div>
              <h3 class="form-section-title">收案文件与材料核验</h3>
              <p class="intake-gate-subtitle">
                本区仅展示收案文件、材料清单和建案门禁预览；不会上传文件，也不会改变创建案件请求。
              </p>
            </div>
            <el-tag type="warning" effect="plain">递交前仍需最终材料核验</el-tag>
          </div>

          <div class="intake-gate-grid">
            <div class="intake-gate-card">
              <div class="intake-card-title">收案文件包</div>
              <div class="intake-drop-zone">
                <strong>上传客户邮件、压缩包或申请文件</strong>
                <span>文件先作为收案证据保存；当前页面只读取门禁预览，不调用上传接口。</span>
                <el-button type="primary" plain disabled>选择文件</el-button>
              </div>
              <el-skeleton v-if="intakeGateLoading" :rows="4" animated />
              <el-alert
                v-else-if="intakeGateError"
                title="收案材料门禁加载失败"
                type="error"
                show-icon
                :closable="false"
                :description="intakeGateError.message"
              />
              <el-empty
                v-else-if="!intakeGate"
                description="暂无收案材料门禁数据"
                :image-size="72"
              />
              <table v-else class="intake-table">
                <thead>
                  <tr>
                    <th>材料要求</th>
                    <th>匹配文件</th>
                    <th>材料角色</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="check in intakeGate.checks" :key="check.requirement_code">
                    <td>{{ check.requirement_name }}</td>
                    <td>{{ matchedDocumentText(check) }}</td>
                    <td>{{ check.role }}</td>
                    <td>
                      <el-tag :type="checkStatusTagType(check)" size="small">
                        {{ checkStatusText(check) }}
                      </el-tag>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="intake-gate-card">
              <div class="intake-card-title">收案材料门禁预览</div>
              <el-skeleton v-if="intakeGateLoading" :rows="4" animated />
              <el-alert
                v-else-if="intakeGateError"
                title="无法获取门禁结论"
                type="error"
                show-icon
                :closable="false"
                :description="intakeGateError.message"
              />
              <el-empty
                v-else-if="!intakeGate"
                description="暂无门禁结论"
                :image-size="72"
              />
              <template v-else>
                <table class="intake-table">
                  <thead>
                    <tr>
                      <th>指标</th>
                      <th>当前值</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>已匹配材料</td>
                      <td>{{ intakeGate.material_count }} 项</td>
                    </tr>
                    <tr>
                      <td>缺失材料</td>
                      <td>{{ intakeGate.missing_items.length }} 项</td>
                    </tr>
                    <tr>
                      <td>硬性阻止</td>
                      <td>{{ intakeGate.hard_block ? '是' : '否' }}</td>
                    </tr>
                    <tr>
                      <td>后补审计</td>
                      <td>{{ intakeGate.afterfill_audit_required ? '需要' : '不需要' }}</td>
                    </tr>
                  </tbody>
                </table>

                <table v-if="intakeGate.missing_items.length" class="intake-table intake-missing-table">
                  <thead>
                    <tr>
                      <th>缺失项</th>
                      <th>材料角色</th>
                      <th>处理方式</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in intakeGate.missing_items" :key="item.requirement_code">
                      <td>{{ item.requirement_name }}</td>
                      <td>{{ item.role }}</td>
                      <td>{{ item.blocks_submission ? '补齐后递交' : item.afterfill_allowed ? '允许后补' : '不阻止' }}</td>
                    </tr>
                  </tbody>
                </table>
                <el-empty
                  v-else
                  description="当前门禁没有缺失材料"
                  :image-size="56"
                  class="intake-empty"
                />

                <el-alert
                  :title="intakeGateConclusionTitle"
                  :type="gateConclusionAlertType(intakeGate.conclusion)"
                  show-icon
                  :closable="false"
                  class="intake-gate-alert"
                />
              </template>
              <el-alert
                title="非闭合范围：不递交、不生成最终申请文件、不生成官费时限。"
                type="error"
                show-icon
                :closable="false"
                class="intake-gate-alert"
              />
            </div>
          </div>
        </div>
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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createCase, getCaseIntakeDocumentGate } from '../../../api/cases'
import { createClient, getClients } from '../../../api/clients'
import type {
  CaseAgentSplit,
  CaseApplicant,
  CaseCreatePayload,
  CaseDocumentGateCheck,
  CaseDocumentGateConclusion,
  CaseDocumentGatePreview,
  CasePriority,
} from '../../../api/cases.types'
import type { Client, ClientCreatePayload } from '../../../api/clients.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import CaseAgentSplitEditor from '../components/CaseAgentSplitEditor.vue'
import { mapValidationDetailsToFieldErrors } from '../../../utils/validation'

interface ValidationItem {
  key: string
  message: string
  section?: string
}

const CASE_TYPE_OPTIONS = [
  { label: '普通案件', value: 'NORMAL' },
  { label: 'PCT 国际阶段', value: 'PCT_INTL' },
  { label: 'PCT 国家阶段', value: 'PCT_NATL' },
  { label: '无效案件', value: 'INVALIDATION' },
  { label: '优先权案件', value: 'PRIORITY' },
  { label: '顾问项目', value: 'CONSULTING' },
  { label: '检索项目', value: 'SEARCH' },
]

const PATENT_CATEGORY_OPTIONS = [
  { label: '发明', value: 'INV' },
  { label: '实用新型', value: 'UM' },
  { label: '外观设计', value: 'DES' },
]

const FLOW_DIR_OPTIONS = [
  { label: '中国国内', value: 'CN_DOMESTIC' },
  { label: '中国向外', value: 'CN_OUTBOUND' },
  { label: '国外进入中国', value: 'FOREIGN_INBOUND' },
]

const PRIORITY_CASE_TYPES = ['PRIORITY', 'PCT_INTL', 'PCT_NATL']
const CONSULTING_CASE_TYPES = ['CONSULTING', 'SEARCH']
const INVALID_ROLE_OPTIONS = [
  { label: '代表专利权人', value: 'PATENTEE' },
  { label: '代表请求人', value: 'REQUESTER' },
  { label: '双方均代表', value: 'BOTH' },
]

const router = useRouter()

const formRef = ref<FormInstance>()
const saving = ref(false)
const loadingClients = ref(false)
const creatingClient = ref(false)
const error = ref<ApiError | null>(null)
const intakeGate = ref<CaseDocumentGatePreview | null>(null)
const intakeGateLoading = ref(false)
const intakeGateError = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const validationSummary = ref<ValidationItem[]>([])
const agentSplitRowErrors = ref<string[][]>([])

const clients = ref<Client[]>([])
const clientsTotal = ref(0)
const expandedSections = ref<string[]>([])
const showQuickClientDialog = ref(false)
const quickClientMode = ref<'client' | 'applicant' | 'foreign_agent'>('client')
const quickApplicantIndex = ref<number | null>(null)
const agentSplitErrorItems = computed(() => {
  const items: ValidationItem[] = []
  const seen = new Set<string>()
  const addMessages = (key: string, label: string) => {
    const messages = fieldErrors.value.get(key) || []
    for (const message of messages) {
      const token = `${key}:${message}`
      if (seen.has(token)) continue
      seen.add(token)
      items.push({ key, message: `${label}${message}` })
    }
  }

  addMessages('agent_splits', '代理人分摊：')
  addMessages('agent_id', '代理人：')
  addMessages('role', '角色：')
  addMessages('share_ratio', '分摊比例：')

  return items
})

const form = reactive<CaseCreatePayload>({
  case_no: '',
  case_type: 'NORMAL',
  title: '',
  client_id: '',
  patent_category: 'INV',
  flow_dir: 'CN_DOMESTIC',
  app_no: '',
  applicants: [],
  priorities: [],
  bio_deposits: [],
  foreign_agent_id: '',
  foreign_ref: '',
  from_country: '',
  to_country: '',
  doc_address_id: '',
  bill_address_id: '',
  recv_date: '',
  issue_date: '',
  cert_no: '',
  draw_pages: undefined,
  claim_pages: undefined,
  manuscript_words: undefined,
  discount_rate: '',
  no_power: false,
  no_prio_text: false,
  require_hk: false,
  first_annuity_year: undefined,
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
  agent_splits: [],
})

const quickClientForm = reactive<ClientCreatePayload>({
  name: '',
  client_code: '',
  name_en: '',
  client_type: '',
  default_currency: 'CNY',
  email: '',
})

const isConsultingCase = computed(() => CONSULTING_CASE_TYPES.includes(form.case_type || 'NORMAL'))
const isForeignFlow = computed(() => (form.flow_dir || 'CN_DOMESTIC') !== 'CN_DOMESTIC')
const isPctIntlCase = computed(() => form.case_type === 'PCT_INTL')
const isPctNatlCase = computed(() => form.case_type === 'PCT_NATL')
const isInvalidationCase = computed(() => form.case_type === 'INVALIDATION')
const showPrioritySection = computed(() => PRIORITY_CASE_TYPES.includes(form.case_type || 'NORMAL'))
const showPublicationSection = computed(() => !isConsultingCase.value)
const showSpecificationSection = computed(() => !isConsultingCase.value)
const showBioDepositSection = computed(() => !isConsultingCase.value)
const hasPriorityForGate = computed(() =>
  showPrioritySection.value
  || (form.priorities || []).some((priority) =>
    [priority.country_code, priority.prio_no, priority.prio_date].some((value) => String(value || '').trim())
  )
)
const intakeGateParams = computed(() => ({
  case_type: form.case_type || 'NORMAL',
  patent_category: form.patent_category || 'INV',
  flow_dir: form.flow_dir || 'CN_DOMESTIC',
  has_exam_request: Boolean(form.has_exam_request),
  no_power: Boolean(form.no_power),
  has_priority: hasPriorityForGate.value,
}))
const intakeGateConclusionTitle = computed(() => {
  if (!intakeGate.value) return '门禁结论：暂无数据'
  const actions = intakeGate.value.suggested_actions.length
    ? `；${intakeGate.value.suggested_actions.join('；')}`
    : ''
  return `门禁结论：${gateConclusionText(intakeGate.value.conclusion)}${actions}`
})
const quickClientDialogTitle = computed(() =>
  quickClientMode.value === 'client'
    ? '快速新建客户'
    : quickClientMode.value === 'foreign_agent'
      ? '快速新建外方代理'
      : '快速新建申请人主数据'
)

const rules: FormRules = {
  case_no: [{ required: true, message: '案号为必填项', trigger: 'blur' }],
  case_type: [{ required: true, message: '请选择案件类型', trigger: 'change' }],
  patent_category: [
    {
      trigger: 'change',
      validator: (_rule, value, callback) => {
        if (isConsultingCase.value || String(value || '').trim()) {
          callback()
          return
        }
        callback(new Error('请选择专利类别'))
      },
    },
  ],
  client_id: [{ required: true, message: '请选择客户', trigger: 'change' }],
}

function gateConclusionText(conclusion: CaseDocumentGateConclusion) {
  if (conclusion === 'PASS') return '通过'
  if (conclusion === 'WARNING') return '需后补'
  if (conclusion === 'BLOCKED') return '阻止'
  return conclusion
}

function gateConclusionAlertType(conclusion: CaseDocumentGateConclusion): 'success' | 'warning' | 'error' | 'info' {
  if (conclusion === 'PASS') return 'success'
  if (conclusion === 'WARNING') return 'warning'
  if (conclusion === 'BLOCKED') return 'error'
  return 'info'
}

function matchedDocumentText(check: CaseDocumentGateCheck) {
  const titles = check.matched_documents
    .map((document) => document.title || document.template_code || '未命名匹配文件')
    .filter(Boolean)
  return titles.length ? titles.join('，') : '未匹配'
}

function checkStatusText(check: CaseDocumentGateCheck) {
  if (check.status === 'MATCHED') return '已匹配'
  if (check.afterfill_allowed) return '允许后补'
  if (check.blocks_submission) return '缺失阻止'
  return '未匹配'
}

function checkStatusTagType(check: CaseDocumentGateCheck): 'success' | 'warning' | 'danger' | 'info' {
  if (check.status === 'MATCHED') return 'success'
  if (check.afterfill_allowed) return 'warning'
  if (check.blocks_submission) return 'danger'
  return 'info'
}

let intakeGateRequestSeq = 0

async function fetchIntakeGatePreview() {
  const requestSeq = ++intakeGateRequestSeq
  intakeGateLoading.value = true
  intakeGateError.value = null

  try {
    const result = await getCaseIntakeDocumentGate(intakeGateParams.value)
    if (requestSeq !== intakeGateRequestSeq) return
    intakeGate.value = result
  } catch (err) {
    if (requestSeq !== intakeGateRequestSeq) return
    intakeGate.value = null
    intakeGateError.value = err as ApiError
  } finally {
    if (requestSeq === intakeGateRequestSeq) {
      intakeGateLoading.value = false
    }
  }
}

watch(
  () => form.case_type,
  (value) => {
    if (CONSULTING_CASE_TYPES.includes(value || '')) {
      form.patent_category = undefined
      form.app_no = ''
      form.pub_date = ''
      form.pub_no = ''
      form.grant_date = ''
      form.grant_no = ''
      form.patent_no = ''
      form.valid_until = ''
      form.spec_pages = undefined
      form.claim_count = undefined
      form.has_exam_request = undefined
      form.is_fee_monitor = undefined
      form.fee_reduction = ''
      form.applicant_kind = ''
      form.foreign_agent_id = ''
      form.foreign_ref = ''
      form.from_country = ''
      form.to_country = ''
      form.doc_address_id = ''
      form.bill_address_id = ''
      form.recv_date = ''
      form.issue_date = ''
      form.cert_no = ''
      form.draw_pages = undefined
      form.claim_pages = undefined
      form.manuscript_words = undefined
      form.discount_rate = ''
      form.no_power = false
      form.no_prio_text = false
      form.require_hk = false
      form.first_annuity_year = undefined
      form.bio_deposits = []
      form.ro = ''
      form.isa = ''
      form.ipea = ''
      form.intl_app_no = ''
      form.intl_app_date = ''
      form.intl_pub_no = ''
      form.intl_pub_date = ''
      form.intl_pub_lang = ''
      form.need_iper = false
      form.iper_date = ''
      form.pct_national_entry_date = ''
      form.original_case_id = ''
      form.invalid_client_id = ''
      form.invalid_patentee = ''
      form.invalid_requester = ''
      form.invalid_role = ''
    } else if (!form.patent_category) {
      form.patent_category = 'INV'
    }

    if (!PRIORITY_CASE_TYPES.includes(value || '')) {
      form.priorities = []
      fieldErrors.value.delete('priorities')
    } else if (!form.priorities?.length) {
      form.priorities = [createEmptyPriority(1)]
      expandedSections.value = Array.from(new Set([...expandedSections.value, 'priority']))
    }

    if (value !== 'PCT_INTL') {
      form.ro = ''
      form.isa = ''
      form.ipea = ''
      form.intl_app_no = ''
      form.intl_app_date = ''
      form.intl_pub_no = ''
      form.intl_pub_date = ''
      form.intl_pub_lang = ''
      form.need_iper = false
      form.iper_date = ''
    }
    if (value !== 'PCT_NATL') {
      form.pct_national_entry_date = ''
    }
    if (value !== 'INVALIDATION') {
      form.original_case_id = ''
      form.invalid_client_id = ''
      form.invalid_patentee = ''
      form.invalid_requester = ''
      form.invalid_role = ''
    }
  },
  { immediate: true }
)

watch(
  () => form.flow_dir,
  (value) => {
    if ((value || 'CN_DOMESTIC') === 'CN_DOMESTIC') {
      form.foreign_agent_id = ''
      form.foreign_ref = ''
      fieldErrors.value.delete('foreign_agent_id')
    }
  }
)

watch(
  intakeGateParams,
  () => {
    void fetchIntakeGatePreview()
  },
  { immediate: true }
)

async function fetchClients() {
  loadingClients.value = true
  try {
    const result = await getClients({ page: 1, page_size: 100 })
    clients.value = result.items
    clientsTotal.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loadingClients.value = false
  }
}

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

function openQuickClientDialog(mode: 'client' | 'applicant' | 'foreign_agent', applicantIndex?: number) {
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

function normalizeFieldErrorsFromSummary(items: ValidationItem[]) {
  const next = new Map<string, string[]>(fieldErrors.value)
  for (const item of items) {
    const current = next.get(item.key) || []
    current.push(item.message)
    next.set(item.key, current)
  }
  fieldErrors.value = next
}

function resetAgentSplitErrors() {
  agentSplitRowErrors.value = []
}

function splitFieldLabel(field: string) {
  if (field === 'agent_id') return '代理人'
  if (field === 'role') return '角色'
  if (field === 'share_ratio') return '分摊比例'
  return field
}

function extractAgentSplitRowErrors(details?: unknown): string[][] {
  const rows: string[][] = []
  const errors = Array.isArray(details)
    ? details
    : details && typeof details === 'object' && Array.isArray((details as Record<string, unknown>).errors)
      ? (details as Record<string, unknown>).errors
      : null
  if (!Array.isArray(errors)) return rows

  for (const err of errors) {
    if (typeof err !== 'object' || err === null) continue
    const loc = (err as { loc?: unknown[] }).loc
    const msg = (err as { msg?: string }).msg
    if (!Array.isArray(loc) || typeof msg !== 'string') continue

    const path = loc.map((item) => String(item))
    const splitIndex = path.indexOf('agent_splits')
    if (splitIndex < 0) continue

    const rowIndex = Number(path[splitIndex + 1])
    if (!Number.isInteger(rowIndex) || rowIndex < 0) continue

    const field = path[splitIndex + 2]
    const prefix = field ? `${splitFieldLabel(field)}：` : ''
    rows[rowIndex] ??= []
    rows[rowIndex].push(`${prefix}${msg}`)
  }

  return rows
}

function normalizeAgentSplitRows(agentSplits: CaseAgentSplit[] | null | undefined): CaseAgentSplit[] {
  return (agentSplits || [])
    .map((split) => ({
      agent_id: String(split.agent_id || '').trim(),
      role: String(split.role || '').trim(),
      share_ratio: split.share_ratio === null || split.share_ratio === undefined ? null : Number(split.share_ratio),
    }))
    .filter((split) =>
      [split.agent_id, split.role, split.share_ratio !== null && split.share_ratio !== undefined].some(Boolean)
    )
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

  if (!form.client_id) {
    add('client_id', '请选择客户，或使用“快速新建客户”后自动回填。')
  }

  if (isForeignFlow.value && !String(form.foreign_agent_id || '').trim()) {
    add('foreign_agent_id', '涉外流程方向下必须选择外方代理。', 'foreign_agent')
  }

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

  if (showPrioritySection.value) {
    ;(form.priorities || []).forEach((priority, index) => {
      const hasAnyValue = [priority.country_code, priority.prio_no, priority.prio_date].some((value) => String(value || '').trim())
      const hasAllValues = [priority.country_code, priority.prio_no, priority.prio_date].every((value) => String(value || '').trim())
      if (hasAnyValue && !hasAllValues) {
        add(
          'priorities',
          `优先权 ${index + 1} 需要同时填写国家/地区、号码和日期。`,
          'priority'
        )
      }
    })
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

  const normalizedAgentSplits = normalizeAgentSplitRows(form.agent_splits)
  if (normalizedAgentSplits.length) {
    const seenAgentIds = new Set<string>()
    let ratioTenThousandths = 0
    let hasRatioError = false

    normalizedAgentSplits.forEach((split, index) => {
      if (!split.agent_id) {
        add('agent_splits', `代理人分摊 ${index + 1} 需要填写代理人。`, 'agent_split')
      } else if (seenAgentIds.has(split.agent_id)) {
        add('agent_splits', `代理人分摊 ${index + 1} 的代理人不能重复。`, 'agent_split')
      } else {
        seenAgentIds.add(split.agent_id)
      }

      if (!split.role) {
        add('agent_splits', `代理人分摊 ${index + 1} 需要选择角色。`, 'agent_split')
      } else if (split.role !== 'Agent') {
        add('agent_splits', `代理人分摊 ${index + 1} 的角色必须为代理人。`, 'agent_split')
      }

      if (split.share_ratio === null || !Number.isFinite(split.share_ratio) || split.share_ratio <= 0) {
        add('agent_splits', `代理人分摊 ${index + 1} 的分摊比例必须大于 0。`, 'agent_split')
        hasRatioError = true
      } else {
        ratioTenThousandths += Math.round(split.share_ratio * 10000)
      }
    })

    if (!hasRatioError && ratioTenThousandths !== 1000000) {
      add('agent_splits', '代理人分摊比例总和必须等于 100。', 'agent_split')
    }
  }

  return items
}

async function handleSave() {
  fieldErrors.value = new Map()
  validationSummary.value = []
  resetAgentSplitErrors()

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) {
    validationSummary.value = [{ key: 'form', message: '请先完成基础必填项。' }]
    return
  }

  const customErrors = runCustomValidation()
  if (customErrors.length) {
    validationSummary.value = customErrors
    normalizeFieldErrorsFromSummary(customErrors)
    expandedSections.value = Array.from(
      new Set([...expandedSections.value, ...customErrors.map((item) => item.section).filter(Boolean) as string[]])
    )
    return
  }

  saving.value = true
  error.value = null

  try {
    await createCase({
      ...form,
      patent_category: isConsultingCase.value ? undefined : form.patent_category,
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
      agent_splits: normalizeAgentSplitRows(form.agent_splits),
    })
    ElMessage.success('案件创建成功')
    router.push('/cases')
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError

    if ((apiError.status === 422 || apiError.status === 400) && apiError.details) {
      fieldErrors.value = mapValidationDetailsToFieldErrors(apiError.details)
      validationSummary.value = [{
        key: 'api',
        message: apiError.status === 400
          ? '后端业务校验未通过，请检查代理人分摊。'
          : '后端校验未通过，请检查表单字段。',
      }]
      const splitRowErrors = extractAgentSplitRowErrors(apiError.details)
      if (splitRowErrors.some((row) => row.length > 0)) {
        agentSplitRowErrors.value = splitRowErrors
        expandedSections.value = Array.from(new Set([...expandedSections.value, 'agent_split']))
        validationSummary.value = validationSummary.value.filter((item) => item.key !== 'api')
      }
    }
  } finally {
    saving.value = false
  }
}

function resetQuickClientDialog() {
  showQuickClientDialog.value = false
  quickApplicantIndex.value = null
  quickClientMode.value = 'client'
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
    if (quickClientMode.value === 'client') {
      form.client_id = created.id
      fieldErrors.value.delete('client_id')
      validationSummary.value = validationSummary.value.filter((item) => item.key !== 'client_id')
      ElMessage.success('客户已创建并回填')
    } else if (quickClientMode.value === 'foreign_agent') {
      form.foreign_agent_id = created.id
      fieldErrors.value.delete('foreign_agent_id')
      validationSummary.value = validationSummary.value.filter((item) => item.key !== 'foreign_agent_id')
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

function handleCancel() {
  router.push('/cases')
}

onMounted(() => {
  fetchClients()
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

.client-field {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: start;
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

.intake-gate-section {
  margin-top: 16px;
}

.intake-gate-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.intake-gate-subtitle {
  margin: 4px 0 0;
  color: var(--text-sub);
  font-size: 13px;
  line-height: 1.6;
}

.intake-gate-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px;
}

.intake-gate-card {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
  background: var(--color-bg-card);
}

.intake-card-title {
  margin-bottom: 12px;
  font-weight: 600;
  color: var(--text-main);
}

.intake-drop-zone {
  display: grid;
  gap: 8px;
  place-items: center;
  min-height: 128px;
  margin-bottom: 14px;
  padding: 16px;
  border: 1px dashed var(--el-color-primary);
  border-radius: 10px;
  background: var(--el-color-primary-light-9);
  text-align: center;
}

.intake-drop-zone span {
  color: var(--text-sub);
  font-size: 13px;
  line-height: 1.5;
}

.intake-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 13px;
}

.intake-table th,
.intake-table td {
  padding: 10px 8px;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
  vertical-align: top;
  overflow-wrap: anywhere;
}

.intake-table th {
  background: var(--el-fill-color-light);
  color: var(--text-main);
  font-weight: 600;
}

.intake-gate-alert {
  margin-top: 12px;
}

.intake-missing-table {
  margin-top: 12px;
}

.intake-empty {
  padding: 8px 0 0;
}

.case-form .el-form-item {
  margin-bottom: 20px;
}

.case-form .el-form-item__label {
  font-weight: 500;
  color: var(--text-main);
}

@media (max-width: 1100px) {
  .intake-gate-header,
  .intake-gate-grid {
    grid-template-columns: 1fr;
  }

  .intake-gate-header {
    display: grid;
  }
}
</style>
