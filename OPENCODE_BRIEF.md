# opencode 续跑简报（每次先读这个）

## 硬约束（不可违反）

1. 这是**新仓库** zcbot-mp，zcbot 原仓库保持单进程且一行不改。
2. 基线是 **zcbot 本来的功能**，在此之上做修改与架构魔改，不是另写一套无关框架。
3. **用户明确要求之前只能打 alpha 版本**：当前 `0.1.0-alpha.0`；禁止 beta / RC / 正式版 / 1.0，
   禁止打非 alpha 的 tag 或 Release。不得自行判断可以升级。
4. 不改 `TASK.md` 里的版本策略与阶段验收标准。
5. 阶段一还没完成前，不要跨阶段动手。

## 当前状态

- 仓库只有文档：`README.md`、`TASK.md`、`docs/架构草案.md`、`docs/架构速写.md`、`VERSION`。
- **尚无任何代码**。阶段一从零开始。

## 阶段一目标（最小可跑）

1 Core + 1 Worker，IPC 跑通，插件 API 最小集。
验收：能收发一条消息；kill worker 后 Core 自动拉起，Web 不中断。

## 本轮任务（只做这一小步）

以 zcbot 双进程的技术思路为参考，落**最小 IPC 信封骨架**，具体：

1. 新建包 `zcbot_mp/`，含 `zcbot_mp/__init__.py` 和 `zcbot_mp/ipc/__init__.py`。
2. 新建 `zcbot_mp/ipc/envelope.py`：定义 JSON-RPC 信封数据结构，
   字段至少 `t`（req/res/event/ping/pong）、`id`、`method`、`params`、`result`、`error`、
   `worker_id`、`route_key`、`request_id`、`seq`、`msg_type`。
   要求：能序列化/反序列化，新字段可缺省（缺省时不破坏老格式），有基本合法性校验。
   **只依赖 Python 标准库**。
3. 新建 `tests/test_envelope.py`：至少 5 个用例，覆盖往返序列化、缺省字段、
   非法字段校验、seq 递增、不同 msg_type。测试用 `pytest`，不许 skip、不许空转。
4. 运行 `python -m pytest tests/test_envelope.py -q`，真跑通过再收工。

## 禁止

- 不读 zcbot 原仓库的源码（太大容易卡）；参考信息以 `docs/架构草案.md` 为准，只读它的前 120 行。
- 不引入第三方依赖，不做网络，不碰数据库，不创建 tag / Release。
- 不改 `TASK.md` 的正文与 `VERSION`、`README.md`；
  **唯一例外**：完成后在 `TASK.md` 的「进度记录」追加一行。

## 完成后

在 `TASK.md` 的「进度记录」追加一行（日期 / 做了什么 / 验收结果 / 当前版本），然后回答一句Done。
