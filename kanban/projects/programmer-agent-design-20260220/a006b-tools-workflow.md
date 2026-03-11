# Programmer Sub-Agent 工具集成和工作流程設計

**任務 ID:** a006b
**設計者:** Charlie Analyst (Sub-Agent)
**狀態:** completed
**時間戳:** 2026-02-21T00:55:00+08:00
**輸入文件:** a004-git-development-pattern.md
**專案:** Programmer Agent Design

---

## 執行摘要

本文檔基於 Dashboard 專案的 Git 開發模式分析，設計 Programmer Sub-Agent 的完整工具集成和工作流程。設計涵蓋**開發工具**、**測試工具**、**工作流程**、**文檔工具**和**部署工具**五大類別，採用**Sprint 模式開發**、**Conventional Commits 規範**、**漸進式重構策略**和**多層次測試**的核心原則。

**關鍵設計決策：**
- ✅ **IDE 集成：** VSCode + 插件生態系統，統一開發環境
- ✅ **Git 工作流：** Git Flow 分支策略 + Conventional Commits 規範
- ✅ **測試金字塔：** 單元測試 (70%) + 集成測試 (20%) + E2E 測試 (10%)
- ✅ **代碼質量：** Pre-commit hooks + CI/CD 自動檢查
- ✅ **文檔驅動：** JSDoc + Markdown + API 自動生成
- ✅ **容器化部署：** Docker + GitHub Actions 自動化流水線

---

## 1. 開發工具集成

### 1.1 IDE 配置和插件

#### VSCode 為核心 IDE

**為什麼選擇 VSCode：**
- 跨平台支持（macOS, Windows, Linux）
- 豐富的擴展生態系統
- 強大的調試功能
- 集成終端和 Git
- Remote Development 支持

#### VSCode 擴展推薦

**後端開發（Python）：**
```json
{
  "recommendations": [
    "ms-python.python",           // Python IntelliSense
    "ms-python.vscode-pylance",   // Python 語言服務器
    "ms-python.black-formatter",  // Black 格式化
    "ms-python.isort",            // Import 排序
    "charliermarsh.ruff",         // Ruff linter
    "ms-python.mypy-type-checker" // 類型檢查
  ]
}
```

**前端開發（JavaScript/TypeScript）：**
```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",     // ESLint
    "esbenp.prettier-vscode",     // Prettier 格式化
    "bradlc.vscode-tailwindcss",  // Tailwind CSS
    "dsznajder.es7-react-js-snippets", // React 代碼片段
    "formulahendry.auto-rename-tag", // 標籤自動重命名
    "christian-kohler.path-intellisense" // 路徑智能感知
  ]
}
```

**通用開發：**
```json
{
  "recommendations": [
    "eamodio.gitlens",            // Git 增強
    "streetsidesoftware.code-spell-checker", // 拼寫檢查
    "usernamehw.errorlens",       // 內行錯誤顯示
    "gruntfuggly.todo-tree",      // TODO 管理
    "oderwat.indent-rainbow",     // 縮進彩虹
    "wakatime.vscode-wakatime"    // 編碼時間追蹤
  ]
}
```

#### VSCode 工作區配置

**`.vscode/settings.json`：**
```json
{
  // Python 配置
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none", // 使用 Ruff 格式化
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["-v"],

  // JavaScript/TypeScript 配置
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ],
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",

  // 通用編輯器配置
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "editor.rulers": [80, 120],
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,

  // Git 配置
  "git.enableSmartCommit": true,
  "git.autofetch": true,
  "git.postCommitCommand": "none",

  // 終端配置
  "terminal.integrated.defaultProfile.osx": "zsh"
}
```

**`.vscode/tasks.json`：**
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Backend: Run Tests",
      "type": "shell",
      "command": "pytest",
      "options": {
        "cwd": "${workspaceFolder}/backend"
      },
      "group": {
        "kind": "test",
        "isDefault": true
      }
    },
    {
      "label": "Frontend: Run Tests",
      "type": "shell",
      "command": "npm",
      "args": ["test", "--", "--run"],
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "group": "test"
    },
    {
      "label": "Frontend: Dev Server",
      "type": "shell",
      "command": "npm",
      "args": ["run", "dev"],
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "group": "build"
    },
    {
      "label": "Backend: Dev Server",
      "type": "shell",
      "command": "uvicorn",
      "args": ["main:app", "--reload", "--port", "8000"],
      "options": {
        "cwd": "${workspaceFolder}/backend"
      },
      "group": "build"
    }
  ]
}
```

**`.vscode/launch.json`：**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/backend/main.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    },
    {
      "name": "Python: Attach",
      "type": "debugpy",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      }
    },
    {
      "name": "Chrome: Debug Frontend",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/frontend"
    }
  ]
}

### 1.2 終端工具和命令行界面

#### Shell 配置推薦

**Zsh + Oh My Zsh（macOS 默認）：**

**`.zshrc` 配置片段：**
```bash
# 開發環境快捷鍵
alias dcu='docker-compose up'
alias dcd='docker-compose down'
alias dcb='docker-compose build'
alias dps='docker ps'

# 專案導航
alias cddev='cd ~/Development'
alias cddash='cd ~/Development/Dashboard'

# Git 快捷鍵
alias gs='git status'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline --graph --all'

# Python 開發
alias py='python'
alias pytest='pytest -v'
alias venv='python -m venv venv'
alias activate='source venv/bin/activate'

# 前端開發
alias npm='npm'
alias nrb='npm run build'
alias nrt='npm run test'

# 工具快捷鍵
alias lint='ruff check backend/ && eslint frontend/'
alias format='ruff format backend/ && prettier --write frontend/'
alias test-all='make test'
```

#### 命令行工具推薦

**包管理器：**
```bash
# Python (uv - 高速 Python 包管理器)
pip install uv
uv venv
uv pip install -r requirements.txt

# Node.js (pnpm - 快速、省空間)
npm install -g pnpm
pnpm install
pnpm build
```

**開發工具：**
```bash
# 跨平台
brew install tmux        # 終端復用器
brew install fzf         # 模糊查找器
brew install ripgrep     # 快速文本搜索
brew install jq          # JSON 處理

# Git 工具
brew install gh          # GitHub CLI
brew install lazygit     # Git TUI 客戶端
```

**監控和調試：**
```bash
brew install htop        # 進程監控
brew install iotop      # I/O 監控
brew install ncdu       # 磁盤使用分析
```

#### Tmux 配置（可選）

**`.tmux.conf`：**
```bash
# 基本配置
set -g default-terminal "screen-256color"
set -g history-limit 10000
set -g mouse on

# 面板分割快捷鍵
bind | split-window -h
bind - split-window -v

# 切換面板快捷鍵
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# 面板調整大小
bind -r H resize-pane -L 5
bind -r J resize-pane -D 5
bind -r K resize-pane -U 5
bind -r L resize-pane -R 5

# 顏色主題
set -g status-bg black
set -g status-fg white
set -g status-left ' #S '
set -g status-right ' %H:%M %Y-%m-%d '
```

### 1.3 Git 工具和配置

#### Git 全局配置

**`.gitconfig` 推薦配置：**
```git
[core]
  editor = code --wait
  autocrlf = input
  fileMode = false

[user]
  name = Your Name
  email = your.email@example.com

[init]
  defaultBranch = main

[alias]
  st = status
  co = checkout
  br = branch
  ci = commit
  unstage = reset HEAD --
  last = log -1 HEAD
  visual = log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit

[pull]
  rebase = false

[push]
  default = simple

[rebase]
  autoStash = true
```

#### Pre-commit Hooks 配置

**`.pre-commit-config.yaml`：**
```yaml
repos:
  # Python 工具
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements
      - id: check-todos
      - id: check-added-large-files
        args: ['--maxkb=1000']

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]

  # JavaScript/TypeScript 工具
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, css, json, markdown]
        args: [--write, --single-quote]

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \.(js|jsx|ts|tsx)$
        args: [--fix]

  # Commit 訊息檢查
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.2.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, refactor, docs, test, debug]
```

#### Git 分支工作流

**初始化專案：**
```bash
# 創建 main 分支
git init
git checkout -b main

# 添加 .gitignore 和基本文件
git add .
git commit -m "feat: initial commit"

# 推送到遠端
git remote add origin <repository-url>
git push -u origin main
```

**創建功能分支：**
```bash
# 確保 main 是最新的
git checkout main
git pull origin main

# 創建並切換到新功能分支
git checkout -b feature/feature-name

# 開發...
git add .
git commit -m "feat: add new feature"
git push -u origin feature/feature-name
```

**Pull Request 流程：**
```bash
# 創建 PR
gh pr create --title "Add new feature" \
  --body "Closes #123" \
  --base main \
  --head feature/feature-name

# 等待審查和 CI 通過後合併
```

### 1.4 代碼質量工具

#### Ruff（Python Linter 和 Formatter）

**`ruff.toml` 配置：**
```toml
# Ruff 配置文件

