import os
import logging
from google.cloud import error_reporting
import googlecloudprofiler

client: error_reporting.client = None


def startup():
    global client
    # noinspection PyBroadException
    try:
        BOT_STATE = os.environ['BOT_STATE']
    except Exception:
        client = error_reporting.Client(service="ReplyBot_Pre-envion")
        client.report_exception()

    # Sets up the error handler
    client = error_reporting.Client(service="ReplyBot" + BOT_STATE)

    # Sets up the google compute cloud logging
    try:
        import googleclouddebugger

        googleclouddebugger.enable(
            module='ReplyBot' + BOT_STATE,
            version='3.2'
        )
    except ImportError:
        client.report_exception()
        logging.error("Failed to connect to google cloud debugger!")

    try:
        googlecloudprofiler.start(
            service='reply-bot',
            service_version='1.0.1',
            # verbose is the logging level. 0-error, 1-warning, 2-info,
            # 3-debug. It defaults to 0 (error) if not set.
            verbose=2,
            # project_id must be set if not running on GCP.
            project_id='discord-reply-bot-sql',
        )
    except (ValueError, NotImplementedError):
        client.report_exception()  # Handle errors here

    # Cloud Logging was really hard, I used these instructions https://www.eightypercent.net/post/docker-gcplogs.html
