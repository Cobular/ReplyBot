from logging import StreamHandler, LogRecord
from google.cloud import error_reporting


class GCELogHandler(StreamHandler):

    def __init__(self, client: error_reporting.client):
        StreamHandler.__init__(self)

        self.client: error_reporting.client = client

    def emit(self, record: LogRecord):
        if record.exc_info[0] is not None:
            self.client.report(record.exc_text)
        else:
            self.client.report(record.getMessage())
        StreamHandler.emit(self, record)
        print("GCE Handled")
