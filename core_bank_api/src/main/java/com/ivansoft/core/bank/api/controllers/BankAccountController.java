package com.ivansoft.core.bank.api.controllers;

import com.ivansoft.core.bank.api.models.RequestAccountTransaction;
import com.ivansoft.core.bank.api.models.Response;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.logging.Logger;
import com.ivansoft.core.bank.api.actors.BankAccountActorClient;


@RestController
@RequestMapping("/mybank/api/v1/account")
public class BankAccountController {
    private static final Logger log = Logger.getLogger(BankAccountController.class.getName());
    private final BankAccountActorClient bankAccountActorClient = new BankAccountActorClient();

    @PostMapping("/transaction")
    public Response createTransaction(@RequestBody RequestAccountTransaction requestAccountTransaction) {
        log.info("Creating transaction for account " + requestAccountTransaction.getAccountId() + " with type " +
                requestAccountTransaction.getTransactionType() + " and amount " + requestAccountTransaction.getAmount());
        try {
            var result = bankAccountActorClient.doTransaction(
                    requestAccountTransaction.getAccountId(),
                    requestAccountTransaction.getTransactionType(),
                    requestAccountTransaction.getAmount()
            );
            log.info("Transaction result: " + result);
            return new Response("OK", "Transaction created", null);
        } catch (Exception e) {
            log.severe("Error creating transaction: " + e.getMessage());
            return new Response("ERROR", "Error creating transaction", null);
        }
    }
}
