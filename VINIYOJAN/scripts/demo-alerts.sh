#!/usr/bin/env sh
set -e
TOKEN=$(curl -fsS http://localhost:8000/auth/login -H 'Content-Type: application/json' -d '{"email":"admin@demo.test","password":"Demo@12345"}' | python3 -c 'import json,sys;print(json.load(sys.stdin)["access_token"])')
curl -fsS -X POST http://localhost:8000/demo/alerts -H "Authorization: Bearer $TOKEN"
echo
