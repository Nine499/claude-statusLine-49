# claude-statusLine-49

Claude Code 两行状态栏：模型与上下文窗口（含缓存命中）、工作区与 git。

## 安装

在项目目录执行：

```bash
uv tool install .
```

安装后得到命令 `claude-statusLine-49`。修改代码后重新安装：

```bash
uv tool install --force .
```

卸载：

```bash
uv tool uninstall claude-statusline-49
```

## 接入 Claude Code

编辑 `~/.claude/settings.json`：

```json
{
  "statusLine": {
    "type": "command",
    "command": "claude-statusLine-49"
  }
}
```

Claude Code 每次刷新状态栏时，会把会话信息以 JSON 写到 stdin，程序把两行文本写到 stdout。

## 输出

```
model: claude-fable-5-2(high) | window[200K]: 42% | cache: 50%
dir: project | git:master | ↑2 ↓1 +3 ~1 ?1 | code:+120/-30
```

- 第一行：模型 id、effort 等级、上下文窗口大小与已用百分比、prompt 缓存命中率。
- 第二行：当前目录名、git 分支与同步/改动计数、本次会话累计增删行数。

字段缺失或读取失败时输出占位值，程序始终以 0 退出，不阻塞状态栏。

## 模块结构

```
src/claude_statusline/
├── cli.py             # 入口：读 stdin、组装两行、打印
├── values.py          # 容错取值与文本拼接
├── model_line.py      # 第一行：模型、上下文窗口与缓存命中
├── workspace_line.py  # 第二行：目录与代码量
├── git.py             # git status 执行与解析
├── __init__.py
└── __main__.py        # python -m claude_statusline
```

## 开发

```bash
uv sync
uv run pytest
ruff check src tests
ruff format --check src tests
```

`legacy/claude_statusLine.py` 是重写前的三行单文件版本，仅作历史参考，不参与构建。
