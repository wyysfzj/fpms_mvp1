<template>
  <section class="masterdata-home">
    <header class="hero">
      <p class="eyebrow">设置 / 主数据</p>
      <h1>主数据入口（预留）</h1>
      <p class="summary">
        这里将作为申请人、国家等主数据对象的稳定入口。当前仅提供路由骨架，不包含对象级 CRUD 页面。
      </p>
    </header>

    <div class="grid">
      <article class="card">
        <h2>申请人</h2>
        <p>后续将承载申请人主数据的列表、编辑与启停用能力。</p>
        <router-link to="/settings/masterdata/applicants">进入申请人入口</router-link>
      </article>

      <article class="card">
        <h2>国家</h2>
        <p>后续将承载国家主数据的列表、编辑与启停用能力。</p>
        <router-link to="/settings/masterdata/countries">进入国家入口</router-link>
      </article>

      <article class="card">
        <h2>部门</h2>
        <p>维护系统中的部门主数据，用于人员、权限和业务归属。</p>
        <router-link to="/settings/masterdata/departments">进入部门入口</router-link>
      </article>
    </div>

    <p class="note">当前任务仅建立入口骨架，具体数据管理能力将在后续任务补齐。</p>
  </section>
</template>

<style scoped>
.masterdata-home {
  display: grid;
  gap: 20px;
  padding: 24px;
}

.hero {
  display: grid;
  gap: 8px;
  max-width: 840px;
}

.eyebrow {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

h1 {
  margin: 0;
  font-size: 28px;
}

.summary,
.note,
.card p {
  margin: 0;
  color: #4b5563;
  line-height: 1.7;
}

.grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.card {
  display: grid;
  gap: 12px;
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

.card h2 {
  margin: 0;
  font-size: 18px;
}

.card a {
  width: fit-content;
  color: #2563eb;
  text-decoration: none;
}

.card a:hover {
  text-decoration: underline;
}

.note {
  padding-top: 4px;
  font-size: 14px;
}
</style>
