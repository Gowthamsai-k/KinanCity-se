package com.kinancity.core.captcha.mock;

/** Fixture outcomes used by the offline capzy-mock provider. */
public enum MockCapzyScenario {
    SUCCESS,
    PENDING,
    TIMEOUT,
    ERROR,
    ZERO_BALANCE;

    public static MockCapzyScenario from(String value) {
        if (value == null || value.trim().isEmpty()) return SUCCESS;
        try {
            return valueOf(value.trim().toUpperCase());
        } catch (IllegalArgumentException ex) {
            return ERROR;
        }
    }
}
