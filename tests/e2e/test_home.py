import re
from playwright.sync_api import Page, expect

def test_has_title(page:Page):
    page.goto("http://127.0.0.1:5000")

    # expect a title "to contain" a substring
    expect(page).to_have_title(re.compile("Mi PlatoIA - Analisis Nutricional Inteligente"))