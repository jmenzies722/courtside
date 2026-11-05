# Glossary

Plain-English definitions, added as we learn them.

## Git
| Term | Meaning |
|---|---|
| Commit | A saved snapshot of the whole project, with an ID |
| Branch | A label that moves forward with each new commit |
| Tag | A label that never moves; marks one exact version |
| Remote (`origin`) | The copy on GitHub; the only backup |
| Staging area | Changes chosen for the next commit |
| PR | A request to merge a branch, with review |

## Reliability
| Term | Meaning |
|---|---|
| SLO | A reliability promise with a number, e.g. "scores under 10 s behind" |
| Golden signals | Latency, traffic, errors, saturation: the 4 health checks for any service |
| Blast radius | How much breaks when one thing fails |
| Alert fatigue | Ignoring alerts because too many fire without needing action |
| Escalation | Alerts that get louder as the problem gets worse |

## Architecture
| Term | Meaning |
|---|---|
| Microservice | A small program with one job that talks to others over the network |
| Monolith | One program that does everything |
| Contract | The agreed data shape services use to talk |
| Queue | A waiting line for events, so nothing is lost if a consumer is down |

## Code
| Term | Meaning |
|---|---|
| Exception | An error that stops code unless something catches it |
| `try` / `except` | Attempt something; handle a specific error if it happens |
| `continue` | Skip to the next item in a loop |
