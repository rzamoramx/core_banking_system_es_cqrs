package main

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"io"
	"log"
	"net/http"
	"os"
	"runtime/debug"

	dapr "github.com/dapr/go-sdk/client"
	"github.com/gorilla/mux"
	"ivansoft.com/corebank/eventsource/store/models"
)

const (
	stateStoreName = "eventstore"
	pubsubName     = "eventsource"
	topic          = "transactions"
	route          = "/transactions/subscriber/v1/handler"
	version        = "transaction.v1"
)

func main() {
	// Define a command-line flag for the port
	appPort := flag.String("port", "6005", "Port for the application to listen on")
	flag.Parse()

	// Create a Dapr client
	client, err := dapr.NewClient()
	if err != nil {
		log.Printf("Failed to create Dapr client: %v", err)
		os.Exit(1)
	}
	defer client.Close()

	r := mux.NewRouter()

	// Programmatic subscription, instead declarative way (pubsub component yaml file in Dapr directory)
	// Handle the /dapr/subscribe route which Dapr invokes to get the list of subscribed endpoints
	r.HandleFunc("/dapr/subscribe", toSubscribe).Methods("GET")

	// Dapr subscription routes transactions topic to this route
	r.HandleFunc("/transactions/subscriber/v1/handler", eventHandler(client, context.Background())).Methods("POST")

	// Start the server; this is a blocking call
	log.Printf("Starting server on port %s", *appPort)
	srv := &http.Server{
		Addr:    ":" + *appPort,
		Handler: recoverMiddleware(r),
	}

	if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Printf("HTTP server error: %v", err)
	}
}

func recoverMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				log.Printf("Panic recovered: %v\nStack trace:\n%s", err, debug.Stack())
				http.Error(w, "Internal server error", http.StatusInternalServerError)
			}
		}()
		next.ServeHTTP(w, r)
	})
}

func eventHandler(client dapr.Client, ctx context.Context) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		data, err := io.ReadAll(r.Body)
		if err != nil {
			log.Printf("Error: reading request body: %v", err)
			http.Error(w, "Error: reading request body", http.StatusBadRequest)
			return
		}

		var e models.Result
		err = json.Unmarshal(data, &e)
		if err != nil {
			log.Printf("Error: unmarshalling event data: %v", err)
			http.Error(w, "Error: unmarshalling event data", http.StatusBadRequest)
			return
		}
		log.Printf("Event received: %+v\n", e)

		// Parse e.Data into a map
		var dataMap map[string]interface{}
		err = json.Unmarshal([]byte(e.Data), &dataMap)
		if err != nil {
			log.Printf("Error: parsing event data: %v", err)
			http.Error(w, "Error: parsing event data", http.StatusInternalServerError)
			return
		}

		// Create a new map with accountId as the key
		accountId, ok := dataMap["account_id"].(string)
		if !ok {
			log.Printf("Error: accountId not found or not a string")
			http.Error(w, "Error: accountId not found or not a string", http.StatusInternalServerError)
			return
		}

		// Convert event object to JSON
		eventJSON, err := json.Marshal(dataMap)
		if err != nil {
			log.Printf("Error: marshalling event object: %v", err)
			http.Error(w, "Error: marshalling event object", http.StatusInternalServerError)
			return
		}

		// Save event to state store
		if err := client.SaveState(ctx, stateStoreName, accountId, eventJSON, nil); err != nil {
			log.Printf("Error: saving state: %v", err)
			http.Error(w, "Error: saving event", http.StatusInternalServerError)
			return
		}
		log.Printf("Event saved with accountID: %s\n", accountId)

		// Get the event to confirm it was saved
		resp, err := client.GetState(ctx, stateStoreName, accountId, nil)
		if err != nil {
			log.Printf("Error: getting state: %v", err)
			http.Error(w, "Error: getting event", http.StatusInternalServerError)
			return
		}
		log.Printf("Event saved retrieved: %s\n", string(resp.Value))

		// print accountID as byte
		log.Printf("AccountID: %s\n", accountId)

		w.WriteHeader(http.StatusOK)
		if _, err := w.Write([]byte("Event saved")); err != nil {
			log.Printf("Error writing response: %v", err)
		}
	}
}

func toSubscribe(w http.ResponseWriter, r *http.Request) {
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
