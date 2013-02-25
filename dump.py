import os
import csv

from zendesk import Zendesk


OUTPUT_FILE_NAME = "output_file_name.csv"
ZENDESK_QUERY = "status>new tags:student-finance"


def create_client(api_version=2):
    return Zendesk(
        'https://govuk.zendesk.com',
        os.getenv('ZENDESK_USERNAME'),
        os.getenv('ZENDESK_PASSWORD'),
        api_version=api_version
    )


def paged_search(client, query):
    page = 1
    while True:
        print("Fetch page {0}".format(page))
        resp = client.search(query=query, page=page)
        for item in resp["results"]:
            if item["result_type"] != "ticket":
                continue
            if isinstance(item["description"], unicode):
                item["description"] = item["description"].encode("ascii", "ignore")
            yield item
        if resp.get("next_page") is not None:
            page += 1
        else:
            break


def get_ticket(client, ticket_id):
    return client.show_ticket(ticket_id=ticket_id)


if __name__ == '__main__':
    client_v1 = create_client(1)
    client_v2 = create_client(2)

    fields = [
        "id", "subject", "url",
        "created_at", "updated_at",
        "group_id", "description"
    ]
    with open(OUTPUT_FILE_NAME, "w+") as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', escapechar='\\')
        writer.writerow(fields + ["comment"])

        for item in paged_search(client_v2, ZENDESK_QUERY):
            values = [item[field] for field in fields]

            ticket = get_ticket(client_v1, item["id"])
            values.append(
                ticket["comments"][0]["value"].encode('ascii', 'ignore')
            )

            writer.writerow(values)
