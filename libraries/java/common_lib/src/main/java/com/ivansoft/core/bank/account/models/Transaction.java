package com.ivansoft.core.bank.account.models;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.Date;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Transaction {
    private String id;
    private String accountId;
    private Double amount;
    private TransactionType type;
    private String status;
    private String description;
    private Date timestamp;
    private int version;

    public String convertToJson() {
        return "{"
                + "\"id\":\"" + id + "\","
                + "\"account_id\":\"" + accountId + "\","
                + "\"amount\":" + amount + ","
                + "\"type\":\"" + type + "\","
                + "\"status\":\"" + status + "\","
                + "\"description\":\"" + description + "\","
                + "\"timestamp\":\"" + timestamp + "\","
                + "\"version\":" + version
                + "}";
    }
}
