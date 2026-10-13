# 依赖、插件与替代工作流

文档核对日：**2026-10-13**。这份清单区分当前环境检测、历史制作记录和上游文档检查；它不是跨平台安装成功报告。

本仓库提供制作规范、工作流 skills、模板，以及只使用 Python 标准库的 `scripts/tbd.py`（`doctor`、`init`、`validate`、`export-srt`）。它能初始化工作区、验证声明的映射／字幕结构并导出 SRT，没有包含转写模型、多机位自动剪辑器或完整剪片／渲染工程。结构通过也不证明声明与真实媒体一致。安装下面所有软件不会获得“一键成片”。

## 从最小环境开始

| 层级 | 需要什么 | 用途与验证 |
| --- | --- | --- |
| 阅读规范、人工执行工作流 | Markdown 阅读器、你熟悉的剪辑软件 | 无须 Codex 或 Python |
| 运行本仓库工具 | Python 3.11+，无第三方 Python 包 | `python3 scripts/tbd.py --help`；实际命令见根目录 README |
| 按规范做媒体检测、转换与技术验收 | `ffmpeg` 与 `ffprobe` CLI | `ffmpeg -version`、`ffprobe -version`；两者需在 `PATH` 中 |
| 自动化分析、ASR 或动态图形 | 按下面各能力单独选择 | 使用独立环境，并保存成功运行时的依赖与模型版本 |

