#!/bin/sh
set -eu

usage() {
  echo "Usage: $0 --email BASE_EMAIL --pattern PATTERN --count N [--start N] [--password PASSWORD]"
  echo "Environment: CAPTCHA_PROVIDER, KC_CAPTCHA_VALUE"
  exit 2
}

email= pattern= password= count= start=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --email) email=${2-}; shift 2 ;;
    --pattern) pattern=${2-}; shift 2 ;;
    --count) count=${2-}; shift 2 ;;
    --start) start=${2-}; shift 2 ;;
    --password) password=${2-}; shift 2 ;;
    *) usage ;;
  esac
done

[ -n "$email" ] && [ -n "$pattern" ] && [ -n "$count" ] || usage
case "$pattern" in *\**);; *) echo "Pattern must contain asterisk characters." >&2; exit 2;; esac
case "$count" in ''|*[!0-9]*) echo "Count must be a positive integer." >&2; exit 2;; esac
case "$start" in ''|*[!0-9]*) echo "Start must be a non-negative integer." >&2; exit 2;; esac
[ "$count" -gt 0 ] || { echo "Count must be greater than zero." >&2; exit 2; }

if [ -z "$password" ]; then
  printf 'Batch password (input hidden): '
  stty -echo
  read -r password
  stty echo
  printf '\n'
fi

mkdir -p runtime
batch="runtime/kinancity-batch.csv"
python3 - "$email" "$pattern" "$count" "$start" "$password" > "$batch" <<'PY'
import sys
email, pattern, count, start, password = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
stars = pattern.count('*')
if stars == 0 or start + count - 1 > (10 ** stars) - 1:
    raise SystemExit('Pattern width is too small for this batch.')
print('#username;password;email')
for n in range(start, start + count):
    username = pattern.replace('*' * stars, str(n).zfill(stars), 1)
    address = (email.replace('@', '+' + username + '@', 1)
               if '@' in email else username + email)
    print(';'.join((username, password, address)))
PY

echo "Batch written to $batch"
echo "Starting dashboard and mail services..."
docker compose up -d --build dashboard mail

echo "This next command can contact external services and create accounts."
printf "Type RUN to continue: "
read -r confirmation
[ "$confirmation" = RUN ] || { echo "Cancelled. Dashboard and mail remain available."; exit 0; }

: "${CAPTCHA_PROVIDER:=local}"
: "${KC_CAPTCHA_VALUE:=DUMMY_LOCAL_KEY}"
docker run --rm \
  -v "$PWD:/data" \
  -e CAPTCHA_PROVIDER="$CAPTCHA_PROVIDER" \
  -e KC_CAPTCHA_VALUE="$KC_CAPTCHA_VALUE" \
  kinancity-core \
  -a /data/runtime/kinancity-batch.csv \
  -o /data/runtime/result.csv

echo "Core results: runtime/result.csv"
echo "Mail events:   runtime/links.log"
echo "Dashboard:     http://127.0.0.1:8080"
