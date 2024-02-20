from google.cloud import dns
client = dns.Client(project="rbz-dev-002")
zone = client.zone("evgeniy-test-zone")
changes = zone.changes()

for i in range(1, 101):
    create_records = dns.resource_record_set.ResourceRecordSet(
        name=f'test{i}.evgeniytestzone.dev.rbzdns.com.',
        record_type="CNAME",
        ttl=300,
        rrdatas=["echo.reblaze.com."],
        zone=zone
    )

    changes.add_record_set(create_records)
changes.create()
