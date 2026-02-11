import csv
def export_to_csv(filename, books):
    if not books:
        return
    headers = books[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(books)