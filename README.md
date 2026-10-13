# TBD-production-taste

**把真实交谈剪得清楚、自然，再用克制的综艺包装帮助观众跟上。**

这是从 TBD 播客制作实践中整理的开源制作手册：叙事与视觉规范、分阶段工作流、六个 AI skills、依赖说明，以及可运行的时间线／字幕示例。创作者可以使用自己的素材、人物和品牌，制作接近 TBD 风格的视频播客。

MIT licensed production playbook and six agent skills for conversational video podcasts: authentic dialogue, deliberate camera cuts, speaker-aware captions, restrained variety-show graphics, and evidence-based delivery checks. Chinese documentation; fictional examples only.

## 先看什么

| 你想做什么 | 入口 |
|---|---|
| 理解什么构成 TBD 风格 | [叙事与视觉品味](docs/style-guide.md) |
| 找到必须遵守的正确性要求与可调默认 | [制作规范](docs/production-standard.md) |
| 从素材开始做一整期 | [分阶段工作流](docs/workflow.md) |
| 让 AI 按这套方法协作 | [六个 skills 与调用示例](skills/README.md) |
| 准备软件、转写器与插件 | [依赖与替代方案](docs/dependencies.md) |
| 交片前逐项核验 | [质量检查单](docs/quality-checklist.md) |
| 查看可运行的数据示例 | [时间线与字幕契约](docs/data-contracts.md) |

## 这套方法的核心

- **内容先成立。** 保住问答、前提、否定、思考和真实回应；镜头因内容而切，不按秒数轮换。
- **完整横版先审。** 默认先交带同步对白的完整纯横屏，再进入字幕与竖屏包装；已有明确继续制作授权时按其范围执行。
- **换人就换字幕。** 先判断说话回合，再合句和排版；短应答独立，机器转写与声纹只提供线索。
- **包装跟着真实词时。** 横幅正文配上下黑区，白色主字幕、黄粉青强调；花字不提前泄露、不遮脸、不制造虚假反应。
- **个人切片直接进正片。** 保留完整词界和必要上下文，不加片头。
- **技术通过有边界。** 同步、取帧、封装完整性、逐句听审、创作者确认分别记录。

```mermaid
flowchart LR
  A[素材身份与同步] --> B[完整纯横版]
  B --> C[正文确认或有效继续制作授权]
  C --> D[同源字幕与包装]
  D --> E[最终文件检查与完整听看]
```

## 运行示例

需要 Python 3.11+。仓库脚本只使用标准库，无须 `pip install`，也不会下载模型。

```bash
git clone https://github.com/cyberpinkman/TBD-production-taste.git
cd TBD-production-taste
python3 scripts/tbd.py validate examples/synthetic/project.json
mkdir -p work
python3 scripts/tbd.py export-srt examples/synthetic/project.json work/demo.srt
```

你会得到由同一编辑映射派生的四条虚构字幕；示例含一次删段和一次片头偏移。它验证的是声明的时间线和回合约束，不证明实际音视频正确。输出拒绝覆盖，重复导出请换文件名。

准备自己的单集：

```bash
python3 scripts/tbd.py init work/my-episode
python3 scripts/tbd.py doctor
```

`init` 生成简报、空时间线和检查记录，随后填入你自己的素材信息。`doctor` 只检测 Python、FFmpeg、ffprobe 是否可运行；没有 FFmpeg 时会提示缺失，JSON／SRT 示例仍可运行。实际剪辑、转写与渲染使用你选择的工具，见[依赖说明](docs/dependencies.md)。

## 安装六个 skills

在仓库根目录运行：

```bash
python3 scripts/install_skills.py
```

默认安装到 `$CODEX_HOME/skills`，未设置时使用 `~/.codex/skills`。任何同名技能已存在时，安装器会在复制前停止，不覆盖修改。支持其他技能目录：

```bash
python3 scripts/install_skills.py --dest /path/to/your/skills
```

| Skill | 负责什么 |
|---|---|
| `tbd-production` | 制作统筹、阶段判断、续作与配套技能路由 |
| `tbd-ingest-sync` | 素材身份、相机分段、同步、PTS 与覆盖缺口 |
| `tbd-roughcut` | 叙事取舍、多机位、停顿与局部对白处理 |
| `tbd-captions` | 转写校对、说话回合、词时、字幕唯一源 |
| `tbd-packaging` | 竖屏布局、花字、提示音和无片头切片 |
| `tbd-delivery-qa` | 最终取帧、字幕、音轨完整性和交付报告 |

安装后，在支持 skills 的客户端新会话中调用，例如：

```text
$tbd-production 用我提供的双机位与录音制作一集 TBD 风格播客。
先整理素材和同步，再做完整纯横版；保留真实问答和正常插话。
```

子技能自包含，整体安装后不会依赖原制作项目或本仓库外的私人目录。也可以不安装，直接把规范作为人工剪辑指南。

## 仓库范围与验证

本仓库包含原创文档、skills、模板、虚构 JSON／SRT、安装和结构检查工具；不包含节目原始素材、真实逐字稿、人物资料、品牌图形、模型权重、第三方 skill 实现或完整视频渲染工程。当前版本是制作方法与起步工具，还不是一键成片产品。

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖共同映射、删段与片头偏移、回合归属约束、区间量化、SRT 同源和文件保护。媒体层仍需执行[质量检查单](docs/quality-checklist.md)。来源与检验边界见[提炼依据](docs/provenance.md)。

欢迎通过 Issue 和 Pull Request 补充有证据的改进，先读 [CONTRIBUTING.md](CONTRIBUTING.md)。规范迭代时区分硬约束、设计默认和待验证观感。

## 许可证

原创代码、文档、模板和 skills 使用 [MIT License](LICENSE)。第三方程序、模型、字体、音效和品牌素材保留各自许可，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
