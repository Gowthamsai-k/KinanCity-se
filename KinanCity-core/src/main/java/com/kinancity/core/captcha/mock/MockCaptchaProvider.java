package com.kinancity.core.captcha.mock;

import com.kinancity.api.errors.TechnicalException;
import com.kinancity.core.captcha.CaptchaException;
import com.kinancity.core.captcha.CaptchaProvider;
import com.kinancity.core.captcha.CaptchaQueue;
import com.kinancity.core.captcha.CaptchaRequest;

/**
 * Offline provider for tests. It never performs network I/O and returns a
 * deterministic token for each queued request.
 */
public class MockCaptchaProvider extends CaptchaProvider {

    private final CaptchaQueue queue;
    private final MockCapzyScenario scenario;
    private final int pollsBeforeSuccess;
    private volatile boolean running = true;

    public MockCaptchaProvider(CaptchaQueue queue) {
        this(queue, MockCapzyScenario.from(System.getProperty("capzy.mock.scenario")),
                Integer.getInteger("capzy.mock.polls", 2));
    }

    public MockCaptchaProvider(CaptchaQueue queue, MockCapzyScenario scenario, int pollsBeforeSuccess) {
        this.queue = queue;
        this.scenario = scenario;
        this.pollsBeforeSuccess = Math.max(0, pollsBeforeSuccess);
    }

    @Override
    public double getBalance() throws CaptchaException, TechnicalException {
        return scenario == MockCapzyScenario.ZERO_BALANCE ? 0 : 1;
    }

    @Override
    public void run() {
        while (running) {
            CaptchaRequest request = queue.getQueue().peek();
            if (request == null) {
                try {
                    Thread.sleep(25);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    running = false;
                }
                continue;
            }
            if (scenario == MockCapzyScenario.TIMEOUT) {
                queue.addCaptcha("MOCK_TIMEOUT_" + request.getUsername());
            } else if (scenario == MockCapzyScenario.ERROR) {
                queue.addCaptcha("MOCK_ERROR_" + request.getUsername());
            } else {
                if (scenario == MockCapzyScenario.PENDING && pollsBeforeSuccess > 0) {
                    try {
                        Thread.sleep(pollsBeforeSuccess * 25L);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        running = false;
                        continue;
                    }
                }
                queue.addCaptcha("MOCK_TOKEN_" + request.getUsername());
            }
        }
    }

    public void stop() {
        running = false;
    }
}
