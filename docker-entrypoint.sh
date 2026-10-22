#!/bin/sh
set -eu

# KinanCity reads config.properties from its current working directory.
cat > /opt/kinancity/config.properties <<EOF
captcha.provider=${CAPTCHA_PROVIDER}
captcha.key=${KC_CAPTCHA_VALUE}
dumpResult=0
captchaMaxTotalTime=600
captchaMaxParallelChallenges=20
EOF

if [ -n "${PROXIES}" ]; then
  printf 'proxies=%s\n' "${PROXIES}" >> /opt/kinancity/config.properties
fi

if [ "$SKIP_PROXY_CHECK" = "true" ]; then
  set -- "$@" -npc
fi

exec java -jar /opt/kinancity/kinancity-core.jar "$@"
