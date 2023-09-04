# 💖 Dividitto

An app to register your home expenses 💰 and divide based on family member income 💵!

## 💡 Motivation

I was tired of using splitwise to divide my home expenses, so I decided to create my own app to do that. The main difference is that this app will divide based on family member income, so if you have a family member that earns more than you, he will pay more than you.

Also I wanted to experiment with [HTMX](htmx.org) + [Django](https://www.djangoproject.com) + [WaterCSS](https://watercss.kognise.dev) as a really **fast** and **minimal** way of creating web apps. This way I reduce drastically the amount of code needed for the frontend maintaining a good UX without a **full page reload.**

## 🦾 Features

- [x] Register expenses
- [x] Register family income per month
- [x] Divide expenses based on family income
- [x] Recalculate expenses if income changes
- [x] Log in
- [x] Logged user as default payer
- [x] Settle up
- [x] Active expenses search
- [x] Edit/Delete expenses
- [x] Infinite scroll
- [x] PWA, can be installed on mobile
- [x] Script to migrate from splitwise

## 😿 Missing features (TODO)
- [ ] Add tests
- [ ] Add user registration with a proper captcha
- [ ] Add groups, rigth now the app only works for two people
- [ ] Add a way to add more than two people to a group
- [ ] Add i18n. Right now the app only works in spanish (perdón amigo 🇦🇷)

## 🧰 How to run it

### Dev
Start your enviroment running:

```bash
pipenv install
```

Configure db running:

```bash
make db_configure
```

Then start db running:

```bash
make db_start
```

The run migrations:

```bash
make migrate
```

Finally run the app:

```bash
make run
```

Also create two user, you can do it with:
```bash
make createsuperuser
```

### Prod
Deploy using docker compose. Use `docker-compose.yml`, `.env.template.prod` to configure your production environment.

You need a Postgres database, you can use the one in `docker-compose-dev.yml` or use another one.