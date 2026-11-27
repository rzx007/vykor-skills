# 数字员工远程 API

数字员工服务的访问地址是 [https://bobanstaff.bobandata.com/](https://bobanstaff.bobandata.com/)。模型服务的 Base URL 由登录后获取的模型配置提供，见[模型目录](#模型目录)。

应用通过远程服务登录、读取模型目录、查积分和办理充值。应用需要 Agent 时，将当前账号的模型目录和模型连接交给 Nomi SDK。用户在应用内选模型并发送消息。

本模块依据仓库维护的 `docs/research/digital-employee-account-billing/`，字段核对基线是 `cd58f1d58a0ecf9f260de88d19f54ae251949937`（2026-11-12）。使用其他部署环境时，按该环境提供的域名和发布前缀接入。登录方式和支付规则以所用环境为准。资料记录了源码中的请求和响应，真实环境联调仍待确认。

## 地址和凭证

| 服务 | 地址和路径 | 凭证 |
| --- | --- | --- |
| 远程账号服务 | 环境提供的账号服务地址，加 `/api/v2/portal/auth/…` 或 `/api/v2/auth/…` | 登录后在受保护请求中提供账号访问令牌 |
| 远程业务服务 | 环境提供的业务服务地址，加 `/digital/api/v1/…` | 账号访问令牌 `access_token` |
| 远程模型服务 | 模型配置返回的 `apiUrl`，加 `/models` | 同次配置返回的模型 `apiKey` |
| Nomi daemon | 应用传给 Client 的 `baseUrl` | daemon `token` 或 AppHost 提供的会话连接 |

受保护 HTTP 请求使用 `Authorization: Bearer <对应凭证>`，JSON 请求设置 `Content-Type: application/json`。账号服务部分部署还有额外发布前缀，以实际完整地址为准。账号凭证由应用后台持有，模型连接按需交给 SDK。

## 登录

| 操作 | 方法和远程路径 | 请求和结果 |
| --- | --- | --- |
| 查询登录能力 | GET `/api/v2/portal/auth/capabilities` | `data.providers` 和 `client_capabilities` 告知可用方式，可能含 `desktop_authorization_url` |
| 密码登录 | POST `/api/v2/portal/auth/sessions/password` | JSON 为 `identifier` 和 `password`，可选渠道身份字段，返回令牌或注册继续步骤 |
| 发送验证码 | POST `/api/v2/portal/auth/verification-challenges` 或 `/api/v2/auth/verification-challenges` | JSON 为 `phone`、`purpose: "phone_login"`、`client_type`，返回 `challenge_id` 和 `expires_in` |
| 手机号登录 | POST `/api/v2/portal/auth/sessions/phone` 或 `/api/v2/auth/sessions/phone` | JSON 为 `phone`、`code`、`challenge_id` 和 `client_type`，可选渠道身份字段，返回令牌或注册继续步骤 |
| 读取当前账号 | GET `/api/v2/portal/auth/me` 或 `/api/v2/auth/me` | 携带账号访问令牌，从 `data.id` 取得当前用户 ID |
| 刷新会话 | POST `/api/v2/portal/auth/refresh` | JSON 为 `{ "refresh_token": "…" }`，返回新令牌 |
| 退出会话 | POST `/api/v2/portal/auth/logout` | JSON 为 `{ "refresh_token": "…" }`，成功回包的 `data` 结构待确认 |

登录、发送登录验证码和读取登录能力可在取得访问令牌前调用。刷新和退出使用请求正文里的刷新凭证。完整账号的 `/me` 可返回 `permissions`，门户接口的字段覆盖以目标环境为准。

验证码用字符串保存，保留前导零。验证码接口可能返回 `emergency_code`，收到 429 可读取 `Retry-After`。除了 `phone_login`，原文还记录了 `password_reset`、`change_phone_current`、`change_phone_new`、`set_password`、`delete_account`。`client_type` 由接入环境确定，已有调用使用 `web` 或 `desktop`。可选的 `registration_role` 和 `registration_personnel_type` 按渠道配置成对传入。

账号响应使用 `{code,msg,data}`，现有令牌调用检查数字 `code === 1`。令牌数据包含 `access_token`、`refresh_token` 和以秒计的 `expires_in`，可选 `token_type` 已使用 `bearer`。若 `data.next_step === "accept_terms"`，使用返回的 `registration_token`、`legal_documents` 和邀请码要求完成注册。继续凭证的期限见 `expires_in`。

| 协议与注册 | 方法和远程路径 | 请求和结果 |
| --- | --- | --- |
| 当前协议版本 | GET `/api/v2/auth/legal-documents/current` | 返回 `data.documents`，包含 `document_type`、`title`、`version`、`effective_at`、`sha256`、`content_url` |
| 指定版本协议 | GET `/api/v2/auth/legal-documents/{document_type}/{version}` | 返回协议 HTML |
| 完成协议注册 | POST `/api/v2/auth/registrations` | 用户确认后提交 `registration_token`、`display_name`、`client_type` 和 `accepted_documents`，有要求时带 `invitation_code`，支持渠道身份字段 |
| 用户名注册 | POST `/api/v2/auth/registrations/username` | 提交 `username`、`password`、`client_type` 和 `accepted_documents`，支持渠道身份字段，按登录结果解析响应 |

`accepted_documents` 的每项都传用户实际看过的 `document_type`、`version` 和 `sha256`。登录能力的 `client_capabilities.username_registration` 和 `registration_invitation_required` 会告知注册是否开放和是否要求邀请码。

飞书和微信走 `GET /api/v2/auth/oauth/{provider}/authorize` 与 `POST /api/v2/auth/oauth/{provider}/exchange`，`provider` 为 `feishu` 或 `wechat`。授权查询提供 `code_challenge`、`code_challenge_method=S256`、`session_nonce` 和 `origin`，返回 `authorize_url` 和 `state`。换票提交 `code`、`state`、`code_verifier` 和 `session_nonce`。若返回 `next_step: "bind_phone"`，向 `POST /api/v2/auth/oauth/{provider}/phone-bindings/verification-challenges` 提交 `binding_token`、`phone` 和 `client_type`。提交绑定时向 `POST /api/v2/auth/oauth/{provider}/phone-bindings` 发送 `binding_token`、`phone`、`client_type`、`challenge_id` 和验证码 `code`，返回令牌或 `accept_terms`。门户授权也可通过 `POST /api/v2/portal/auth/desktop/token` 提交 `code`、`state`、`code_verifier` 换票。

### 账号维护

| 操作 | 方法和远程路径 | 凭证和请求 JSON |
| --- | --- | --- |
| 修改资料 | PATCH `/api/v2/portal/auth/me` 或 `/api/v2/auth/me` | 账号 Bearer，提交 `username`、`display_name`、`email`，后两项可为 `null` |
| 修改或设置密码 | PUT `/api/v2/portal/auth/me/password` | 账号 Bearer，提交 `password`，按账号状态提供 `current_password` |
| 找回密码 | POST `/api/v2/auth/password-resets` | 用 `password_reset` 用途获取验证码，提交 `phone`、`code`、`challenge_id`、`password` 和 `client_type` |
| 注销账号 | DELETE `/api/v2/auth/me` | 账号 Bearer，使用 `delete_account` 用途的验证码，提交 `phone`、`code`、`challenge_id`、`client_type` 和 `confirmation: "注销账号"` |

## 模型目录

1. 用账号访问令牌请求 `GET /digital/api/v1/model/provider`。个人请求显式传 `billing_scope=personal` 或省略查询参数。企业请求传 `billing_scope=enterprise&enterprise_id=<企业ID>`。读取响应 `{code,msg,data}` 中的 `data.apiUrl`、`data.apiKey` 和默认模型 `data.modelName`。个人配置核对 `ownerUserId` 和 `isActive`。原企业调用检查配置已启用、必要字段有效且 key 以 `ent_` 开头，正式凭证规则按目标环境确认。
2. 用同次配置的 `apiKey` 请求 `GET {apiUrl}/models`，保留基础路径，例如 `/v1`。示例读取 `{"data":[{"id":"example-chat","display_name":"示例模型"}]}`。原通用解析还接受顶层数组或 `models` 数组，认字符串项或对象的 `id`、`name`、`model`。需要展示能力时读取可选的 `capabilities.supports_vision`、`supports_reasoning`、`max_input_tokens`、`context_window` 等。模型目录请求返回 401 或 403 时，核对模型 key 和服务权限。资费以计费服务为准。
3. 用模型 ID、显示名和需要的能力生成 `models`，把同一账号的 `apiUrl` 和 `apiKey` 配成供应商的 `connection`。一起传给 `BobanNomiClient`。模型选项从 `client.models.list()` 取得。应用切换账号时取消旧请求，按新账号重建 Client。
4. 用选项的供应商 `name` 和模型 `id` 设置 `configuration.model`。调用 `session.prompt()` 发消息，以 `session.waitForRun()` 读取结果。Nomi 用应用提供的模型连接执行。 [会话示例](./test-model.md)

### 把远程模型交给 SDK

下面的 `remoteModels` 是应用已取得的模型列表，`loadModelConnection` 按当前登录返回 `{ baseUrl: apiUrl, apiKey, apiFormat: "openai" }`。`clientOptions` 由 AppHost 的 `host.getAuthorizedAgentConnection()` 提供。

```js
import { BobanNomiClient } from "@bobannomi/client"

const providerId = "digital-employee"
const providerName = "数字员工"
const providers = [{
  name: providerId,
  displayName: providerName,
  models: remoteModels.map(({ id, display_name, name }) => ({
    id,
    label: display_name ?? name ?? id,
    provider: providerName,
    providerName: providerId,
  })),
  connection: ({ signal }) => loadModelConnection({ signal }),
}]

const client = new BobanNomiClient({ ...clientOptions, providers })
```

## 积分

以下路径都以 `/digital/api/v1` 开头，使用账号访问令牌。积分类响应读取 `{code,msg,data}`，原调用支持成功 `code` 为 `1`、`200` 或对应字符串。金额和积分的十进制字符串按原精度保存。

| 操作 | 方法和相对路径 | 请求和结果 |
| --- | --- | --- |
| 积分余额 | GET `/credits/account` | `balancePoints`、`hasRecharged`、可选 `buckets`。每个来源有 `id`、`name`、`totalPoints`、`balancePoints`、`expiresAt`（可为 `null`） |
| 消耗汇总或明细 | GET `/credits/usage` | `startDate`、`endDate`（`YYYY-MM-DD`）、`view`（`conversations`、`tasks` 或 `records`）、`page`、`pageSize`。可选 `userId`、`conversationId`、`taskId`，`taskId=unassigned` 表示无关联分组。返回 `summary`、`items`、`total` 和分页字段 |
| 消耗查询人员 | GET `/credits/people` | query 为 `q` 和 `page`。返回人员 `items`、`total` 和分页字段 |
| 每日登录奖励 | POST `/credits/daily-login` | 无请求正文，返回 `granted`、`rewardDate`、`rewardPoints` |
| 企业成员身份 | GET `/auth/my-enterprises` | 返回 `enterprise_id`、`enterprise_name`、`membership_id`、`role`、`enterprise_status`、`membership_status` |
| 企业额度 | GET `/enterprises/{enterpriseId}/billing/me` | 返回 `account_status`、`subscription_status`、`subscription_expires_at`、`limit_credits`、`used_credits`、`held_credits`、`remaining_credits`、`mode`（`inherit` 或 `override`）、`version`、`resets_at` |
| 邀请活动和汇总 | GET `/invitations/mine` | 返回 `campaigns` 和 `summary` |
| 生成邀请链接 | POST `/invitations/mine/{campaignId}` | 无请求正文，返回 `campaigns` 和 `summary` |
| 邀请奖励记录 | GET `/invitations/mine/rewards` | query 为 `page`、`page_size`，返回 `items` 和 `total` |

## 充值

同样使用业务服务的 `/digital/api/v1` 前缀和账号访问令牌。

| 操作 | 方法和相对路径 | 请求和结果 |
| --- | --- | --- |
| 查看可用方式 | GET `/credits/recharge-options` | `enabled`、`pointsPerYuan`、`feeRate`、`presets`，每个 `methods` 项有 `id`、`name`、`minAmount` 和 `maxAmount` |
| 查看积分包 | GET `/credits/recharge-products` | 返回 `pointsPerYuan` 和 `products`，每个产品含 `id`、`name`、`description`、`priceCny`、`basePoints`、`bonusPoints`、`totalPoints`、`sortOrder`、`version` |
| 创建订单 | POST `/credits/orders` | 提交每次购买的 UUID `requestId` 和 `paymentMethod`（`alipay` 或 `wxpay`）。购买参数二选一，自定义金额传十进制字符串 `amount`，固定积分包传 `productId` 和数字 `productVersion` |
| 订单列表 | GET `/credits/orders` | query 为 `page`、`pageSize`，返回 `items`、`total` 和分页字段 |
| 查原订单 | GET `/credits/orders/{orderId}` | 返回同一订单的支付与入账状态 |
| 取消原订单 | POST `/credits/orders/{orderId}/cancel` | 无请求正文，返回订单状态 |

先读取充值开关、支付方式和产品版本，用户确认后再下单。以下是固定积分包和自定义金额的示例正文。

```json
{
  "requestId": "00000000-0000-4000-8000-000000000001",
  "paymentMethod": "alipay",
  "productId": "example-product",
  "productVersion": 3
}
```

```json
{
  "requestId": "00000000-0000-4000-8000-000000000002",
  "paymentMethod": "wxpay",
  "amount": "37.50"
}
```

### 订单回包

创建、查询和取消返回同一种订单对象。用返回的 `id` 查询或取消原订单。

| 字段 | 含义 |
| --- | --- |
| `id`、`status`、`paymentMethod` | 订单 ID、服务端状态和实际支付方式 |
| `payAmount`、`currency`、`points` | 实际支付金额、币种和订单总积分，金额和积分使用十进制字符串 |
| `product`、`basePoints`、`bonusPoints` | 可选且可为 `null`，分别为产品快照、基础积分和赠送积分 |
| `createdAt`、`expiresAt`、`completedAt` | 创建、支付截止和入账时间，`completedAt` 可为 `null` |
| `qrImage`、`paymentUnavailable` | 可为 `null` 的支付二维码图片，以及当前支付是否不可用 |

### 订单状态

| `status` | 原文含义 | 应用处理 |
| --- | --- | --- |
| `pending` | 待支付 | 查询原订单。付款码存在、支付可用且仍在有效期内时展示付款码 |
| `processing` | 支付成功，正在入账 | 继续查原订单，提示正在入账 |
| `completed` | 已到账 | 显示到账并刷新积分余额 |
| `expired` | 已过期 | 停用原付款码 |
| `cancelled` | 已取消 | 显示取消结果 |
| `failed` | 订单异常 | 提示异常，保留订单 ID 供核对 |
| `refunding` | 退款处理中 | 提示退款处理中，可查询同一订单 |
| `refunded` | 已退款 | 展示退款结果，当前积分以余额为准 |
| `partially_refunded` | 部分退款 | 展示部分退款，以远程订单和余额核对结果 |
| `refund_failed` | 退款异常 | 提示异常，保留订单 ID 供核对 |

工作台只对 `pending` 和 `processing` 自动查询，遇到未知状态提示「订单状态待确认」并保留手动查询。付款码缺失、`paymentUnavailable` 为 `true` 或本地显示已到截止时间时，停用付款入口并重查原订单，订单状态仍取远程返回值。取消和支付同时发生时，以远程查询为准。退款状态用于展示，发起退款的端点和状态转换仍需向远程服务确认。

下单回包丢失时保留原 `requestId` 和购买参数，若需重试沿用原值。已知 `orderId` 时直接查询原订单。上线前确认服务端对 `requestId` 的去重范围、期限、参数冲突及到账一次性的保证。
