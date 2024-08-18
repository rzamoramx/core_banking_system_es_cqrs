package com.ivansoft.java.core.bank.aggregates;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class AggregatesApplication {
	public static void start(int port) {
		SpringApplication app = new SpringApplication(AggregatesApplication.class);

		app.run(String.format("--server.port=%d", port));
	}
}
