# KinanCity

[![Last Version](https://img.shields.io/badge/version-1.0.0--Alpha1-brightgreen.svg)](https://github.com/drallieiv/KinanCity/releases/latest)
[![Build Status](https://travis-ci.org/drallieiv/KinanCity.svg?branch=master)](https://travis-ci.org/drallieiv/KinanCity)

Any issues with KinanCity, or you just want to talk about the project ? Go to [our discord server]( http://discord.gg/3jkb3zA)

## Were is Kinan City ?

**Kinan City** (キナンシティ) is one of the cities of the Kalos region in Pokemon XY games and anime.
It is known as **Kiloude City** is the English version and **Batisques** in French.

Kinan City is known for it **Friend Safari** where many trainer comes to find pokemon. This is a good place if you want to meet a **lot of new trainers**.

## How does one get a Pokemon Trainer Club account ?

In order to get a PTC account you need to go the pokemon website and request to create a new account, and complete theses steps.

![](docs/0_PTCsignup.png)

You then first have to fill some personal informations such as your country and birthdate. Then information about the account you want.

You also need to complete a Captcha task to prove that you are a human.

Once the subscription is done, the account still needs to be activated in the next 48 hours. An email will be sent to the given address with a link. You need to follow that link to activate the account.

NOTE : You cannot use the same email twice for multiple PTC account, they each need their own email address.

Theses steps must be done for each PTC account you want to create.

## What does KinanCity do ?

**KinanCity** is a tool that automates the creation of Pokemon Trainer Accounts and contains multiple modules when you need to create a lot of accounts, fast.

- **KinanCity-core** : is the core module that can also be used in command line. [more info here](KinanCity-core/README.md)
- **KinanCity-mail** : is a minimalist Email server that does auto-activation. [more info here](KinanCity-mail/README.md)

## Why another tool ?

There are already many accout creator with each their specific features.  
KinanCity was born by taking the best features of them to have a complete solution.

The advantages of KinanCity :
* is cross platform compatible (Unix, Windows, Mac)
* can work on headless systems without any need of a web driver
* does parallel processing to be faster
* can use multiple proxies to go over the limit of 20 accounts per hour (5 accounts per 15 minutes)

## How to install KinanCity ?

If you just want to **use Kinan Core and/or Kinan Mail**, you can get the last stable build [here](https://github.com/drallieiv/KinanCity/releases)

or

To use the very last build of each module, you can **download** the latest version of each maven module [here](https://github.com/drallieiv/KinanCity/packages)

or  

You can **compile** it yourself using a **maven** goal : `mvn package`  

## Local batch dashboard

The repository includes a small dashboard at [`dashboard/index.html`](dashboard/index.html). The normal view asks for a username pattern and account count. The orchestrator uses the local `.env` settings, runs the configured core image after an explicit browser confirmation, and exposes a CSV download only for successful rows that also have an activation event. It does not solve CAPTCHAs or rotate proxies.

For preview-only local use, serve the dashboard with:

```bash
python3 -m http.server 8080 --directory dashboard
```

Then visit `http://127.0.0.1:8080`. This preview mode performs no network requests.

## Docker

The root `Dockerfile` builds the core CLI and creates its runtime `config.properties` inside the container. Build it with:

```bash
docker build -t kinancity-core .
```

Running without arguments only shows the CLI help:

```bash
docker run --rm kinancity-core
```

The image defaults to the local CAPTCHA provider with a dummy key. For an explicitly configured provider, pass credentials at runtime rather than baking them into the image:

```bash
docker run --rm \
  -e CAPTCHA_PROVIDER=2captcha \
  -e KC_CAPTCHA_VALUE="$TWOCAPTCHA_KEY" \
  kinancity-core \
  -m '@example.invalid' -f 'demo***' -p 'Passw0rd!' -c 5 -s 0 -t 3
```

The entrypoint adds `-npc` by default. Set `SKIP_PROXY_CHECK=false` if you intentionally configure proxies with `PROXIES`. The container does not include a CAPTCHA-solving service; `CAPTCHA_PROVIDER=local` therefore requires a separately available local provider before real processing can work.

To run KinanCity-mail in its own container, build the mail image:

```bash
docker build -f Dockerfile.mail -t kinancity-mail .
```

The default is log mode on port `2525`:

```bash
docker run --rm -p 2525:2525 kinancity-mail
```

Set `MAIL_MODE=direct` to follow activation links, or leave it as `log` to record links without activating them. You can also set `MAIL_HOSTNAME`, `MAIL_ALLOWED_DOMAINS`, and `MAIL_PORT` with `-e` options. The mail image is separate from the core image and is optional if activation links are handled manually.

To start the dashboard and mail service together:

```bash
docker compose up --build
```

Open `http://127.0.0.1:8080`. The dashboard uses the orchestrator on port `8090`; completed output is downloaded from the page. Runtime files are stored in `runtime/`. A row is exported only when the core result is `OK` and the mail log contains an `OK` or `DONE` activation event.

The **Run through local orchestrator** panel can now start the core container from the dashboard. It sends the batch and provider settings to a localhost-only service on port `8090`, requires a browser confirmation, and writes outputs under `runtime/`. This service mounts `/var/run/docker.sock`; run it only on a machine you control because Docker socket access is equivalent to host Docker control.

To make the dashboard ask only for pattern and count, copy the environment template once:

```bash
cp .env.example .env
```

Set `CAPTCHA_PROVIDER`, `KC_CAPTCHA_VALUE`, `KINAN_BASE_EMAIL`, and `KINAN_ACCOUNT_PASSWORD` in `.env`. Compose loads these values for the local orchestrator; the browser never receives them. The explicit browser confirmation remains required before a core job starts.

For a guided command-line orchestration, use the confirmation-gated script:

```bash
chmod +x scripts/run-batch.sh
CAPTCHA_PROVIDER=2captcha KC_CAPTCHA_VALUE="$TWOCAPTCHA_KEY" \
  scripts/run-batch.sh --email '@example.invalid' --pattern 'demo***' --count 5 --start 0
```

It writes `runtime/kinancity-batch.csv`, starts the services, then pauses until you type `RUN`. Leaving the confirmation unanswered or typing anything else cancels the core run while leaving the local services running.

**KinanCity** modules are java applications and all you need is a Java 8 Runtime Environment on your system.

### References

KinanCity is born from previous projects :

* [pikaptcha](https://github.com/sriyegna/Pikaptcha) by [sriyegna](https://github.com/sriyegna)
* [PalletTown](https://github.com/novskey/PalletTown) by [novskey](https://github.com/novskey)
