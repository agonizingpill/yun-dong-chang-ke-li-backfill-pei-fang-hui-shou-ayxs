# 屿岸回收料称量

屿岸运动铺装维护队在两块社区运动场回收可再用胶粒。拆补来源登记、1 kg 筛分、粒径配方和逐行称量共同生成可追溯的发料单。补坪班凭单占用现场网格，复核员在各格实铺测厚合格后签开场。

## 班组工作

模拟的 7 人维护队原来用一张电子表追踪回收袋，用手抄筛分单计算不同粒径比例，再由工头核对秤单。筛分表更新会掩盖旧版配方，少量零读数经常被当成真实缺档，领料后旧料余量也容易扣两次。拆补工把旧料装袋入场，检测员记粒径样和杂物，仓管按实秤交给铺装班。场地负责人可以回查每张单用了哪袋料和哪个筛分版本，并查看实际补了哪些格、哪些格返工后才达标。

| 角色 | 演示账号 | 操作 |
|---|---|---|
| 作业员 | `operator@demo.test` | 旧料入场、复筛签单、配方对照、锁料、秤读校验、划格、实铺及测厚 |
| 复核员 | `reviewer@demo.test` | 作业员权限以及发料、退订返还、开场签字 |
| 只读访客 | `viewer@demo.test` | 核查场区、检验版本、称量、扣减与补坪验收记录 |

演示密码均为 `DemoC0de!2026`。

## 启动与环境

```bash
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
```

浏览器打开 `http://localhost:18303`。FastAPI 文档为 `http://localhost:19303/docs`。MySQL 端口为 17803，数据库和用户为 `desk`。日常停止使用 `docker compose down`，带 `-v` 会删除演示库和缓存。

| 服务 | 职责 |
|---|---|
| frontend | Nginx 与原生 HTML/CSS/ES modules |
| backend | Python 3.11、FastAPI、Pydantic、SQLAlchemy |
| worker | Redis 队列、CLR 向量与称量刻度枚举 |
| db | MySQL 8，领域表、外键、事务锁 |
| redis | 排队与计算凭证，计算结果可取用 24 小时 |

`.env.example` 中有容器名前缀 `COMPOSE_PROJECT_NAME`、宿主端口 `FRONTEND_PORT` / `BACKEND_PORT` / `DB_PORT`、`DB_PASSWORD`、`JWT_SECRET` 和启动种子开关 `SEED_DEMO`。开发可在 `backend/` 安装 `requirements.txt` 后运行 `uvicorn core.app:app --port 8000`，设置 `DATABASE_URL`、`REDIS_URL` 和 `JWT_SECRET`，另行运行 `python -m core.worker`。浏览器通过 nginx 同源代理调用 API。

## 一个上午的工作

1. 07:40，现场登记北端边线拆补产生的 `EP-1123-A`，袋批净重 25.500 kg。
2. 08:00，复核 1 kg 筛分纸单 `EP-1123-A-1`，细、中、粗粒分别为 150、630、220 g。
3. 08:20，`EP-1123-B` 含 24 g 杂物，隔离并拒绝入配方。
4. 08:25，`EP-1123-C` 细档读数为零，筛分记录明确是低于检出限。另一个真实缺档的批次隔离。
5. 09:00，将通过的 A、C 两批带入 `YH-NORTH` 的 12.000 kg 配方，检查目标距离和筛分版号。
6. 09:10，保存称量单并使回收袋批重量预占。试填多 50 g 的读数，秤单拒绝。
7. 09:20，每行精确匹配秤读后，由复核员签发。回收料扣减和领料凭证在同一事务落库。
8. 09:35，取消另一张未发称量单，袋批预占归零，实物余量保留。
9. 09:45，补坪班按已发单在北区划出 A1、A2 两格。另一张发料单遇到 A1 占用，可在看板查看哪些网格能划定。
10. 10:05，登记实铺。A1 读到 12、16、14 mm，虽各点在 12–16 mm 内，4 mm 极差超出 2 mm。现场修整后补录同格复测，原读数和签测人可回查。
11. 10:20，A1、A2 的最新读数均合格。复核员签开场并释放这两个格位。发料扣减仍以 09:20 的流水为准。

## 算法

`backend/domain/learning.py` 对剔除杂物后的三个粒径成分闭合。小于 1 g 检出限而记零的档补入 0.5 g，已观测质量按比例缩减，保持样本总质量。真实缺档或零值声明不匹配阻止放行。对于闭合比例 p，逐档取自然对数并减去三个对数的算术平均得到 CLR 向量。

回收袋批和新料按实际整数克数捏合，从场区比例上限和未锁余量可支持的最大回收量起向下，以 50 g 步长搜索。可行配方要求混料 CLR 与目标 CLR 的欧氏距离满足场区阈值。回收量相同优先距离较小，再按已排序批号重量确定性决胜。找不到方案则计算拒绝；更换候选料批后可重算。浏览器展示同一 Python 计算结果。

`intake_tables.py`、`blend_tables.py`、`movements.py` 声明持久化结构。筛分在 `screening.py`，版本校验与锁料在 `planning.py`，审核发料与退订在 `scale.py`。补坪网格、占位和读数存于 `field_tables.py`，工单划定、实铺、测厚、复测及开场签字在 `fieldwork.py`。页面位于 `frontend/src/pages/`。枚举在 `backend/domain/rules.py` 和 `frontend/src/mill-state.js`，筛分、袋批和称量状态亦写入 SQLAlchemy 的 CHECK。角色由 `backend/core/roles.py`、`frontend/src/store.js` 共同定义。

源码使用 MIT 许可，见 `LICENSE`。
