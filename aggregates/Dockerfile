FROM maven:3.9.6-eclipse-temurin-21 AS builder
WORKDIR /app

# Copy and install the shared library
COPY libraries/java/common_lib /app/libraries/java/common_lib
RUN cd /app/libraries/java/common_lib && mvn clean install -DskipTests

# Copy and build the aggregates component
COPY aggregates /app/aggregates
RUN cd /app/aggregates && mvn clean package -DskipTests

FROM eclipse-temurin:21-jre-jammy
WORKDIR /app
COPY --from=builder /app/aggregates/target/bank_account_aggregate-0.0.1-SNAPSHOT.jar ./app.jar
EXPOSE 3000
ENTRYPOINT ["java", "-jar", "app.jar", "com.ivansoft.java.core.bank.aggregates.BankAccountActorService", "-p", "3000"]
