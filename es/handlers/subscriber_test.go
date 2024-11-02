package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"ivansoft.com/corebank/eventsource/store/models"
)

func TestToSubscribe(t *testing.T) {
	// Create request
	req := httptest.NewRequest(http.MethodGet, "/dapr/subscribe", nil)
	w := httptest.NewRecorder()

	// Call handler
	ToSubscribe(w, req)

	// Assert response status
	assert.Equal(t, http.StatusOK, w.Code)

	// Assert Content-Type header
	assert.Equal(t, "application/json", w.Header().Get("Content-Type"))

	// Parse response body
	var subscriptions []models.SubscriptionObj
	err := json.NewDecoder(w.Body).Decode(&subscriptions)
	assert.NoError(t, err)

	// Assert subscription details
	assert.Len(t, subscriptions, 1)
	subscription := subscriptions[0]

	// Check pubsub name
	assert.Equal(t, pubsubName, subscription.PubsubName)

	// Check topic
	assert.Equal(t, topic, subscription.Topic)

	// Check routes
	assert.Equal(t, route, subscription.Routes.Default)
	assert.Len(t, subscription.Routes.Rules, 1)

	// Check rule
	rule := subscription.Routes.Rules[0]
	assert.Equal(t, `event.type == "transaction.v1"`, rule.Match)
	assert.Equal(t, route, rule.Path)
}

func TestToSubscribeErrorCase(t *testing.T) {
	// Create a request with a method that would trigger the error case
	req := httptest.NewRequest(http.MethodPost, "/dapr/subscribe", nil)
	w := httptest.NewRecorder()

	// Call handler
	ToSubscribe(w, req)

	// Even with POST method, it should still return OK as the handler doesn't check method
	assert.Equal(t, http.StatusOK, w.Code)

	// Verify the response is still valid JSON
	var subscriptions []models.SubscriptionObj
	err := json.NewDecoder(w.Body).Decode(&subscriptions)
	assert.NoError(t, err)
}
