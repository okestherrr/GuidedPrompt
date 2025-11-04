WITH search_term AS (
    SELECT
        ? AS term
)
SELECT
    vol.volume_name,
	ver.v_name,
    SUM(
        (
            LENGTH(v.text) - LENGTH(REPLACE(v.text, st.term, ''))
        ) / LENGTH(st.term)
    ) AS total_occurrences
FROM
    verse v
    JOIN chapter c ON v.chapter_id = c.id
    JOIN book b ON c.book_id = b.id
    JOIN volume vol ON b.volume_id = vol.id
	JOIN version ver ON b.version_id = ver.id
    JOIN search_term st ON 1 = 1
WHERE
    v.text LIKE CONCAT('%', st.term, '%')
GROUP BY
	vol.volume_name,
    ver.v_name
ORDER BY
	ver.id;
