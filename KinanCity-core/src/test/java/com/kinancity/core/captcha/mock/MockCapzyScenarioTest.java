package com.kinancity.core.captcha.mock;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class MockCapzyScenarioTest {

    @Test
    public void unknownScenarioFallsBackToErrorFixture() {
        assertEquals(MockCapzyScenario.ERROR, MockCapzyScenario.from("not-a-scenario"));
    }

    @Test
    public void scenarioParsingIsCaseInsensitive() {
        assertEquals(MockCapzyScenario.PENDING, MockCapzyScenario.from("pending"));
    }
}