# 目標 Python 版本
target-version = "py311"

# 行長度
line-length = 100

# 排除目錄
exclude = [
  ".git",
  ".venv",
  "venv",
  "__pycache__",
  "node_modules",
  ".tox",
  "build",
  "dist"
]

# 選擇的規則
select = [
  "E",   # pycodestyle 錯誤
  "W",   # pycodestyle 警告
  "F",   # Pyflakes
  "I",   # isort
  "N",   # pep8-naming
  "UP",  # pyupgrade
  "B",   # flake8-bugbear
  "C4",  # flake8-comprehensions
  "DTZ", # flake8-datetimez
  "T10", # flake8-debugger
  "T20", # flake8-print
  "SIM", # flake8-simplify
  "TCH", # flake8-type-checking
  "ARG", # flake8-unused-arguments
  "PTH", # flake8-use-pathlib
  "RUF", # Ruff 特定規則
]

# 忽略的規則
ignore = [
  "E501",  # 行長度（由 formatter 處理）
  "B008",  # 函數默認參數中的函數調用
  "T201",  # print 語句
]

# 格式化設置
[format]
indent-style = "space"
quote-style = "double"
line-ending = "auto"

# Lint 設置
[lint]
per-file-ignores = {
  "tests/*" = ["S101"],  # 允許在測試中使用 assert
  "__init__.py" = ["F401"]  # 允許未使用的導入
}
```

**使用 Ruff：**
```bash
# Lint 檢查
ruff check backend/

# 自動修復
ruff check --fix backend/

# 格式化
ruff format backend/

# 同時 lint 和格式化
ruff check --fix backend/ && ruff format backend/
```

#### ESLint（JavaScript Linter）

**`eslint.config.js` 配置：**
```javascript
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  { ignores: ['dist', '.output', 'node_modules'] },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      'no-console': 'off',
      'no-unused-vars': 'warn',
    },
  },
]
```

**使用 ESLint：**
```bash
# Lint 檢查
eslint frontend/src/

# 自動修復
eslint frontend/src/ --fix

# 規則列表
eslint --print-config frontend/src/App.jsx
```

#### Pylint（Python 代碼質量）

**`.pylintrc` 配置：**
```ini
[MESSAGES CONTROL]
disable=
  C0111,  # missing-docstring
  C0103,  # invalid-name
  R0903,  # too-few-public-methods

[FORMAT]
max-line-length=100

[DESIGN]
max-args=7
max-locals=15
max-returns=6
max-branches=12
max-statements=50

[BASIC]
good-names=i,j,k,ex,Run,_
```

#### MyPy（類型檢查）

**`mypy.ini` 配置：**
```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
strict_equality = True

[mypy-tests.*]
disallow_untyped_defs = False
```

---

## 2. 測試工具集成

### 2.1 單元測試工具

#### Pytest（Python）

**`pytest.ini` 配置：**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=line
    --strict-markers
    -n auto
    --timeout=10
    --timeout-method=thread
    -m "not slow"
    -rN
    --cov=.
    --cov-report=html
    --cov-report=term-missing

markers =
    smoke: Quick smoke tests
    fast: Fast unit tests (<1s each)
    slow: marks tests as slow
    integration: marks tests as integration
    unit: marks tests as unit tests
    contract: Contract tests
```

**Pytest 最佳實踐：**

**測試結構：**
```
tests/
├── unit/
│   ├── test_services/
│   │   ├── test_backtest_service.py
│   │   └── test_strategy_service.py
│   └── test_models/
│       ├── test_strategy.py
│       └── test_signal.py
├── integration/
│   ├── test_api/
│   │   └── test_backtest_api.py
│   └── test_database/
│       └── test_data_store.py
├── contract/
│   └── test_backtest_contract.py
└── conftest.py
```

**測試範例：**
```python
# unit/test_services/test_backtest_service.py
import pytest
from unittest.mock import Mock, patch
from services.backtest_service import BacktestService

@pytest.mark.unit
@pytest.mark.fast
class TestBacktestService:
    """BacktestService 單元測試"""

    @pytest.fixture
    def service(self):
        """創建 BacktestService 實例"""
        return BacktestService()

    @pytest.fixture
    def mock_strategy(self):
        """Mock 策略"""
        strategy = Mock()
        strategy.generate_signals.return_value = []
        return strategy

    def test_run_backtest_with_valid_params(self, service, mock_strategy):
        """測試使用有效參數運行回測"""
        # Arrange
        params = {"symbol": "AAPL", "start_date": "2023-01-01"}

        # Act
        result = service.run_backtest(mock_strategy, params)

        # Assert
        assert result is not None
        assert hasattr(result, "equity_curve")

    def test_run_backtest_with_invalid_symbol(self, service):
        """測試使用無效符號運行回測"""
        # Arrange
        params = {"symbol": "INVALID"}

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid symbol"):
            service.run_backtest(Mock(), params)

    @pytest.mark.parametrize("period", [14, 21, 50])
    def test_rsi_strategy_different_periods(self, service, period):
        """測試不同 RSI 週期"""
        # Arrange
        params = {"period": period}

        # Act
        result = service.calculate_rsi(params)

        # Assert
        assert result is not None
        assert 0 <= result <= 100
```

**並行測試執行：**
```bash
# 自動檢測 CPU 核心數並並行運行
pytest -n auto

# 指定並行數量
pytest -n 4

# 只運行快速測試
pytest -m "fast"

# 只運行單元測試
pytest -m "unit"

# 運行所有測試（包括慢速）
pytest -m ""  # 或不使用 -m 選項
```

#### Vitest（JavaScript/React）

**`vitest.config.js` 配置：**
```javascript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom', // 或 'happy-dom'
    setupFiles: ['./src/test/setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.config.js',
        '**/*.config.jsx',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@services': path.resolve(__dirname, './src/services'),
      '@components': path.resolve(__dirname, './src/components'),
    },
  },
})
```

**`src/test/setup.js`：**
```javascript
import { vi } from 'vitest'
import { cleanup } from '@testing-library/react'

// 每個測試後清理
afterEach(() => {
  cleanup()
})

// Mock API calls
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  })
)
```

**Vitest 測試範例：**
```javascript
// src/components/__tests__/BacktestForm.test.jsx
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import BacktestForm from '../BacktestForm'

describe('BacktestForm', () => {
  const mockSubmit = vi.fn()

  beforeEach(() => {
    mockSubmit.mockClear()
  })

  it('renders form with all required fields', () => {
    render(<BacktestForm onSubmit={mockSubmit} />)

    expect(screen.getByLabelText(/Symbol/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Start Date/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/End Date/i)).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    render(<BacktestForm onSubmit={mockSubmit} />)

    const submitButton = screen.getByRole('button', { name: /Submit/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/Symbol is required/i)).toBeInTheDocument()
    })
  })

  it('calls onSubmit with valid data', async () => {
    render(<BacktestForm onSubmit={mockSubmit} />)

    fireEvent.change(screen.getByLabelText(/Symbol/i), {
      target: { value: 'AAPL' },
    })
    fireEvent.change(screen.getByLabelText(/Start Date/i), {
      target: { value: '2023-01-01' },
    })

    fireEvent.click(screen.getByRole('button', { name: /Submit/i }))

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        symbol: 'AAPL',
        startDate: '2023-01-01',
      })
    })
  })
```

**運行 Vitest：**
```bash
# 運行測試
npm run test

# 監視模式
npm run test:watch

# 覆蓋率
npm run test:coverage

# UI 模式
npm run test:ui
```

### 2.2 集成測試工具

#### Pytest 集成測試

**集成測試配置：**
```python
# integration/test_api/test_backtest_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.mark.integration
@pytest.mark.slow
class TestBacktestAPI:
    """回測 API 集成測試"""

    @pytest.fixture
    def client(self):
        """創建測試客戶端"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """認證頭"""
        return {"Authorization": "Bearer test-token"}

    def test_create_backtest_success(self, client, auth_headers):
        """測試成功創建回測"""
        response = client.post(
            "/api/backtest",
            json={
                "symbol": "AAPL",
                "strategy": "rsi",
                "params": {"period": 14}
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "backtest_id" in data
        assert data["status"] == "running"

    def test_create_backtest_invalid_symbol(self, client, auth_headers):
        """測試無效符號"""
        response = client.post(
            "/api/backtest",
            json={
                "symbol": "INVALID",
                "strategy": "rsi"
            },
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "error" in response.json()

    def test_get_backtest_results(self, client, auth_headers):
        """測試獲取回測結果"""
        # 先創建回測
        create_response = client.post(
            "/api/backtest",
            json={
                "symbol": "AAPL",
                "strategy": "rsi"
            },
            headers=auth_headers
        )
        backtest_id = create_response.json()["backtest_id"]

        # 獲取結果
        response = client.get(
            f"/api/backtest/{backtest_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "equity_curve" in data
        assert "metrics" in data
```

