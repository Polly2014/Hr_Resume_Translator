# 📄 简历解析助手 (Hr Resume Translator)

一键将简历（PDF/Word）转换为标准化 Excel 模板，基于 AI 智能提取信息。

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 功能特点

- 🔍 **智能解析**：支持 PDF 和 Word (.docx) 格式简历
- 🤖 **AI 提取**：使用 DeepSeek 大模型智能提取结构化信息
- 📊 **Excel 输出**：自动填充标准化 Excel 模板
- 🎯 **缺失提醒**：未识别字段黄色高亮 + 红色【待补充】标记
- 🎓 **学历支持**：本科/硕士/博士多学历自动识别
- 🌐 **Web 界面**：精美的 Streamlit Web 界面，拖拽上传

## 📸 界面预览

![Web界面](docs/screenshot.png)

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/Polly2014/Hr_Resume_Translator.git
cd Hr_Resume_Translator

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API

创建 `.env` 文件：

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 3. 运行 Web 界面

```bash
streamlit run app.py
```

打开浏览器访问 http://localhost:8501

## 📁 项目结构

```
Hr_Resume_Translator/
├── app.py                      # Streamlit Web 界面
├── resume_parser.py            # 简历解析核心模块
├── resume_template_generator.py # Excel 模板生成器
├── process_resume.py           # 命令行工具
├── build_exe.py                # 打包脚本
├── launcher.py                 # 应用启动器
├── requirements.txt            # 依赖列表
├── .env                        # API 配置 (需自行创建)
├── Templates/
│   └── template.xlsx           # Excel 模板
├── Resumes/                    # 简历文件目录
└── .github/
    └── workflows/
        └── build.yml           # GitHub Actions 自动打包
```

## 🔧 命令行使用

```bash
# 解析单个简历
python process_resume.py Resumes/example.pdf

# 批量解析目录
python process_resume.py Resumes/

# 指定输出目录
python process_resume.py Resumes/example.pdf -o output/
```

## 📦 打包独立应用

### 本地打包

```bash
python build_exe.py
```

### GitHub Actions 自动打包

推送 tag 到 GitHub 会自动触发打包：

```bash
git tag v1.0.0
git push origin v1.0.0
```

支持平台：
- ✅ Windows (.exe)
- ✅ macOS (.app)

## 📋 提取的信息

| 类别 | 字段 |
|------|------|
| 基本信息 | 姓名、供应商 |
| 个人信息 | 性别、出生年月、联系方式、邮箱、户籍、现居地、婚姻状况 |
| 学历信息 | 学校、专业、学历、入学/毕业时间（支持多段学历） |
| 工作经历 | 公司、职位、时间、工作内容（支持多段经历） |
| 项目经历 | 项目名称、职责、时间、项目描述（支持多段经历） |
| 技术特长 | 技能列表 |

## 🛠️ 技术栈

- **PDF 解析**: PyMuPDF (fitz)
- **Word 解析**: python-docx
- **AI 模型**: DeepSeek (via LiteLLM)
- **Excel 处理**: openpyxl
- **Web 框架**: Streamlit
- **打包工具**: PyInstaller

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

Made with ❤️ for HR
