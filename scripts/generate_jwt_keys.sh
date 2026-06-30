#!/usr/bin/env bash
#
# Generate an RS256 JWT signing keypair for Cognivest.
#
# Writes:
#   secrets/jwt_private.pem   (PKCS#8 RSA private key — signs access/refresh tokens)
#   secrets/jwt_public.pem    (public key — verifies tokens)
#
# These paths match JWT_PRIVATE_KEY_PATH / JWT_PUBLIC_KEY_PATH in .env.example.
# ./secrets/ is git-ignored — NEVER commit private keys.
#
# Usage:
#   bash scripts/generate_jwt_keys.sh [--force] [--bits 2048] [--dir ./secrets]
#
# See docs/authentication.md and docs/setup.md.

set -euo pipefail

SECRETS_DIR="./secrets"
BITS=2048
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir)   SECRETS_DIR="$2"; shift 2 ;;
    --bits)  BITS="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "error: unknown argument '$1'" >&2
      exit 2
      ;;
  esac
done

if ! command -v openssl >/dev/null 2>&1; then
  echo "error: openssl is required but not found on PATH" >&2
  exit 1
fi

PRIVATE_KEY="${SECRETS_DIR}/jwt_private.pem"
PUBLIC_KEY="${SECRETS_DIR}/jwt_public.pem"

mkdir -p "${SECRETS_DIR}"

if [[ -e "${PRIVATE_KEY}" || -e "${PUBLIC_KEY}" ]] && [[ "${FORCE}" -ne 1 ]]; then
  echo "error: key(s) already exist in ${SECRETS_DIR}. Re-run with --force to overwrite." >&2
  exit 1
fi

echo "Generating ${BITS}-bit RSA private key -> ${PRIVATE_KEY}"
openssl genpkey -algorithm RSA -pkeyopt "rsa_keygen_bits:${BITS}" -out "${PRIVATE_KEY}"

echo "Extracting public key -> ${PUBLIC_KEY}"
openssl rsa -in "${PRIVATE_KEY}" -pubout -out "${PUBLIC_KEY}"

# Tighten permissions on the private key where the OS supports it.
chmod 600 "${PRIVATE_KEY}" 2>/dev/null || true
chmod 644 "${PUBLIC_KEY}" 2>/dev/null || true

echo "Done. RS256 keypair written to ${SECRETS_DIR}/"
echo "  private: ${PRIVATE_KEY}"
echo "  public:  ${PUBLIC_KEY}"
echo "Ensure JWT_PRIVATE_KEY_PATH / JWT_PUBLIC_KEY_PATH in .env point here."
