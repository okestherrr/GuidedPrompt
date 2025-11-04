SELECT
    ver.id AS version_id,
    MIN(v.id) AS min_verse_id,
    MAX(v.id) AS max_verse_id
FROM
    verse v
    JOIN chapter c ON v.chapter_id = c.id
    JOIN book b ON c.book_id = b.id
    JOIN version ver ON b.version_id = ver.id
GROUP BY
    ver.id;
