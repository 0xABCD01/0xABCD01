#!/usr/bin/env bash
# Create a nuclei signing keypair without going through nuclei's interactive
# prompts, and optionally sign templates with it.
#
# Why this exists: `nuclei -sign` with no keys asks for a user/organization name
# and then twice for a passphrase (input hidden). A mismatch is fatal
# ("passphrase did not match try again") and nothing is written. There is no flag
# to skip those prompts, so the fast path is to pre-create a keypair in exactly
# the format the signer reads:
#
#   <keys>/nuclei-user.crt                x509 cert, EC P-256, CN set
#   <keys>/nuclei-user-private-key.pem    SEC1 "EC PRIVATE KEY", unencrypted
#
# With both files present, `nuclei -sign -t <template>` never prompts: no key
# generation (keys exist) and no passphrase question (the key is not encrypted).
#
# Formats matter: nuclei parses the key with x509.ParseECPrivateKey, which needs
# SEC1 ("BEGIN EC PRIVATE KEY"), not PKCS#8 ("BEGIN PRIVATE KEY"). `openssl
# ecparam -genkey` produces the right one, `openssl genpkey` does not. The
# certificate must carry a CN or ParseUserCert refuses it.
#
# Usage:
#   ./make-signing-keys.sh                          # ~/.config/nuclei/keys
#   ./make-signing-keys.sh --dir ./keys             # custom directory
#   ./make-signing-keys.sh --name hax0r             # certificate CN
#   ./make-signing-keys.sh --force                  # replace an unusable pair
#   ./make-signing-keys.sh --print-env              # print NUCLEI_USER_* exports
#   ./make-signing-keys.sh --check                  # verify, create nothing
#   ./make-signing-keys.sh --sign p.yaml            # keys if needed, then sign
#   ./make-signing-keys.sh --sign a.yaml --sign b.yaml --no-create
set -euo pipefail

KEYS_DIR="${NUCLEI_KEYS_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/nuclei/keys}"
CN_NAME="${USER:-nuclei-local}"
FORCE=0
PRINT_ENV=0
CHECK_ONLY=0
CREATE=1
SIGN_FILES=()

while [ $# -gt 0 ]; do
  case "$1" in
    --dir)       KEYS_DIR="${2:?--dir needs a path}"; shift 2 ;;
    --name)      CN_NAME="${2:?--name needs a value}"; shift 2 ;;
    --force)     FORCE=1; shift ;;
    --print-env) PRINT_ENV=1; shift ;;
    --check)     CHECK_ONLY=1; shift ;;
    --no-create) CREATE=0; shift ;;
    --sign)      SIGN_FILES+=("${2:?--sign needs a template path}"); shift 2 ;;
    -h|--help)   sed -n '2,31p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) printf 'unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
done

CERT_FILE="$KEYS_DIR/nuclei-user.crt"
KEY_FILE="$KEYS_DIR/nuclei-user-private-key.pem"

fail() { printf '%s\n' "$*" >&2; exit 1; }

# check_pair mirrors what nuclei validates: SEC1 EC private key + cert with a CN
check_pair() {
  [ -f "$KEY_FILE" ] && [ -f "$CERT_FILE" ] || return 1
  head -1 "$KEY_FILE" | grep -q 'BEGIN EC PRIVATE KEY' || {
    printf '%s is not a SEC1 EC key - nuclei (x509.ParseECPrivateKey) will reject it\n' "$KEY_FILE" >&2
    printf 'openssl genpkey writes PKCS#8; use: openssl ecparam -name prime256v1 -genkey -noout\n' >&2
    return 1
  }
  openssl ec -in "$KEY_FILE" -check -noout >/dev/null 2>&1 || {
    printf '%s does not parse as an EC key\n' "$KEY_FILE" >&2
    return 1
  }
  KEY_SUBJECT="$(openssl x509 -in "$CERT_FILE" -noout -subject 2>/dev/null | sed 's/^subject=//')"
  [ -n "$KEY_SUBJECT" ] || {
    printf '%s has no subject/CN - nuclei (ParseUserCert) rejects that\n' "$CERT_FILE" >&2
    return 1
  }
  return 0
}

command -v openssl >/dev/null 2>&1 || fail "openssl is required to create or inspect the keypair"

