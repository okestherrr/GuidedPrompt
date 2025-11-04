SELECT
    v.id AS verse_id,
    vol.volume_name,
    ver.v_name AS version_name,
    b.book_name,
    c.chapter_num,
    v.verseno,
    v.text
FROM
    verse v
    JOIN chapter c ON v.chapter_id = c.id
    JOIN book b ON c.book_id = b.id
    JOIN volume vol ON b.volume_id = vol.id
    JOIN version ver ON b.version_id = ver.id
WHERE
    v.text REGEXP(?)
ORDER BY
    vol.id,
    b.id,
    c.id,
    v.id;
