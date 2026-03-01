<template>
  <div class="case-panel">
    <!-- Applicants -->
    <div class="claims-section">
      <h3 class="panel-heading">申请人</h3>
      <div v-if="applicants.length === 0" class="placeholder-content">
        <p>暂无申请人信息</p>
      </div>
      <el-table v-else :data="applicants" stripe style="width: 100%">
        <el-table-column prop="seq" label="序号" width="70" />
        <el-table-column prop="name_cn" label="中文名" min-width="160" />
        <el-table-column prop="name_en" label="英文名" min-width="160" />
      </el-table>
    </div>

    <!-- Inventors -->
    <div class="claims-section" style="margin-top: 20px;">
      <h3 class="panel-heading">发明人</h3>
      <div v-if="inventors.length === 0" class="placeholder-content">
        <p>暂无发明人信息</p>
      </div>
      <el-table v-else :data="inventors" stripe style="width: 100%">
        <el-table-column prop="seq" label="序号" width="70" />
        <el-table-column prop="name_cn" label="中文名" min-width="160" />
        <el-table-column prop="name_en" label="英文名" min-width="160" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CaseApplicant, CaseInventor } from '../../../api/cases.types'

defineProps<{
  applicants: CaseApplicant[]
  inventors: CaseInventor[]
}>()
</script>
