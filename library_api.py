import requests
from urllib.parse import urljoin

baseUrl = "https://openlibrary.org/"

class LibraryAPI:
    def __init__(self, keyword, year_from=None, year_to=None, limit=50, sort=None):
        self.keyword = keyword
        self.year_from = year_from
        self.year_to = year_to
        self.limit = limit
        self.sort = sort

    def fetch_books(self):
        try:
            query = self.keyword

            if self.year_from or self.year_to:
                from_year = self.year_from if self.year_from else "*"
                to_year = self.year_to if self.year_to else "*"
                query += f" first_publish_year:[{from_year} TO {to_year}]"


            params = {
                "q": query,
                "limit": self.limit
            }

            if self.sort :
                params.update({"sort" : self.sort})

            response = requests.get("https://openlibrary.org/search.json", params=params, timeout=10)

            response.raise_for_status()
            
            data = response.json().get("docs")

            books = []
            for book in data:
                authors = book.get("author_name")
                authors_str = " & ".join(authors) if authors else "Unknown"
                books.append({
                    "title": book.get("title"),
                    "author_name": authors_str,
                    "first_publish_year": book.get("first_publish_year"),
                    "url": urljoin(baseUrl,book.get("key"))
                })
            return books
        
        except requests.exceptions.Timeout:
            raise Exception("Timeout")

        except requests.exceptions.ConnectionError:
            raise Exception("Connection Error")

        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP Error: {e}")

        except Exception as e:
            raise Exception(f"Unknown Error: {e}")