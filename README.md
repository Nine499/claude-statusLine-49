# claude-statusLine-49

Claude Code 三行状态栏：模型与上下文、工作区与 git、请求速度与缓存命中。

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

Claude Code 每次刷新状态栏时，会把会话信息以 JSON 写到 stdin，程序把三行文本写到 stdout。

## 输出

```
model: claude-fable-5-2(high) | window[200K]: 42%
dir: project | git:master | ↑2 ↓1 +3 ~1 ?1 | code:+120/-30
ttft: 1.2s | tpot: 33.3ms | tps: 30 | cache: 50%
```

- 第一行：模型 id、effort 等级、上下文窗口大小与已用百分比。
- 第二行：当前目录名、git 分支与同步/改动计数、本次会话累计增删行数。
- 第三行：最近一次请求的 TTFT、TPOT、TPS，以及 prompt 缓存命中率。

字段缺失或读取失败时输出占位值，程序始终以 0 退出，不阻塞状态栏。

## 模块结构

```
src/claude_statusline/
├── cli.py             # 入口：读 stdin、组装三行、打印
├── values.py          # 容错取值与文本拼接
├── model_line.py      # 第一行：模型与上下文窗口
├── workspace_line.py  # 第二行：目录与代码量
├── git.py             # git status 执行与解析
├── speed_line.py      # 第三行：速度与缓存
├── transcript.py      # transcript 尾部读取与速度估算
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

`legacy/claude_statusLine.py` 是重写前的单文件版本，仅作参考，不参与构建。
