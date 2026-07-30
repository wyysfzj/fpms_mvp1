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
              <el-form-item label="法律状态">
                <el-input :model-value="compatibilityStatusText" disabled />
                <div class="field-hint">
                  兼容状态由案件生命周期维护，此处仅供查看，保存时不会提交。
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
            <el-col :span="8">
              <el-form-item label="收文日" :error="fieldErrors.get('recv_date')?.join('，')">
                <el-date-picker v-model="form.recv_date" type="date" placeholder="请选择收文日" format="YYYY-MM-DD" value-format="YYYY-MM-DD" class="full-width" />
              </el-form-item>
            </el-col>
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
            <el-col :span="8">
              <el-form-item label="发证日" :error="fieldErrors.get('issue_date')?.join('，')">
                <el-date-picker v-model="form.issue_date" type="date" placeholder="请选择发证日" format="YYYY-MM-DD" value-format="YYYY-MM-DD" class="full-width" />
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
              <div class="official-field-group">官方提交字段</div>
              <el-row :gutter="16" class="applicant-address-row">
                <el-col :span="8">
                  <el-form-item label="国籍">
                    <el-input v-model="applicant.nationality" placeholder="例如：中国 / CN" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="证件类型">
                    <el-input v-model="applicant.certificate_type" placeholder="例如：统一社会信用代码" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="证件号">
                    <el-input v-model="applicant.certificate_no" placeholder="请输入官方证件号" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="16">
                <el-col :span="8">
                  <el-form-item label="官方邮编">
                    <el-input v-model="applicant.official_postcode" placeholder="请输入官方邮编" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="官方申请人类型">
                    <el-input v-model="applicant.official_applicant_kind" placeholder="例如：企业 / 个人" />
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
          </el-collapse-item>

          <el-collapse-item v-if="!CONSULTING_CASE_TYPES.includes(caseData?.case_type || '')" title="发明人信息" name="inventor">
            <div class="section-toolbar">
              <div class="field-hint">维护官方递交所需的发明人姓名、国籍和中国籍身份证号。</div>
              <el-button text type="primary" @click="addInventor">新增发明人</el-button>
            </div>
            <div v-if="fieldErrors.get('inventors')?.length" class="section-error">
              {{ fieldErrors.get('inventors')?.join('，') }}
            </div>
            <div v-if="!form.inventors?.length" class="field-hint">当前未维护发明人信息。</div>
            <div
              v-for="(inventor, index) in form.inventors"
              :key="inventor.seq"
              class="priority-card"
            >
              <div class="priority-card-header">
                <span>发明人 {{ index + 1 }}</span>
                <el-button text type="danger" @click="removeInventor(index)">删除</el-button>
              </div>
              <el-row :gutter="16">
                <el-col :span="8">
                  <el-form-item label="中文姓名">
                    <el-input v-model="inventor.name_cn" placeholder="请输入发明人中文姓名" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="英文姓名">
                    <el-input v-model="inventor.name_en" placeholder="请输入发明人英文姓名" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="国籍">
                    <el-input v-model="inventor.nationality" placeholder="例如：中国 / CN" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="16">
                <el-col :span="8">
                  <el-form-item label="中国籍身份证号">
                    <el-input v-model="inventor.china_id_no" placeholder="中国籍发明人需维护" />
                  </el-form-item>
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
                <el-col :span="8"><el-form-item label="国际公开语言"><el-input v-model="form.intl_pub_lang" placeholder="请输入国际公开语言代码" /></el-form-item></el-col>
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
                <el-form-item label="年费监视">
                  <el-switch v-model="form.is_fee_monitor" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="客户减免比例" :error="fieldErrors.get('fee_reduction')?.join('，')">
                  <el-select
                    v-model="form.fee_reduction"
                    data-testid="case-fee-reduction"
                    class="full-width"
                    placeholder="请选择费用减免比例"
                    :disabled="Boolean(reductionApprovalLoadError)"
                    @change="handleFeeReductionSelection"
                  >
                    <el-option label="不减缴" value="0" />
                    <el-option label="70%" value="0.7" :disabled="selectedCanonicalReductionRatio !== '0.7'" />
                    <el-option label="85%" value="0.85" :disabled="selectedCanonicalReductionRatio !== '0.85'" />
                  </el-select>
                  <el-alert
                    v-if="feeReductionSelectionWarning"
                    :title="feeReductionSelectionWarning"
                    type="warning"
                    show-icon
                    :closable="false"
                    class="fee-reduction-selection-warning"
                  />
                  <div class="field-hint">0.7/0.85 仅在选择同一比例的审批依据后可选。</div>
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
              <el-col :span="24">
                <div class="section-toolbar">
                  <div class="field-hint">仅展示并选择后端返回的审批记录；是否适用于具体费用由后端校验。</div>
                  <el-button type="primary" plain @click="openReductionApprovalDialog">记录减缴审批证据</el-button>
                </div>
                <el-alert
                  v-if="reductionApprovalLoadError"
                  :title="reductionApprovalLoadError"
                  type="error"
                  show-icon
                  :closable="false"
                  class="reduction-approval-error"
                />
                <el-form-item label="减缴审批依据">
                  <el-select
                    v-model="selectedReductionApprovalId"
                    aria-label="减缴审批依据"
                    clearable
                    class="full-width"
                    placeholder="请选择后端返回的减缴审批依据"
                  >
                    <el-option
                      v-for="approval in reductionApprovals"
                      :key="approval.approval_id"
                      :label="reductionApprovalOptionLabel(approval)"
                      :value="approval.approval_id"
                    />
                  </el-select>
                  <template v-if="selectedReductionApproval">
                    <div class="field-hint">来源证据：{{ selectedReductionApproval.source_evidence_version_id }}</div>
                    <div class="field-hint">适用范围：{{ reductionApprovalScopeText(selectedReductionApproval.scope_type) }}</div>
                    <div class="field-hint">费用代码：{{ reductionApprovalFeeCodesText(selectedReductionApproval) }}</div>
                    <div class="field-hint">费用年度：{{ reductionApprovalYearsText(selectedReductionApproval) }}</div>
                    <div class="field-hint">生效区间：{{ reductionApprovalEffectiveText(selectedReductionApproval) }}</div>
                    <div class="field-hint">申请人集合：{{ selectedReductionApproval.applicant_set_key || '不适用' }}</div>
                    <div class="field-hint">后端当前标记：{{ selectedReductionApproval.is_current ? '是' : '否' }}</div>
                  </template>
                  <div class="field-hint">选择审批依据仅解锁同一比例选项，不自动写入案件减缴字段。</div>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="系统减免比例" :error="fieldErrors.get('discount_rate')?.join('，')">
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
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="首年年费序号（第几年）" :error="fieldErrors.get('first_annuity_year')?.join('，')">
                  <el-input-number v-model="form.first_annuity_year" :min="1" controls-position="right" placeholder="请输入第几年，例如 1" class="full-width" />
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

    <el-dialog
      v-model="showReductionApprovalDialog"
      title="记录减缴审批证据"
      width="760px"
      destroy-on-close
      @closed="resetReductionApprovalDialog"
    >
      <el-form :model="reductionApprovalDraft" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="审批范围">
              <el-select v-model="reductionApprovalDraft.scope_type" class="full-width" placeholder="请选择审批范围">
                <el-option label="案件" value="CASE" />
                <el-option label="申请人集合" value="APPLICANT_SET" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="减缴比例">
              <el-select v-model="reductionApprovalDraft.reduction_ratio" class="full-width" placeholder="请选择减缴比例">
                <el-option label="70%" value="0.7" />
                <el-option label="85%" value="0.85" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="申请人标识">
          <el-input v-model="reductionApprovalDraft.applicant_ids" placeholder="请输入申请人标识，多个用逗号分隔" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="资格属性版本">
              <el-input v-model="reductionApprovalDraft.eligibility_attributes_version" placeholder="请输入资格属性版本" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="费用代码">
              <el-input v-model="reductionApprovalDraft.fee_codes" placeholder="请输入费用代码，多个用逗号分隔" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="资格属性 JSON">
          <el-input
            v-model="reductionApprovalDraft.eligibility_attributes_json"
            type="textarea"
            :rows="3"
            placeholder="请输入资格属性 JSON"
          />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="费用年度起始">
              <el-input-number v-model="reductionApprovalDraft.fee_year_from" :min="1" class="full-width" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="费用年度截止">
              <el-input-number v-model="reductionApprovalDraft.fee_year_to" :min="1" class="full-width" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="生效起始日">
              <el-input v-model="reductionApprovalDraft.effective_from" placeholder="请选择生效起始日" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生效截止日">
              <el-input v-model="reductionApprovalDraft.effective_to" placeholder="请选择生效截止日（可选）" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="来源证据版本标识">
          <el-input v-model="reductionApprovalDraft.source_evidence_version_id" placeholder="请输入来源证据版本标识" />
        </el-form-item>
        <el-form-item label="来源内容哈希">
          <el-input v-model="reductionApprovalDraft.expected_source_content_hash" placeholder="请输入来源内容哈希" />
        </el-form-item>
        <el-form-item label="确认时间（无时区）">
          <el-input v-model="reductionApprovalDraft.confirmed_at" placeholder="请选择确认时间" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReductionApprovalDialog = false">取消</el-button>
        <el-button type="primary" :loading="recordingReductionApproval" @click="handleReductionApprovalRecord">
          确认记录
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
import { getCase, getCaseByCaseNo, updateCase } from '../../../api/cases'
import { createClient, getClients } from '../../../api/clients'
import { createFeeReductionApproval, getFeeReductionApprovals } from '../../../api/fees'
import type {
  Case,
  CaseAgentSplit,
  CaseApplicant,
  CaseInventor,
  CasePriority,
  CaseUpdatePayload,
} from '../../../api/cases.types'
import type { Client, ClientCreatePayload } from '../../../api/clients.types'
import type {
  FeeReductionApprovalCreatePayload,
  FeeReductionApprovalListItem,
  FeeReductionApprovalScopeType,
} from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import CaseAgentSplitEditor from '../components/CaseAgentSplitEditor.vue'
import { CASE_STATUS_TEXT } from '../../../constants/displayText'
import { mapValidationDetailsToFieldErrors } from '../../../utils/validation'

