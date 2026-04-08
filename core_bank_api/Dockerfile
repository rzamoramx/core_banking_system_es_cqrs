FROM maven:3.9.6-eclipse-temurin-21 AS builder
WORKDIR /app

# Copy and install the shared library
COPY libraries/java/common_lib /app/libraries/java/common_lib
RUN cd /app/libraries/java/common_lib && mvn clean install -DskipTests

# Copy and build the core bank api component
COPY core_bank_api /app/core_bank_api
RUN cd /app/core_bank_api && mvn clean package -DskipTests

FROM eclipse-temurin:21-jre-jammy
WORKDIR /app
COPY --from=builder /app/core_bank_api/target/api-0.0.1-SNAPSHOT.jar ./app.jar
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "app.jar"]