# ---------------------------------------------------------------- --check only
if [ "$CHECK_ONLY" = "1" ]; then
  if check_pair; then
    echo "keypair in $KEYS_DIR is usable by nuclei"
    echo "  certificate: $KEY_SUBJECT"
    exit 0
  fi
  echo "no usable keypair in $KEYS_DIR"
  [ -n "${NUCLEI_USER_CERTIFICATE:-}${NUCLEI_USER_PRIVATE_KEY:-}" ] &&
    echo "(NUCLEI_USER_CERTIFICATE / NUCLEI_USER_PRIVATE_KEY are set - nuclei would use those instead)"
  exit 1
fi

# ------------------------------------------------------------------- keypair
if check_pair; then
  echo "using the existing keypair in $KEYS_DIR"
  echo "  certificate: $KEY_SUBJECT"
elif [ -f "$CERT_FILE" ] || [ -f "$KEY_FILE" ]; then
  [ "$FORCE" = "1" ] || fail "a keypair already exists in $KEYS_DIR but is unusable
  (re-create it with --force, or choose another directory with --dir)"
  echo "replacing the unusable keypair in $KEYS_DIR (--force)"
  rm -f "$CERT_FILE" "$KEY_FILE"
elif [ "$CREATE" != "1" ]; then
  fail "no keypair in $KEYS_DIR and --no-create was given"
fi

if [ ! -f "$KEY_FILE" ] || [ ! -f "$CERT_FILE" ]; then
  mkdir -p "$KEYS_DIR"
  chmod 700 "$KEYS_DIR"
  # SEC1 EC private key (what x509.ParseECPrivateKey expects), no passphrase
  openssl ecparam -name prime256v1 -genkey -noout -out "$KEY_FILE"
  # self-signed certificate carrying the identifier as CN
  openssl req -new -x509 -key "$KEY_FILE" -subj "/CN=$CN_NAME" -days 1460 -sha256 -out "$CERT_FILE" 2>/dev/null
  chmod 600 "$KEY_FILE" "$CERT_FILE"
  check_pair || fail "the generated keypair failed validation"
  echo "signing keypair created"
  echo "  certificate: $CERT_FILE  ($KEY_SUBJECT)"
  echo "  private key: $KEY_FILE  (SEC1, unencrypted, chmod 600)"
fi

if [ "$PRINT_ENV" = "1" ]; then
  printf '\nor use it without installing into ~/.config/nuclei/keys:\n\n'
  printf '  export NUCLEI_USER_CERTIFICATE=%s\n' "$CERT_FILE"
  printf '  export NUCLEI_USER_PRIVATE_KEY=%s\n' "$KEY_FILE"
fi

# --------------------------------------------------------------------- signing
if [ "${#SIGN_FILES[@]}" -gt 0 ]; then
  command -v nuclei >/dev/null 2>&1 || fail "--sign needs nuclei on PATH (the keypair itself was created)"
  failed=0
  for file in "${SIGN_FILES[@]}"; do
    [ -f "$file" ] || { printf 'not a file: %s\n' "$file" >&2; failed=1; continue; }
    echo
    echo "signing $file"
    if ! nuclei -sign -t "$file" >/dev/null 2>&1; then
      printf '  nuclei -sign failed - re-run it without redirection to see why:\n    nuclei -sign -t %s\n' "$file" >&2
      failed=1
      continue
    fi
    if grep -q '^# digest:' "$file"; then
      printf '  signed: %s...\n' "$(grep -m1 '^# digest:' "$file" | cut -c1-60)"
      printf '  scan:   nuclei -u <target> -t %s\n' "$file"
    else
      printf "  no '# digest:' line appeared - nuclei did not write a signature\n" >&2
      failed=1
    fi
    # an encrypted key would make nuclei ask for a passphrase on the next run
    grep -qE 'ENCRYPTED|Proc-Type: 4,ENCRYPTED' "$KEY_FILE" 2>/dev/null &&
      printf '  note: this key is passphrase-protected, so nuclei will ask for the passphrase again\n' >&2
  done
  [ "$failed" = "0" ] || exit 1
  exit 0
fi

cat <<EOF

next:
  nuclei -sign -t <template.yaml>            # single pass, no prompts
  grep -n '^# digest:' <template.yaml>       # confirm it is signed
  nuclei -u <target> -t <template.yaml>

  ...or let this script do it:  $0 --sign <template.yaml>
EOF
