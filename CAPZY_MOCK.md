# capzy-mock provider

`capzy-mock` is an offline teaching fixture. It is not a Capzy client and never opens a network connection.

Select it in `config.properties`:

```properties
captcha.provider=capzy-mock
```

The provider returns deterministic tokens such as `MOCK_TOKEN_demo-user`. Fixture behavior can be selected with JVM properties:

```text
-Dcapzy.mock.scenario=success|pending|timeout|error|zero_balance
-Dcapzy.mock.polls=2
```

The scenarios model the control-flow cases a real adapter would need to handle:

- `success`: immediate successful result.
- `pending`: waits for the configured number of simulated polls, then succeeds.
- `timeout`: returns a timeout fixture token.
- `error`: returns an error fixture token.
- `zero_balance`: reports an empty simulated balance.

No API key is read, stored, transmitted, or logged. The fixture deliberately does not implement a real HTTP client, provider authentication, CAPTCHA task submission, webhook, or third-party integration.
