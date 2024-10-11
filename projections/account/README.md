# Core banking system rest API for clients like mobile apps #

According to CQRS pattern, this API is a projection of the core banking system. Specifically
this handle reads for clients like mobile apps (transactions, user accounts, etc).

For transactions, this projection are subscribed to transactions topic of the event sourcing system and store
the transactions in own database. It exposes a REST API (fastapi) to get transactions by account id.

## Dependencies ##

- Python 3.12 or higher
- poetry

Run this command to install dependencies:

```poetry install```

Also is required to subscribe in a declarative way to a Dapr pubsub component, using scopes in pubsub.yaml file.
where a scope is an app ID when we run the Dapr app (next section "Run").

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: transactions
spec:
    type: pubsub.redis
    metadata:
    - name: redisHost
        value: "redis://localhost:6379"
    - name: redisPassword
        value: ""
scopes:
  - clientsapi
```


## Run ##

```dapr run --app-id clientsapi --resources-path ./myComponents -- python3 app.py```