#### 測試數據管理

**`conftest.py` 共享 fixtures：**
```python
import pytest
import pandas as pd
from datetime import datetime
from services.data_service import DataService

@pytest.fixture
def sample_ohlcv_data():
    """樣本 OHLCV 數據"""
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    return pd.DataFrame({
        "date": dates,
        "open": [100 + i * 0.1 for i in range(100)],
        "high": [101 + i * 0.1 for i in range(100)],
        "low": [99 + i * 0.1 for i in range(100)],
        "close": [100.5 + i * 0.1 for i in range(100)],
        "volume": [1000000 for _ in range(100)]
    })

@pytest.fixture
def mock_database():
    """Mock 數據庫連接"""
    with patch('services.data_service.Database') as mock_db:
        yield mock_db

@pytest.fixture
def test_user():
    """測試用戶"""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "token": "test-token"
    }
```

### 2.3 E2E 測試工具

#### Cypress 配置

**`cypress.config.js`：**
```javascript
import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:8000',
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
  },
})
```

**Cypress 測試範例：**
```javascript
// cypress/e2e/backtest.cy.js
describe('Backtest Flow', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should create and view backtest results', () => {
    // 導航到回測頁面
    cy.get('[data-testid="nav-backtest"]').click()

    // 填寫表單
    cy.get('[data-testid="input-symbol"]').type('AAPL')
    cy.get('[data-testid="select-strategy"]').select('RSI')
    cy.get('[data-testid="input-period"]').clear().type('14')

    // 提交表單
    cy.get('[data-testid="button-submit"]').click()

    // 等待結果
    cy.get('[data-testid="loading-spinner"]', { timeout: 30000 }).should('not.exist')

    // 驗證結果
    cy.get('[data-testid="backtest-results"]').should('be.visible')
    cy.get('[data-testid="equity-chart"]').should('exist')
    cy.get('[data-testid="metrics-table"]').should('contain', 'Total Return')
  })

  it('should show validation errors for missing fields', () => {
    cy.get('[data-testid="nav-backtest"]').click()

    // 不填寫任何字段直接提交
    cy.get('[data-testid="button-submit"]').click()

    // 驗證錯誤消息
    cy.get('[data-testid="error-symbol"]').should('contain', 'Symbol is required')
  })

  context('Mobile view', () => {
    beforeEach(() => {
      cy.viewport(375, 667)
    })

    it('should display responsive layout', () => {
      cy.get('[data-testid="nav-backtest"]').click()
      cy.get('[data-testid="backtest-form"]').should('be.visible')

      // 驗證移動端特有的佈局
      cy.get('[data-testid="form-grid"]').should('have.css', 'grid-template-columns', '1fr')
    })
  })
})
```

**運行 Cypress：**
```bash
# 打開 Cypress UI
npm run test:e2e:open

# 運行所有測試（無頭模式）
npm run test:e2e

# 運行特定測試文件
npx cypress run --spec "cypress/e2e/backtest.cy.js"

# 不同視口測試
npm run test:e2e:mobile   # 375x667
npm run test:e2e:tablet   # 768x1024
npm run test:e2e:desktop  # 1920x1080
```

### 2.4 測試報告和覆蓋率分析

#### 覆蓋率配置

**Pytest 覆蓋率：**
```ini
# pytest.ini
[pytest]
addopts =
    --cov=.
    --cov-report=html:coverage/html
    --cov-report=term-missing
    --cov-report=xml:coverage.xml
    --cov-report=json:coverage.json
    --cov-fail-under=80
```

**Vitest 覆蓋率：**
```javascript
// vitest.config.js
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      all: true,
      lines: 80,
      functions: 80,
      branches: 75,
      statements: 80,
    },
  },
})
```

#### 覆蓋率目標

| 類型 | 當前覆蓋率 | 目標覆蓋率 | 優先級 |
|------|-----------|-----------|--------|
| 🐍 後端核心邏輯 | 70% | 90% | High |
| 🐍 後端 API | 65% | 85% | High |
| ⚛️ 前端 Utils | 100% | ✅ | Done |
| ⚛️ 前端 Components | 30% | 75% | Medium |
| ⚛️ 前端 Services | 50% | 80% | Medium |

#### 測試報告整合

**HTML 覆蓋率報告：**
```bash
# 生成並打開 HTML 報告
pytest --cov=. --cov-report=html
open coverage/html/index.html

# 或前端
npm run test:coverage
open coverage/index.html
```

**Codecov 整合（CI）：**
```yaml
# .github/workflows/ci.yml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    flags: backend
    fail_ci_if_error: false
```

---

## 3. 工作流程設計

### 3.1 開發任務流程（從需求到部署）

#### 完整開發生命週期

```
┌─────────────────────────────────────────────────────────────┐
│  1. 需求分析與規劃                                         │
│  - 創建 Issue 或任務                                       │
│  - 明確需求和驗收標準                                       │
│  - 預估工作量和時間線                                       │
│  - 識別依賴和風險                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. 技術設計與架構                                           │
│  - 創建設計文檔                                             │
│  - 定義 API 接口                                            │
│  - 設計數據庫模型                                           │
│  - 識別重構需求                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. 環境準備                                                 │
│  - 創建功能分支 (git checkout -b feature/xxx)               │
│  - 安裝依賴                                                 │
│  - 配置本地環境                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. TDD 開發循環                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  4.1 編寫測試（紅）                                   │   │
│  │     - 單元測試                                         │   │
│  │     - 定義預期行為                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  4.2 實現功能（綠）                                   │   │
│  │     - 編寫最小可工作代碼                               │   │
│  │     - 通過測試                                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  4.3 重構（優化）                                     │   │
│  │     - 改進代碼質量                                     │   │
│  │     - 保持測試通過                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  4.4 重複循環                                         │   │
│  │     - 返回 4.1 直到功能完成                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. 集成測試                                                 │
│  - API 集成測試                                             │
│  - 組件集成測試                                             │
│  - 數據庫集成測試                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. 代碼審查準備                                             │
│  - 自我審查                                                 │
│  - 運行完整測試套件                                         │
│  - 檢查代碼覆蓋率                                           │
│  - 編譯前端                                                 │
│  - 更新文檔                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  7. 創建 Pull Request                                       │
│  - 使用 PR 模板                                             │
│  - 清晰描述變更                                             │
│  - 關聯 Issue 和任務標記                                    │
│  - 添加截圖/演示                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  8. CI/CD 自動檢查                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  8.1 Lint 檢查                                        │   │
│  │     - Ruff / ESLint                                   │   │
│  │     - 代碼風格                                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  8.2 單元測試                                          │   │
│  │     - Pytest / Vitest                                  │   │
│  │     - 覆蓋率檢查                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  8.3 構建驗證                                          │   │
│  │     - Frontend build                                   │   │
│  │     - Docker image                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  8.4 E2E 測試（可選）                                  │   │
│  │     - Cypress                                         │   │
│  │     - 關鍵流程驗證                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  9. 代碼審查                                                 │
│  - 審查者審查代碼                                           │
│  - 討論和改進                                               │
│  - 修復審查反饋                                             │
│  - 審查通過                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  10. 合併到主分支                                            │
│  - Squash and Merge                                         │
│  - 創建 release tag                                         │
│  - 自動部署到生產環境                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  11. 部署後驗證                                             │
│  - 健康檢查                                                 │
│  - 功能驗證                                                 │
│  - 監控日誌                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  12. 文檔更新與歸檔                                         │
│  - 更新 README                                             │
│  - 更新 API 文檔                                            │
│  - 更新 CHANGELOG                                           │
│  - 關閉 Issue                                               │
└─────────────────────────────────────────────────────────────┘
```

#### 任務跟踪和進度管理

**使用 Issue + PR 關聯：**

```bash
# 1. 創建 Issue
gh issue create --title "Add momentum indicator" \
  --body "## Description\nAdd momentum indicator to the backtest system." \
  --label "feature","enhancement"

# 2. 從 Issue 創建分支
gh issue create --title "Add momentum indicator" \
  --label "feature" \
  --web
# 或使用: gh issue develop <issue-number>

# 3. 開發並創建 PR
gh pr create --title "feat: add momentum indicator" \
  --body "Closes #123" \
  --base main \
  --head feature/add-momentum-indicator

# 4. 自動關聯 Issue（PR 合併後自動關閉）
```

**Kanban 板管理：**

```
Backlog → In Progress → In Review → Testing → Done
   │          │             │           │      │
   │          │             │           │      └── 已部署
   │          │             │           └────────── E2E 通過
   │          │             └────────────────────── PR 已批准
   │          └──────────────────────────────────── 正在開發
   └────────────────────────────────────────────── 待處理
```

### 3.2 代碼審查流程

#### PR 模板

