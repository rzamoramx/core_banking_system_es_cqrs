package handlers

import (
	"encoding/json"
	"log"
	"net/http"

	"ivansoft.com/corebank/eventsource/store/models"
)

const (
	pubsubName = "eventsource"
	topic      = "transactions"
	route      = "/transactions/subscriber/v1/handler"
	version    = "transaction.v1"
)

func ToSubscribe(w http.ResponseWriter, r *http.Request) {
	t := []models.SubscriptionObj{
		{
			PubsubName: pubsubName,
			Topic:      topic,
			Routes: models.Routes{
				Rules: []models.Rule{
					{
						Match: `event.type == "` + version + `"`,
						Path:  route,
					},
				},
				Default: route,
			},
		},
	}

	jsonBytes, err := json.Marshal(t)
	if err != nil {
		log.Printf("Error marshalling subscription data: %v", err)
		http.Error(w, "Error processing subscription data", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if _, err := w.Write(jsonBytes); err != nil {
		log.Printf("Error writing response: %v", err)
	}
}
