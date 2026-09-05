# 重启恢复手册

写于 2026-09-02。这份文件本身在 git 里,重启一定还在。

## 一句话状态

所有工作都已发布：本地分支 `fusion/evidence-authority` 与 GitHub 仓库 `crossaudit-harness` 的 main 同步。
`v5-redesign` 未动；要不要把融合线合回它由你定。

- 决策记录：`docs/DECISIONS.md`，D39–D149 连续无缺口（有测试守着）
- 融合方案与逐文件对比：`docs/findings/codex-fusion-dd725d3.md`（含三份分簇报告）
- 设计文档：`docs/EVIDENCE_AUTHORITY.md`；DESIGN.md §7.1；README 两个档位说明
- 打好的安装包：`~/Documents/Crossaudit/builds/CrossAudit-4.16.0-arm64.dmg`（153M，sha256 前 16 位 `5f3f46387167c230`，来自发布后的 main（含 Thinking Orbs））；上一版 4.15.0 仍在同目录

## 融合线做了什么（2026-09-02）

| 切片 | 内容 | 状态 |
|---|---|---|
| A | 合入 `feat/finding-states`，复核后修了 5 处（sidecar 未 git add、状态词进了模型 prompt 等） | 已合 |
| B+C | `auditor/authority.py` 证据授权层（判定阶梯不动，其后派生）、回执 `authority` 块、档位 `authority.lone_model_blocker` | 已合，复核 9 处已修 |
| D | `repair_guard.py`：硬拒绝只剩越界文件与非渲染二进制，其余为"提醒"送入下一轮审计 | 已合，两轮复核 20 处已修 |
| E | 文档 | 已合 |
| 搁置分支 | `fix/approximately-means-approximately`、`fix/guard-name-states-its-reach` 复核后修好合入；套件不再联网 | 已合 |
| 控制台 | 决策卡文案、发现的层级标注、无障碍名、拒绝文案中文接线 | 已合，第 3 轮体验修复见下 |
| 中文化 | 540 条拒绝文案 538 条有中文；语言解析改为所有命令生效 | 见下 |

## 重启后怎么恢复

1. `cd ~/Documents/Crossaudit/crossaudit_integ && git checkout fusion/evidence-authority && git status --short`
2. 开 Claude Code：`读 docs/RESTART.md，从"下一步"继续。`
3. 跑测试必须带 PYTHONPATH（共享 venv 里装着旧包）：

       PYTHONPATH=$PWD/src /Users/ericdong/Documents/Crossaudit/crossaudit_v4/.venv/bin/python -m pytest -q tests/

4. 打包：`PYTHON_BIN=/Users/ericdong/Documents/Crossaudit/crossaudit_v4/.venv/bin/python bash packaging/macos/build_dmg.sh`
5. 浏览器实测控制台时，Claude in Chrome 有两个已连接的 Chrome 实例，选 "macbook"。

## 第二轮（2026-09-03）

| 切片 | 内容 | 状态 |
|---|---|---|
| 感知延迟 | 发送即返回（~3 ms），每阶段叙述，流式默认开启、Anthropic 流式，审计阶段逐项检查，8 秒静默心跳 | 已合，复核修复已合 |
| 安装与预检 | 缺凭据前置设置卡（所有入口）、异厂商句子、向导默认单仓库、DMG 打开说明、卸载说明 | 已合，复核修复已合 |
| 结果与决策 | 人话判定、观察句优先、详情折叠、耗时费用预估、每个升级分支有原因与动作 | 已合，复核修复已合 |
| 预警与计费 | 归属到任务/循环/轮次/角色、80%/95% 预警、429 倒计时、顶栏胶囊、未计价可见与覆盖价、导出与汇总 | 已合，复核修复已合 |
| 闭环复核 | 两轮闭环审计（e0e3b36、e3b9388），其后两处遗留已修 | `docs/findings/fusion-round2/review-closure*.md` |

## 发布（2026-09-03）

