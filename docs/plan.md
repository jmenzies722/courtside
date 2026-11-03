# Courtside roadmap

## How the prediction works
1. **Player agents**: profiles built from real stats (shot mix and accuracy, rim attempts, passing, turnovers, rebounding, defense).
2. **Game simulator**: plays games possession by possession from those profiles. Plain math (Python + NumPy), not AI, so it's fast and cheap.
3. **GM agents**: 30 AI GMs with different strategies make lineup, minutes and trade decisions once per simulated week, through an AI gateway with a budget each.
4. **Monte Carlo**: simulate the season 10,000 times; title odds = share of seasons each team wins.
5. **Backtest**: replay last season from its start, compare with what happened, and publish the Brier score.

Design rule: AI makes decisions and writes recaps; it is never inside the 10,000-season loop.

## Tech stack
| Layer | Tech |
|---|---|
| Services | Python, FastAPI, WebSockets / SSE |
| Web | Next.js on CloudFront |
| Sim | Python + NumPy as Kubernetes Jobs, autoscaled with KEDA |
| Data | Postgres (RDS), Redis (ElastiCache), S3 |
| Messaging | SQS with dead-letter queues, EventBridge schedules |
| AI | Amazon Bedrock behind an AI gateway (keys, budgets, caching, fallback) |
| AI quality | Evals in CI, prediction backtests |
| Infra | Terraform (dev + prod), EKS, Karpenter, Helm |
| Delivery | GitHub Actions (OIDC), ECR, ArgoCD, Argo Rollouts |
| Security | Kyverno, IRSA / Pod Identity, KMS, Trivy, cosign |
| Observability | OpenTelemetry, Prometheus, Loki, Tempo, Grafana |
| On-call | SLOs as code, burn-rate alerts, PagerDuty, runbooks |
| Resilience | k6 load tests, AWS FIS chaos |

## Phases
### Part A: platform (Nov 2026 - Jan 2027)
- [ ] Ingest worker + GitHub Actions OIDC pipeline to ECR
- [ ] Canary deploys locally (kind + Argo Rollouts)
- [ ] Terraform modules: VPC + EKS, dev and prod
- [ ] SQS + stats engine + Redis, deployed with Helm
- [ ] ArgoCD GitOps + Kyverno policies
- [ ] OpenTelemetry + Grafana stack, freshness and latency SLOs as code
- [ ] Burn-rate alerts to PagerDuty + runbooks
- [ ] Chaos: data feed outage mid-game, node loss at tip-off
- [ ] Architecture diagram + first ADRs

### Part B: agent league (Feb - Mar 2027)
- [ ] Player agents + possession-level game sim
- [ ] 10,000-season Monte Carlo as parallel Jobs
- [ ] 30 GM agents with tools and explanations
- [ ] Agent safety rails: timeouts, retries, max steps, budgets, fallback model, DLQ
- [ ] AI gateway
- [ ] Evals in CI + backtested accuracy

### Part C: platform for engineers (Apr - May 2027)
- [ ] Golden path `new-service` template
- [ ] DORA metrics dashboard
- [ ] Scale and cost: Karpenter, spot, OpenCost

### Part D: prove it (Jun - Jul 2027)
- [ ] k6 load: normal night, Christmas Day, playoff spike
- [ ] Game days with AWS FIS + postmortems
- [ ] Security review
- [ ] Public beta + accuracy scorecard

## Cost rules
- Budget alarms at $10 / $20 / $50.
- Build locally first; AWS only on lab days (`make up` / `make down`).
- AI calls only through the gateway with a hard monthly cap.
