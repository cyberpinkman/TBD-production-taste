# 记录格式与最小可运行示例

仓库带一个仅依赖 Python 标准库的记录工具，不包含自动剪辑器、ASR 或视频渲染器。完整制作按[规范](production-standard.md)执行；这里用虚构数据演示统一时间映射、回合约束和同源 SRT。

## 运行

在仓库根目录：

```bash
python3 scripts/tbd.py validate examples/synthetic/project.json
python3 scripts/tbd.py export-srt examples/synthetic/project.json /tmp/tbd-example.srt
python3 scripts/tbd.py init work/my-episode
```

导出路径必须尚不存在，重复运行请改用新文件名。`init` 也拒绝覆盖已有目录。新建的 `project.json` 是空制作记录，补齐素材和剪辑区间前不会通过验证。

示例完全虚构：不存在对应音视频，没有转写或人工听审结果。正文是 8 秒，演示片头偏移为 2 秒，最终 250 帧；这个片头时长不是节目默认。字幕示例见 [captions.srt](../examples/synthetic/captions.srt)。

## 时间线契约

所有 JSON 字段以 [project.json](../examples/synthetic/project.json) 为完整样例。当前 `schema_version` 为 `1`。

| 字段 | 含义 |
|---|---|
| `kind` | `synthetic` 是无真实媒体的演示；实际制作使用 `episode` |
| `profile` | 输出宽高、`fps_num/fps_den` 有理数帧率、`intro_frames`、`format`（`full` / `short`） |
| `sources[]` | 稳定 `id`、本地 `path`、SHA-256、时长和 `clock_origin` |
| `segments[]` | 按正文顺序列出保留区间，绑定 `source_id`、源入出秒数及正文入出帧号 |
| `captions[]` | 唯一文字源；每条绑定一个保留区间、源入出秒数、`speaker_id`、`turn_id` 和 `text` |
| `review` | 人工审片、听审、发布状态和适用授权记录；程序不替人确认 |
| `editorial_notes` | 制作疑点与修订依据，不进入交付字幕 |

源时间是明确归零后的解码时间；`clock_origin` 写清实际原点、PTS / 编码预延迟怎样换算到该坐标。不要直接把未知原点的容器 PTS 填入。相机同步、色彩、音轨和覆盖范围另存完整清单；这一简化格式只表达直切保留区间。

所有区间使用半开区间 `[start,end)`。正文帧从 `0` 连续排列；本示例不支持变速、交叠转场、多声部字幕或在正文中插入卡片。需要这些能力时应扩展契约与相应检查，不能关闭校验后声称通过。

```text
source delta = caption source time - segment source start
final start  = intro frames + segment body start + floor(source delta × fps)
final end    = intro frames + segment body start + ceil(end delta × fps)
```

片头只加一次。结束帧限制在所属保留区间内；跨剪辑点的字幕须先按实际词界拆分。向外量化可能让相邻字幕重叠，工具会报错，应复核实际回合边界与词时，不能通过盲目平移整条字幕修饰结果。若一句话被剪掉中间部分，不能靠保留整句文本掩盖删节。

镜头、音频和效果的实际渲染器必须使用同一份编辑映射；本工具仅派生字幕时间，不处理媒体。字幕渲染器应读取这里的 canonical JSON 和同一派生结果；导出的 SRT 不应成为另一份独立修改的文字源。像素测宽、字幕位置和字体另由渲染层检查。

## 回合规则

每条字幕只允许一个 `turn_id` 和一个说话人。换人、插话再返回原说话人，都建立新回合；不能把同一人的不连续发言视为一个回合。归属不明用 `speaker_id: null` 并独立成回合，不把 `unknown` 写进画面。

校验器能拒绝：重复 ID、区间越界、映射空洞、声明的时长不一致、同回合混说话人、恢复旧回合 ID、unknown 合并、成片帧重叠以及明显的内部占位符。它不能判断“一条文字里其实有两个人说话”，也不能识别全部内部备注；这些必须回到声音和实际成片审核。

`episode` 类型要求填写真实素材的路径与 64 位 SHA-256。校验器只检查声明格式，**不会读取素材或证明哈希匹配**。`synthetic` 仅用于虚构演示，不能作为绕过真实素材记录要求的方式。

## 检查边界

`validate` 成功仅表示声明的数据满足本工具的结构契约，不代表：源文件存在或身份正确、同步准确、音频无截断、字幕听写正确、人物归属真实、人工已审片或已经发布。`doctor` 只检查 Python、FFmpeg 与 ffprobe 是否可运行，不安装软件、不下载模型、不调用云服务。
