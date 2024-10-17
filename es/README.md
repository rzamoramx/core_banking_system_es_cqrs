# ES #

This is the Event Source that handles system events using Dapr's pubsub building block and stores event logs in ImmuDB.

## Prerequisites ##

Read global README prerequisites [here](../README.md#prerequisites).

## Installation ##

Read global README installation [here](../README.md#installation).

Also you will need to install dependencies for the project:

```bash
go mod tidy
```

## Building the project ##

To build the project, locate into root_project/es directory and execute the following command:

```bash
dapr run --app-id eventsourcestore --app-port 8002 -- go run main.go -port 8002
```