- 公开仓库：https://github.com/dongzhaohe321418-lab/crossaudit-harness （main = 融合线完整历史，CI 在 Linux/macOS 全绿，Windows 为咨询性）
- Release：https://github.com/dongzhaohe321418-lab/crossaudit-harness/releases/tag/v4.16.0 （DMG + sha256；临时签名、未公证）
- 官网源码在 `website/`，线上 `crossaudit-v4.vercel.app`；内容已按 4.16.0 更新，截图由 `website/scripts/shoot-console.mjs` 重新生成
- Thinking Orbs（MIT）已内置：`src/crossaudit/console/vendor/thinking_orbs_engine.js`，`scripts/vendor_thinking_orbs.py` 重新生成

## 测量线（2026-09-05）——四个结论全部不成立，前提被推翻

**这一轮最重要的事：我让 Codex（另一家厂商）只读复核了我们自己的测量代码。**
之前所有复核都是 Claude 审 Claude。它一遍找出五个足以阻止发表的缺陷，报给你的
四个主要结论**没有一个以原样成立**。完整报告在 `benchmarks/reviews/`，撤回与
替代结论在 `benchmarks/CORRECTIONS.md`，规矩写进 D153。

最严重的一个是**写进预登记里的**，所以后面每一轮复核都继承了它：研究 4 的主结局
只统计"发生了修订"的实例，而处理本身决定修订是否发生。条件式 −19.60（n=7），
全样本 −4.01，CI [−16.54, +8.33]，跟零没区别。"修订净负面"已撤回。
**你当时叫停那个默认值改动是对的。**

它还纠正了更正文件自己的第一版——我说"2.6pp 噪声地板查无出处"，那是只搜了一个
分支的已提交树。数字是真的，缺陷是估计量用错了。

**前提研究 n=30 的结果，改变了产品该怎么说自己：**

| | 提出的发现 | 判为阻断 | 拦下的增量 | 召回 |
|---|---|---|---|---|
| 自审 | 64 | 3 | 3.3% | **31.7%** |
| 跨厂商 | 48 | 48 | **80.0%** | 19.8% |

自审**不是看不见，是看见了放行**。能站住的话是"陌生人更不宽容"，不是"陌生人看得更多"。
README 里两处相反的说法已改（官网中英两版原本就是对的，说的是"给自己作业打分"）。
**这个改动还没推到公开仓库，等你看过。**

含生成的噪声地板首次测出：SD 1.84。它撤回了研究 3 的"+2.04 F1，初稿没有下降"
——那句正是让"拆分规则"看起来免费的保证。召回 2%→23.5% 的收益仍稳固，但代价
现在是**未测量**，不是零。

**没被推翻的（同样是结果）**：CLEAR 的分母、方向、F1、聚合都对得上论文，无思维链
泄漏；代码研究无任何路径的隐藏测试泄漏，样本量精确复现；跨厂商"误报更低"站得住。

其他已做：原始运行数据从临时目录抢救到 `~/Documents/Crossaudit/study-data`（21 MB，
多个后续分析靠它才便宜，永不提交——语料是 CC BY-NC-SA）；完成的研究分支已并入
发布分支；受影响的报告在标题上方带了更正横幅；修了打分器静默解析矛盾回复、浮点
并列拆分两个缺陷（各带守卫测试）；建了持久 `.venv`（Codex 当时因为没有它跑不了
基准测试）。全套 2744 通过，基准 116 通过。

## 架构探索（2026-09-05 下午）——已上线架构在前沿上，两个提案被自己的测试杀掉

你授权我自行优化甚至放弃现有架构。做了三件事，全部预登记、全部可零成本复现：

1. **可执行检查提案（"没被执行的不许拦"）——证伪条件触发。** 代码域 56 个
   P 层解，审计员只在 13 个上写出能区分对错的检查（线是 19），复制臂 11 个。
   格式不是瓶颈（288/288 编译，96% 能跑）；它拦正确解 22 次、拦缺陷解 18 次，
   **反向**。它会给题目发明规格再断言。D155：模型可以**指名**证据由代码验证
   存在（A4 的 `governed_source_ids`，未动摇），不可以**陈述证据会说什么**。
