from elasticsearch_dsl import connections, Document, analyzer, Text, Long, Date
from os import environ

elasticsearch_host = environ['ELASTICSEARCH_HOST']
connections.create_connection(hosts=[elasticsearch_host], timeout=20)


# Possible option to make searching even better:
# https://www.freshconsulting.com/how-to-create-a-fuzzy-search-as-you-type-feature-with-elasticsearch-and-django/
# Article on how the fuzzies work
# https://sematext.com/blog/search-relevance-solr-elasticsearch-similarity/#toc-similarity-options-in-solr-elasticsearch-1
class TestMessageDoc(Document):
    """Document that stores the messages sent to the server"""

    message_content = Text()
    message_id = Long()
    message_sender = Long()
    message_server = Long()
    message_sent_time = Date()

    class Index:
        name = "test_messages_3"
        settings = {
            "number_of_replicas": 2
        }


