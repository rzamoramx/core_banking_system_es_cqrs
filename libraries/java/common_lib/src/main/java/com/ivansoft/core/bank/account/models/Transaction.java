package com.ivansoft.core.bank.account.models;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.TimeZone;

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
        SimpleDateFormat isoFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSXXX");
        isoFormat.setTimeZone(TimeZone.getTimeZone("UTC"));
        String timestampStr = isoFormat.format(timestamp);

        return "{"
                + "\"id\":\"" + id + "\","
                + "\"account_id\":\"" + accountId + "\","
                + "\"amount\":" + amount + ","
                + "\"type\":\"" + type + "\","
                + "\"status\":\"" + status + "\","
                + "\"description\":\"" + description + "\","
                + "\"timestamp\":\"" + timestampStr + "\","
                + "\"version\":" + version
                + "}";
    }
}
