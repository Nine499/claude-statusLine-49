# claude-statusLine-49

Claude Code 的两行状态栏：第一行显示模型、上下文窗口占用与 prompt 缓存命中，第二行显示当前目录、git 分支/同步/改动状态，以及本次会话的代码增删行数。

## 快速开始

需要 Python 3.11+ 和 [uv](https://docs.astral.sh/uv/)。

**1. 安装命令**（在仓库根目录执行）：

```bash
uv tool install .
```

安装后得到命令 `claude-statusLine-49`。

**2. 接入 Claude Code**：在 `~/.claude/settings.json` 中加入（已有其他配置就合并，不要整个覆盖）：

```json
{
  "statusLine": {
    "type": "command",
    "command": "claude-statusLine-49"
  }
}
```

**3. 新开一个 Claude Code 会话**，状态栏即显示两行文本。

改动代码后需要重新安装才生效：

```bash
uv tool install --force .
```

卸载：

```bash
uv tool uninstall claude-statusline-49
```

## 输出说明

```
model: claude-fable-5-2(high) | window[200K]: 42% | cache: 50%
dir: project | git:master | ↑2 ↓1 +3 ~1 ?1 | code:+120/-30
```

Claude Code 每次刷新状态栏时，把会话信息以 JSON 写到 stdin，程序读完后向 stdout 输出两行。

**第一行**

| 片段 | 含义 | 取值来源 |
| --- | --- | --- |
| `model: <id>(<effort>)` | 模型 id 与 effort 等级 | `model.id`、`effort.level`（缺失时显示 `-`） |
| `window[<size>]: <n>%` | 上下文窗口大小与已用百分比 | `context_window.context_window_size`、`context_window.used_percentage` |
| `cache: <n>%` | prompt 缓存命中率 | `prompt_cache.hit_ratio`，0~1 视为小数、大于 1 视为百分数 |

窗口大小按 1000 进制向下取整显示：`999`、`200K`、`1M`。

**第二行**

| 片段 | 含义 | 取值来源 |
| --- | --- | --- |
| `dir: <name>` | 当前目录名 | `workspace.current_dir` → `cwd` → `workspace.project_dir`，取 basename |
| `git:...` | git 状态，非仓库或超时则不显示 | 在目录下执行 `git status --porcelain=v2 --branch` |
| `code:+<a>/-<r>` | 会话累计增删行数 | `cost.total_lines_added`、`cost.total_lines_removed` |

git 段各标记：

- `git:master`：分支名，超过 32 字符截断为 `…`；detached HEAD 显示 `@<短 oid>`，无法确定时显示 `unknown`。
- `↑2 ↓1`：领先/落后上游的数量；两者都为 0 时显示 `sync`。
- `no-up`：当前分支没有上游；`no-ab`：没有 ahead/behind 信息。
- `!1` 冲突、`+2` 已暂存、`~3` 工作区改动、`-4` 删除、`?5` 未跟踪；全部为 0 时显示 `clean`。

字段缺失、类型不对、stdin 不是合法 JSON 时，用 `unknown(-)`、`0` 等占位值降级；程序始终以 0 退出，不向 stderr 写内容，不会阻塞状态栏。

## 常用命令

| 用途 | 命令 |
| --- | --- |
| 安装 | `uv tool install .` |
| 改代码后重装 | `uv tool install --force .` |
| 卸载 | `uv tool uninstall claude-statusline-49` |
| 手动跑一次（开发用） | `echo '{}' \| uv run python -m claude_statusline` |
| 同步开发依赖 | `uv sync` |
| 跑测试 | `uv run pytest` |
| 静态检查 | `ruff check src tests` |
| 格式检查 | `ruff format --check src tests` |

## 配置

没有环境变量、配置文件或命令行参数。可调行为都写在代码里：

- git 命令超时：`GIT_TIMEOUT_SECONDS = 0.15`（`src/claude_statusline/git.py`），超时后直接省略 git 段。
- 唯一的外部配置是 Claude Code 的 `~/.claude/settings.json` 中的 `statusLine.command`。

## 项目结构

```
src/claude_statusline/
├── cli.py             # 入口：读 stdin、拼两行、打印
├── model_line.py      # 第一行：模型、上下文窗口、缓存命中
├── workspace_line.py  # 第二行：目录、git、代码量
├── git.py             # 执行并解析 git status --porcelain=v2
├── values.py          # 容错取值与文本工具
├── __init__.py
└── __main__.py        # 支持 python -m claude_statusline
tests/                 # pytest 用例，按源码模块一一对应
legacy/                # 重写前的三行单文件版本，仅作参考
```

运行时零第三方依赖；uv.lock 已提交，开发依赖只有 pytest。

## 常见问题

**装完状态栏没出现？**
检查 `~/.claude/settings.json` 的 `statusLine.command` 是否就是 `claude-statusLine-49`，并新开一个会话。改过代码要执行 `uv tool install --force .`，否则跑的还是旧版本。

**第二行没有 git 段？**
当前目录不是 git 仓库、系统里没有 `git`，或 git 在 0.15 秒内没返回，都会静默省略这一段，不影响其他片段。

**一直是 `cache: 0%`？**
stdin 里没有可用的 `prompt_cache.hit_ratio`。该字段既接受 `0.5` 也接受 `50`，两者都显示 `50%`。

**显示 `@xxxxxxx` 而不是分支名？**
处于 detached HEAD，只能显示提交短号。

**显示 `window[0]: 0%`？**
stdin 里缺少 `context_window`，属于正常降级。

## 开发

```bash
uv sync
uv run pytest
ruff check src tests
ruff format --check src tests
```

`legacy/claude_statusLine.py` 是重写前的三行版本（含 TTFT/TPOT/TPS 与 transcript 逻辑），只作历史参考，不参与构建、不被测试引用。

## 链接

- Agent 文档：[AGENTS.md](AGENTS.md)
- 项目开发规则：[CLAUDE.md](CLAUDE.md)
