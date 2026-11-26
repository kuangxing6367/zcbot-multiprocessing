# zcbot-multiprocessing（zcbot-mp）

zcbot 的**多进程专版**仓库。品牌仍是 zcbot；单进程版全名 **Zero Creat Bot**（仓库 `kuangxing6367/zcbot`），保持原样、本仓库不改动它。

## 这个仓库做什么

把原本单进程的 zcbot 演进成 **1 个 Core + N 个 Worker** 的多进程运行时：

- **Core**：持有真实数据库、协议接入端、Web/WebUI、全局路由表、Worker 监督器；不执行用户插件。
- **Worker**：执行用户插件、维护本地 hook / 命令注册表，通过 IPC 代理访问 Core 的资源。
- 目标：插件级故障隔离——某个 Worker 崩溃只影响它承载的插件，Core 自动隔离或重启，协议与 Web 不中断。

## 设计文档

- [架构草案](docs/架构草案.md) — 完整设计：定位、进程模型、IPC 1:1 → 1:N、兼容边界、三阶段路径、排除项。
- [架构速写](docs/架构速写.md) — 速写版，便于快速过一遍取舍。

当前状态：**设计阶段**。代码尚未落地，仓库先用于收敛架构与评审。

## 技术参考

原 zcbot 的 `dual_process`（core/host 双进程 + `multiprocessing.connection` JSON-RPC）只作为技术参考：借鉴它验证过的 IPC 边界，不继承它的代码与兼容负担。原仓库继续单进程维护。

## 明确不做

- 跨机分布式集群 / Core 多实例（本仓库只做单机多进程）；
- 安全沙箱（进程隔离不等于安全边界）；
- 改动原 zcbot 仓库。

其余排除项见架构草案第 6 节。

## 许可

MIT，与 zcbot 一致。
