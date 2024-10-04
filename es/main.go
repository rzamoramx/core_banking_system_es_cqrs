package main

import (
	"errors"
	"flag"
	"log"
	"net/http"
	"runtime/debug"

	"github.com/gorilla/mux"

	"ivansoft.com/corebank/eventsource/store/db"
	"ivansoft.com/corebank/eventsource/store/handlers"
)

func main() {
	// Define a command-line flag for the port
	appPort := flag.String("port", "6005", "Port for the application to listen on")
	flag.Parse()

	// Create Immudb client
	immudbClient, err := createDbClient()
	if err != nil {
		log.Fatalf("Failed to create Immudb client: %v", err)
	}
	defer immudbClient.Close()

	r := mux.NewRouter()

	// Programmatic subscription, instead declarative way (pubsub component yaml file
	// in Dapr directory). Handle the /dapr/subscribe route which Dapr invokes to get
	// the list of subscribed endpoints
	r.HandleFunc("/dapr/subscribe",
		handlers.ToSubscribe).Methods("GET")

	// Dapr subscription routes transactions topic to this route
	r.HandleFunc("/transactions/subscriber/v1/handler",
		handlers.SaveEvent(immudbClient)).Methods("POST")

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

func createDbClient() (*db.Immudb, error) {
	// TODO: retrieve host, port, user, password, and database from env file

	immudbClient, err := db.NewImmudb("localhost", 3322, "immudb", "immudb1", "eventsourcedb")
	if err != nil {
		log.Fatalf("Failed to create Immudb client: %v", err)
	}
	return immudbClient, nil
}
