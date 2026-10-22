#!/bin/sh
set -eu

cat > /opt/kinancity-mail/config.properties <<EOF
port=${MAIL_PORT}
EOF

if [ -n "${MAIL_HOSTNAME}" ]; then
  printf 'hostname=%s\n' "${MAIL_HOSTNAME}" >> /opt/kinancity-mail/config.properties
fi
if [ -n "${MAIL_ALLOWED_DOMAINS}" ]; then
  printf 'allowedDomains=%s\n' "${MAIL_ALLOWED_DOMAINS}" >> /opt/kinancity-mail/config.properties
fi

exec java -jar /opt/kinancity-mail/kinancity-mail.jar "${MAIL_MODE}" "$@"