interface ValidationItem {
  key: string
  message: string
  section?: string
}

interface ReductionApprovalDraft {
  scope_type: FeeReductionApprovalScopeType | ''
  applicant_ids: string
  eligibility_attributes_version: string
  eligibility_attributes_json: string
  reduction_ratio: '0.7' | '0.85' | ''
  fee_codes: string
  fee_year_from: number | undefined
  fee_year_to: number | undefined
  effective_from: string
  effective_to: string
  source_evidence_version_id: string
  expected_source_content_hash: string
  confirmed_at: string
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
const agentSplitRowErrors = ref<string[][]>([])
const clients = ref<Client[]>([])
const creatingClient = ref(false)
const showQuickClientDialog = ref(false)
const quickApplicantIndex = ref<number | null>(null)
const quickClientMode = ref<'applicant' | 'foreign_agent'>('applicant')
const reductionApprovals = ref<FeeReductionApprovalListItem[]>([])
const selectedReductionApprovalId = ref('')
const reductionApprovalLoadError = ref('')
const storedFeeReductionLegacyValue = ref('')
const feeReductionSelectionRequired = ref(false)
const showReductionApprovalDialog = ref(false)
const recordingReductionApproval = ref(false)
const reductionApprovalDraft = reactive<ReductionApprovalDraft>({
  scope_type: '',
  applicant_ids: '',
  eligibility_attributes_version: '',
  eligibility_attributes_json: '',
  reduction_ratio: '',
  fee_codes: '',
  fee_year_from: undefined,
  fee_year_to: undefined,
  effective_from: '',
  effective_to: '',
  source_evidence_version_id: '',
  expected_source_content_hash: '',
  confirmed_at: '',
})

const form = reactive<CaseUpdatePayload>({
  title: '',
  app_no: '',
  filing_date: '',
  recv_date: '',
  issue_date: '',
  cert_no: '',
  from_country: '',
  to_country: '',
  doc_address_id: '',
  bill_address_id: '',
  draw_pages: undefined,
  claim_pages: undefined,
  manuscript_words: undefined,
  discount_rate: '',
  no_power: false,
  no_prio_text: false,
  require_hk: false,
  first_annuity_year: undefined,
  applicants: [],
  inventors: [],
  priorities: [],
  bio_deposits: [],
  agent_splits: [],
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
  pub_date: '',
  pub_no: '',
  grant_date: '',
  grant_no: '',
  patent_no: '',
  valid_until: '',
  spec_pages: undefined,
  claim_count: undefined,
  has_exam_request: undefined,
  primary_agent_id: '',
  second_agent_id: '',
  draftor_id: '',
  is_fee_monitor: false,
  fee_reduction: '',
  applicant_kind: '',
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
const selectedReductionApproval = computed(() =>
  reductionApprovals.value.find((approval) => approval.approval_id === selectedReductionApprovalId.value) || null
)
const selectedCanonicalReductionRatio = computed(() =>
  canonicalReductionRatio(selectedReductionApproval.value?.reduction_ratio || '')
)
const feeReductionSelectionWarning = computed(() => {
  if (!feeReductionSelectionRequired.value) return ''
  if (storedFeeReductionLegacyValue.value) {
    return `历史减免值“${storedFeeReductionLegacyValue.value}”无法识别，请明确选择不减缴、70% 或 85% 后再保存。`
  }
  return '当前案件未设置费用减免比例，请明确选择后再保存。'
})
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

function resetAgentSplitErrors() {
  agentSplitRowErrors.value = []
}

function splitFieldLabel(field: string) {
  if (field === 'agent_id') return '代理人'
  if (field === 'role') return '角色'
  if (field === 'share_ratio') return '分摊比例'
  return field
}

function extractAgentSplitRowErrors(details?: Record<string, unknown>): string[][] {
  const rows: string[][] = []
  const errors = details?.errors
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
const quickClientDialogTitle = computed(() =>
  quickClientMode.value === 'foreign_agent' ? '快速新建外方代理' : '快速新建申请人主数据'
)

const compatibilityStatus = computed(() => (caseData.value?.status || '').trim())
const compatibilityStatusText = computed(() => {
  const status = compatibilityStatus.value
  return CASE_STATUS_TEXT[status] || status || '未设置'
})

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
    nationality: '',
    certificate_type: '',
    certificate_no: '',
    official_postcode: '',
    official_applicant_kind: '',
  }
}

function createEmptyInventor(seq: number): CaseInventor {
  return {
    seq,
    name_cn: '',
    name_en: '',
    nationality: '',
    china_id_no: '',
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

function hasApplicantValue(applicant: CaseApplicant) {
  return [
    applicant.name_cn,
    applicant.name_en,
    applicant.address_cn,
    applicant.address_en,
    applicant.nationality,
    applicant.certificate_type,
    applicant.certificate_no,
    applicant.official_postcode,
    applicant.official_applicant_kind,
  ].some((value) => String(value || '').trim())
}

function hasInventorValue(inventor: CaseInventor) {
  return [inventor.name_cn, inventor.name_en, inventor.nationality, inventor.china_id_no]
    .some((value) => String(value || '').trim())
}

function isChinaNationality(value?: string | null) {
  const normalized = String(value || '').trim().toUpperCase()
  return ['CN', 'CHN', 'CHINA', 'PRC'].includes(normalized) || normalized.includes('中国')
}

async function fetchClients() {
  try {
    const result = await getClients({ page: 1, page_size: 100 })
    clients.value = result.items
  } catch (err) {
    error.value = err as ApiError
  }
}

function reductionApprovalScopeText(scopeType: FeeReductionApprovalScopeType) {
  if (scopeType === 'CASE') return '案件'
  return '申请人集合'
}

function canonicalReductionRatio(value: string): '0.7' | '0.85' | null {
  const [whole, fraction = ''] = value.split('.')
  if (whole !== '0') return null
  const normalizedFraction = fraction.replace(/0+$/, '')
  if (normalizedFraction === '7') return '0.7'
  if (normalizedFraction === '85') return '0.85'
  return null
}

function storedCanonicalReductionRatio(value: unknown): '0' | '0.7' | '0.85' | '' {
  if (value === '0' || value === '0.7' || value === '0.85') {
    storedFeeReductionLegacyValue.value = ''
    feeReductionSelectionRequired.value = false
    return value
  }
  storedFeeReductionLegacyValue.value = typeof value === 'string' ? value : ''
  feeReductionSelectionRequired.value = true
  return ''
}

function handleFeeReductionSelection() {
  storedFeeReductionLegacyValue.value = ''
  feeReductionSelectionRequired.value = false
}

function reductionApprovalOptionLabel(approval: FeeReductionApprovalListItem) {
  const ratio = canonicalReductionRatio(approval.reduction_ratio)
  const ratioText = ratio === '0.7' ? '70%' : ratio === '0.85' ? '85%' : approval.reduction_ratio
  return `${ratioText} · ${reductionApprovalScopeText(approval.scope_type)} · ${approval.source_evidence_version_id}`
}

function reductionApprovalFeeCodesText(approval: FeeReductionApprovalListItem) {
  return approval.fee_codes.join('、')
}

function reductionApprovalYearsText(approval: FeeReductionApprovalListItem) {
  if (approval.fee_year_from === null && approval.fee_year_to === null) return '不限'
  return `${approval.fee_year_from ?? '未指定'} 至 ${approval.fee_year_to ?? '未指定'}`
}

function reductionApprovalEffectiveText(approval: FeeReductionApprovalListItem) {
  return `${approval.effective_from} 至 ${approval.effective_to || '无截止日'}`
}

function splitCommaSeparated(value: string) {
  return value.split(',').map((item) => item.trim()).filter(Boolean)
}

function resetReductionApprovalDialog() {
  Object.assign(reductionApprovalDraft, {
    scope_type: '',
    applicant_ids: '',
    eligibility_attributes_version: '',
    eligibility_attributes_json: '',
    reduction_ratio: '',
    fee_codes: '',
    fee_year_from: undefined,
    fee_year_to: undefined,
    effective_from: '',
    effective_to: '',
    source_evidence_version_id: '',
    expected_source_content_hash: '',
    confirmed_at: '',
  })
}

function openReductionApprovalDialog() {
  resetReductionApprovalDialog()
  showReductionApprovalDialog.value = true
}

async function fetchReductionApprovals(caseId: string, selectedApprovalId = '') {
  reductionApprovals.value = await getFeeReductionApprovals(caseId)
  selectedReductionApprovalId.value = reductionApprovals.value.some(
    (approval) => approval.approval_id === selectedApprovalId
  ) ? selectedApprovalId : ''
}

async function loadReductionApprovals(caseId: string, selectedApprovalId = '') {
  reductionApprovalLoadError.value = ''
  try {
    await fetchReductionApprovals(caseId, selectedApprovalId)
  } catch {
    reductionApprovals.value = []
    selectedReductionApprovalId.value = ''
    reductionApprovalLoadError.value = '减缴审批依据加载失败，减缴比例已锁定，请稍后重试。'
  }
}

async function handleReductionApprovalRecord() {
  const caseId = String(caseData.value?.id || route.params.id || '').trim()
  const scopeType = reductionApprovalDraft.scope_type
  const reductionRatio = reductionApprovalDraft.reduction_ratio
  const feeCodes = splitCommaSeparated(reductionApprovalDraft.fee_codes)
  if (
    !caseId
    || !scopeType
    || !reductionRatio
    || !reductionApprovalDraft.eligibility_attributes_version.trim()
    || !reductionApprovalDraft.eligibility_attributes_json.trim()
    || !feeCodes.length
    || !reductionApprovalDraft.effective_from.trim()
    || !reductionApprovalDraft.source_evidence_version_id.trim()
    || !reductionApprovalDraft.expected_source_content_hash.trim()
    || !reductionApprovalDraft.confirmed_at.trim()
  ) {
    ElMessage.warning('请完整填写减缴审批证据必填项')
    return
  }

  const payload: FeeReductionApprovalCreatePayload = {
    case_id: caseId,
    scope_type: scopeType,
    applicant_ids: splitCommaSeparated(reductionApprovalDraft.applicant_ids),
    eligibility_attributes_version: reductionApprovalDraft.eligibility_attributes_version.trim(),
    eligibility_attributes_json: reductionApprovalDraft.eligibility_attributes_json.trim(),
    reduction_ratio: reductionRatio,
    fee_codes: feeCodes,
    fee_year_from: reductionApprovalDraft.fee_year_from ?? null,
    fee_year_to: reductionApprovalDraft.fee_year_to ?? null,
    effective_from: reductionApprovalDraft.effective_from.trim(),
    effective_to: reductionApprovalDraft.effective_to.trim() || null,
    source_evidence_version_id: reductionApprovalDraft.source_evidence_version_id.trim(),
    expected_source_content_hash: reductionApprovalDraft.expected_source_content_hash.trim(),
    confirmed_at: reductionApprovalDraft.confirmed_at.trim(),
  }

  recordingReductionApproval.value = true
  try {
    const result = await createFeeReductionApproval(caseId, payload)
    await loadReductionApprovals(caseId, result.approval_id)
    showReductionApprovalDialog.value = false
    ElMessage.success('减缴审批证据已记录')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    recordingReductionApproval.value = false
  }
}

async function fetchCase() {
  const caseNo = String(route.params.caseNo || '').trim()
  const id = String(route.params.id || '').trim()
  if (!caseNo && !id) return

  loading.value = true
  error.value = null

  try {
    caseData.value = caseNo ? await getCaseByCaseNo(caseNo) : await getCase(id)
    if (!caseNo && caseData.value.case_no) {
      await router.replace({ name: 'case_edit_by_no', params: { caseNo: caseData.value.case_no } })
    }
    form.title = caseData.value.title || ''
    form.app_no = caseData.value.app_no || ''
    form.filing_date = caseData.value.filing_date || ''
    form.recv_date = caseData.value.recv_date || ''
    form.issue_date = caseData.value.issue_date || ''
    form.cert_no = caseData.value.cert_no || ''
    form.from_country = caseData.value.from_country || ''
    form.to_country = caseData.value.to_country || ''
    form.doc_address_id = caseData.value.doc_address_id || ''
    form.bill_address_id = caseData.value.bill_address_id || ''
    form.draw_pages = caseData.value.draw_pages ?? undefined
    form.claim_pages = caseData.value.claim_pages ?? undefined
    form.manuscript_words = caseData.value.manuscript_words ?? undefined
    form.discount_rate = caseData.value.discount_rate || ''
    form.no_power = caseData.value.no_power ?? false
    form.no_prio_text = caseData.value.no_prio_text ?? false
    form.require_hk = caseData.value.require_hk ?? false
    form.first_annuity_year = caseData.value.first_annuity_year ?? undefined
    form.applicants = (caseData.value.applicants || []).map((applicant, index) => ({
      seq: index + 1,
      is_first: applicant.is_first ?? index === 0,
      source_client_id: '',
      name_cn: applicant.name_cn || '',
      name_en: applicant.name_en || '',
      address_cn: applicant.address_cn || '',
      address_en: applicant.address_en || '',
      nationality: applicant.nationality || '',
      certificate_type: applicant.certificate_type || '',
      certificate_no: applicant.certificate_no || '',
      official_postcode: applicant.official_postcode || '',
      official_applicant_kind: applicant.official_applicant_kind || '',
    }))
    form.inventors = (caseData.value.inventors || []).map((inventor, index) => ({
      seq: index + 1,
      name_cn: inventor.name_cn || '',
      name_en: inventor.name_en || '',
      nationality: inventor.nationality || '',
      china_id_no: inventor.china_id_no || '',
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
    form.agent_splits = (caseData.value.agent_splits || []).map((split) => ({
      agent_id: split.agent_id || '',
      role: split.role || '',
      share_ratio: split.share_ratio ?? null,
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
    form.fee_reduction = storedCanonicalReductionRatio(caseData.value.fee_reduction)
    form.applicant_kind = caseData.value.applicant_kind || ''
    if ((caseData.value.agent_splits || []).length > 0) {
      expandedSections.value = Array.from(new Set([...expandedSections.value, 'agent_split']))
    }
    if ((caseData.value.inventors || []).length > 0) {
      expandedSections.value = Array.from(new Set([...expandedSections.value, 'inventor']))
    }
    await loadReductionApprovals(caseData.value.id)
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

function addInventor() {
  const nextSeq = (form.inventors?.length || 0) + 1
  form.inventors = [...(form.inventors || []), createEmptyInventor(nextSeq)]
  expandedSections.value = Array.from(new Set([...expandedSections.value, 'inventor']))
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

function removeInventor(index: number) {
  const nextInventors = [...(form.inventors || [])]
  nextInventors.splice(index, 1)
  form.inventors = nextInventors.map((inventor, seq) => ({ ...inventor, seq: seq + 1 }))
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

  if (feeReductionSelectionRequired.value || !['0', '0.7', '0.85'].includes(String(form.fee_reduction || ''))) {
    add('fee_reduction', feeReductionSelectionWarning.value || '请选择费用减免比例。', 'flags')
  }

  if (
    (form.fee_reduction === '0.7' || form.fee_reduction === '0.85')
    && selectedCanonicalReductionRatio.value !== form.fee_reduction
  ) {
    add('fee_reduction', '选择 0.7/0.85 前必须选择同一比例的减缴审批依据。', 'flags')
  }

  const status = compatibilityStatus.value
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

  const filledApplicants = (form.applicants || []).filter(hasApplicantValue)
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

  const filledInventors = (form.inventors || []).filter(hasInventorValue)
  filledInventors.forEach((inventor, index) => {
    if (![inventor.name_cn, inventor.name_en].some((value) => String(value || '').trim())) {
      add('inventors', `发明人 ${index + 1} 至少填写中文名或英文名。`, 'inventor')
    }
    if (isChinaNationality(inventor.nationality) && !String(inventor.china_id_no || '').trim()) {
      add('inventors', `发明人 ${index + 1} 为中国籍时需填写身份证号。`, 'inventor')
    }
  })

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
  const id = String(caseData.value?.id || route.params.id || '').trim()
  if (!id) return

  fieldErrors.value = new Map()
  validationSummary.value = []
  resetAgentSplitErrors()

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
        ?.filter(hasApplicantValue)
        .map((applicant, index) => ({
          ...applicant,
          seq: index + 1,
        })),
      inventors: form.inventors
        ?.filter(hasInventorValue)
        .map((inventor, index) => ({
          ...inventor,
          seq: index + 1,
        })),
      priorities: form.priorities?.filter((priority) =>
        [priority.country_code, priority.prio_no, priority.prio_date].some((value) => String(value || '').trim())
      ),
      bio_deposits: form.bio_deposits?.filter((bioDeposit) =>
        [bioDeposit.deposit_no, bioDeposit.deposit_unit_name, bioDeposit.deposit_date, bioDeposit.name].some((value) => String(value || '').trim())
      ),
      agent_splits: normalizeAgentSplitRows(form.agent_splits),
    }

    const updated = await updateCase(id, payload)
    ElMessage.success('案件更新成功')
    const targetCaseNo = updated.case_no || caseData.value?.case_no
    if (targetCaseNo) {
      router.push({ name: 'case_detail_by_no', params: { caseNo: targetCaseNo } })
      return
    }
    router.push({ name: 'case_detail', params: { id } })
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

function handleCancel() {
  if (caseData.value?.case_no) {
    router.push({ name: 'case_detail_by_no', params: { caseNo: caseData.value.case_no } })
    return
  }
  const id = caseData.value?.id || route.params.id
  router.push({ name: 'case_detail', params: { id } })
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

.official-field-group {
  margin-top: 14px;
  color: var(--text-main);
  font-size: 13px;
  font-weight: 600;
}
</style>
