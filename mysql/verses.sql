SELECT
    id,
    chapter_id,
    verseno,
    text
FROM
    verse
WHERE
    chapter_id = ?;