**`.github/PULL_REQUEST_TEMPLATE.md`：**
```markdown
## Pull Request

### 描述
簡短描述此 PR 的目的和範圍。

### 變更類型
- [ ] 新功能 (feat)
- [ ] Bug 修復 (fix)
- [ ] 性能優化 (performance)
- [ ] 重構 (refactor)
- [ ] 文檔更新 (docs)
- [ ] 測試相關 (test)
- [ ] 調試記錄 (debug)

### 相關 Issue
關聯 Issue: #<issue_number>
任務標記: `ARCH-XXX`, `REF-XXX`, `Q4-#XX`

### 變更摘要
- [ ] 前端變更
- [ ] 後端變更
- [ ] 資料庫變更
- [ ] Docker 配置變更

### 測試檢查清單
- [ ] 前端已編譯 (`cd frontend && npm run build`)
- [ ] 後端測試通過 (`cd backend && pytest -m "not slow"`)
- [ ] 前端測試通過 (`cd frontend && npm test -- --run`)
- [ ] E2E 測試通過（如適用）
- [ ] 測試覆蓋率未下降
- [ ] 代碼 lint 通過（`ruff check backend/`, `npm run lint`）

### 部署檢查清單
- [ ] Docker 鏡像可構建
- [ ] 本地 Docker 測試通過
- [ ] 環境變數已更新（如需要）
- [ ] 數據庫遷移腳本已準備（如適用）

### 截圖 / 演示
（如適用，添加 UI 變更的截圖或 GIF）

### 審查者
@reviewer1 @reviewer2

### 檢查清單
- [ ] 我已經自審過此代碼
- [ ] 我已經在本地測試過變更
- [ ] 代碼遵循項目風格指南
- [ ] 文檔已相應更新
- [ ] 提交訊息遵循 Conventional Commits
```

#### 代碼審查標準

**功能正確性：**
- [ ] 功能符合需求和驗收標準
- [ ] 邊界情況已處理（空值、極限值等）
- [ ] 錯誤處理完善
- [ ] API 接口符合規範

**代碼質量：**
- [ ] 代碼可讀性好，命名清晰
- [ ] 遵循項目風格指南
- [ ] 無重複代碼（DRY 原則）
- [ ] 函數/方法單一職責
- [ ] 適當的註釋和文檔字符串

**測試覆蓋：**
- [ ] 新功能有測試覆蓋
- [ ] 測試通過率 100%
- [ ] 覆蓋率未下降（目標 >80%）
- [ ] 測試用例覆蓋關鍵路徑和邊界情況

**安全性：**
- [ ] 無硬編碼密碼/API keys
- [ ] 適當的權限檢查
- [ ] 輸入驗證完善（SQL 注入、XSS 等）
- [ ] 敏感數據加密存儲

**性能：**
- [ ] 無明顯性能退化
- [ ] 數據庫查詢優化（避免 N+1）
- [ ] 前端渲染優化（避免重複渲染）
- [ ] 適當的緩存策略

**文檔：**
- [ ] README 已更新（如需要）
- [ ] API 文檔已更新
- [ ] 註釋清晰
- [ ] CHANGELOG 已更新

#### 審查者角色和責任

| 角色 | 職責 | 建議人員 |
|------|------|---------|
| **技術審查者** | 代碼質量、架構、最佳實踐 | 資深開發者 |
| **功能審查者** | 功能正確性、需求符合度 | 產品經理/需求方 |
| **測試審查者** | 測試覆蓋、測試質量 | QA 工程師 |
| **安全審查者** | 安全漏洞、權限檢查 | 安全專家（如需要） |

#### 審查反饋模板

**建設性反饋示例：**

```markdown
## 審查反饋

### 🔴 必須修復（Blockers）

1. **安全問題**
   - ❌ 硬編碼的 API key 已提交到代碼庫
   - 建議：使用環境變量或 secrets manager
   - 位置：`backend/config.py:15`

### 🟡 建議修改（Suggestions）

1. **性能優化**
   - ⚠️ 這個查詢可能會有 N+1 問題
   - 建議：使用 `select_related` 或預加載
   - 位置：`backend/services/backtest_service.py:45`

2. **代碼可讀性**
   - 💡 這個函數有點長，可以拆分
   - 建議：提取為更小的單元函數
   - 位置：`backend/services/backtest_service.py:89-120`

### 🟢 很好的地方（Good Points）

1. ✅ 測試覆蓋率很好，達到了 85%
2. ✅ 文檔字符串寫得很清晰
3. ✅ 遵循了項目的命名規範
```

### 3.3 重構和優化流程

#### 重構原則

**重構前的檢查清單：**
- [ ] 是否有現有的測試覆蓋？
- [ ] 是否有回歸測試？
- [ ] 是否理解現有代碼？
- [ ] 是否有重構計劃？
- [ ] 是否評估了影響範圍？

**重構最佳實踐：**

1. **小步驟重構**
   - 每次只做一個小改變
   - 每次改變後都運行測試
   - 如果失敗，立即回滾

2. **向後兼容**
   ```python
   # 舊函數標記為 deprecated
   import warnings

   def deprecated_get_futures_spec(symbol):
       warnings.warn(
           "Use get_spec_for_symbol instead",
           DeprecationWarning,
           stacklevel=2
       )
       return _get_spec_impl(symbol)

   # 新函數
   def get_spec_for_symbol(symbol):
       return _get_spec_impl(symbol)
   ```

3. **測試驅動重構**
   - 先寫測試確保現有行為
   - 再重構
   - 確保測試通過

#### 重構工作流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. 發現重構機會                                             │
│  - Code Review 中的反饋                                     │
│  - 技術債務積累                                             │
│  - 性能瓶頸                                                 │
│  - 代碼異味（Code Smell）                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. 重構規劃                                                 │
│  - 識別重構範圍                                             │
│  - 定義重構目標                                             │
│  - 預估影響和風險                                           │
│  - 創建重構 Issue（REF-XXX）                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. 重構前測試                                               │
│  - 運行完整測試套件                                         │
│  - 記錄測試基線                                             │
│  - 備份代碼（git tag 或 branch）                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. 漸進式重構                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 1: 準備階段                                     │   │
│  │  - 添加接口/抽象層                                     │   │
│  │  - 添加適配器                                           │   │
│  │  - 保持舊代碼工作                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 2: 遷移階段                                     │   │
│  │  - 遷移核心功能到新架構                                 │   │
│  │  - 逐步替換調用點                                       │   │
│  │  - 持續測試                                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 3: 清理階段                                     │   │
│  │  - 移除棄用代碼                                       │   │
│  │  - 更新文檔                                           │   │
│  │  - 最終驗證                                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. 重構後驗證                                               │
│  - 運行完整測試套件                                         │
│  - 性能基準測試                                             │
│  - 回歸測試                                                 │
│  - 代碼審查                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. 文檔更新                                                 │
│  - 更新重構計劃文檔                                         │
│  - 更新架構文檔                                             │
│  - 更新 CHANGELOG                                           │
│  - 關閉重構 Issue                                           │
└─────────────────────────────────────────────────────────────┘
```

#### 重構模式和策略

**模式 1：提取方法（Extract Method）**
```python
# Before
def calculate_metrics(result):
    total_return = (result.equity_curve[-1] - result.equity_curve[0]) / result.equity_curve[0]
    max_drawdown = (result.equity_curve.max() - result.equity_curve.min()) / result.equity_curve.max()
    sharpe_ratio = result.returns.mean() / result.returns.std()
    return total_return, max_drawdown, sharpe_ratio

# After
def calculate_metrics(result):
    return (
        _calculate_total_return(result),
        _calculate_max_drawdown(result),
        _calculate_sharpe_ratio(result)
    )

def _calculate_total_return(result):
    return (result.equity_curve[-1] - result.equity_curve[0]) / result.equity_curve[0]

def _calculate_max_drawdown(result):
    return (result.equity_curve.max() - result.equity_curve.min()) / result.equity_curve.max()

def _calculate_sharpe_ratio(result):
    return result.returns.mean() / result.returns.std()
```

**模式 2：策略模式（Strategy Pattern）**
```python
# Before
class BacktestService:
    def run_backtest(self, strategy_type, params):
        if strategy_type == "rsi":
            return self._run_rsi_backtest(params)
        elif strategy_type == "macd":
            return self._run_macd_backtest(params)
        # ... 更多策略

# After
from abc import ABC, abstractmethod

class IStrategy(ABC):
    @abstractmethod
    def generate_signals(self, context):
        pass

    @abstractmethod
    def get_metadata(self):
        pass

class RSIStrategy(IStrategy):
    def generate_signals(self, context):
        # RSI 邏輯
        pass

    def get_metadata(self):
        return {"name": "RSI", "params": ["period"]}

class BacktestService:
    def run_backtest(self, strategy: IStrategy, params):
        signals = strategy.generate_signals(params)
        # 統一的回測邏輯
        pass
```

### 3.4 測試驅動開發流程

#### TDD 循環

