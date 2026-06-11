# 工作周报系统

按周统计分析工作内容，自动生成周报。支持手动录入、图表可视化和 Markdown 导出。

## 技术栈

- 后端：Python 3 / FastAPI / SQLite
- 前端：Vue 3 / Element Plus / ECharts

## 启动

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173
