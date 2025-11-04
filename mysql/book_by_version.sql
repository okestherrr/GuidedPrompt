SELECT
    id,
    book_name,
    abbreviation
FROM
    book
WHERE
    version_id = ?;
