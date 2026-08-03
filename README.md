# ⚽ Football Stats

A modern football statistics website built with **Python**, **Flask**, and the **Football-Data.org API**.

The application allows users to explore clubs from Europe's top leagues, view fixtures, league tables, recent form, match details, and more through a clean, responsive interface.

---

## 📸 Features

- 🔍 Search for clubs across multiple European leagues
- 🏆 Browse teams by league
- 📅 View upcoming fixtures
- 📖 Detailed match pages
- 📊 League standings
- 📈 Team form (last 5 matches)
- ⚽ Recent results
- 🗓 Upcoming fixtures for each team
- 👥 Squad information (where available on the Football-Data.org free plan)
- 💜 Custom dark football-themed user interface
- ⚡ Built-in caching to reduce API requests and improve performance
- ⚠️ Error pages 404 and 500 in place in case of user error

---

## 🌍 Supported Competitions

- Premier League
- La Liga
- Bundesliga
- Serie A
- Ligue 1

---

## 🛠 Technologies Used

- Python
- Flask
- HTML5
- CSS3
- Jinja2
- Football-Data.org API

---

## ⚡ Performance

To minimise API requests and improve loading speeds, the application caches frequently requested data, including:

- Team information
- League tables
- Fixtures
- Results
- Team lists

This significantly reduces the number of API calls made while keeping data reasonably up to date.

---

## 📂 Project Structure

```
football-stats/
│
├── app.py
├── static/
│   ├── style.css
│   └── images/
│
├── templates/
│   ├── about.html
│   ├── layout.html
│   ├── home.html
│   ├── fixtures.html
│   ├── match.html
│   ├── team.html
│   ├── teams.html
│   ├── league_teams.html
│   └── scorers.html
│
└── README.md
```

---

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/football-stats.git
```

Move into the project folder

```bash
cd football-stats
```

Install the required packages

```bash
pip install flask requests
```

Create your API key from Football-Data.org.

In `app.py`, replace:

```python
FOOTBALL_DATA_KEY = "YOUR_API_KEY"
```

with your own API key.

Run the application

```bash
python app.py
```

Open your browser and visit

```
http://127.0.0.1:5000
```

---

## ⚠ Limitations

This project uses the **Football-Data.org Free Plan**.

Because of this:

- Some competitions do not provide squad information.
- Live match events (goal scorers, yellow cards, substitutions, etc.) are unavailable.
- Some data depends on what is provided by the API.

The website has been designed to handle missing data gracefully rather than displaying errors.

---

## 🎯 Future Improvements

Potential future features include:

- Live match updates
- Player statistics pages
- Favourite teams
- Multiple league support across every page
- Advanced filtering and sorting
- Mobile-first responsive layout
- User accounts

---

## 👨‍💻 Author

Created by **Safwan Ahmed**

This project was developed to improve my skills in:

- Python
- Flask
- API integration
- HTML & CSS
- Web application development
- Performance optimisation through caching

---

## 📄 Data Source

Football data provided by:

https://www.football-data.org/

This project is for educational and portfolio purposes only.
