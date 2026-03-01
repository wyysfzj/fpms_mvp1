// 视图切换逻辑
        function switchView(viewId) {
            // 1. 隐藏所有视图
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

            // 2. 显示目标视图
            document.getElementById('view-' + viewId).classList.add('active');

            // 3. 更新 Header 状态
            const titleMap = {
                'dashboard': '工作台',
                'list-cases': '案件管理',
                'list-tasks': '任务管理',
                'detail-case': '案件详情 / P2310-008'
            };
            document.getElementById('page-title').innerText = titleMap[viewId] || '工作台';

            // 4. 控制“沉浸模式”按钮的显示 (仅详情页显示)
            const immersiveBtn = document.getElementById('immersive-toggle');
            if (viewId === 'detail-case') {
                immersiveBtn.style.display = 'block';
            } else {
                immersiveBtn.style.display = 'none';
                // 离开详情页自动退出沉浸模式
                document.body.classList.remove('mode-immersive');
                immersiveBtn.innerText = "进入沉浸模式";
            }
        }

        // 抽屉控制
        function openDrawer() {
            document.getElementById('drawer').classList.add('open');
        }
        function closeDrawer() {
            document.getElementById('drawer').classList.remove('open');
        }

        // 沉浸模式切换
        function toggleImmersive() {
            const body = document.body;
            const btn = document.getElementById('immersive-toggle');
            
            body.classList.toggle('mode-immersive');
            
            if (body.classList.contains('mode-immersive')) {
                btn.innerText = "退出沉浸模式";
            } else {
                btn.innerText = "进入沉浸模式";
            }
        }