```
Red → Green → Refactor
```

**詳細 TDD 工作流程：**

```
┌─────────────────────────────────────────────────────────────┐
│  1. Red：編寫失敗的測試                                     │
│  - 理解需求                                                 │
│  - 編寫測試定義預期行為                                     │
│  - 運行測試（應該失敗）                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Green：編寫最簡代碼使測試通過                           │
│  - 編寫最小可工作代碼                                       │
│  - 不關注代碼質量                                           │
│  - 運行測試（應該通過）                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Refactor：重構並保持測試通過                             │
│  - 改進代碼質量                                             │
│  - 提取重複代碼                                             │
│  - 改善命名                                                 │
│  - 運行測試（應該仍然通過）                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. 重復循環直到功能完成                                     │
└─────────────────────────────────────────────────────────────┘
```

#### TDD 實戰範例

**場景：添加新的回測策略**

**Step 1: Red - 編寫測試**
```python
# tests/unit/test_strategies/test_bollinger_bands.py
import pytest
from services.strategies import BollingerBandsStrategy

@pytest.mark.unit
def test_bollinger_bands_generate_signals():
    """測試布林帶策略信號生成"""
    # Arrange
    strategy = BollingerBandsStrategy(period=20, std=2)
    ohlcv = pd.DataFrame({
        "close": [10, 11, 12, 13, 14, 15, 14, 13, 12, 11]
    })

    # Act
    signals = strategy.generate_signals(ohlcv)

    # Assert
    assert len(signals) > 0
    assert all(signal.action in ["BUY", "SELL"] for signal in signals)
```

**Step 2: Green - 編寫最小代碼**
```python
# services/strategies/bollinger_bands.py
import pandas as pd
from services.strategies import IStrategy, Signal

class BollingerBandsStrategy(IStrategy):
    def __init__(self, period=20, std=2):
        self.period = period
        self.std = std

    def generate_signals(self, ohlcv: pd.DataFrame) -> list[Signal]:
        """生成布林帶交易信號"""
        # 計算布林帶
        sma = ohlcv["close"].rolling(self.period).mean()
        rolling_std = ohlcv["close"].rolling(self.period).std()
        upper_band = sma + (rolling_std * self.std)
        lower_band = sma - (rolling_std * self.std)

        # 生成信號
        signals = []
        for i in range(len(ohlcv)):
            if ohlcv["close"].iloc[i] < lower_band.iloc[i]:
                signals.append(Signal(action="BUY", date=ohlcv.index[i]))
            elif ohlcv["close"].iloc[i] > upper_band.iloc[i]:
                signals.append(Signal(action="SELL", date=ohlcv.index[i]))

        return signals

    def get_metadata(self):
        return {"name": "Bollinger Bands", "params": ["period", "std"]}
```

**Step 3: Refactor - 重構**
```python
# services/strategies/bollinger_bands.py
import pandas as pd
from services.strategies import IStrategy, Signal

class BollingerBandsStrategy(IStrategy):
    def __init__(self, period=20, std=2):
        self.period = period
        self.std = std

    def generate_signals(self, ohlcv: pd.DataFrame) -> list[Signal]:
        """生成布林帶交易信號"""
        bands = self._calculate_bands(ohlcv)
        return self._generate_signals_from_bands(ohlcv, bands)

    def _calculate_bands(self, ohlcv: pd.DataFrame) -> dict:
        """計算布林帶"""
        sma = ohlcv["close"].rolling(self.period).mean()
        rolling_std = ohlcv["close"].rolling(self.period).std()
        return {
            "sma": sma,
            "upper": sma + (rolling_std * self.std),
            "lower": sma - (rolling_std * self.std)
        }

    def _generate_signals_from_bands(self, ohlcv: pd.DataFrame, bands: dict) -> list[Signal]:
        """根據布林帶生成信號"""
        signals = []
        for i in range(len(ohlcv)):
            close = ohlcv["close"].iloc[i]
            if close < bands["lower"].iloc[i]:
                signals.append(Signal(action="BUY", date=ohlcv.index[i]))
            elif close > bands["upper"].iloc[i]:
                signals.append(Signal(action="SELL", date=ohlcv.index[i]))
        return signals

    def get_metadata(self):
        return {"name": "Bollinger Bands", "params": ["period", "std"]}
```

### 3.5 調試和問題診斷流程

#### 調試工作流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. 重現問題                                                 │
│  - 獲取錯誤訊息和堆棧跟踪                                     │
│  - 理解問題的上下文                                         │
│  - 確定重現步驟                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. 添加日誌和調試輸出                                       │
│  - 在關鍵位置添加日誌                                       │
│  - 使用 logging 模塊（不要用 print）                         │
│  - 設置日誌級別                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. 使用調試器                                               │
│  - VSCode 調試器（斷點、監視）                               │
│  - Python pdb                                              │
│  - Chrome DevTools（前端）                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. 隔離問題                                                 │
│  - 編寫最小重現案例                                         │
│  - 排除外部依賴                                             │
│  - 確定問題範圍                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. 形成假設並驗證                                           │
│  - 基於證據形成假設                                         │
│  - 設計驗證實驗                                             │
│  - 記錄發現                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. 修復問題                                                 │
│  - 實施修復                                                 │
│  - 添加測試防止回歸                                         │
│  - 運行完整測試套件                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  7. 驗證和部署                                               │
│  - 本地驗證                                                 │
│  - Code Review                                              │
│  - 部署到測試環境                                           │
│  - 監控生產環境                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 調試工具配置

**Python Logging 配置：**
```python
# backend/config/logging.py
import logging
import sys
from pathlib import Path

def setup_logging(level=logging.INFO):
    """設置日誌配置"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # 設置根 logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('backend/logs/app.log')
        ]
    )

    # 設置第三方庫日誌級別
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
```

**VSCode 調試配置：**
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/backend/main.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend",
        "LOG_LEVEL": "DEBUG"
      },
      "justMyCode": false
    },
    {
      "name": "Python: Test Current File",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": [
        "${file}",
        "-v"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

#### 常見問題診斷

**問題 1：性能慢**
```python
# 使用 cProfile 分析性能
import cProfile
import pstats
from io import StringIO

def profile_function(func):
    """性能分析裝飾器"""
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()

        # 打印性能報告
        s = StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)
        print(s.getvalue())

        return result
    return wrapper

# 使用
@profile_function
def run_backtest():
    # ... 你的代碼
    pass
```

**問題 2：內存泄漏**
```python
# 使用 tracemalloc
import tracemalloc

tracemalloc.start()

# ... 你的代碼

# 打印內存使用快照
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

---

## 4. 文檔工具集成

### 4.1 JSDoc 註解和生成

#### JSDoc 配置

**`.jsdoc.json`：**
```json
{
  "source": {
    "include": ["frontend/src"],
    "includePattern": ".+\\.js(x)?$",
    "exclude": ["frontend/src/test"]
  },
  "opts": {
    "destination": "./docs/jsdoc/",
    "recurse": true
  },
  "plugins": ["plugins/markdown"]
}
```

#### JSDoc 註解範例

**React 組件文檔：**
```javascript
/**
 * 回測表單組件
 * @component
 * @example
 * return (
 *   <BacktestForm
 *     onSubmit={handleSubmit}
 *     strategies={['RSI', 'MACD', 'Bollinger Bands']}
 *   />
 * )
 */
export function BacktestForm({ onSubmit, strategies = [] }) {
  // ... 組件代碼
}

/**
 * 格式化貨幣數值
 * @param {number} value - 要格式化的數值
 * @param {string} [currency='USD'] - 貨幣代碼
 * @returns {string} 格式化後的貨幣字符串
 * @example
 * formatCurrency(1234.56) // "$1,234.56"
 * formatCurrency(1234.56, 'TWD') // "NT$1,234.56"
 */
export function formatCurrency(value, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency
  }).format(value)
}
```

**服務類文檔：**
```javascript
/**
 * API 客戶端服務
 * @class
 * @classdesc 處理所有 API 請求的統一客戶端
 * @example
 * const api = new APIClient('http://localhost:8000')
 * const result = await api.post('/api/backtest', params)
 */
export class APIClient {
  /**
   * 創建 API 客戶端實例
   * @param {string} baseURL - API 基礎 URL
   * @param {Object} [config] - 配置選項
   * @param {number} [config.timeout=30000] - 請求超時時間（毫秒）
   */
  constructor(baseURL, config = {}) {
    this.baseURL = baseURL
    this.timeout = config.timeout || 30000
  }

  /**
   * 發送 POST 請求
   * @async
   * @param {string} endpoint - API 端點
   * @param {Object} data - 請求數據
   * @returns {Promise<Object>} 響應數據
   * @throws {Error} 當請求失敗時拋出錯誤
   * @example
   * const result = await client.post('/api/backtest', { symbol: 'AAPL' })
   */
  async post(endpoint, data) {
    // ... 實現
  }
}
```

#### 生成 JSDoc

```bash
# 安裝 jsdoc
npm install --save-dev jsdoc

