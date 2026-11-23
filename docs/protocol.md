# Observed UART telemetry protocol

The following describes passive captures from one SBC1200R unit on 2026-11-23. It is not a manufacturer specification.

## Receive settings

| Parameter | Working setting | Evidence / limitation |
|---|---|---|
| Baud rate | 4800 | Stable structure, plausible values and matching checksums |
| Data bits | 8 | Full binary payload, including bytes above 0x7F |
| Parity | None | Both 8E1 and 8O1 produced parity errors |
| Stop bits | 1 works | 8N2 also received; actual transmitted stop count is unresolved |
| Flow control | None | Passive RX + GND capture |
| Typical interval | About 250 ms | Host read timestamps; not logic-analyzer edge timing |

## Frame layout

Offsets are zero-based. All captured complete frames have 12 bytes.

| Offset | Size | Field | Interpretation |
|---|---:|---|---|
| 0–3 | 4 | `FE FE FE FE` | Repeated synchronization header |
| 4 | 1 | `07` | Constant observed; probably length of payload plus checksum |
| 5–6 | 2 | Output voltage | Unsigned little-endian integer × 0.01 V |
| 7–8 | 2 | Output current | Unsigned little-endian integer × 0.01 A; supported by display comparison |
| 9–10 | 2 | Input voltage | Unsigned little-endian integer × 0.01 V |
| 11 | 1 | Checksum | `sum(frame[5:11]) & 0xFF` |

Example at zero current:

```text
FE FE FE FE 07 CE 16 00 00 18 08 04
               ----- ----- ----- --
               Vout  Iout  Vin   sum
```

- `0x16CE / 100 = 58.38 V` output.
- `0x0000 / 100 = 0 A` current.
- `0x0818 / 100 = 20.72 V` input.
- `(0xCE + 0x16 + 0 + 0 + 0x18 + 0x08) & 0xFF = 0x04`.

Example under load:

```text
FE FE FE FE 07 E0 19 19 01 4B 07 65
```

Output 66.24 V, current 2.81 A, input 18.67 V; derived output power 186.1344 W. Checksum: `(E0 + 19 + 19 + 01 + 4B + 07) & FF = 65`.

## Confidence and scope

Voltage positions/scaling match the reported LCD readings. Current scaling is supported by a reported 2.8 A. Output-current assignment is an inference supported by a reported 186 W and approximately 187.3 W mean derived power in the first loaded recording. Reference readings were asynchronous; independent metrology remains useful.

The three principal recordings contain 120 + 240 + 240 complete frames, all checksum-valid. Their six payload bytes are accounted for by the three measurements above. No separate temperature, power, energy, flags or command identifier has been identified. Other frame types or modes may still exist.

The checksum is a simple additive byte sum, not CRC-16. Consumers should also validate the header and observed `07` byte and resynchronize after corruption. Do not treat an outgoing telemetry frame as a proven command that can be transmitted back.

No commands have been sent to the MPPT. No read, write, configuration, firmware-dump or bootloader protocol is known. J9.4's receive function has not been verified.
