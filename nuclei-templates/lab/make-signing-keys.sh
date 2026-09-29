#!/usr/bin/env bash
# Create a nuclei signing keypair without going through nuclei's interactive
# prompts.
#
# Why this exists: `nuclei -sign` with no keys asks for a user/organization name
# and then twice for a passphrase (input hidden). A mismatch is fatal
# ("passphrase did not match try again") and nothing is written. There is no flag
# to skip those prompts, so the fast path is to pre-create a keypair in exactly
# the format the signer reads:
#
#   ~/.config/nuclei/keys/nuclei-user.crt                x509 cert, EC P-256, CN set
#   ~/.config/nuclei/keys/nuclei-user-private-key.pem    SEC1 "EC PRIVATE KEY", plain
#
# With both files present, `nuclei -sign -t <template>` never prompts: no key
# generation (keys exist) and no passphrase question (the key is unencrypted).
#
# Formats matter: nuclei parses the key with x509.ParseECPrivateKey, which needs
# SEC1 ("BEGIN EC PRIVATE KEY"), not PKCS#8 ("BEGIN PRIVATE KEY"). `openssl
# ecparam -genkey` produces the right one, `openssl genpkey` does not.
#
# Usage:
#   ./make-signing-keys.sh                       # into ~/.config/nuclei/keys
#   ./make-signing-keys.sh --dir ./keys          # into a custom directory
#   ./make-signing-keys.sh --name hax0r          # certificate CN
#   ./make-signing-keys.sh --force               # overwrite an existing keypair
#   ./make-signing-keys.sh --print-env           # also print the env-var exports
set -euo pipefail

KEYS_DIR="${NUCLEI_KEYS_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/nuclei/keys}"
CN_NAME="${USER:-nuclei-local}"
FORCE=0
PRINT_ENV=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dir)       KEYS_DIR="${2:?--dir needs a path}"; shift 2 ;;
    --name)      CN_NAME="${2:?--name needs a value}"; shift 2 ;;
    --force)     FORCE=1; shift ;;
    --print-env) PRINT_ENV=1; shift ;;
    -h|--help)   sed -n '2,28p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) printf 'unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
done

CERT_FILE="$KEYS_DIR/nuclei-user.crt"
KEY_FILE="$KEYS_DIR/nuclei-user-private-key.pem"

command -v openssl >/dev/null 2>&1 || {
  echo "openssl is required to create the keypair" >&2
  exit 1
}

if [ -f "$CERT_FILE" ] || [ -f "$KEY_FILE" ]; then
  if [ "$FORCE" != "1" ]; then
    echo "a keypair already exists in $KEYS_DIR - refusing to overwrite it"
    echo "  (use --force to replace it, or --dir to write somewhere else)"
    exit 0
  fi
  echo "overwriting the existing keypair in $KEYS_DIR (--force)"
fi

mkdir -p "$KEYS_DIR"
chmod 700 "$KEYS_DIR"

# SEC1 EC private key (what x509.ParseECPrivateKey expects), no passphrase
openssl ecparam -name prime256v1 -genkey -noout -out "$KEY_FILE"
# self-signed certificate carrying the identifier as CN
openssl req -new -x509 -key "$KEY_FILE" -subj "/CN=$CN_NAME" -days 1460 -sha256 -out "$CERT_FILE" 2>/dev/null

chmod 600 "$KEY_FILE" "$CERT_FILE"

# sanity check the two properties nuclei validates, so a broken pair fails here
# instead of inside nuclei
openssl ec -in "$KEY_FILE" -check -noout >/dev/null 2>&1 || {
  echo "generated private key does not parse as an EC key" >&2
  exit 1
}
subject="$(openssl x509 -in "$CERT_FILE" -noout -subject 2>/dev/null | sed 's/^subject=//')"
[ -n "$subject" ] || {
  echo "generated certificate has no subject" >&2
  exit 1
}

echo "signing keypair created"
echo "  certificate: $CERT_FILE  ($subject)"
echo "  private key: $KEY_FILE  (SEC1, unencrypted, chmod 600)"
echo
echo "next:"
echo "  nuclei -sign -t <template.yaml>      # single pass, no prompts"
echo "  grep -n '^# digest:' <template.yaml> # confirm it is signed"
echo "  nuclei -u <target> -t <template.yaml>"

if [ "$PRINT_ENV" = "1" ]; then
  cat <<EOF

or use the keypair without installing it into ~/.config/nuclei/keys:

  export NUCLEI_USER_CERTIFICATE=$CERT_FILE
  export NUCLEI_USER_PRIVATE_KEY=$KEY_FILE
EOF
fi
