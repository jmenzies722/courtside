# Courtside

Live NBA game center + an AI agent league that simulates seasons to predict the real NBA champion. Built like production: Terraform, EKS, GitOps, SLOs, on-call and chaos.

```
LIVE:          NBA data -> ingest -> SQS -> stats engine -> Redis/Postgres -> live scores, win odds, alerts
AGENT LEAGUE:  player agents (real stats) + 30 AI GMs -> AI gateway -> Bedrock
               season simulator -> 10,000 seasons -> title odds -> checked vs reality

Delivery:  GitHub Actions (OIDC, no stored keys) -> ECR -> ArgoCD -> Argo Rollouts canary
Signals:   OpenTelemetry -> Prometheus / Loki / Tempo -> Grafana -> SLO burn alerts -> PagerDuty
```

## Layout
| Folder | What lives there |
|---|---|
| `services/ingest` | Pulls live NBA game data, pushes events to SQS |
| `services/stats` | Turns events into scores, box scores, win odds |
| `services/api` | FastAPI for the web app (REST + live updates) |
| `services/sim` | Player agents, game simulator, Monte Carlo seasons |
| `web` | Next.js front end |
| `infra` | Terraform modules and dev/prod environments |
| `deploy` | Helm charts and ArgoCD apps |
| `docs` | Plan, architecture decisions (ADRs), runbooks |

## SLOs (targets)
- **Freshness:** live scores are no more than 10 seconds behind the real game.
- **Latency:** API answers in under 300 ms (p95).

## Status
Week 1 (Nov 7, 2026): ingest worker + OIDC pipeline to ECR. Full roadmap in [docs/plan.md](docs/plan.md).

*Personal project. Not affiliated with or endorsed by the NBA. Predictions are for entertainment, not betting advice.*
