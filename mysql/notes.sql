SELECT
    id,
    verse_id,
    TYPE,
    description
FROM
    note
WHERE
    verse_id = ?;
