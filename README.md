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

The repository includes a small browser-only dashboard at [`dashboard/index.html`](dashboard/index.html). It previews sequence batches, checks CSV headers, missing required fields, duplicate usernames, and basic date formatting, then produces the corresponding KinanCity command. It does not submit registrations, call CAPTCHA providers, or rotate proxies.

Open it directly, or serve the repository with a local static server:

```bash
python3 -m http.server 8080 --directory dashboard
```

Then visit `http://127.0.0.1:8080`. Review the generated command, configure `config.properties` separately, and run the command manually from the repository root. Keep API keys and passwords out of the dashboard and shell history.

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

Open `http://127.0.0.1:8080`. Use **Download batch CSV** to create the input file for the core container. Store shared files under `runtime/` and run the core job with an explicit output path:

```bash
docker run --rm -v "$PWD:/data" \
  -e CAPTCHA_PROVIDER=2captcha -e KC_CAPTCHA_VALUE="$TWOCAPTCHA_KEY" \
  kinancity-core -a /data/kinancity-batch.csv -o /data/runtime/result.csv
```

After the core job finishes, select `runtime/result.csv` in **Import core results**; the dashboard can download only rows marked `OK`. Select `runtime/links.log` in **Import mail status** to see mail activation events. The dashboard only reports created accounts after reading an `OK` row from KinanCity’s result file, and it only reports activation after reading an `OK` or `DONE` mail event. Receiving those events still requires your domain’s MX record and reachable SMTP port.

For a guided local orchestration, use the confirmation-gated script:

```bash
chmod +x scripts/run-batch.sh
CAPTCHA_PROVIDER=2captcha KC_CAPTCHA_VALUE="$TWOCAPTCHA_KEY" \
  scripts/run-batch.sh --email '@example.invalid' --pattern 'demo***' --count 5 --start 0
```

It writes `runtime/kinancity-batch.csv`, starts the dashboard and mail containers, then pauses until you type `RUN`. After the core job, import `runtime/result.csv` and `runtime/links.log` in the dashboard. Leaving the confirmation unanswered or typing anything else cancels the core run while leaving the local services running.

**KinanCity** modules are java applications and all you need is a Java 8 Runtime Environment on your system.

### References

KinanCity is born from previous projects :

* [pikaptcha](https://github.com/sriyegna/Pikaptcha) by [sriyegna](https://github.com/sriyegna)
* [PalletTown](https://github.com/novskey/PalletTown) by [novskey](https://github.com/novskey)
