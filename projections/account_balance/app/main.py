import json
from fastapi import FastAPI, Response
from app.api.eventsource.v1.transaction_subscriber import router as transaction_subscriber_handler
from app.api.routes.v1.balance_handlers import router as balance_handler

app = FastAPI()
# Include routers
app.include_router(transaction_subscriber_handler, prefix="/projectionbalance/subscriber/v1")
app.include_router(balance_handler, prefix="/projectionbalance/api/v1")

# Register Dapr pub/sub subscriptions for this projection(pattern) app, in context of CQRS pattern
# this endpoint is called by Dapr runtime to get the list of topics to subscribe to
@app.get('/dapr/subscribe')
def subscribe():
    subscriptions = [{
        'pubsubname': 'eventsource',
        'topic': 'transactions',
        'route': '/projectionbalance/subscriber/v1/handler'
    }]
    print(f'Subscribing... : {subscriptions}')
    return Response(content=json.dumps(subscriptions), media_type='application/json')


# ping route
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI application"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
