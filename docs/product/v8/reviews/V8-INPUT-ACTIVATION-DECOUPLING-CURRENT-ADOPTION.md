# V8 Input Activation Decoupling — Current Adoption

Status: CURRENT / CUSTOMER ADOPTED
Risk: PROTECTED
Customer written adoption: 2026-08-13

The current successor authority is the independently approved design at commit
`bd88cb3e38d88ef83359f4b2c70e2454bb27aeb4`, cumulative reviewed patch SHA-256
`8f471d53690b91a222591c991c6b602cae65f827c37a8c01d3ab77578cea3b0c`.
It supersedes only the development-versus-production prerequisite interpretation for
rows 175, 176, 214-229, 278, 281-283. It does not alter the frozen catalog or any existing
task's closure, non-closure, allowlist, permissions, primary tests, or evidence duties.

Development may reach `CAPABILITY_READY` using isolated `TEST_ONLY` inputs. A missing real
institution input remains `CONFIG_REQUIRED`; every production action fails with
`409 / NO WRITE`. `DG-PAYMENT-WORKBOOK:GLOBAL` and
`DG-SERVICE-RATE-VERSION:GLOBAL` remain the production gates. This adoption never claims production activation.

The exact payment dependency order is:
`FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01 (row175) -> WB-I1 -> row214 -> WB-I2 -> WB-I3 -> rows215-222 -> row278`.
WB-I1, WB-I2, and WB-I3 are external prerequisites to the frozen row-175 lane, not members of
its eleven-row manifest. The row-176 manifest likewise remains exactly eight members.

Full, Final, and Release may accept `CAPABILITY_READY + CONFIG_REQUIRED` only when the negative
path proves `409 / NO WRITE` and `TEST_ONLY` isolation. The release receipt must state the real
configuration status and must never claim production activation without reviewed active real
input.