Python 从 [Python 官方下载页](https://www.python.org/downloads/)安装。FFmpeg 从 [FFmpeg 官方下载入口](https://ffmpeg.org/download.html)选择对应平台的构建；官方直接发布源码，下载页列出的预编译包由相应提供方维护。macOS 的一种安装方式为 `brew install ffmpeg`，MLX Whisper 的[官方说明](https://github.com/ml-explore/mlx-examples/tree/main/whisper#setup)也采用此方式。

仅创建目录、填写模板、验证清单时，不需要安装下面的分析或渲染包。`doctor` 成功只表示其检查的环境项通过，不代表转写、渲染、字幕校对或成片验收已经完成。

## 可选分析依赖

以下安装命令是供读者在自己的独立虚拟环境中执行的入口。本次开源整理没有重新安装这些包或下载模型，也没有提交生产环境的 `requirements.txt`。命令没有锁定版本；实际使用后应在自己的工程中记录版本并做短样本验证。

| 能力 | 包与官方安装入口 | 原制作项目中的证据 | 不使用它时 |
| --- | --- | --- | --- |
| 波形、声道、偏移、误差统计 | `python -m pip install numpy`；[NumPy 安装文档](https://numpy.org/install/) | 多个同步、声音诊断、渲染验收脚本直接使用 | 用剪辑软件波形和 FFmpeg 分析，手工记录偏移与证据 |
| 相关性与信号分析 | `python -m pip install scipy`；[SciPy 安装文档](https://scipy.org/install/) | 分段同步与源时钟复核脚本使用 | NumPy 或剪辑软件的波形定位；仍需检查首中尾漂移 |
| 联系表、字幕版式、透明图层 | `python -m pip install Pillow`；[Pillow 安装文档](https://pillow.readthedocs.io/en/stable/installation/basic-installation.html) | 抽帧联系表、花字、字幕图层及检验脚本使用 | FFmpeg 抽帧与剪辑软件文字／图形工具 |
| 自定义图像分析 | `python -m pip install opencv-python-headless`；[OpenCV Python 安装说明](https://pypi.org/project/opencv-python/) | 本次查阅的制作脚本未发现 OpenCV 导入；只是扩展选项 | FFmpeg + Pillow；没有图像算法需求就不安装 |

NumPy、SciPy、Pillow 和 OpenCV 的可用 wheel 与 Python／操作系统／CPU 架构有关；本次未验证 Windows 或 Linux 安装。OpenCV 的各个 Python 包共享 `cv2`，按[官方说明](https://pypi.org/project/opencv-python/)只选择一个合适变体，避免同时安装 GUI、headless、contrib 等互相冲突的包。

## 转写：选择一个引擎，再校对

### MLX Whisper

历史制作使用 `mlx-whisper`，以本地 Whisper large-v3-turbo 转写，并用 large-v3 做重点交叉检查。引擎和模型只提供机器稿，字幕定稿仍需听审与语义校对。

- 安装：`python -m pip install mlx-whisper`，见 [MLX Whisper 官方说明](https://github.com/ml-explore/mlx-examples/tree/main/whisper)。
- 平台：这里描述的是历史使用的 **Apple silicon + macOS + Metal** 路径；[MLX 安装文档](https://ml-explore.github.io/mlx/build/html/install.html)列出该平台和原生 Python 的要求。不要把它当作本仓库已经验证的 Windows／Linux 方案。
- 模型：可从 [MLX Whisper 模型集合](https://huggingface.co/collections/mlx-community/whisper-663256f9964fbb1177db93dc)选择。传入 Hub 名称可能自动下载；传入本地完整模型目录可复用本地模型。下载会占用网络、磁盘和内存，应记录模型仓库、revision、文件摘要与参数。
- 凭据与费用：本地推理路径无需 OpenAI API key；不代表零硬件成本。若改用托管推理、私有模型或受限模型，应另查服务凭据、条款和费用。

### faster-whisper

历史制作使用 `faster-whisper` 的本地 CPU / INT8 路径做机器转写。它是无 Apple silicon 环境时可评估的替代引擎，并非本仓库自动选择的后端。

- 安装：`python -m pip install faster-whisper`，见 [faster-whisper 官方仓库](https://github.com/SYSTRAN/faster-whisper)。
- 平台：CPU 路径与 NVIDIA CUDA 路径的依赖不同；GPU 需按上游核对 CTranslate2、CUDA 与 cuDNN 的匹配。Apple Metal 路径不能直接套用 `device="cuda"`。
- 媒体：上游通过 PyAV 解码，包本身不要求系统 FFmpeg CLI；本仓库制作规范中的检测、转换和验收步骤仍会使用 CLI。
- 模型：按模型名初始化通常会从 Hugging Face 下载；也支持完整本地模型目录。模型缓存不应加入本仓库。
- 凭据与费用：本地推理不需要 OpenAI API key；云 GPU、托管 API 或受限 Hub 内容另计。

完全不用 ASR 时，可以人工转写或导入自己有权使用的 SRT／VTT。记录其来源、版本和时间基准，不把导入成功当作内容正确。

## 说话人辅助：可选，不替代回合审校

历史制作曾使用 **sherpa-onnx + 3D-Speaker CAM++ 中文 16 kHz ONNX 模型**，通过长回合锚点与局部声学窗口帮助定位换人。未使用声道编号推断人物，也未把余弦相似度当作身份正确率。

CPU 包的上游入口为 `python -m pip install sherpa-onnx sherpa-onnx-bin`，见 [sherpa-onnx 安装文档](https://k2-fsa.github.io/sherpa/onnx/python/install.html)；调用方式见[官方说话人识别示例](https://github.com/k2-fsa/sherpa-onnx/blob/master/python-api-examples/speaker-identification.py)，模型背景见 [3D-Speaker](https://github.com/modelscope/3D-Speaker)。软件包与模型文件分别获取，模型来源与许可证分别记录。

本次没有重新下载模型或运行识别。短应答、笑声、重叠说话和混合录音尤其需要人工视听复核；没有该工具时，用明确长回合锚点、嘴型和原声审校，无法确定就保留未知。不会因此缺少制作 TBD 风格所必需的能力。

## Remotion 与包装引擎

Remotion 是可选的 React 视频合成方案。历史工程用过 Remotion **4.0.530**，对应 `remotion`、`@remotion/cli`、`@remotion/captions`、`@remotion/media` 等同版本包，另有 React **19.2.3**、TypeScript **5.9.3** 和 Tailwind CSS **4.0.0**。这些是读到的工程声明与制作记录，不能当成当前机器重新渲染成功或新建项目的推荐锁文件。

本仓库不复制那份单集工程。要新建自己的工程，按 [Remotion 官方快速开始](https://www.remotion.dev/docs/)运行 `npx create-video@latest`，由向导创建，再在自己的工程中锁定依赖。使用 Node.js、包管理器和 Remotion 所需的浏览器／渲染运行时；本仓库没有提供这些二进制。安装及首次渲染可能下载依赖与浏览器。

Remotion 的 [Agent Skills](https://www.remotion.dev/docs/ai/skills)可通过 `npx skills add remotion-dev/skills` 单独获取；skill 负责指导，不等于安装了 `remotion` 包或生成了可渲染 composition。

Remotion 使用自己的 [Remotion License](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)，部分使用主体需要 Company License。请按所选版本与主体条件核对；本仓库的 MIT 不覆盖它。云渲染费用另计。不用 Remotion 时，可用 FFmpeg + 透明 PNG 时间线，或自己的剪辑软件完成字幕与包装，保留同一份字幕源、时间映射和验收记录。

## Codex plugins、skills、MCP 分别是什么

Skill 是工作流说明；plugin 可打包 skills、连接器或服务；MCP 是工具调用接口。它们不保证底层程序、模型、账号或素材已经就绪。本仓库的 `skills/` 是新整理的公开流程，不包含本机已安装的第三方 skills 源码。`scripts/install_skills.py` 只负责安装本仓库 skills，也只需 Python 标准库；使用方法见根目录 README。Codex 的通用格式可查[官方 skills 文档](https://developers.openai.com/codex/skills/)。

| 组件 | 角色与本次能确认的状态 | 安装、凭据与替代方式 |
| --- | --- | --- |
| 本仓库 `skills/` | 把素材登记、同步、粗剪、字幕、包装、验收整理成可执行的审查流程 | 可直接阅读，也可按 README 在支持 skills 的客户端中使用；本身不发起云服务请求 |
| Remotion plugin／上游 skills | 提供创建、预览、字幕、渲染的指导；原项目确实用过 Remotion 工程。本次读到本机插件说明版本 4.0.534，这与历史渲染库 4.0.530 不同 | 插件可用性依客户端；上游公开 skills 安装入口见上一节。没有插件时直接用 Remotion CLI 或其他合成工具 |
| `transcribe-media` 本地 skill | 原流程曾调用；其中一条跨进程文件描述符传递路径失败，后续通过本地 PCM + MLX 原始转写路径完成。不能将前一条调用标成成功 | 本次未确认它有可供社区安装的公开发行源，也未重新验证失败路径。无需为本仓库安装；按上面的 ASR 官方入口得到带时间戳机器稿，再做来源登记与校对 |
| `video-learning` 本地 skill / MCP | 已安装能力用于参考视频采集、转写、拉片等；未找到本项目依赖它完成制作的证据 | 本次未确认公开安装入口、服务端部署或费用，不列为必需依赖。若已有该服务，先查它的状态、外传范围与凭据要求；没有时对有权使用的本地参考视频人工拉片 |
| Codex 或其他 AI 客户端 | 协助读规范、编排命令与审查证据；不构成本仓库运行依赖 | 客户端账号、套餐、模型调用与连接器服务可能单独收费。纯 CLI 或人工工作流同样可执行这些规范 |

插件存在、MCP 返回“已配置”、环境变量非空，都不证明登录或一次真实服务调用成功。不要将账号配置、API key、Cookie、服务端 `.env` 或模型缓存提交到制作仓库。

## 本次核对的证据等级

| 对象 | 版本／状态 | 此结论具体意味着什么 |
| --- | --- | --- |
| shell Python | 3.14.6 | 本次执行 `python3 --version` 得到；不是所有可选包的共同环境 |
| 另一现有 Python 环境 | Python 3.12.14；NumPy 2.3.5；Pillow 12.3.0 | 本次读取解释器版本与已安装包 metadata；未由此声称分析或渲染通过 |
| FFmpeg / ffprobe | 8.1 | 本次分别执行 `-version`；历史项目存在全轨解码、同步与验收记录；本次未重渲染单集 |
| Node.js / npm | 25.9.0 / 11.12.1 | 本次执行版本命令；未重新安装 Remotion 工程 |
| MLX / mlx-whisper | 0.32.3 / 0.4.3；当时 NumPy 2.5.3 | 历史转写产物的运行身份记录，并有机器转写产物；未在本次重新推理 |
| faster-whisper / CTranslate2 / PyAV | 1.2.1 / 4.8.1 / 18.1.0；当时 NumPy 2.5.2 | 历史转写产物的版本记录；未在本次重新推理 |
| sherpa-onnx | 1.13.8 | 历史声学分析产物记录；未在本次重新识别 |
| Remotion | 工程声明 4.0.530；本机插件说明 4.0.534 | 分别是运行库与指导文档，不是同一版本指标 |
| SciPy | 制作脚本有使用证据；本次未恢复版本 | 不猜测历史版本；新运行应自己记录 |
| OpenCV、上述新安装命令、跨平台方案 | 文档检查／扩展选项 | 本次没有完成从零安装或端到端制作验证 |

社区复现时请记录自己的 OS、CPU／GPU、Python、FFmpeg 构建选项、包版本、模型 revision 与校验值，以及实际输入、命令、产物和检查结果。先验证短样本，再投入长片；保留机器结果与人工通过的区别。

许可证范围与字体、音效、模型、素材处理见 [第三方声明](../THIRD_PARTY_NOTICES.md)。
