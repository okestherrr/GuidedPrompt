SELECT
    LOWER(
    	STRING_AGG(
    		v.text,
    		' '
    	)
    )
FROM
    verse v
WHERE
    v.id BETWEEN ? AND ?;