# 生成文檔
npx jsdoc -c .jsdoc.json

# 使用插件支持 Markdown
npm install --save-dev jsdoc-plugin-markdown
```

### 4.2 Markdown 文檔編寫

#### 文檔結構標準

**專案文檔目錄結構：**
```
docs/
├── README.md                    # 專案概述
├── CONTRIBUTING.md             # 貢獻指南
├── DEVELOPMENT.md              # 開發指南
├── ARCHITECTURE.md             # 架構文檔
├── API.md                      # API 文檔
├── DEPLOYMENT.md               # 部署文檔
├── CHANGELOG.md                # 變更日誌
├── guides/                     # 指南文檔
│   ├── getting-started.md
│   ├── testing.md
│   └── debugging.md
└── refactoring/               # 重構計劃
    ├── REF-001-symbol-type-unification.md
    ├── REF-002-strategy-system.md
    └── ...
```

#### Markdown 模板

**README.md 模板：**
```markdown
# [專案名稱]

簡短描述專案的目的和核心功能。

## 快速開始

### 前置條件
- Python 3.11+
- Node.js 24+
- Docker

### 安裝

\`\`\`bash
# 克隆專案
git clone <repository-url>
cd <project-name>

# 後端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 前端
cd frontend
npm install

# 運行
# 後端
cd backend
uvicorn main:app --reload

# 前端
cd frontend
npm run dev
\`\`\`

## 專案結構

\`\`\`
.
├── backend/           # FastAPI 後端
├── frontend/          # React 前端
├── tests/             # 測試套件
├── docs/              # 文檔
└── docker/            # Docker 配置
\`\`\`

## 功能

- ✅ 功能 1
- ✅ 功能 2
- 🚧 功能 3（開發中）

## 技術棧

### 後端
- FastAPI
- Python 3.11
- Pytest

### 前端
- React 19
- Vite
- Vitest

### 部署
- Docker
- GitHub Actions

## 文檔

- [開發指南](./docs/DEVELOPMENT.md)
- [API 文檔](./docs/API.md)
- [部署文檔](./docs/DEPLOYMENT.md)

## 貢獻

請參考 [貢獻指南](./docs/CONTRIBUTING.md)

## 授權

MIT License
```

**DEVELOPMENT.md 模板：**
```markdown
# 開發指南

## 環境設置

### 本地開發

\`\`\`bash
# 啟動開發環境
docker-compose -f docker-compose.dev.yml up

# 或分別啟動
# 後端
cd backend && uvicorn main:app --reload

# 前端
cd frontend && npm run dev
\`\`\`

## 代碼風格

### Python
- 使用 Ruff 進行 linting 和格式化
- 遵循 PEP 8
- 使用類型註解（推薦）

\`\`\`bash
# Lint
ruff check backend/

# Format
ruff format backend/
\`\`\`

### JavaScript/React
- 使用 ESLint 和 Prettier
- 遵循 Airbnb Style Guide（部分）

\`\`\`bash
# Lint
npm run lint

# Format
npm run format
\`\`\`

## 測試

### 運行測試

\`\`\`bash
# 後端測試
cd backend && pytest -v

# 前端測試
cd frontend && npm test

# E2E 測試
npm run test:e2e
\`\`\`

### 測試覆蓋率

\`\`\`bash
# 後端覆蓋率
cd backend && pytest --cov=. --cov-report=html

# 前端覆蓋率
cd frontend && npm run test:coverage
\`\`\`

## 提交規範

遵循 Conventional Commits 規範：

\`\`\`
<type>(<scope>): <description>

[optional body]

[optional footer]
\`\`\`

提交類型：
- \`feat\` - 新功能
- \`fix\` - Bug 修復
- \`refactor\` - 代碼重構
- \`docs\` - 文檔更新
- \`test\` - 測試相關

## Pull Request 流程

1. 創建功能分支
2. 開發並測試
3. 創建 Pull Request
4. 等待 Code Review
5. 修復反饋
6. 合併

## 調試

### 後端調試
- 使用 VSCode 調試器
- 查看日誌：\`backend/logs/app.log\`

### 前端調試
- 使用 Chrome DevTools
- React DevTools 瀏覽器擴展

## 常見問題

### 問題 1：...

解決方案：...

### 問題 2：...

解決方案：...
```

#### Markdown 最佳實踐

1. **使用清晰的標題層級**
   ```markdown
   # H1 - 只在文檔頂部使用一次
   ## H2 - 主要章節
   ### H3 - 子章節
   #### H4 - 詳細說明
   ```

2. **使用代碼塊指定語言**
   ```markdown
   \`\`\`python
   def hello():
       print("Hello, World!")
   \`\`\`

   \`\`\`javascript
   const hello = () => console.log("Hello, World!");
   \`\`\`
   ```

3. **使用表格組織信息**
   ```markdown
   | 工具 | 用途 | 配置文件 |
   |------|------|---------|
   | Ruff | Python linter | `ruff.toml` |
   | ESLint | JavaScript linter | `eslint.config.js` |
   | Pytest | Python 測試 | `pytest.ini` |
   ```

4. **使用警告和注意塊**
   ```markdown
   > **注意**
   > 這是一個重要的提示。

   > **警告**
   > 這是一個警告信息，請小心。
   ```

5. **使用引用標記文檔類型**
   ```markdown
   > [!NOTE]
   > 有用的信息

   > [!TIP]
   > 實用技巧

   > [!WARNING]
   > 重要警告

   > [!IMPORTANT]
   > 重要信息
   ```

### 4.3 API 文檔生成

#### FastAPI 自動文檔

FastAPI 自動生成 OpenAPI 文檔，可通過以下 URL 訪問：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**自定義文檔配置：**
```python
# backend/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Dashboard API",
    description="Backtest system and market data API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Dashboard API",
        version="1.0.0",
        description="""
        ## Dashboard API Documentation

        This API provides endpoints for:
        - Backtesting trading strategies
        - Fetching market data
        - Managing tracked symbols
        - Analyzing performance metrics
        """,
        routes=app.routes,
    )

    # 添加額外的 tags
    openapi_schema["tags"] = [
        {
            "name": "Backtest",
            "description": "Backtesting operations"
        },
        {
            "name": "Market Data",
            "description": "Market data operations"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

#### API 端點文檔範例

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal

router = APIRouter(prefix="/api/backtest", tags=["Backtest"])

class BacktestRequest(BaseModel):
    """回測請求模型"""

    symbol: str
    """股票代碼"""

    strategy: Literal["RSI", "MACD", "Bollinger Bands"]
    """策略名稱"""

    start_date: Optional[str] = None
    """開始日期 (YYYY-MM-DD)"""

    end_date: Optional[str] = None
    """結束日期 (YYYY-MM-DD)"""

    params: Optional[dict] = {}
    """策略參數"""

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "strategy": "RSI",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "params": {"period": 14, "overbought": 70, "oversold": 30}
            }
        }

@router.post("/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    運行回測

    ## 參數

    - **symbol**: 股票代碼（例如：AAPL, GOOGL）
    - **strategy**: 策略名稱（RSI, MACD, Bollinger Bands）
    - **start_date**: 開始日期（可選，默認為 1 年前）
    - **end_date**: 結束日期（可選，默認為今天）
    - **params**: 策略參數（可選）

    ## 返回

    返回回測結果，包括權益曲線和性能指標。

    ## 錯誤

    - **400**: 無效請求參數
    - **404**: 找不到股票代碼
    - **500**: 內部服務器錯誤
    """
    try:
        result = await backtest_service.run_backtest(
            symbol=request.symbol,
            strategy=request.strategy,
            start_date=request.start_date,
            end_date=request.end_date,
            params=request.params
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### 導出 API 文檔

```bash
# 導出 OpenAPI JSON
curl http://localhost:8000/openapi.json -o docs/api/openapi.json

# 導出為 Markdown（使用 openapi2md）
npx openapi2md docs/api/openapi.json -o docs/api/API.md
```

#### 手動 API 文檔模板

**`docs/api/API.md`：**
```markdown
# API Documentation

## Authentication

所有 API 請求需要在 Header 中包含認證 token：

