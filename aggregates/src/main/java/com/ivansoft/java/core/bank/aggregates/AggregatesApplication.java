package com.ivansoft.java.core.bank.aggregates;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.util.logging.Logger;

@SpringBootApplication
public class
AggregatesApplication {
	private static final Logger log = Logger.getLogger(AggregatesApplication.class.getName());

	public static void start(int port) {
		SpringApplication app = new SpringApplication(AggregatesApplication.class);
		log.info(String.format("Starting Dapr Actor app on port %d", port));
		app.run(String.format("--server.port=%d", port));
	}
}
