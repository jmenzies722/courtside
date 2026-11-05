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
| `services/ingest` | Fetch live game data, send events to a queue | Planned (L3-1) |
| `services/stats` | Turn events into scores, box scores, win odds | Planned |
| `services/api` | Serve the website (REST + live updates) | Planned |
| `services/sim` | Simulate seasons, produce title odds | Planned |
| `web` | The site fans see | Planned |

## SLOs (reliability promises)

- **Freshness:** live scores are no more than 10 seconds behind the real game.
- **Latency:** the API answers in under 300 ms (p95).

## Run it locally

Coming in L3-1.

## Status

Rebuilding from scratch (Nov 2026). The first version is preserved at tag `v0-reference`.

*Personal project. Not affiliated with or endorsed by the NBA. Predictions are for entertainment, not betting advice.*