\`\`\`http
Authorization: Bearer <your-token>
\`\`\`

## Endpoints

### Backtest

#### Run Backtest

運行指定的策略回測。

\`\`\`http
POST /api/backtest/run
Content-Type: application/json
Authorization: Bearer <token>

{
  "symbol": "AAPL",
  "strategy": "RSI",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "params": {
    "period": 14,
    "overbought": 70,
    "oversold": 30
  }
}
\`\`\`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Stock symbol |
| strategy | string | Yes | Strategy name (RSI, MACD, Bollinger Bands) |
| start_date | string | No | Start date (YYYY-MM-DD) |
| end_date | string | No | End date (YYYY-MM-DD) |
| params | object | No | Strategy parameters |

**Response (200 OK):**

\`\`\`json
{
  "backtest_id": "bt-123456",
  "status": "completed",
  "equity_curve": [...],
  "metrics": {
    "total_return": 0.25,
    "max_drawdown": -0.15,
    "sharpe_ratio": 1.5
  }
}
\`\`\`

**Error Response (400 Bad Request):**

\`\`\`json
{
  "error": "Invalid symbol",
  "detail": "Symbol 'INVALID' not found"
}
\`\`\`

---

### Market Data

#### Get Symbol Data

獲取指定股票的市場數據。

\`\`\`http
GET /api/market-data/symbol/{symbol}?start_date=2023-01-01&end_date=2023-12-31
Authorization: Bearer <token>
\`\`\`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | path param | Yes | Stock symbol |
| start_date | query param | No | Start date |
| end_date | query param | No | End date |

**Response (200 OK):**

\`\`\`json
{
  "symbol": "AAPL",
  "data": [
    {
      "date": "2023-01-01",
      "open": 100.0,
      "high": 101.0,
      "low": 99.0,
      "close": 100.5,
      "volume": 1000000
    }
  ]
}
\`\`\`
```

---

## 5. 部署工具集成

### 5.1 Docker 容器化

#### 多階段構建

**生產環境 `Dockerfile`：**
```dockerfile
# ============================================
# Stage 1: Frontend Build
# ============================================
FROM node:24-alpine AS frontend-build

WORKDIR /app/frontend

# 複製 package.json 和鎖定文件
COPY frontend/package*.json ./

# 安裝依賴
RUN npm ci --production=false

# 複製源代碼
COPY frontend/ ./

# 構建生產版本
RUN npm run build

# ============================================
# Stage 2: Backend Base
# ============================================
FROM python:3.11-slim AS backend-base

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY backend/requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 3: Final Production Image
# ============================================
FROM backend-base

WORKDIR /app

# 複製後端代碼
COPY backend/ ./backend/

# 複製構建好的前端靜態文件
COPY --from=frontend-build /app/frontend/dist ./backend/static

# 複製配置文件
COPY tracked_symbols.json .

# 創建非 root 用戶
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

WORKDIR /app/backend

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 啟動命令
CMD ["gunicorn", \
     "-w", "1", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "main:app"]
```

#### 開發環境 `Dockerfile.dev`：**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴（包含開發依賴）
COPY backend/requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# 安裝 Node.js 和 npm（用於前端構建）
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y nodejs

WORKDIR /app/backend

# 暴露端口
EXPOSE 8000

# 開發環境啟動命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

#### Docker Compose 配置

**生產環境 `docker-compose.yml`：**
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: dashboard_app
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - dashboard_data:/app/backend/market_data_db
      - app_logs:/app/backend/logs
    environment:
      - ENV=production
      - PYTHONUNBUFFERED=1
      - SKIP_AUTO_IMPORT=true
    networks:
      - dashboard_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  dashboard_data:
  app_logs:

networks:
  dashboard_network:
    driver: bridge
```

**開發環境 `docker-compose.dev.yml`：**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: dashboard_backend_dev
    restart: on-failure
    ports:
      - "8001:8000"
    volumes:
      - ./backend:/app/backend
      - ./tracked_symbols.json:/app/tracked_symbols.json
    environment:
      - ENV=development
      - PYTHONUNBUFFERED=1
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: dashboard_frontend_dev
    restart: on-failure
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    environment:
      - NODE_ENV=development
      - VITE_API_URL=http://backend:8000
    command: npm run dev -- --host 0.0.0.0

volumes:
  node_modules:

networks:
  default:
    name: dashboard_dev_network
```

#### Docker 最佳實踐

**1. 多階段構建減小鏡像大小：**
```dockerfile
# ❌ 壞例子：單一階段
FROM python:3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN npm install  # 不需要 Node.js 運行時！

# ✅ 好例子：多階段
FROM node:24-alpine AS frontend-build
# ... 構建前端

FROM python:3.11-slim
# ... 只複製構建好的靜態文件
COPY --from=frontend-build /app/frontend/dist ./static
```

**2. 使用 .dockerignore 減少構建上下文：**
```
# .dockerignore
.git
.gitignore
__pycache__
*.pyc
*.pyo
*.pyd
venv
.venv
node_modules
.env
.vscode
.idea
*.md
!requirements.txt
!requirements-dev.txt
!README.md
```

**3. 使用非 root 用戶：**
```dockerfile
# 在最終階段創建非 root 用戶
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser
```

**4. 健康檢查：**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### 5.2 GitHub Actions CI/CD

#### CI Workflow

**`.github/workflows/ci.yml`：**
```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install Python lint tools
        run: |
          pip install ruff black isort mypy

      - name: Install Node dependencies
        run: |
          cd frontend && npm ci

      - name: Backend lint
        run: |
          ruff check backend/
          ruff format --check backend/
          mypy backend/

      - name: Frontend lint
        run: |
          cd frontend
          npm run lint
          npm run type-check

  test-backend:
    name: Backend Tests
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt

      - name: Run smoke tests
        run: |
          cd backend
          pytest -m "smoke" -v

      - name: Run fast tests
        run: |
          cd backend
          pytest -m "fast or unit" -v

      - name: Run all tests (main/develop only)
        if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
        run: |
          cd backend
          pytest -v --cov=. --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        if: github.event_name == 'push'
        uses: codecov/codecov-action@v4
        with:
          file: ./backend/coverage.xml
          flags: backend

  test-frontend:
    name: Frontend Tests
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend && npm ci

      - name: Run tests
        run: |
          cd frontend
          npm run test -- --run

      - name: Run coverage (main/develop only)
        if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
        run: |
          cd frontend
          npm run test:coverage

      - name: Upload coverage to Codecov
        if: github.event_name == 'push'
        uses: codecov/codecov-action@v4
        with:
          file: ./frontend/coverage/coverage-final.json
          flags: frontend

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '24'

      - name: Install Node dependencies
        run: |
          cd frontend && npm ci

      - name: Build frontend
        run: |
          cd frontend
          npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: frontend-dist
          path: frontend/dist
```

#### CD Workflow

**`.github/workflows/cd.yml`：**
```yaml
name: CD

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'production'
        type: choice
        options:
          - production
          - staging

jobs:
  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: production
      url: http://172.235.215.225
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub (optional)
        if: env.DOCKER_USERNAME != ''
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build Docker image
        run: |
          docker buildx build \
            --platform linux/amd64 \
            -t dashboard-app:${{ github.sha }} \
            -t dashboard-app:latest \
            --load \
            .

      - name: Export Docker image
        run: |
          docker save dashboard-app:latest | gzip > dashboard-app.tar.gz

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.LINODE_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.LINODE_HOST }} >> ~/.ssh/known_hosts

      - name: Transfer Docker image to production
        run: |
          scp -o StrictHostKeyChecking=no \
            dashboard-app.tar.gz \
            root@${{ secrets.LINODE_HOST }}:/tmp/

      - name: Deploy on production server
        run: |
          ssh -o StrictHostKeyChecking=no root@${{ secrets.LINODE_HOST }} << 'ENDSSH'
            set -e

            echo "[Production] Stopping current container..."
            docker stop dashboard_app 2>/dev/null || true
            docker rm dashboard_app 2>/dev/null || true

            echo "[Production] Loading new Docker image..."
            docker load < /tmp/dashboard-app.tar.gz

            echo "[Production] Starting new container..."
            docker run -d \
              --name dashboard_app \
              --network dashboard_network \
              -v dashboard_data:/app/backend/market_data_db \
              -v app_logs:/app/backend/logs \
              -e ENV=production \
              -e PYTHONUNBUFFERED=1 \
              -e SKIP_AUTO_IMPORT=true \
              --restart unless-stopped \
              --health-cmd 'curl -f http://localhost:8000/health || exit 1' \
              --health-interval 30s \
              --health-timeout 10s \
              --health-retries 3 \
              --health-start-period 40s \
              -p 8000:8000 \
              dashboard-app:latest

            echo "[Production] Waiting for container to be healthy..."
            sleep 15
          ENDSSH

      - name: Health check
        run: |
          sleep 5
          curl -f http://${{ secrets.LINODE_HOST }}/health || exit 1

      - name: Notify deployment success
        if: success()
        run: |
          echo "✅ Deployment successful!"

      - name: Notify deployment failure
        if: failure()
        run: |
          echo "❌ Deployment failed!"
```

#### GitHub Secrets 配置

需要在 GitHub Repository Settings → Secrets and variables → Actions 中配置以下 secrets：

| Secret Name | Description |
|-------------|-------------|
| `LINODE_HOST` | 生產服務器 IP 地址 |
| `LINODE_SSH_KEY` | SSH 私鑰（用於連接生產服務器） |
| `DOCKER_USERNAME` | Docker Hub 用戶名（可選） |
| `DOCKER_PASSWORD` | Docker Hub 密碼（可選） |