2. **探索循环（15 个架构，代码域，非模型真值，预登记目标）——零假设。**
   目标：确认半集上正确代码误报 ≤ 6.7% 的规格里 P 层召回最高者。**没有一个
   超过已上线的 `holistic-cross`**（20.0% 召回、6.8% 误报、$0.0069/实例）。
   约束内的都召回更低（−5.5 到 −16.4），召回更高的（+1.8 到 +21.8）都违反
   约束。一致性过滤第三次失败；便宜模型三次抽样成本 1.9× 且找得更少。
   `benchmarks/code/explore.py` 可续跑，重跑 $0，10/15 个规格是已有记录的集合
   运算。花费 $4.42。
3. **噪声地板修正（CORRECTIONS #12）**：整天引用的"代码域 1.8 点"是三组配对里
   最窄的一组，不是地板。三次完整抽样最宽一对 **6.4 点（n=110）、9.1 点（n=55）**。
   C 列（约束所在）稳定在 5/5/4。

设计文档 `docs/design/AUDIT_ARCHITECTURE.md` 把撤回的提案原样保留加标记，
下面是仍站得住的部分：并集检测（含生成模型自身）、不按一致性过滤、去掉裁决
模型（130/130 与确定性映射一致）、模型单独发现走 `lone_model_blocker` 旋钮。
**唯一让召回动过几个点以上的是"告诉审计员看什么"（+21.5 pp）——参照物，不是
结构。下一个架构问题是产品问题：项目能提供什么已知为真的东西。**

## 论文支线（2026-09-05 晚）——AI 审计的上限

owner 开了一条支线：AI 审计的上限在哪，能否自审提高准确性。目标 ICML 级；
可复现、精确、真实优先。私有仓库 `dongzhaohe321418-lab/audit-ceiling-paper`
（本地 `~/Documents/Crossaudit/audit-ceiling-paper`）。**研究已完成（`study/ceiling`，工作树 `~/Documents/Crossaudit/crossaudit_ceiling`，未合并，
astra 复核已回（`benchmarks/reviews/2026-09-05-ceiling-study-astra.md`）：**所有数字复现
（我也独立复现了标题的 3/56、2/56、+0.89 pp、p=1.0），但不可按现状引用**——标题"95% 精确
区间"估计错量，模拟覆盖率 0.416；未按问题聚类（112 实例/96 问题，110 P/56 问题）；实际比较
16 次而非 12；7 个超时在"断言确认"总体内；"极限下""参照物做到了"超出数据（参照臂减 cross
臂 +5.36 [−1.54, 9.54], p=0.146）。修改意见已发，含把覆盖率模拟写成测试；
EXPERIMENT_RECORD §10 新增"区间必须声明并核验覆盖率"。第二轮复核前不得引用。）** 构建者报告的结论：**owner 的问题
答案是否**——自审→修订后隐藏测试通过率净变化 +0.89 pp，CI [−3.16, +3.99]，p=1.0，n=112
（修好 3/56，弄坏 2/56），预登记证伪条件触发。"看"的上限：cross 渐近 31.5% [21.7, 45.6]
（K=8 原始 30.0%，曲线未拐平、标为外推），self 16.6% [8.1, 26.3]，astra 32.5% [20.5, 44.8]；
A(self)−A(cross) = −14.9 pp [−32.1, −2.3]。**代码域里自审看得比他审少**（散文域相反，
CORRECTIONS #13 记为任务相关），且 self 近乎确定性（每对抽样 0–3 处分歧），重读无益；
一次 astra 读优于八次 cross 并集。残差 57/110 从未被任何家族任何一次标出，其中 46 个只在
可见测试从未构造的输入类上失败——**上限的形状：模型没有证据那些输入类存在**。唯一有效的：
一条宪法规则"找可见测试没覆盖的"，标记率 +26.8 pp，闭环净 +8.04 [1.06, 11.16]（次要，
十二次比较 Bonferroni 后唯一存活，只授权一次确认性运行）。构建者自抓一个 Clopper–Pearson
尾部反转 bug（数字未流出）。$13.23 + 4.4M astra 订阅 token。原计划：两个上限分开量
——"看"的饱和曲线（跨厂商 / 自审 / 混合 / astra 四个家族，K 到 8）与"改"的闭环
（自审→修订后隐藏测试通过率的净变化，预登记证伪条件：自审净变化 ≤ 0 即为标题）。
写作与统计审查用 `~/Documents/Crossaudit/nature-skills`（只读，不装全局）。
astra 走 Codex CLI（≥0.153）：`codex exec -m gpt-6-astra -c 'model_reasoning_effort="high"' --sandbox read-only --skip-git-repo-check -`。

