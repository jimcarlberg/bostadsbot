# .github/workflows/scraper.yml
name: Bostadsbot Scheduler

on:
  schedule:
    - cron: '15 0 * * *'  # Kör dagligen 00:15
  workflow_dispatch:

jobs:
  run-scraper:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          playwright install --with-deps

      - name: Run scraper
        env:
          EMAIL_USER: ${{ secrets.EMAIL_USER }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        run: |
          python main.py
