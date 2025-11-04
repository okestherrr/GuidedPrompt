SELECT
    id,
    verse_id,
    type,
    start,
    end,
    group_id,
    position
FROM
    element
WHERE
    group_id = ?;
