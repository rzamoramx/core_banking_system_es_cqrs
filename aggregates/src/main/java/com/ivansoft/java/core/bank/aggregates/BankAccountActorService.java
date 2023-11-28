package com.ivansoft.java.core.bank.aggregates;

import com.ivansoft.java.core.bank.aggregates.actors.BankAccountActorImpl;
import io.dapr.actors.runtime.ActorRuntime;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Options;
import java.time.Duration;

/**
 * Service for Actor runtime.
 * 1. Build and install jars:
 * mvn clean install
 * 2. cd to [repo-root]
 * 3. Run the server:
 * dapr run --app-id bankaccountactorservice --app-port 3000 -- java -jar target/bank_account_aggregate-0.0.1-SNAPSHOT.jar com.ivansoft.java.core.bank.aggregates.BankAccountActorService -p 3000
 */
public class BankAccountActorService {
    public static void main(String[] args) throws Exception {
        Options options = new Options();
        options.addRequiredOption("p", "port", true, "Port the will listen to.");

        CommandLineParser parser = new DefaultParser();
        CommandLine cmd = parser.parse(options, args);

        // If port string is not valid, it will throw an exception.
        final int port = Integer.parseInt(cmd.getOptionValue("port"));

        // Idle timeout until actor instance is deactivated.
        ActorRuntime.getInstance().getConfig().setActorIdleTimeout(Duration.ofSeconds(30));
        // How often actor instances are scanned for deactivation and balance.
        ActorRuntime.getInstance().getConfig().setActorScanInterval(Duration.ofSeconds(10));
        // How long to wait until for draining an ongoing API call for an actor instance.
        ActorRuntime.getInstance().getConfig().setDrainOngoingCallTimeout(Duration.ofSeconds(10));
        // Determines whether to drain API calls for actors instances being balanced.
        ActorRuntime.getInstance().getConfig().setDrainBalancedActors(true);

        // Register the Actor class.
        ActorRuntime.getInstance().registerActor(BankAccountActorImpl.class);

        // Start Dapr's callback endpoint.
        AggregatesApplication.start(port);
    }
}
