================================================================================
 tinbox-mx
================================================================================

IMAP importer for tinbox.

build --rm -t trak-mx .

docker run -it --rm --env TINBOX_API_URL=http --env TINBOX_CLIENT_ID=a --env TINBOX_CLIENT_SECRET=b --env IMAP_USERNAME=trak@5monkeys.se --env IMAP_PASSWORD=traktrak trak-mx
