# Deriv Bot

A Python-based trading bot for the Deriv platform that automates trading operations, provides real-time market data monitoring, and sends notifications via Telegram.

![Deriv Bot](https://deriv.com/static/logo-deriv-512x512-5e5d5970.png)

## Features

- **Deriv API Integration**: Connect to the Deriv trading platform using their official API
- **Telegram Notifications**: Receive account status and trading activity notifications via Telegram
- **Web Dashboard**: Monitor account balance and market data through a real-time web interface
- **Market Tick Streaming**: Subscribe to real-time price updates for various markets
- **Multiple Trading Strategies**: Support for different trading strategies (Basic, Martingale, Soros)
- **Error Handling**: Robust error handling for market availability and connection issues

## Technologies Used

- **Python 3.12+**: Core programming language
- **Deriv API**: Official Python client for the Deriv trading platform
- **Flask**: Web framework for the dashboard interface
- **Aiogram**: Framework for Telegram Bot integration
- **Asyncio**: For asynchronous operations
- **WebSockets**: For real-time data streaming
- **ReactiveX**: For reactive programming patterns

## Installation

### Prerequisites

- Python 3.12 or higher
- Git
- Deriv account with API access
- Telegram Bot token

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/leonardolimanas/deriv-bot.git
   cd deriv-bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (see Configuration section)

## Configuration

Create a `.env` file in the project root or set the following environment variables:

```
DERIV_API_TOKEN=your_deriv_api_token
DERIV_APP_ID=your_deriv_app_id
DERIV_API_TOKEN_REAL=your_deriv_real_account_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Alternatively, you can modify the default values in `utils/config.py`.

## Usage

### Running the Bot

To start the bot with Telegram notifications and web dashboard:

```bash
python main.py
```

This will:
1. Connect to the Deriv platform
2. Send the initial account balance via Telegram
3. Start the web dashboard on http://0.0.0.0:5001

### Web Dashboard

The web dashboard provides:

- Real-time account balance display
- Market selection dropdown
- Tick streaming controls
- Real-time price data visualization

To access the dashboard, open a browser and navigate to:
```
http://localhost:5001
```

### Market Tick Streaming

1. Select a market from the dropdown menu
2. Click "Subscribe to Ticks"
3. View real-time tick data in the table
4. Click "Unsubscribe" to stop the stream

Note: Some markets may be unavailable during certain hours or days. The dashboard will display appropriate status messages.

## Project Structure

```
deriv-bot/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── strategies/             # Trading strategies
│   ├── basic_strategy.py
│   ├── martingale_strategy.py
│   └── soros_strategy.py
├── utils/                  # Utility modules
│   ├── config.py           # Configuration settings
│   ├── deriv_handler.py    # Deriv API integration
│   └── telegram_bot.py     # Telegram notifications
└── web/                    # Web dashboard
    ├── dashboard.py        # Flask application
    ├── static/             # Static assets
    │   ├── css/
    │   └── js/
    └── templates/          # HTML templates
```

## Trading Strategies

The project includes support for multiple trading strategies:

- **Basic Strategy**: Simple entry and exit rules
- **Martingale Strategy**: Increases stake after each loss
- **Soros Strategy**: Based on George Soros' trading principles

Note: Strategy implementations are currently in development.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

Trading involves risk. This software is for educational and research purposes only. Use at your own risk.