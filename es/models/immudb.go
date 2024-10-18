package models

type SetRequest struct {
	Key         string            `json:"key"`
	Value       any               `json:"value"`
	ETag        *string           `json:"etag,omitempty"`
	Metadata    map[string]string `json:"metadata,omitempty"`
	ContentType *string           `json:"contentType,omitempty"`
}

type GetRequest struct {
	Key      string            `json:"key"`
	Metadata map[string]string `json:"metadata"`
}

type GetResponse struct {
	Data        []byte            `json:"data"`
	ETag        *string           `json:"etag,omitempty"`
	Metadata    map[string]string `json:"metadata"`
	ContentType *string           `json:"contentType,omitempty"`
}