## 留给你定的两件事

1. **"跨厂商"是不是正确的分割轴。** `sibling − self = −22.2 pp`（p≈2×10⁻⁵）——
   同一厂商两个模型之间的差距，接近两家厂商之间的两倍。真正起作用的可能是"与作者
   的距离"而不是"与训练语料的距离"。若如此，强制不同厂商这条硬约束既太严也太松。
2. **报告而非修订的默认值**仍处于你叫停的状态，我没动。证据比当初强（零成本重算：
   保留最优的门控相对"干脆不修订"是 +0.00；36 次转移里只有 3 次高于自己的初稿，
   全在只跑了 4/10 的那一臂；运行时没有任何信号能预测有害修订，门控做不出来），
   但仍只有一个任务。

## 下一步（按优先级）

0a. **对照检查设计研究已完成并合并**（`docs/design/PROVENANCE_CHECKS.md`，518c970）。
   数据定下的约束：注释必须精确到**行/片段**，不能只到文件——16 份归档草稿里，错误
   文件含有所声称的（值，单位）对的比例 27.7%，错误行 0.0%（探针已复现）。读代码
   发现两个已上线缺陷：science 配置里有 provenance 没有 declared，所以引用的输入
   可以不存在；A4 的 sources fence 在生成端没有任何指令，`checks: research` 无法
   触发。第一片（这两个修复 + `number_source` 检查 + house skill）已派出构建，
   验收门是 §6 Arm 1（$0，现有字节上假阻断率 > 2% 即杀）。
   **第一片被 astra 复核否决（不能合并）**，报告存于 `benchmarks/reviews/2026-09-05-provenance-slice-1-astra.md`。
   两个内核削弱我自己复现了：片段剥离让 `runs.csv@v3#garbage` 之类以前被拦的源通过，
   还让合法文件名 `runs#raw.csv` 被误拦；`declared` 进 science 后 `sources: [doi:…]`、
   `requires: [python>=3.11]` 变成假阻断。构建者正按项修（片段只剥 `#L<n>(-L<n>)?`
   且在精确匹配失败后；science 撤回 declared，改在 provenance 里对 metadata.yml 的
   inputs 做带版本的存在性检查；数值比较改十进制字符串、带符号、复合单位）。修完再送
   第二轮独立复核。**第二轮修复已回（57100d7，全套 2811 通过）：六项全部复现并修好，
   另发现 `available()` 没导入内置包、靠调用方碰巧导入而通过，以及仓库夹具里 43 处声明了
   从未写过的 `scripts/run_demo.py`——均已修，无断言放松。第二轮 astra 复核（`benchmarks/reviews/…-round2.md`）仍否决但已收窄：剩两个根因——
   `number_source` 信任 `check_units` 校验 value 而后者从不校验（畸形量引用 `#L999` 整个
   science 配置零发现通过）、数值比较的子串兜底（`1e3 K` 标 `1e3/g` 通过）；外加**我第二轮
   指令自己造成的削弱**（非字符串条目降为 ADVISORY，`requires: [3]` 从 BLOCKER 变 ADVISORY），
   已撤回：一律 `str()` 强转、保持基线严重度。第三轮修复已回（da8ddfe，全套 **2856** 通过，`PYTHONPATH=src .venv/bin/python -m pytest tests/ -q --timeout=60`）：
   两个根因各设独立守卫（provenance 只在 value 为数字形且 unit 为字符串时越过 `#L`，
   否则精确匹配；number_source 读不了的带片段行报 CA-NUM-001）；`results_files`/
   `declared_inputs` 抽到 `dcl/quantities.py` 共享；子串兜底删除，Decimal 归一化、U+2212、
   `\s*`、最长单位匹配 + 连字符区间/指数前瞻；`requires: [3]` 恢复 BLOCKER。
   **Arm 1 如实报告：主分母 6/365 = 1.64%（Wilson 0.76–3.54%），点估计在杀线下、区间跨线；
   六例全是探针注释把 `°C/min` 截成 `°C`（草稿自身单位延续），构建者拒绝用产品自己的
   单位语法去"修正"它们——那是把检查器的读法喂回去。同义表消融 12/365 = 3.29%，过杀线。**
   第三轮 astra 复核仍否决但已极窄（`…-round3.md`）：前两轮全部确认修好（差分零差异），
   剩一个根因——**单位匹配接受 token 前缀**（`5 m-2s-1` 标 `m` 通过；`1e10001` 截成 `1e1000`
   + "单位" `1`，指数 10000–10099 扫描 100/100 假通过）。第四轮：整 token 提取、整对整比较、
   前缀即不匹配；指数无位数上限、超出 Decimal 合理范围报 CA-NUM-001 而非截断；区间显式拆分。
   复核者同意 Arm 1 那 6 例是探针注释错误而非验证器假阻断，脚本标签要改词不改数。
   第四轮已回（331f2ee，全套 **2892** 通过）：单位改为字符扫描整 token 提取、整对整比较、
   前缀即 CA-NUM-002；数字 `_NUMBER` 无界 + `normalise_number` 用 `fullmatch`，超界报
   CA-NUM-001 不截断；`1,000` 只读作一千；所有定位器解析器统一 `[0-9]` + 绝对末尾、去掉
   `.strip()`；技能门控改为 front-matter `requires_check:`。**注意：本轮改了 `skills.py`
   （内核外，可加），与 `fix/skills-not-in-audit` 冲突——合并顺序：先 skills 片，本片再 rebase。**
   第四轮 astra 复核（`…-round4.md`）仍否决，剩**一个**缺陷：扫描器是字符白名单，白名单外的
   字符（句中 `.`、`β`、`%` 后续接）截断 token，前缀再次通过（`5 kg.m` 标 `kg`）。第五轮：
   反转规则——穷举边界（空白、未配对闭括号、`,;:!?"'«»…`、句末 `.`），其余一律 token；
   fence `at` 与 `src` 同等校验；结构化源去 `.strip()`；指数 >99999 报 CA-NUM-001。
   第五轮修复进行中，预计为最后一轮。**
   `skills/` 排除片（D156）已在文件不相交的分支 `fix/skills-not-in-audit` 上并行构建，
   过滤放在 `_materialise_tree_scope` 的 TEMPLATE 过滤旁（无条件），不放 `excluded` 集
   （那只在非显式范围时生效）。**已交付（6bf00e6，全套 2752 通过）**，并发现审计员有
   **两扇门**：`cmd_run` 按变更路径建增量、不经范围读取器，只改技能的提交会把技能当增量
   送审——两扇都已关，技能-only 提交走既有的"未改动科学文件"拒绝。D156 里我写错的两处
   （"现成排除列表"不在那个函数；只说了一扇门）已当日更正。astra 复核**否决**（`benchmarks/reviews/2026-09-05-skills-not-in-audit-astra.md`）：
   两扇门对规范路径已关，但**加载器按文件系统解析 `skills/`（大小写不敏感主机上会打开
   `SKILLS/`、会跟随符号链接），过滤器按 Git 树路径比较**——两者对"技能目录是什么"
   没有统一身份，别名即绕过。修法定在加载器：真实目录名必须恰为 `skills` 且非符号链接，
   否则 ConfigDenial。另：宪法路径不得位于 `skills/` 下；"没有检查读技能字节"这句前提
   为假（`internal`/`complete-strict` 会读任何文本），改为断言真实性质——技能在任何检查
   运行前已被移出增量。第二轮 astra 复核仍否决但更窄（宪法别名 `SKILLS/`、`work/../skills/`
   在配置加载时被接受；`--lang zh run` 回退叙述为英文；文件名 `skills` 的文案与行为矛盾）。
   **第三轮修复已交（a5ec01e，全套 2763 通过）**：宪法路径 `normpath` 后首段大小写不敏感比较、
   逃出项目的值单独拒绝，`skills/../AUDIT_RULES.md` 归一化后为合法路径**有意接受**（守卫管位置
   不管拼法）；`_is_house_skill` 只匹配目录**之下**的路径，裸文件 `skills` 三处口径统一为"工作"；
   `cmd_run` 顶部 `_speak(args)` 只尊重显式 `--lang`、不用环境变量回退（`run` 叙述 2/33 走目录，
   半翻译屏 D21 禁止；更宽的 i18n 缺口另开一片）。第三轮 astra 复核（`…-round3.md`，首次
   满负荷中断后重跑）否决，四项小问题：`/abs/skills/house.md` 配置加载仍接受；通过守卫的
   `skills/../AUDIT_RULES.md` 以原始拼法存储、下游严格读取器拒绝；性质测试依赖注册表状态、
   新进程下失败；**"只尊重显式 --lang"与 `init`/`doctor`/拒绝处理器不一致（它们经
   `_language_for` 尊重环境）——我已推翻该决定，改为与其它命令一致。** 第四轮修复中。
   **顺带发现两个已上线的旧缺陷**：(1) `general` 包里的 `check_declared` 把标量
   `sources: x` 逐字符当文件名、`requires: 3` 抛 TypeError——每个项目都在跑的默认包；
   (2) 审计范围若包含 `skills/`，技能字节会作为增量数据进入**审计员**提示词
   （`cli/main.py:280` → `auditor/prompt.py:86`），早于本分支。两者已记入 **D156**：前者在第一片里加固；后者裁定为在第一片落地后单独一片，把 `skills/` 像 `TEMPLATE` 一样排除出审计增量。
   **等 owner 决定**：`web_fetch` 的正文是否保留（提交=可由 verify 再推导但第三方
   文本入库；gitignore 缓存=无许可变化但不可再推导）。不保留则 claim→citation 只能
   做增量内的一半。
