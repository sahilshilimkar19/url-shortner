# 🔗 URL Shortener (Flask-based)

A lightweight URL shortener inspired by TinyURL.  
Built with Flask, SQLite, and raw HTML/CSS — no ORMs or frontend frameworks.

---

## 🚀 Features

- ✅ Anonymous users can create short URLs
- ✅ Registered users can:
  - Log in / Sign up
  - Create custom short codes
  - View their own URLs via dashboard
- ✅ All data stored in SQLite (no ORM used)
- ✅ Clean HTML/CSS UI without frameworks

---

## 🧪 Testing

Unit tests are included for:
- Homepage loading
- Anonymous URL shortening
- User registration and login
- Custom short code creation
- Redirection logic

Run tests locally with:
```bash
python -m unittest discover tests
