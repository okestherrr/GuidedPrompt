SELECT
    id,
    book_id,
    chapter_num,
    author, 
    desc
FROM
    chapter
WHERE
    book_id = ?;
