# app.py
import os
import sys
import time
import json
import argparse
from web3 import Web3
from typing import Dict, Any, Optional

RPC = os.getenv("RPC_URL", "https://mainnet.infura.io/v3/your_api_key")
TIMEOUT = float(os.getenv("TIMEOUT", "15"))
SLOT = os.getenv("DEFAULT_SLOT", "0x0")

def connect(rpc: str) -> Web3:
    w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": TIMEOUT}))
    if not w3.is_connected():
        print("❌ Failed to connect to RPC.", file=sys.stderr)
        sys.exit(1)
    return w3

def checksum(addr: str) -> str:
    if not Web3.is_address(addr):
        print("❌ Invalid Ethereum address.", file=sys.stderr)
        sys.exit(2)
    return Web3.to_checksum_address(addr)

def parse_slot(slot: str) -> int:
    try:
        return int(slot, 0)
    except:
        print("❌ Invalid slot format.", file=sys.stderr)
        sys.exit(2)

def get_value(w3: Web3, address: str, slot: int, block: int) -> bytes:
    return w3.eth.get_storage_at(address, slot, block_identifier=block)

def leaf(chain_id: int, address: str, slot: int, block: int, value: bytes) -> str:
    payload = (
        chain_id.to_bytes(8, "big")
        + bytes.fromhex(address[2:])
        + slot.to_bytes(32, "big")
        + block.to_bytes(8, "big")
        + value.rjust(32, b"\x00")
    )
    return "0x" + Web3.keccak(payload).hex()

def pair(a: str, b: str) -> str:
    ba, bb = bytes.fromhex(a[2:]), bytes.fromhex(b[2:])
    x, y = (ba, bb) if ba < bb else (bb, ba)
    return "0x" + Web3.keccak(x + y).hex()

def now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

def run(address: str, slot: str, rpc: str) -> Dict[str, Any]:
    w3 = connect(rpc)
    slot_int = parse_slot(slot)
    addr = checksum(address)
    chain_id = w3.eth.chain_id
    tip = w3.eth.block_number

    if tip < 3:
        print("❌ Chain height too low.", file=sys.stderr)
        sys.exit(2)

    a_blk, b_blk = tip - 2, tip

    v_a = get_value(w3, addr, slot_int, a_blk)
    v_b = get_value(w3, addr, slot_int, b_blk)

    leaf_a = leaf(chain_id, addr, slot_int, a_blk, v_a)
    leaf_b = leaf(chain_id, addr, slot_int, b_blk, v_b)
    root = pair(leaf_a, leaf_b)

    return {
        "address": addr,
        "slotHex": hex(slot_int),
        "blockA": a_blk,
        "blockB": b_blk,
        "valueA": "0x" + v_a.hex(),
        "valueB": "0x" + v_b.hex(),
        "leafA": leaf_a,
        "leafB": leaf_b,
        "pairRoot": root,
        "changed": v_a != v_b,
        "timestamp": now(),
        "rpc": rpc,
        "chainId": chain_id
    }

def main():
    p = argparse.ArgumentParser(description="Minimal slot-delta soundness probe.")
    p.add_argument("address", help="Contract address")
    p.add_argument("--slot", default=SLOT, help="Storage slot to check (decimal or hex)")
    p.add_argument("--rpc", default=RPC, help="RPC URL")
    p.add_argument("--json", action="store_true", help="Output JSON only")
    args = p.parse_args()

    out = run(args.address, args.slot, args.rpc)

    if args.json:
        print(json.dumps(out, indent=2))
        return

    print("📦 Slot Soundness Probe")
    print(f"Address: {out['address']}")
    print(f"Slot:    {out['slotHex']}")
    print("")
    print(f"BlockA={out['blockA']}  ValueA={out['valueA']}")
    print(f"BlockB={out['blockB']}  ValueB={out['valueB']}")
    print("")
    print(f"LeafA: {out['leafA']}")
    print(f"LeafB: {out['leafB']}")
    print(f"Pair Root: {out['pairRoot']}")
    print(f"Changed: {'YES' if out['changed'] else 'NO'}")
    print(f"Timestamp: {out['timestamp']}")
    print(f"RPC: {out['rpc']}")
    print(f"ChainId: {out['chainId']}")

if __name__ == "__main__":
    main()
