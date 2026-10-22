package com.kinancity.core.captcha.mock;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

import com.kinancity.core.captcha.CaptchaQueue;
import com.kinancity.core.captcha.CaptchaRequest;

public class MockCaptchaProviderTest {

    @Test
    public void returnsDeterministicOfflineToken() throws Exception {
        CaptchaQueue queue = new CaptchaQueue();
        CaptchaRequest request = queue.addRequest(new CaptchaRequest("demo-user"));
        MockCaptchaProvider provider = new MockCaptchaProvider(queue);
        Thread worker = new Thread(provider);
        worker.start();
        assertEquals("MOCK_TOKEN_demo-user", request.getResponse());
        provider.stop();
        worker.join(1000);
    }
}
