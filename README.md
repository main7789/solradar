# SolRadar — Solana Meme Token Intelligence

Real-time Solana token discovery and security analysis powered by Birdeye Data API.

## Features
- Top 20 trending tokens with live price, volume, and liquidity
- New token listings discovery
- Token security scanner (mint authority, creator holdings, top holders)

## Birdeye API Endpoints Used
- /defi/token_trending
- /v2/tokens/new_listing
- /defi/token_security
- /defi/token_overview

## How to Run
pip install streamlit requests
streamlit run solradar.py

Built for Birdeye Data 4-Week BIP Competition Sprint 4 | #BirdeyeAPI
