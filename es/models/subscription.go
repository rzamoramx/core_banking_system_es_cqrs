package models

type Result struct {
	ID   string `json:"id"`
	Data string `json:"data"`
}

type SubscriptionObj struct {
	PubsubName string            `json:"pubsubname"`
	Topic      string            `json:"topic"`
	Metadata   map[string]string `json:"metadata,omitempty"`
	Routes     Routes            `json:"routes"`
}

type Routes struct {
	Rules   []Rule `json:"rules,omitempty"`
	Default string `json:"default,omitempty"`
}

type Rule struct {
	Match string `json:"match"`
	Path  string `json:"path"`
}
