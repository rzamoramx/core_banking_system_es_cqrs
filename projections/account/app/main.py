import json
from fastapi import FastAPI, Response
from app.api.eventsource.v1.subscribers import router as subscriber_handlers

app = FastAPI()
# Include routers
app.include_router(subscriber_handlers, prefix="/mybank/subscriber/v1")

# Register Dapr pub/sub subscriptions for this projection app (CQRS pattern)
# this endpoint is called by Dapr runtime to get the list of topics to subscribe (programmatic subscription)
# there is another way to subscribe to a topic, by adding scope in yaml file for pubsub component (declarative subscription)
#
# You can only subscribe to one route to one topic, so you can't subscribe to the same topic with different routes.
#
# In context of CQRS pattern and projections, you can handle multiple projections in the same microservice whenever its
# are related maintaining coherence between them. Even you can separate them in different microservices if you need to
# scale them independently this decision depends on the business requirements and the complexity of the domain. In this
# example, we are handling two projections in the same microservice.
@app.get('/dapr/subscribe')
def subscribe():
    subscriptions = [
        {
            'pubsubname': 'eventsource',
            'topic': 'transactions',
            'route': '/mybank/subscriber/v1/account_projections/handler'
        }]
    print(f'Subscribing... : {subscriptions}')
    return Response(content=json.dumps(subscriptions), media_type='application/json')


# ping route
@app.get("/")
async def ping():
    return {"message": "pong"}


if __name__ == "__main__":
    import uvicorn
    print('running account projections on port 8000')
    uvicorn.run(app, host="0.0.0.0", port=8000)
