# E.B  Ecocash — Mobile Money Simulation

A desktop mobile money banking simulator built with Python and Tkinter. It mimics a simplified Ecocash-style wallet experience: PIN login, sending money, buying airtime and data bundles, checking balances, and viewing transaction history — all persisted locally in a JSON file.

## Features

- **Dual wallets** — separate ZWG and USD balances, each with its own PIN
- **PIN login** with a limited number of attempts before lockout
- **Send Money** to a mobile number (validated against the `07XXXXXXXX` format)
- **Airtime top-up** for any mobile number
- **Data bundles** — choose from preset bundle sizes (100 MB up to 5 GB)
- **Balance check**
- **Transaction history** shown in a sortable table, with date, type, amount, and running balance
- **Persistent storage** — all wallet data is saved to `mobile_money_data.json` and reloaded on the next run

## Requirements

- Python 3.9+
- Tkinter (included with most standard Python installs)

No external packages are required — the project only uses the Python standard library (`tkinter`, `json`, `os`, `re`, `datetime`).

## Getting Started

```bash
# Clone the repository
git clone https://github.com/ebenezermakore/Ecocash-simulation.git
cd Ecocash-simulation

# Run the app
python groupproject.py
```

On first run, the app creates `mobile_money_data.json` with two default wallets:

| Wallet | Default PIN | Starting Balance |
|--------|-------------|-------------------|
| ZWG    | `1234`      | 2500.00           |
| USD    | `4321`      | 500.00            |

## Project Structure

```
Ecocash-simulation/
├── groupproject.py          # Main application (UI + logic)
├── mobile_money_data.json   # Wallet data, generated on first run
└── README.md
```

## How It Works

- `load_data()` / `save_data()` handle reading and writing wallet state to JSON.
- `record_transaction()` appends an entry to a wallet's history and saves it.
- `valid_mobile_number()` checks numbers against the pattern `07` followed by 8 digits.
- `MobileMoneyApp` (a `tkinter.Tk` subclass) drives all screens: currency selection → PIN entry → wallet menu → send money / airtime / bundles / history.

## Possible Improvements

- Add unit tests for `valid_mobile_number` and transaction logic
- Hash PINs instead of storing them in plain text
- Support multiple user accounts instead of a single shared data file
- Add a "cancel/back" option mid-transaction

  

## License

This project currently has no license file. Consider adding one (e.g. MIT) if you want others to freely use or contribute to the code — see [choosealicense.com](https://choosealicense.com/).
