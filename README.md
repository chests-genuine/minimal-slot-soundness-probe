# README.md

minimal-slot-soundness-probe

Overview
This repository contains a minimalistic script that performs a small “soundness probe” on an Ethereum-like chain. It reads a storage slot at two different blocks and computes a commitment pair root to quickly detect data drift or instability across recent blocks.

This is a reduced version of a slot-delta soundness tool used to test RPC correctness, preimage consistency, and contract state stability.

Files
- app.py — main script performing slot checks.
- README.md — this documentation.

Purpose
This script offers a simple fast sanity-check for:
- light RPC soundness
- node consistency across recent blocks
- slot stability monitoring
- commitment root generation as used in zk-proofs or audit workflows

It does not prove correctness, but flags obvious inconsistencies.

Setup
1) Install Python 3.9+.
2) Install dependencies:

   pip install web3

3) Ensure you have an RPC endpoint available.  
   You can set the environment variable:

   export RPC_URL="https://mainnet.infura.io/v3/YOUR_KEY"

Usage
Basic run:

   python app.py 0xContractAddress

Specify a slot explicitly:

   python app.py 0xABC... --slot 0x5

Or decimal:

   python app.py 0xABC... --slot 12

Use a custom RPC endpoint:

   python app.py 0xABC... --rpc https://eth.llamarpc.com

JSON-only output (for dashboards / pipelines):

   python app.py 0xABC... --json

What the script does
1) Connects to an RPC endpoint.
2) Fetches the latest block and two blocks before it.
3) Reads the specified storage slot at both blocks.
4) Computes:
   - leaf commitment for block A
   - leaf commitment for block B
   - commitment pair root
5) Reports whether the value changed between the two blocks.
6) Prints results in human-readable or JSON format.

Expected output
A successful run prints:
- contract address + slot
- block range inspected
- raw storage values
- leaf commitments
- pair root
- changed / unchanged flag
- timestamp + chain ID

Notes
- Requires an archive node only if slot is read at a block not stored by the RPC provider.
- Useful for verifying state-stability during deployments, upgrades, or preimage extraction tasks.
- Compatible with all EVM-based chains (Ethereum, Polygon, Base, Optimism, Arbitrum, etc.).

License
MIT or any license you prefer.
