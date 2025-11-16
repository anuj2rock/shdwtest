# shdwtest

## Logging configuration

`shadow_lambda.py` sets its log level based on the `LOG_LEVEL` environment
variable, defaulting to `INFO` during cold start initialization. Configure the
Lambda's environment variable to `DEBUG` (or any other valid Python logging
level string such as `WARNING`, `ERROR`, etc.) whenever you need more verbose
diagnostics.
