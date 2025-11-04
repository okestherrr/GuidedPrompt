""" purpose of this is to search scripture for specific refrences of words. In the end it collect and output: how many time word was refrenced, scripture it was most refrenced in, verses and books it was refrenced in. """

#import bible and other scriptures
import sqlite3 

with sqlite3.connect('scriptures.db') as conn:
    print(conn.execute('SELECT * FROM version;').fetchone())
    print(conn.execute('''
                        SELECT
                            id,
                            v_name,
                            version_year
                        FROM
                            version
                        WHERE
                            id = ?;''', (3,)).fetchone())


# def getbook(scriptures):
#     #want it to return correct book that has refrence
#     return getbook ------ here I need to find how to return the BOM< BIBLE,DC,PG

# def extract(verseRefrence):
#     #want it to return refrences of the looked up word
#     return extract

# def correctRefrence(bookname, chapter, verse= None, end_chap = None, end_verse= None):
#     #verfies scripture ref
#     return correctRefrence(bookname, chapter, verse= None, endVerse = None, end_chap= None)
# #needs to read the script

# def main


# - 
