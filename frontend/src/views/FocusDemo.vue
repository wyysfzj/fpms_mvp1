<template>
  <div class="focus-demo">
    <h1 class="demo-title">专注模式示例</h1>
    <p class="demo-subtitle">
      本页用于演示双模式布局系统。
      可点击右上角按钮切换专注模式。
    </p>

    <div class="demo-grid">
      <!-- Main Content Panel -->
      <div class="demo-panel demo-main">
        <h2 class="demo-heading">文档内容</h2>
        <div class="demo-content">
          <p class="demo-paragraph">
            这是用于展示专注模式阅读体验的示例文档。
            开启专注模式后，侧边栏与页头会收起，正文区域会扩展到更舒适的阅读宽度，
            字体也会切换为更适合长文本阅读的衬线样式。
          </p>
          <p class="demo-paragraph">
            布局会根据当前模式自动调整。工作模式下，你会看到双栏布局，右侧用于元信息或工具；
            专注模式下，界面简化为单栏的纸面式阅读体验，以减少干扰。
          </p>
          <p class="demo-paragraph">
            权利要求书：一种基于激光雷达点云数据的车辆自动驾驶避障方法，其特征在于，
            包括以下步骤：步骤S1：获取激光雷达采集的原始点云数据，并对所述原始点云数据
            进行预处理，得到目标点云数据；步骤S2：利用基于体素网格的聚类算法对所述目标
            点云数据进行障碍物检测，获取障碍物的三维边界框信息。
          </p>
          <p class="demo-paragraph">
            根据权利要求1所述的方法，其特征在于，所述步骤S1具体包括：利用直通滤波算法
            去除所述原始点云数据中的背景噪声，并通过统计离群值移除算法去除离群点。
          </p>
          <p class="demo-paragraph">
            本段刻意写得更长，用于展示专注模式下阅读体验的提升。更宽的页边距、更大的字号以及
            衬线字体能降低视觉疲劳，提升对技术或法律长文的理解效率。
          </p>
        </div>
      </div>

      <!-- Side Panel (hidden in immersive mode) -->
      <div class="demo-panel demo-side">
        <h3 class="demo-side-title">元信息</h3>
        <div class="demo-side-item">
          <span class="demo-side-label">案件编号：</span>
          <span class="demo-side-value">P2310-008</span>
        </div>
        <div class="demo-side-item">
          <span class="demo-side-label">状态：</span>
          <span class="demo-side-value">审查中</span>
        </div>
        <div class="demo-side-item">
          <span class="demo-side-label">截止日期：</span>
          <span class="demo-side-value">2024-03-15</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 专注模式示例页面
</script>
