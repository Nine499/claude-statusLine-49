# 项目规则 · claude-statusLine-49

## 项目说明

Claude Code 两行状态栏：读 stdin 的 JSON，向 stdout 输出两行文本。可执行名 `claude-statusLine-49`，运行时零第三方依赖。

Agent 文档见 `AGENTS.md`。

## 代码结构

- `src/claude_statusline/cli.py`：入口，读 stdin、组装两行、打印
- `model_line.py` / `workspace_line.py`：两行渲染
- `git.py`：git status 执行与解析
- `values.py`：容错取值与文本工具
- `tests/`：pytest 用例
- `legacy/`：重写前的单文件版本，仅作参考，不参与构建

## 开发方式

- 依赖与命令只用 uv：`uv sync`、`uv run pytest`、`uv add`
- 检查与格式化只用 ruff：`ruff check src tests`、`ruff format --check src tests`
- 不引入运行时第三方依赖
- 保持 statusline 协议：stdin JSON、stdout 两行、失败静默降级、退出码恒为 0
- 每次改动后运行 pytest、ruff check 与 ruff format --check

## 版本管理

每次改动项目后，按顺序执行：

1. 用 `time-version-49` skill 生成时间版本号，禁止手写或沿用旧号。
2. 把新版本号写入 `pyproject.toml` 的 `[project].version`。
3. 运行 `uv sync`，让 `uv.lock` 跟上新版本。
4. 在下方「更新记录」追加一行：版本号、更新时间（本地时区 `YYYY-MM-DD HH:MM`）、改动内容。
5. 需要让已安装命令生效时，提示用户手动执行 `uv tool install --force .`；Claude 不执行 `uv tool install`（全局禁令）。

## 更新记录

| 版本号 | 更新时间 | 内容 |
| --- | --- | --- |
| 20261117.1415.3279 | 2026-11-17 14:15 | 重写为多文件项目，加入 tests 与 README，改用时间版本号 |
| 20261117.1926.0705 | 2026-11-17 19:26 | 精简为两行：cache 并入第一行，删除第三行及 TTFT/TPOT/TPS、transcript 代码 |
| 20261118.1935.2223 | 2026-11-18 19:35 | 重写 README，新增 AGENTS.md，CLAUDE.md 增加 Agent 文档指引 |
