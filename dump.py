import os
import csv

from zendesk import Zendesk

client = Zendesk('https://govuk.zendesk.com', os.getenv("ZENDESK_USERNAME"), os.getenv("ZENDESK_PASSWORD"), api_version=2)

OUTPUT_FILE_NAME = "output_file_name.csv"
ZENDESK_QUERY = "status>new tags:student-finance"

fields = ["id", "subject", "url", "created_at", "updated_at", "group_id", "description"]
with open(OUTPUT_FILE_NAME, "w+") as f:
  writer = csv.writer(f, delimiter=',', quotechar='"', escapechar='\\')
  writer.writerow(fields)

  page = 1

  while True:
    print("Fetch page %s" % page)
    resp = client.search(query=ZENDESK_QUERY, page=page)
    for item in resp["results"]:
      if item["result_type"] == "ticket":
        if isinstance(item["description"], unicode):
          item["description"] = item["description"].encode("ascii", "ignore")
        writer.writerow([item[field] for field in fields])
    if resp.get("next_page") is not None:
      page += 1
    else:
      break
