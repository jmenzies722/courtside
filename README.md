# Courtside

Courtside is a live NBA game center with real-time scores and win odds, plus an AI league that predicts the champion.

Built like production: Terraform, Kubernetes, GitOps, SLOs, on-call, and chaos testing, with cost and safety controls on every AI call.

## How it works

```
LIVE:          NBA data -> ingest -> SQS -> stats -> Redis/Postgres -> api -> web
AGENT LEAGUE:  player agents + 30 AI GMs -> AI gateway -> Bedrock
               season simulator -> 10,000 seasons -> title odds -> checked vs reality

Delivery:      GitHub Actions (OIDC) -> ECR -> ArgoCD -> Argo Rollouts canary
Signals:       OpenTelemetry -> Prometheus / Loki / Tempo -> Grafana -> SLO alerts -> PagerDuty
```

## Services

| Service | Job | Status |
|---|---|---|
| `services/ingest` | Fetch live game data (ESPN or fake `sim` feed), send events to a queue | Walking skeleton |
| `services/stats` | Turn events into scores, box scores, win odds | Planned |
| `services/api` | Read the queue, keep newest per game, stream live updates (SSE) | Walking skeleton |
| `services/sim` | Simulate seasons, produce title odds | Planned |
| `web` | Next.js live scoreboard with freshness SLO indicator | Walking skeleton |

## SLOs (reliability promises)

- **Freshness:** live scores are no more than 10 seconds behind the real game.
- **Latency:** the API answers in under 300 ms (p95).

## Run it locally

Needs Docker, [uv](https://docs.astral.sh/uv/) and Node. Four terminals:

```bash
make sqs                 # local queue (ElasticMQ), UI at http://localhost:9325
make ingest SOURCE=sim   # fake live games (or SOURCE=espn for real ones)
make api                 # API at http://localhost:8000
make web                 # scoreboard at http://localhost:3000
```

`make test` runs every test. `make down` stops the queue.

## Status

Rebuilding from scratch (Nov 2026). The first version is preserved at tag `v0-reference`.

*Personal project. Not affiliated with or endorsed by the NBA. Predictions are for entertainment, not betting advice.*