### 5.3 部署腳本和自動化

#### 部署腳本

**`scripts/deploy.sh`：**
```bash
#!/bin/bash
set -e

# 配置
ENVIRONMENT="${1:-production}"
CONTAINER_NAME="dashboard_app"
IMAGE_NAME="dashboard-app"
REGISTRY_URL=""  # 如果使用 Docker Hub，填寫 registry URL

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 構建 Docker 鏡像
log_info "Building Docker image for platform linux/amd64..."
docker buildx build \
    --platform linux/amd64 \
    -t ${IMAGE_NAME}:latest \
    -t ${IMAGE_NAME}:$(date +%Y%m%d-%H%M%S) \
    --load \
    .

# 導出並壓縮鏡像
log_info "Exporting Docker image..."
docker save ${IMAGE_NAME}:latest | gzip > ${IMAGE_NAME}.tar.gz
log_info "Image size: $(du -h ${IMAGE_NAME}.tar.gz | cut -f1)"

# 生產環境部署
if [ "$ENVIRONMENT" = "production" ]; then
    PRODUCTION_HOST=${LINODE_HOST:-"root@172.235.215.225"}

    log_info "Transferring image to production server..."
    scp ${IMAGE_NAME}.tar.gz ${PRODUCTION_HOST}:/tmp/

    log_info "Deploying on production server..."
    ssh ${PRODUCTION_HOST} << ENDSSH
        set -e

        echo "[Production] Stopping current container..."
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true

        echo "[Production] Loading new Docker image..."
        docker load < /tmp/${IMAGE_NAME}.tar.gz

        echo "[Production] Starting new container..."
        docker run -d \
          --name ${CONTAINER_NAME} \
          --network dashboard_network \
          -v dashboard_data:/app/backend/market_data_db \
          -v app_logs:/app/backend/logs \
          -e ENV=production \
          -e PYTHONUNBUFFERED=1 \
          -e SKIP_AUTO_IMPORT=true \
          --restart unless-stopped \
          --health-cmd 'curl -f http://localhost:8000/health || exit 1' \
          --health-interval 30s \
          --health-timeout 10s \
          --health-retries 3 \
          --health-start-period 40s \
          -p 8000:8000 \
          ${IMAGE_NAME}:latest

        echo "[Production] Waiting for container to be healthy..."
        sleep 15

        # 清理舊鏡像
        docker image prune -f

        echo "[Production] Deployment completed!"
ENDSSH

    log_info "Waiting for health check..."
    sleep 5
    if curl -f http://${LINODE_HOST}/health; then
        log_info "✅ Health check passed!"
    else
        log_error "❌ Health check failed!"
        exit 1
    fi

else
    log_warn "Local deployment (not to production)"
    log_info "To deploy locally:"
    echo "  docker-compose -f docker-compose.yml up -d"
fi

log_info "Cleaning up..."
rm ${IMAGE_NAME}.tar.gz

log_info "✅ Deployment completed!"
```

**使用腳本：**
```bash
# 添加執行權限
chmod +x scripts/deploy.sh

# 部署到生產環境
./scripts/deploy.sh production

# 本地部署
./scripts/deploy.sh local
```

#### 零停機部署腳本

**`scripts/rolling-deploy.sh`：**
```bash
#!/bin/bash
set -e

ENVIRONMENT="${1:-production}"
OLD_CONTAINER="dashboard_app"
NEW_CONTAINER="dashboard_app_new"
IMAGE_NAME="dashboard-app"

log_info "Starting rolling deployment..."

# 構建新鏡像
log_info "Building new image..."
docker buildx build --platform linux/amd64 -t ${IMAGE_NAME}:new --load .

# 啟動新容器
log_info "Starting new container..."
docker run -d \
  --name ${NEW_CONTAINER} \
  --network dashboard_network \
  -v dashboard_data:/app/backend/market_data_db \
  -v app_logs:/app/backend/logs \
  -e ENV=${ENVIRONMENT} \
  -e PYTHONUNBUFFERED=1 \
  -p 8001:8000 \
  ${IMAGE_NAME}:new

# 健康檢查新容器
log_info "Waiting for new container to be healthy..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8001/health; then
        log_info "✅ New container is healthy!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log_error "New container failed health check!"
    docker stop ${NEW_CONTAINER}
    docker rm ${NEW_CONTAINER}
    exit 1
fi

# 切換流量（更新 nginx 或 reverse proxy）
log_info "Switching traffic to new container..."
# 這裡需要更新你的 reverse proxy 配置
# 例如：更新 nginx 配置並重載

# 停止舊容器
log_info "Stopping old container..."
docker stop ${OLD_CONTAINER}
docker rm ${OLD_CONTAINER}

# 重命名新容器
docker rename ${NEW_CONTAINER} ${OLD_CONTAINER}

# 標記鏡像為 latest
docker tag ${IMAGE_NAME}:new ${IMAGE_NAME}:latest

log_info "✅ Rolling deployment completed!"
```

#### 數據庫遷移腳本

**`scripts/migrate.sh`：**
```bash
#!/bin/bash
set -e

# 數據庫遷移腳本

log_info "Starting database migration..."

# 備份現有數據庫
log_info "Backing up database..."
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).duckdb"
cp backend/market_data_db/data.duckdb backups/${BACKUP_FILE}
log_info "Backup saved to: ${BACKUP_FILE}"

# 運行遷移
log_info "Running migration scripts..."
for migration in migrations/*.sql; do
    if [ -f "$migration" ]; then
        log_info "Running: ${migration}"
        # 使用 DuckDB 執行遷移
        duckdb backend/market_data_db/data.duckdb < "${migration}"
    fi
done

log_info "✅ Database migration completed!"
```

---

## 6. 總結和建議

### 6.1 工具鏈總覽

| 類別 | 工具 | 用途 | 配置文件 |
|------|------|------|---------|
| **IDE** | VSCode | 開發環境 | `.vscode/settings.json` |
| **代碼質量** | Ruff | Python lint/format | `ruff.toml` |
| **代碼質量** | ESLint | JavaScript lint | `eslint.config.js` |
| **測試** | Pytest | Python 測試 | `pytest.ini` |
| **測試** | Vitest | JavaScript 測試 | `vitest.config.js` |
| **測試** | Cypress | E2E 測試 | `cypress.config.js` |
| **文檔** | JSDoc | API 文檔生成 | `.jsdoc.json` |
| **文檔** | FastAPI | 自動 API 文檔 | OpenAPI 配置 |
| **容器化** | Docker | 容器化部署 | `Dockerfile`, `docker-compose.yml` |
| **CI/CD** | GitHub Actions | 自動化流水線 | `.github/workflows/*.yml` |
| **Git Hooks** | pre-commit | Git 鉤子 | `.pre-commit-config.yaml` |

### 6.2 實施優先級

**P0 - 必須立即實施（阻塞性）：**
- [ ] VSCode 工作區配置（`.vscode/`）
- [ ] Pre-commit hooks 配置
- [ ] CI workflow（lint + test）
- [ ] Docker 多階段構建

**P1 - 優先實施（重要增強）：**
- [ ] Ruff 和 ESLint 配置
- [ ] Pytest 和 Vitest 配置
- [ ] PR 模板和 Code Review 標準
- [ ] CD workflow（自動部署）

**P2 - 後續優化（可選增強）：**
- [ ] Cypress E2E 測試
- [ ] JSDoc 文檔生成
- [ ] 零停機部署腳本
- [ ] 數據庫遷移腳本

### 6.3 最佳實踐總結

#### 開發流程
1. 使用 Git Flow 分支策略
2. 遵循 Conventional Commits 提交規範
3. 小步驟提交，頻繁推送
4. 使用 Pull Request 進行代碼審查

#### 代碼質量
1. 使用 pre-commit hooks 自動檢查
2. 遵循項目代碼風格指南
3. 編寫全面的單元測試
4. 保持測試覆蓋率 > 80%

#### 測試策略
1. 測試金字塔：單元測試 (70%) + 集成測試 (20%) + E2E 測試 (10%)
2. TDD 開發循環：Red → Green → Refactor
3. 使用 marker 分類測試（smoke, fast, slow, unit, integration）
4. 並行測試執行提高效率

#### 部署流程
1. 使用 Docker 容器化部署
2. CI/CD 自動化流水線
3. 健康檢查和自動重啟
4. 零停機部署策略

### 6.4 持續改進

**定期審查：**
- 每月審查工具鏈配置
- 每季度評估測試覆蓋率
- 每半年審查 CI/CD 流水線
- 每年評估工具選擇

**指標跟踪：**
- 測試通過率
- 測試覆蓋率
- CI/CD 構建時間
- 部署頻率
- 平均修復時間 (MTTR)

---

**文檔版本：** 1.0
**最後更新：** 2026-02-21
**維護者：** Charlie Analyst