0b. **把三种对照检查做进确定性层**（owner 于 2026-09-05 认可方向）：数字→来源、
   图→生成代码、断言→引用。原则来自 D155：模型只**指名**依据（"这个数来自表 3"），
   代码去**验证**依据存在且说的是这个；模型永远不陈述依据会说什么。Claude Science
   的审查器（2026-06）正是这三件事，但同厂商、固定三项、边审边改；我们的差异化是
   跨厂商分离 + 确定性阻断 + 收据 + 测出来的数字。先做设计研究，看 A4 的
   `check_source_provenance` 能扩到哪一步，再写代码。

1. **官网部署**：需要你先 `cd website && npx --yes vercel@58.9.4 login`，然后 `npx vercel link`（选现有项目 crossaudit-v4）并 `npm run release:vercel`；或在 Vercel 控制台把 Git 集成改连到 crossaudit-harness。
2. **公证**：`CROSSAUDIT_PUBLIC_RELEASE=1` + Developer ID + notarytool profile 重新打包，替换 Release 资产，官网与 README 去掉"右键打开"说明。
3. **Windows 移植**（可选切片）：CONTRIBUTING.md "Windows" 一节列出的五类问题。
4. `docs/dcl-lifecycle-states` 分支仍需先 rebase 再看（会删 68 个文件），未动。
5. 待定的产品问题：`lone_model_blocker` 的默认何时切到 `escalate`；`generator_streaming` 是否也该管审计端进度。
6. **发表前必须跨厂商复核**（D153）：`codex exec --sandbox read-only --cd <repo>` 带一份书面复核提示，任何它报的问题都要从 `study-data/` 归档里复现才算数。它提议，确定性重算裁决——和产品自己的分级结构一样。

## 不可动摇的规矩(别让任何人改掉)

- `auditor/ broker/ ledger/ policy/ dcl/` 是审计内核,只能加不能削,必须向后兼容
- 没有 agent 可以复核自己写的东西；**测量代码要由另一家厂商的模型复核**（D153）
- 数字走到哪里，它的区间和估计量就跟到哪里（`EXPERIMENT_RECORD.md` §9）；小样本报计数不报百分比（"2 of 2"，不是"100%"）；没有同估计量的复制臂就不许写"在噪声范围内"
- 合并门槛三条同时成立:独立复核干净 + 全量测试在宿主机上绿 + 内核规矩没被动
- 推送 / 发布 / 删数据这类不可逆的事,先问你
