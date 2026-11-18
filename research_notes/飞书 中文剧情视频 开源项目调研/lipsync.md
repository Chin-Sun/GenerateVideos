# 中文角色对白口型与音频驱动视频：60 秒多镜头短剧调研

研究日期：2026-11-17。只做公开文档、官方 GitHub README/LICENSE、官方模型卡核验；未运行模型、未生成视频、未调用付费 API。以下显存/速度全部为作者文档陈述，不是实测；没有公布就标未知，不从参数量推算。直接读取 GitHub raw/Hugging Face，未依赖此前报 401 的搜索服务。共 13 个可核验项目/家族条目；并非声称覆盖截至当日所有新项目。

## 1. 先验证 H3 原生音视频还是 TTS 加口型路线？

### Takeaway
H3 已文档化多模态音频参考，但没有文档化“逐字复述指定中文台词/保留输入音轨/指定声音属于哪个脸”的保证。应先把 H3 原生对白作为待验收路线，而不是已解决能力；准确台词的可控基线是预先锁定配音音轨，再对短镜头做音频驱动口型或生成。

### Cited Findings
- PPAPI 的模型名是 `MiniMax-H3`，`POST /v2/video_generation`，异步结果读 `task.status` 和 `task.content.url`；不是旧 `/v1/video/generations` 结构。支持 768P/2K、4–15 秒生成。多模态参考最多 9 图、3 视频、3 音频，单个参考视频/音频 2–15 秒，每种媒体总长度最多 15 秒。首尾帧角色不能和 `reference_*` 混合。— [PPAPI H3 原文](https://pp-api.docs.buildwithfern.com/docs/advanced/video-generation/mini-max-h-3.md)
- `reference_audio` 示例原话是 “Follow the reference video movement and use the reference audio voice timbre.” 因而此字段有音色参考证据，没有精确台词、输入音频逐采样保留、音素时间对齐或多人说话者绑定的文档承诺。— [同一 H3 文档](https://pp-api.docs.buildwithfern.com/docs/advanced/video-generation/mini-max-h-3.md)
- Wav2Lip 官方库直接链接其商业 hosted API；Sonic 官方 README 明确开源版本非商用，商业化建议腾讯云 VCLM。这只是官方给出的商业替代入口，不表示这些 hosted 产品免费，也不表示其模型就是开源检查点。— [Wav2Lip](https://github.com/Rudrabha/Wav2Lip#commercial-version)、[Sonic 商业化说明](https://github.com/jixiaozhong/Sonic#-news)、[腾讯 VCLM API](https://cloud.tencent.com/document/api/1616/109378)

### Inferences
- 60 秒应按剧情拆成约 6–12 个可替换镜头；先固定分角色中文台词、情绪、停顿、音轨时长，然后分镜。此为生产建议，不是任何模型能力承诺。
- 验证 H3 的最小实验应包括：逐字中文短句；两个人轮流说不同句；数字/人名；明显停顿；同音字；侧脸和嘴部遮挡。检查录音是否被改写、漏词、串人、重配音，再决定是否省去后期口型。本文没有执行该实验。
- 确切台词的主路线：合法 TTS/演员配音锁轨 → H3 生成镜头底片（或直接音频驱动生成）→ 单镜头/单角色 lip-sync → 人工验收 → 合成。固定原音轨保证“听到什么”，不自动保证“嘴形准确”。
- H3 的首尾帧与参考模式互斥，是接口设计约束：不要设计一个同时依赖首尾帧锁构图和 `reference_audio` 的请求。

### Gaps
- 没有实际 H3 原生中文对白成功率、音轨保真或人物指派实测；仅凭文档不能否定其潜在能力，也不能认证精确对白。
- 未核验 hosted 服务当前价格、合同、数据保留、地区可用性；不将其列为已选型服务。

## 2. 哪些开源/开放权重项目值得比较？

### Takeaway
优先分清三类：A 已有视频口部重绘，B 单肖像说话动画，C 音频驱动身体/场景/多人。短剧应优先 A 保留已有镜头，C 解决双人交互；B 主要适合正面近景，不能当作完整短剧引擎。所有“推荐/风险”是研究者的生产判断。

### Cited Findings

| 项目/准确官方仓库 | 输入与用途、中文证据 | 代码与权重许可证（分别看） | 文档化计算条件（作者报告） | 镜头边界与生产复用判断 |
|---|---|---|---|---|
| **1. [LatentSync](https://github.com/bytedance/LatentSync)** | A：视频+音频的扩散口型；1.5 更新明确改善 Chinese videos；1.6 提升到 512 分辨率。[README](https://github.com/bytedance/LatentSync/blob/main/README.md) | 代码 [Apache-2.0 LICENSE](https://github.com/bytedance/LatentSync/blob/main/LICENSE)；官方 [HF 检查点包](https://huggingface.co/ByteDance/LatentSync/blob/main/README.md) 却写 `license: openrail++`，包还含 Whisper/脸检测等辅助检查点，不能把所有权重说成 Apache。 | 推理最小 1.5 **8GB**，1.6 **18GB**；20/30/55GB 是不同训练配置，不能混为推理。没有已核验统一推理时长。[README](https://github.com/bytedance/LatentSync#inference) | 优先作为高质量单角色近景补口型候选。中文有直接更新证据；侧脸/遮挡/多人没有本文核验的可靠成功率或保证，切镜头/选人/跟踪须由系统承担；商业前审计辅助权重。 |
| **2. [MuseTalk](https://github.com/TMElyralab/MuseTalk)** | A：已有视频局部脸区域音频驱动；明确支持 Chinese/English/Japanese。[README](https://github.com/TMElyralab/MuseTalk/blob/main/README.md) | README 明确 **代码 MIT；模型 any purpose, even commercially**；第三方 Whisper/ft-mse-vae/DWPose/S3FD 等各遵许可证；测试数据仅非商用研究。[许可段](https://github.com/TMElyralab/MuseTalk#disclaimerlicense) | V100 生成过程 **30fps+**，有预处理/头像准备，不应等同任意输入端到端实时。另明确 RTX3050Ti Laptop **4GB FP16，8 秒视频约 5 分钟**。训练表 32GB 等不要误读。[README](https://github.com/TMElyralab/MuseTalk/blob/main/README.md) | **近期工程首选之一**：中文、许可、低显存证据清楚。作者列脸区 256×256、胡须/唇色/唇形保留不佳和抖动；旧限制段与新版时序改进共存，应版本冻结后测试，不能保证没有抖动。[限制](https://github.com/TMElyralab/MuseTalk#limitations) |
| **3. [Wav2Lip](https://github.com/Rudrabha/Wav2Lip)** | A：视频+音频；经典基线而非最新商业服务。语言泛化不等于本次已核验中文专项评测。[开源段](https://github.com/Rudrabha/Wav2Lip#non-commercial-open-source-version) | README 明确开源代码、demo 结果用于 research/academic/personal；LRS2 训练模型 **commercial use strictly prohibited**，商业需另谈，不能以第三方 fork 宽松许可证洗掉原权重限制。[许可](https://github.com/Rudrabha/Wav2Lip#license-and-citation) | 本次未找到可信明确的最低 VRAM/统一推理时长，不填网传数字。 | 研究基线；**不推荐直接进入商业短剧流水线**。当前 README 顶部商业 API 示例与下方旧开源模型必须分开。 |
| **4. [SadTalker](https://github.com/OpenTalker/SadTalker)** | B：单照片+音频，3D motion coefficients 的 talking head；中文 Windows 教程不是中文准确率证据。[README](https://github.com/OpenTalker/SadTalker/blob/main/README.md) | 官方 2023 更新明确改 Apache-2.0、去掉非商用限制，[LICENSE](https://github.com/OpenTalker/SadTalker/blob/main/LICENSE)；作者 HF [vinthony/SadTalker 卡](https://huggingface.co/vinthony/SadTalker/blob/main/README.md) 标 MIT 且内容是模板，属权重包元数据不一致，依赖需另查。 | 本次读取 README 未给明确最低显存或可比较推理时长。 | 可复用低复杂度正面说话近景/分镜草稿，不是动作、多人、场景连续性方案。中文质量需验收；不从作者国籍推导能力。 |
| **5. Hallo 家族：[Hallo](https://github.com/fudan-generative-vision/hallo)、[Hallo2](https://github.com/fudan-generative-vision/hallo2)、[Hallo3](https://github.com/fudan-generative-vision/hallo3)** | B，3 扩展动态前景背景但仍 portrait animation。**1/2/3 输入说明都要求 English**；1/2 要正脸旋转 <30°，不能把“复旦”当中文支持。[Hallo 输入](https://github.com/fudan-generative-vision/hallo#-prepare-inference-data)、[Hallo2 输入](https://github.com/fudan-generative-vision/hallo2#-prepare-inference-data)、[Hallo3 README](https://github.com/fudan-generative-vision/hallo3/blob/main/README.md) | 三库 [1 LICENSE](https://github.com/fudan-generative-vision/hallo/blob/main/LICENSE)、[2 LICENSE](https://github.com/fudan-generative-vision/hallo2/blob/main/LICENSE)、[3 LICENSE](https://github.com/fudan-generative-vision/hallo3/blob/main/LICENSE) MIT；1/2 HF 卡 MIT。**InsightFace 预训练权重非商用**是下游依赖风险；Hallo2 高清模块要求 CodeFormer S-Lab1.0，不能只看 MIT。[Hallo2 警告](https://github.com/fudan-generative-vision/hallo2/blob/main/README.md) | Hallo1/2 测试 A100；Hallo3 测试 H100。未给本文可核验的最低 VRAM/推理秒数。Hallo2 4K 23min 演示是**输出长度**不是运行时长。 | **中文短剧不优先**。Hallo README 指向支持 Mandarin 的 JoyHallo 扩展，但该扩展未单独完成许可证/计算核验，不充数列为已验证选项。 |
| **6. [EchoMimic](https://github.com/antgroup/echomimic)** | B：音频与可编辑 landmarks 驱动肖像。官方 Chinese gallery、英/普通话预训练权重发布项。[README](https://github.com/antgroup/echomimic/blob/main/README.md) | 代码 [Apache-2.0](https://github.com/antgroup/echomimic/blob/main/LICENSE)；[官方权重卡](https://huggingface.co/BadToBest/EchoMimic/blob/main/README.md) 本次未见单独明确权重许可元数据，勿直接等同所有依赖 Apache。 | 测试 A100 80G/4090D24G/V10016G；加速版作者报 V100 约 **50 秒/240 帧**，原约7min，不是本机复测。[README](https://github.com/antgroup/echomimic/blob/main/README.md) | 中文 portrait 备选，landmark 可控；不是已有多镜头电影无损配音，也无已验证双人指派。 |
| **7. [EchoMimicV2](https://github.com/antgroup/echomimic_v2)** | B→C 半身：audio + hand pose + reference image，中文 gallery，英/普通话模型。[README](https://github.com/antgroup/echomimic_v2/blob/main/README.md) | 代码 [Apache-2.0](https://github.com/antgroup/echomimic_v2/blob/main/LICENSE)；[权重卡](https://huggingface.co/BadToBest/EchoMimicV2/blob/main/README.md) 未核出独立清晰元数据/权重全文授权，商业前补审依赖和模型包。 | 测试 A10080G/4090D24G/V10016G；加速 A100 **~50 秒/120 帧**，原~7min。不是“只要1分钟就生成1分钟视频”。[README](https://github.com/antgroup/echomimic_v2/blob/main/README.md) | 有手势需求的中文单人中景可试；多人物对白不作已证实能力。 |
| **8. [EchoMimicV3 / Flash](https://github.com/antgroup/echomimic_v3)** | C：1.3B 多模态多任务 human animation，talking head/body；中文 gallery；Flash 用 chinese-wav2vec2。[README](https://github.com/antgroup/echomimic_v3/blob/main/README.md) | README 明确 **models Apache-2.0**，[HF 卡](https://huggingface.co/BadToBest/EchoMimicV3/blob/main/README.md) 同；本次标准 `LICENSE` URL 404，**代码单独授权全文未核验**，不能把模型声明当代码全文。Wan2.1-Fun 基座等还须审计。 | 2026-01-22 Flash 更新：**12G、8-step、最高768×768、无 face mask**；另12G量化 Gradio/16G ComfyUI 路线不要混为统一基准。作者建议 talking head5步/body15–25步是其他配置建议，不强行等同 Flash8步。[README](https://github.com/antgroup/echomimic_v3/blob/main/README.md) | **中文单人身体动画优先 PoC**；多于138帧要 Long Video CFG；动作/文本/口型 CFG 有权衡。未经证实多人可靠性，不能替代 MultiTalk。 |
| **9. [Sonic](https://github.com/jixiaozhong/Sonic)** | B：单肖像+音频，global audio perception；不是 `SonicThe3rd/Sonic`。官方 README 未核出明确中文指标。[README](https://github.com/jixiaozhong/Sonic/blob/main/README.md) | [LICENSE](https://github.com/jixiaozhong/Sonic/blob/main/LICENSE) **CC BY-NC-SA4.0**，README 明确非商用，另依赖 SVD-XT；不推荐未经许可商业上线。 | 官方仅说单 **32G GPU** 测试、Linux CUDA；不能改写成最低32G或推理速度保证。 | 研究情绪/头动参考；商用转向其官方指向 hosted 服务另签条款，不把开源模型包装后直接销售。 |
| **10. [HunyuanVideo-Avatar](https://github.com/Tencent-Hunyuan/HunyuanVideo-Avatar)** | C：头像/上身/全身、多角色、情绪控制，face-aware audio adapter。中文专项质量未在本次读取 README 中核出，不从腾讯品牌推断。[README](https://github.com/Tencent-Hunyuan/HunyuanVideo-Avatar/blob/main/README.md) | **Tencent Hunyuan Community License，不是 Apache/MIT**；代码/权重等被 license 定义纳入。地域排除 EU/UK/Korea，包含 outputs 的域外使用限制；>1亿 MAU 条件另需授权，禁止用输出改进其他 AI 模型（规定例外除外）。精确原文见下文。[LICENSE](https://github.com/Tencent-Hunyuan/HunyuanVideo-Avatar/blob/main/LICENSE) | 官方 minimum **24GB for704×768×129f，very slow**，recommended96GB；80GB 也可能降分辨率。10GB 是作者感谢 Wan2GP 的**社区实现路线**，不是原生同配置最低。[README](https://github.com/Tencent-Hunyuan/HunyuanVideo-Avatar#-requirements) | 功能很贴近动态多人短剧，但算力和全球发行许可阻力大；不作为第一商用集成。 |
| **11. [MultiTalk](https://github.com/MeiGen-AI/MultiTalk)** | C：多路音频+参考图+prompt，多人会话与交互；chinese-wav2vec2 encoder 是中文适配线索，不等同专项中文验收。[README](https://github.com/MeiGen-AI/MultiTalk/blob/main/README.md) | README 明确 **models Apache-2.0**；本次标准 LICENSE URL404，代码授权全文未核到；Wan2.1基座与可选 FusioniX/Lightx2v LoRA 不应自动继承同许可。 | 作者报480P单4090低显存；8GB 是社区 Wan2GP。README 标“支持15秒”，同时 tips 说81帧25fps训练、81帧最佳，最多201帧且prompt跟随变弱；当前代码480P，720P多GPU待更新。**保留文档内部不同段的范围，不写15秒稳定保证**。[README](https://github.com/MeiGen-AI/MultiTalk/blob/main/README.md) | **双人同框短对白优先基线**，尤其要验证不说话的人是否乱动嘴、人物交叉遮挡后身份绑定。不能自动完成跨镜头身份。 |
| **12. [InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk)** | A+C：sparse-frame视频配音，也能图+音频生成；嘴、头、身体、表情都可能随音频改变，不是只编辑嘴。官方声称比MultiTalk减少手体畸变；chinese-wav2vec2 encoder。[README](https://github.com/MeiGen-AI/InfiniteTalk/blob/main/README.md) | README models Apache-2.0；本次标准LICENSE404，代码授权全文待补；依赖与加速 LoRA单审。 | 支持低显存卸载/INT8但本次未找到官方具体最小GB/端到端耗时，**不借用 MultiTalk8GB**。默认max_frame_num=1000（40秒）；“unlimited”是长视频能力声明，不是默认60秒直接出片。 | **已有 H3 动作镜头需整体配音时优先 PoC**；保留动作只是程度，不是像素不变。长时延续不代表跨剪辑/跨场景角色资产系统。 |
| **13. [LongCat-Video-Avatar 1.5/1.6](https://github.com/meituan-longcat/LongCat-Video)** | C：AT2V/ATI2V/continuation，单/多音频，单/多人。1.5模型卡有中英508组素材主观评测（作者自报）；1.6卡语言zh/en。不是只靠新闻名称。[1.5卡](https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5/blob/main/README.md)、[1.6卡](https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.6/blob/main/README.md) | [代码 LICENSE MIT](https://github.com/meituan-longcat/LongCat-Video/blob/main/LICENSE)；官方README和1.5/1.6卡明确权重 MIT。仍需依赖审计/肖像声音权利。 | 1.5 8-step、1.6双LoRA8-step；官方 avatar示例用2GPU context parallel，但**未核到最低显存GB和统一wall time**，不把基础文生视频性能外推avatar。1.6声称>10min是作者输出能力声明。[README](https://github.com/meituan-longcat/LongCat-Video/blob/main/README.md) | **新一轮多人物/身体对白首要候选**，需与MultiTalk/InfiniteTalk对照验证。1.6 由官方README标2026-11-15发布，HF具体模型卡HTTP200且描述相符；未查独立release tag时间，不称独立确认发布史或生产成熟。 |

### 关键许可原文与冲突记录
- **Hunyuan 域外输出限制是真正许可证原文，不是转述 README**。LICENSE 第3行：“THIS LICENSE AGREEMENT DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA”；Territory 定义排除这三地；5(c)：“You must not use, reproduce, modify, distribute, or display the Tencent Hunyuan Works, Output or results of the Tencent Hunyuan Works outside the Territory. Any such use outside the Territory is unlicensed and unauthorized under this Agreement.” 5(b)：“You must not use the Tencent Hunyuan Works or any Output or results ... to improve any other AI model (other than Tencent Hunyuan or Model Derivatives thereof).” §4 的阈值是版本发布时此前月所有产品/服务 **greater than100million MAU**。注意“鼓励 Powered by Tencent”不是强制品牌条款；不得把其他 Hunyuan 模型许可证套到 Avatar。— [本次读取完整 LICENSE](https://github.com/Tencent-Hunyuan/HunyuanVideo-Avatar/blob/main/LICENSE)
- **InsightFace代码与模型分离**：官方 README 原文 “The code ... MIT ... no limitation ... commercial usage”，但 “The training data containing the annotation (and the models trained with these data) are available for non-commercial research purposes only.” 且手工/自动下载模型均适用。Hallo1/2/3依赖明确列InsightFace；LatentSync数据处理提到InsightFace，实际部署所用脸检测/对齐权重需沿代码确认，不断言所有路径均调用同一受限包。— [InsightFace 授权](https://github.com/deepinsight/insightface#license)、[Hallo依赖](https://github.com/fudan-generative-vision/hallo/blob/main/README.md)、[LatentSync](https://github.com/bytedance/LatentSync/blob/main/README.md)
- **LatentSync HF卡 `openrail++` 与代码 Apache 是不同范围，不应覆盖冲突**。HF卡明确该仓库存储 U-Net、SyncNet、Whisper、auxiliary checkpoints；仅模型卡标识不是逐个权重法律意见，商业应锁定文件哈希与适用条款。— [HF模型卡](https://huggingface.co/ByteDance/LatentSync/blob/main/README.md)
- **Hallo3中文边界非常明确**：“Audio must be in English since our training datasets are only in this language.” Hallo1/2 同样英文限制，1/2角度<30°。— [Hallo3 README](https://github.com/fudan-generative-vision/hallo3/blob/main/README.md)、[Hallo2 README](https://github.com/fudan-generative-vision/hallo2/blob/main/README.md)
- **LongCat新版本核验范围**：官方 GitHub README 标 Nov15,2026 v1.6，实际 HF v1.6卡存在且含模型下载/单多人命令/MIT/zh。作者称>10min和human preference排名，本文不据此宣布比所有竞品更好，也不把2026-11-17以后状态臆造进来。— [官方README](https://github.com/meituan-longcat/LongCat-Video/blob/main/README.md)、[具体v1.6卡](https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.6/blob/main/README.md)

### Inferences
- 许可证应拆成：项目代码、主权重、基础模型、音频编码器、检测/识别权重、增强器、可选LoRA、demo素材、输入演员授权。GitHub写MIT/Apache不构成全依赖商用清单。
- 第一批只集成三种接口适配器：`video+locked_audio→video`（MuseTalk/LatentSync），`image+speaker_tracks+prompt→video`（MultiTalk/LongCat），`source_video+audio→resynthesized_video`（InfiniteTalk）。不要把所有模型称为同一种lip-sync API。
- 文档支持Chinese或中文编码器不表示方言、强情绪、快速台词、打断对话都已过关；中文README也不是能力证据。

### Gaps
- 没有对这些模型做一致输入的中文短剧情节 A/B；没有可靠统一排名。
- 除Hallo明确角度限制外，未核到其余项目量化的90°侧脸、手遮嘴、人物交叉、同时说话、硬切镜头成功率。不能把缺少限制描述当“支持任意场景”。
- SadTalker权重卡模板/仓库许可范围不同；Echo1/2权重单独授权、Echo3/MultiTalk/InfiniteTalk代码授权全文仍需部署前补查（标准LICENSE404并不证明仓库绝无其他命名许可证）。
- 多个效率图为图片，本次未解析图中数字，故不填未经读取的A100耗时表。

## 3. 60秒多镜头短剧如何选型、验收与保持角色一致？

### Takeaway
最现实的是“分镜资产与身份管理 + 分角色锁音轨 + 逐镜头择模型 + 剪辑验收”。持续60秒的单人说话与60秒多镜头剧情是两种需求；长视频宣称不能替代角色、服装、空间、道具和说话者跨镜头一致性。

### Cited Findings
- MuseTalk明确身份细节损失（胡须、唇形、唇色），InfiniteTalk会联动头/身体，说明口型处理本身可能改变角色外观/表演，不是无损覆盖。— [MuseTalk限制](https://github.com/TMElyralab/MuseTalk#limitations)、[InfiniteTalk特性](https://github.com/MeiGen-AI/InfiniteTalk#-key-features)
- MultiTalk用多路音频和参考图生成多人互动；LongCat支持双音频 `para`（等长求和）或 `add`（顺序拼接并填静音，默认person1先说再person2）。可以建立speaker轨，但不是任意电影台词自动分配器。— [MultiTalk](https://github.com/MeiGen-AI/MultiTalk/blob/main/README.md)、[LongCat](https://github.com/meituan-longcat/LongCat-Video/blob/main/README.md)
- H3参考模式与首尾帧互斥；InfiniteTalk默认40秒；MultiTalk短片prompt遵从随长度下降；这些都支持按镜头拆任务、保存可重试中间资产而非60秒一次完成。— [H3](https://pp-api.docs.buildwithfern.com/docs/advanced/video-generation/mini-max-h-3.md)、[InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk/blob/main/README.md)、[MultiTalk](https://github.com/MeiGen-AI/MultiTalk/blob/main/README.md)

### Inferences
**建议短名单（不是实测排名）**
1. **MuseTalk**：工程基线、中文近景、商用授权陈述最直白；先测色差/胡须/抖动。
2. **LatentSync1.6（预算不足试1.5）**：较高质量视频补口型对照；正式生产先澄清权重与脸分析依赖授权。
3. **MultiTalk + LongCat-Video-Avatar1.5/1.6**：双人同框对照组；LongCat有新版本/清楚MIT权重，但硬件成本与新版本可靠性不能从README推断。
4. **InfiniteTalk**：H3动作底片与锁定对白的整体重新配音候选，验收是否改变重要动作/道具。
5. **EchoMimicV3 Flash**：12G文档路径的中文单人中景/身体动画备选。
6. Wav2Lip、Sonic只作研究基线；Hallo家族不优先中文；HunyuanAvatar待许可证地域与资源条件过关后再试。

**设计约束**
- 每个角色独立 reference pack（正面/三分之二/服装/身形）和固定voice ID；每镜头有speaker ID、start/end、文本、固定音频、参考图、机位、服装、道具、上/下镜衔接记录。模型不负责这套资产管理。
- 易失败的侧背面、吃东西、手遮嘴、奔跑和远景可采用反应镜头、过肩或画外音叙事，而非强行每帧可见嘴部；这仍可是真正角色对白，不等于整片旁白。
- 同框先用独立时轴音轨，静默角色音轨留白。每个镜头检查说话者对应，不只检查“某张嘴在动”。
- TTS锁定台词后测中文ASR字符错误率（用人工复核同音字、人名）和听感；嘴形检查爆破音/闭唇、音画偏移、静音嘴动。身份检查脸/头发/服装/手持物；跨镜头检查眼线与空间方向。
- 测试集建议：中文40–80字多情绪短句；正脸/三分之二/侧脸；遮嘴；1人/2人轮流/2人重叠；中近景/中景/远景；带背景音乐与纯人声；15秒/长音频边界。分别记录可用率、重试次数、GPU峰值、wall time、模型版本和依赖许可，不做未测性能承诺。

### Gaps
- 需要用户确认商业发行地区、可用NVIDIA GPU、演员/声音授权、画风和可接受近景比例；这些决定许可证和镜头设计，但不阻碍当前文献级短名单。
- 本次不证明任何项目“一键稳定生成60秒中文多镜头剧情”；跨镜头角色一致性与剧情编辑仍需独立编排层、资产复用和人工质量门。
