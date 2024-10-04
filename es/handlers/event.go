package handlers

import (
	"encoding/json"
	"io"
	"log"
	"net/http"

	"ivansoft.com/corebank/eventsource/store/db"
	"ivansoft.com/corebank/eventsource/store/models"
)

func SaveEvent(immudb *db.Immudb) http.HandlerFunc {
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

		// Save event to Immudb
		if err := immudb.SaveEvent(accountId, eventJSON); err != nil {
			log.Printf("Error: saving event: %v", err)
			http.Error(w, "Error: saving event", http.StatusInternalServerError)
			return
		}
		log.Printf("Event saved with accountID: %s\n", accountId)

		// Get the event to confirm it was saved
		savedEvent, err := immudb.GetEvent(accountId)
		if err != nil {
			log.Printf("Error: getting event: %v", err)
			http.Error(w, "Error: getting event", http.StatusInternalServerError)
			return
		}
		log.Printf("Event saved retrieved: %s\n", string(savedEvent))

		w.WriteHeader(http.StatusOK)
		if _, err := w.Write([]byte("Event saved")); err != nil {
			log.Printf("Error writing response: %v", err)
		}
	}
}
