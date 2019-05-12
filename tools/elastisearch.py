import datetime
import typing
from os import environ

from elasticsearch import Elasticsearch
from elasticsearch_dsl import connections, Document, Text, Long, Date, Search
from elasticsearch_dsl.response import Response

elasticsearch_host = environ['ELASTICSEARCH_HOST']
connections.create_connection(hosts=[elasticsearch_host], timeout=20)
es = Elasticsearch()


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
    message_channel = Long()
    message_sent_time = Date()

    class Index:
        name = "test_messages_4"
        doc_type = "message"
        settings = {
            "number_of_replicas": 2
        }

    @staticmethod
    def save_message(content: str, message_id: int, channel_id: int, sender_id: int, server_id: int) -> bool:
        """Saves a message based on the input parameters. Returns true if the message was saved.

         datetime.now() is saved as the timestamp automatically.
         """
        current_message = TestMessageDoc(message_content=content, message_sender=sender_id, message_channel=channel_id,
                                         message_server=server_id, message_id=message_id,
                                         message_sent_time=datetime.datetime.now())
        return current_message.save()


def test_search_2(message: str, server_id: int, channel_id: int, user_id: typing.Optional[int] = None) -> Response:
    if user_id is not None:
        filter_data = [
            {"term": {"message_channel": channel_id}},
            {"term": {"message_server": server_id}},
            {"term": {"message_sender": user_id}}
        ]
    else:
        filter_data = [
            {"term": {"message_channel": channel_id}},
            {"term": {"message_server": server_id}}
        ]
    print(filter_data)
    s = Search(index="test_messages_4").from_dict(
        {
            "query": {
                "function_score": {
                    "gauss": {
                        "message_sent_time": {
                            "origin": "now",
                            "scale": "2d",
                            "decay": 0.5
                        }
                    },
                    "query": {
                        "match": {
                            "message_content": {
                                "query": message,
                                "fuzziness": "auto"
                            }
                        }
                    },
                    "score_mode": "multiply"
                }
            },
            "post_filter": {
                "bool": {
                    "must": filter_data
                }
            }
        }
    ).execute()
    return s


if __name__ == "__main__":
    print(TestMessageDoc.init())
    test_search_2("Discord", channel_id=448285120634421278, server_id=336642139381301249)
