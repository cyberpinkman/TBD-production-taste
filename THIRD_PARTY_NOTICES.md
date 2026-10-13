# 第三方软件与素材声明

核对日：**2026-10-13**。

本仓库的 [MIT License](LICENSE)只适用于本仓库有权授权的原创代码、文档、模板和 skills。文档中提到、运行时另行安装、或被用于制作媒体的第三方软件、模型、字体和素材，继续适用其各自许可证与使用条款。提及产品名称不表示其作者参与或认可本项目。

本次发行不附带第三方程序源码／二进制、模型权重、字体、音乐、音效、视频素材或本机已安装的第三方 skill 实现。下面是可选工具链的来源索引，并非随仓库分发组件的完整 SBOM，也不会把整个工具链重新授权为 MIT。

## 软件来源与许可证

| 软件／组件 | 上游许可证或条款入口 | 范围提示 |
| --- | --- | --- |
| Python | [PSF License 与所含组件声明](https://docs.python.org/3/license.html) | Python 及其所含组件保留各自声明 |
| FFmpeg / ffprobe | [FFmpeg 法律与许可证页](https://ffmpeg.org/legal.html) | FFmpeg 基础为 LGPL-2.1-or-later；启用某些组件会使构建适用 GPL，具体看构建配置与分发方。本次本机构建启用了 GPL 和 version3，不能描述为纯 LGPL 构建 |
| NumPy | [BSD-3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt) | wheel 中的额外组件可能另有声明 |
| SciPy | [BSD-3-Clause](https://github.com/scipy/scipy/blob/main/LICENSE.txt) | 额外组件与构建依赖另查对应分发包 |
| Pillow | [MIT-CMU](https://github.com/python-pillow/Pillow/blob/main/LICENSE) | Pillow 的许可证名称与本仓库 MIT 不完全相同 |
| OpenCV / opencv-python | [OpenCV 许可证](https://opencv.org/license/)、[Python 包许可及第三方组件](https://pypi.org/project/opencv-python/#licensing) | OpenCV 4.5.0 起为 Apache-2.0；Python 包装脚本为 MIT；wheel 可含 FFmpeg 等第三方二进制，不能只看包装脚本许可证 |
| MLX / MLX Examples（含 MLX Whisper） | [MLX MIT](https://github.com/ml-explore/mlx/blob/main/LICENSE)、[MLX Examples MIT](https://github.com/ml-explore/mlx-examples/blob/main/LICENSE) | 软件许可证不自动涵盖另行取得的全部模型 |
| faster-whisper | [MIT](https://github.com/SYSTRAN/faster-whisper/blob/master/LICENSE) | 它调用的推理库、音频库、模型也需各自核对 |
| CTranslate2 | [MIT](https://github.com/OpenNMT/CTranslate2/blob/master/LICENSE) | CUDA、cuDNN 等可选平台依赖另有条件 |
| PyAV | [BSD-3-Clause](https://github.com/PyAV-Org/PyAV/blob/master/LICENSE.txt)、[安装与 FFmpeg 依赖](https://pyav.org/docs/stable/overview/installation.html) | PyAV 与其所链接／打包的 FFmpeg 不是同一许可证层 |
| sherpa-onnx | [Apache-2.0](https://github.com/k2-fsa/sherpa-onnx/blob/master/LICENSE) | 运行库许可证不等于每个下载模型的许可证 |
| 3D-Speaker | [Apache-2.0 源码许可](https://github.com/modelscope/3D-Speaker/blob/main/LICENSE) | CAM++ 模型／转换版本的来源、模型卡、权重条款需单独记录 |
| Remotion | [Remotion License](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) | 不是 MIT。依据使用主体及条件，可能需要 Company License；升级版本时重新核对 |
| React、TypeScript、Tailwind CSS 等 Remotion 周边包 | 各包所选版本的 `LICENSE`、`package.json` 和分发声明 | 此仓库未分发这些包；新工程生成锁文件后自行核对完整依赖树 |
| 第三方 skills、Codex plugins、MCP 服务 | 各发布者的源码许可、市场条款与服务条款 | 本仓库只说明角色及替代路径，不复制它们的实现，不替第三方作可用性或授权承诺 |

## 模型、字体、声音与画面

- Whisper 的[上游代码许可](https://github.com/openai/whisper/blob/main/LICENSE)为 MIT；下载转换版、微调版或其他说话人模型时，仍应核对具体模型卡、revision 和许可文件，不能只凭“Whisper”或“CAM++”名称判定授权范围。本仓库不打包模型。
- 字体由读者自行取得。操作系统自带字体不因已安装就成为本仓库可分发资产；使用、嵌入或再分发时按字体许可处理。本仓库不附字体文件。
- 音乐、音效、插图、Logo、节目参考截图和原始录音录像不因剪辑规范开源而开放使用。请使用自己制作或已获适当授权的素材，并在单集素材表中保留来源与授权范围。
- 真实节目的人物形象、录音、文字稿及品牌标识不包含在本仓库 MIT 授权中。本仓库提供可学习的制作方法，不授予这些媒体或标识的使用权。

如果后续贡献实际引入第三方文件，应同时提交可核验来源、准确版本、许可证及必须保留的声明；不要仅向本表追加一个软件名字。若重新分发程序二进制或组合发行包，应基于真正打包的内容整理完整清单，而非将本索引当作分发合规证明。
