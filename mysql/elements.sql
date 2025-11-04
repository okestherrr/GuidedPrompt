SELECT
    id,
    verse_id,
    TYPE,
    START,
END,
group_id,
position
FROM
    element
WHERE
    verse_id = ?;
