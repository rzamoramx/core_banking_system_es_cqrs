package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"runtime/debug"
	"strconv"

	"github.com/gorilla/mux"

	"ivansoft.com/corebank/eventsource/store/db"
	"ivansoft.com/corebank/eventsource/store/handlers"
)

type Config struct {
	Immudb struct {
		Host     string `json:"host"`
		Port     int    `json:"port"`
		User     string `json:"user"`
		Password string `json:"password"`
		Database string `json:"database"`
	} `json:"immudb"`
}

func main() {
	// Load configuration and set environment variables
	if err := loadConfigToEnv(); err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

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
	host := os.Getenv("IMMUDB_HOST")
	port, _ := strconv.Atoi(os.Getenv("IMMUDB_PORT"))
	user := os.Getenv("IMMUDB_USER")
	password := os.Getenv("IMMUDB_PASSWORD")
	database := os.Getenv("IMMUDB_DATABASE")

	immudbClient, err := db.NewImmudb(host, port, user, password, database)
	if err != nil {
		return nil, err
	}

	log.Printf("Successfully connected to Immudb at %s:%d", host, port)
	return immudbClient, nil
}

func loadConfig() (*Config, error) {
	file, err := os.Open("config-dev.json")
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var config Config
	decoder := json.NewDecoder(file)
	err = decoder.Decode(&config)
	if err != nil {
		return nil, err
	}

	return &config, nil
}

func loadConfigToEnv() error {
	// if not set ENV variable, by default use config-dev.json, otherwise use environment variables
	if os.Getenv("ENV") == "" || os.Getenv("ENV") == "dev" {
		config, err := loadConfig()
		if err != nil {
			return fmt.Errorf("failed to load config: %w", err)
		}

		os.Setenv("IMMUDB_HOST", config.Immudb.Host)
		os.Setenv("IMMUDB_PORT", strconv.Itoa(config.Immudb.Port))
		os.Setenv("IMMUDB_USER", config.Immudb.User)
		os.Setenv("IMMUDB_PASSWORD", config.Immudb.Password)
		os.Setenv("IMMUDB_DATABASE", config.Immudb.Database)

		log.Println("Configuration loaded from config.json into environment variables")
	} else {
		requiredEnvVars := []string{"IMMUDB_HOST", "IMMUDB_PORT", "IMMUDB_USER", "IMMUDB_PASSWORD", "IMMUDB_DATABASE"}
		for _, envVar := range requiredEnvVars {
			if os.Getenv(envVar) == "" {
				return fmt.Errorf("required environment variable %s is not set", envVar)
			}
		}
		log.Println("Using existing environment variables for configuration")
	}

	return nil
}
