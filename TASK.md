# 长期任务书：zcbot-multiprocessing

本文件是本仓库的**长期任务契约**。opencode 每次续跑先读这里，再读 `OPENCODE_BRIEF.md`。

## 身份与边界

- 本仓库 = `kuangxing6367/zcbot-multiprocessing`（zcbot-mp），**zcbot 的多进程专版**。
- 品牌仍是 zcbot。单进程版全名 **Zero Creat Bot**，仓库 `kuangxing6367/zcbot`。
- **原 zcbot 保持单进程，一行不改**。本仓库独立演进。
- 本仓库的 `dual_process` 参考资料只来自文档摘录，不继承其代码、配置与兼容负担。

## 任务性质

**长期、分阶段、可续跑。** 执行口径：

> 以 zcbot 本来的功能为基线（命令、事件、插件、Web、权限、数据库、协议适配等），
> 在此基础上做**修改与架构魔改**，把单进程运行时改造成 1 Core + N Worker 的多进程运行时。

不是另起炉灶重写一套无关框架，也不是给原仓库加开关。功能连续性优先，架构可以大改。

## 版本策略（硬约束）

**在用户明确要求之前，只允许发布 alpha 版本。**

- 当前版本基线：`0.1.0-alpha.0`（见 `VERSION`）。
- 允许：`0.1.0-alpha.N`，按补丁号递增；需要新特性时用 `0.1.N-alpha.0`。
- **禁止**：beta、RC、正式版、`1.0.0`、去掉 `-alpha` 后缀。
- **禁止**：打非 alpha 的 Git tag，创建非 alpha 的 GitHub Release。
- 解除条件只有一条：用户明确说「可以发 beta / 正式版」之类的话。opencode 不得自行判断时机。

## 阶段与验收

### 阶段一 · 骨架（最小可跑）

- Core 持真实 DB、协议、Web、注册表、监督器；Worker 执行插件，全部资源经 IPC 代理。
- 先落最小 IPC 信封与 worker 注册/路由骨架，再逐模块移植 zcbot 功能。
- 验收：能收发一条消息；kill worker 后 Core 自动拉起，Web 不中断。

### 阶段二 · 隔离

- N Worker、插件到 worker 的分组/分片、命令注册表聚合、崩溃 quarantine。
- 验收：kill 一个 worker，其它插件继续工作，被杀插件的注册项消失。

### 阶段三 · 生产化

- 背压、逐 worker 可观测、单 worker 热替换。
- 验收：压测下慢 worker 不拖垮 Core；可不停机替换单个 worker。

## 从 zcbot 继承的坑（必须从第一天设计对）

1. `trigger_sync` 与 `trigger_async` 必须同语义，短路型 handler 返回 `False` 要真短路。
2. Guard 类 handler 抛异常按 **fail-closed** 处理，不能静默放行事件。
3. 不向插件暴露全局框架引用，宿主级接口走显式、带权限的 API。
4. 数据库连接 `close()` 不得关闭共享连接池；关池只能是停机路径的 `shutdown()`。
5. 短命线程的 DB 连接必须在运行期回收，不能等到停机。

## 明确不做

- 跨机分布式集群、Core 多实例；
- 安全沙箱（进程隔离不等于安全边界）；
- 改动原 zcbot 仓库；
- 在用户要求前发布非 alpha 版本。

## 续跑方式

```bash
cd C:/zc-repos/zcbot-mp
opencode run --auto --model opencode/big-pickle \
  "先读 TASK.md 和 OPENCODE_BRIEF.md，再继续当前阶段未完成的工作。"
```

端点不稳定时**多等、多重试**；读大代码文件容易卡，优先读小摘录文件。

## 进度记录

opencode 每完成一个可验收的小步，在此追加一行：日期 / 做了什么 / 验收结果 / 当前版本。

- 2026-11-26：建立仓库骨架、任务书、版本基线 `0.1.0-alpha.0`；架构草案两份已入库。尚未开始实现。
- 2026-11-26：opencode 完成阶段一第一小步 —— `zcbot_mp/ipc/envelope.py` 最小 IPC 信封
  （标准库、新字段可缺省、合法性校验）+ `tests/test_envelope.py`。验收：`19 passed`；版本仍 `0.1.0-alpha.0`。
