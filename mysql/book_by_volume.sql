SELECT
    id,
    book_name,
    abbreviation
FROM
    book
WHERE
    volume_id = ?;
