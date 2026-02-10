import csv

class CSVExporter:
    def __init__(self, filename,books):
        self.filename = filename
        self.export(books)

    def export(self, books):
        if not books:
            return

        headers = books[0].keys()

        with open(self.filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            for book in books:
                writer.writerow(book)
