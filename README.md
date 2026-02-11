# OpenLibrary Telegram Bot

Lightweight Telegram bot that searches Open Library and exports results to CSV.

Files
- `bot.py`: Main Telegram bot entrypoint and user interaction.
- `library_api.py`: Open Library API wrapper used to fetch book data.
- `csv_exporter.py`: Helper to write search results to CSV.
- `requirements.txt`: Python dependencies.
- `Procfile`: Heroku process file.

Requirements
- Python from `runtime.txt`: python-3.13.5
- Install dependencies:

```bash
pip install -r requirements.txt
```

Configuration
- Create a `.env` file or set environment variable `API_KEY` with your Telegram bot token. Example `.env`:

```
API_KEY=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

Usage
- Run locally:

```bash
python bot.py
```

- The bot will start polling. Use `/start` in Telegram to begin a search. The bot generates a CSV and sends it to the user.

Deployment
- This project includes a `Procfile` for Heroku. Ensure `API_KEY` is set in the app's config vars and push the repo to Heroku.

Notes
- Logs are written to `bot_telegram.log` by default.
- If you want to change the license holder, update the `LICENSE` file author/year.

License
- This project is licensed under the MIT License. See `LICENSE`.
