package com.ivansoft.java.core.bank.aggregates.services;

import io.dapr.client.DaprClient;
import io.dapr.client.DaprClientBuilder;
import io.dapr.client.domain.CloudEvent;
import io.dapr.client.domain.Metadata;
import io.dapr.client.domain.PublishEventRequest;
import com.ivansoft.core.bank.account.models.Transaction;
import com.ivansoft.core.bank.account.lib.Utils;
import java.util.UUID;
import java.util.logging.Logger;
import static java.util.Collections.singletonMap;

public class EventSourceService {
    private static final Logger log = Logger.getLogger(EventSourceService.class.getName());

    private String MESSAGE_TTL_IN_SECONDS = "3600";
    private String PUBSUB_NAME = "eventsource";
    private String TOPIC_NAME = "transactions";

    public void publishTransaction(Transaction transaction) throws Exception {
        try (DaprClient client = new DaprClientBuilder().build()) {
            CloudEvent<String> cloudEvent = new CloudEvent<>();
            cloudEvent.setId(UUID.randomUUID().toString());
            cloudEvent.setType("com.ivansoft.java.core.bank.transactions.v1");
            cloudEvent.setSpecversion("1");
            cloudEvent.setDatacontenttype("application/application/json"); // octet-stream

            //cloudEvent.setData(Utils.serializeTransactions(transaction));
            cloudEvent.setData(transaction.convertToJson());

            // Publishing messages
            var publishEventRequest = new PublishEventRequest(PUBSUB_NAME, TOPIC_NAME, cloudEvent)
                    .setContentType(CloudEvent.CONTENT_TYPE)
                    .setMetadata(singletonMap(Metadata.TTL_IN_SECONDS, MESSAGE_TTL_IN_SECONDS));
            log.info("publishing to pubsub name: " + publishEventRequest.getPubsubName());
            log.info("publishing to pubsub topic: " + publishEventRequest.getTopic());

            client.publishEvent(publishEventRequest).block();

            log.info("Published cloud event with message: " + cloudEvent.getData());
        }
    }
}
