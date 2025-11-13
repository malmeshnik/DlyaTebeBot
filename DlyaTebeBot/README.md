# DlyaTebeBot

This is a Telegram bot for the "DlyaTebe" store.

## Features

* **Bonus Card:** Users can view their bonus card with a QR code.
* **Promotions:** Users can view current promotions.
* **Purchase History:** Users can view their purchase history.
* **Catalog:** Users can browse the store's catalog.
* **Contact:** Users can contact the store.
* **Social Media:** Users can find links to the store's social media pages.

## Setup

1. **Clone the repository:**
   ```
   git clone <repository-url>
   ```
2. **Install the dependencies:**
   ```
   pip install -r requirements.txt
   ```
3. **Set up the environment variables:**
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
   - `PHONE_CRM_AUTH`: The phone number for CRM authentication.
   - `PASSWORD_CRM`: The password for CRM authentication.
   - `BASE_CRM_URL`: The base URL of the CRM API.
   - `DOMAIN`: The domain of the website.
4. **Run the migrations:**
   ```
   python manage.py migrate
   ```
5. **Run the bot:**
   ```
   python manage.py runbot
   ```

## Usage

To use the bot, simply start a conversation with it on Telegram.
