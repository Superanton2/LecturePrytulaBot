# Event Registration Telegram Bot 🎟️

This project is an asynchronous Python-based Telegram bot designed to automate the registration of participants for events and lectures. It utilizes the `aiogram` framework, a PostgreSQL database, and the Google Sheets API to handle user registrations, data validation, profile management, and real-time synchronization with a Google Spreadsheet.

## Features

- **Event Registration:** Collects essential user data including Full Name (ПІБ), Phone number, Email, Education status, and Faculty.
- **Strict Data Validation:** Automatically formats and validates phone numbers (ensuring a 10-digit format) and email addresses.
- **Dynamic Profile Management:** Allows users to view and update their submitted data. Faculty options dynamically adapt based on the user's education status.
- **Rules Agreement:** Integrates with Telegraph to ensure users read and agree to event rules before finalizing their registration.
- **Google Sheets Integration:** Automatically synchronizes new registrants and profile updates to a Google Spreadsheet for easy administration.
- **Admin Dashboard:** Administrators can open/close the registration process globally and broadcast messages to all registered participants directly via the Telegram interface.
- **Dockerized Environment:** Fully containerized using Docker and Docker Compose, optimized for deployment on VPS or Proxmox LXC containers.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine or server.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A registered Telegram Bot token from [@BotFather](https://t.me/botfather)

### Installation

1.  **Clone the repository:**
```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
```

2.  **Set up Google Sheets API Credentials:**
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Enable the **Google Sheets API** and **Google Drive API**.
    - Create a Service Account and download the JSON key.
    - Rename the downloaded file to `credentials.json` and place it in the root directory of the project.
    - *Important:* Share your target Google Spreadsheet with the `client_email` found inside `credentials.json` with "Editor" permissions.
    - Create two sheets (tabs) in your document named exactly: `Users` and `Admins`.

### Configuration

Before starting the bot, you need to configure your environment variables. 

1. Create a `.env` file in the root directory.
2. Populate it with the required configuration:

```env
    # Telegram Bot Token
    BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
    
    # Database connection string
    BD_ENGINE="postgresql+asyncpg://admin:secret@db:5432/event_db"
    
    # Telegram id of admins
    SUPER_ADMINS=1234567890,0987654321
    
    # Google Sheets Configuration
    LOG_SHEET_NAME="YOUR_GOOGLE_SHEET_NAME"
    SHEET_URL="https://docs.google.com/spreadsheets/d/YOUR_DOCUMENT_ID/"
    
    # Telegraph Rules Link (telegra.ph)
    RULES_URL="URL_TO_YOUR_RULS" 
```



## Usage

To run the bot and the database, use Docker Compose. This is the recommended method for both development and production.

```bash
docker-compose up -d --build
```
The script will perform the following actions:
1. Pull the necessary Python and PostgreSQL images.
2. Initialize the event_db database and create the user_list table.
3. Launch the bot in polling mode.

## Project Structure
``` text
.
├── app/
│   ├── db/
│   │   ├── db_setup.py             # Database models and table definitions.
│   │   └── db_requests.py          # Async SQLAlchemy CRUD operations.
│   ├── routers/
│   │   ├── admin_router.py         # Handlers for the admin dashboard and broadcasting.
│   │   ├── controller_router.py    # Handlers for the main menu and basic navigation.
│   │   ├── profile_router.py       # Handlers for viewing and editing user profiles.
│   │   └── registration_router.py  # FSM logic for the multi-step registration process.
│   └── utils/
│       ├── bot_state.py            # Global state variables (e.g., registration open/close toggle).
│       ├── funcs.py                # Helper functions.
│       ├── google_sheets.py        # gspread integration for database syncing.
│       └── keyboards.py            # Inline and Reply keyboard builders.
│
├── docker-compose.yml              # Docker services configuration (Bot + DB).
├── Dockerfile                      # Instructions to build the Python bot image.
├── .env                            # Environment variables (Ignored by Git).
├── credentials.json                # Google Service Account key (Ignored by Git).
├── main.py                         # Application entry point and dispatcher setup.
├── requirements.txt                # Python dependencies.
└── README.md                       # This file.
```