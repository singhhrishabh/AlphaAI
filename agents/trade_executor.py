"""
AlphaAI — Initial Alpaca Execution Agent
Handles real-time execution of Portoflio Manager signals via Alpaca API.
"""
import logging
import os
import alpaca_trade_api as tradeapi

logger = logging.getLogger("alphaai.executor")

class TradeExecutor:
    def __init__(self):
        # YC Standard: Use environment variables instead of hardcoded setups
        self.api_key = os.getenv("ALPACA_API_KEY", "")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY", "")
        self.base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        
        self.enabled = bool(self.api_key and self.secret_key)
        self.api = None
        
        if self.enabled:
            try:
                self.api = tradeapi.REST(self.api_key, self.secret_key, self.base_url, api_version='v2')
                account = self.api.get_account()
                logger.info(f"✅ Alpaca Account linked. Status: {account.status}, Equity: ${account.equity}")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Alpaca: {e}")
                self.enabled = False
        else:
            logger.warning("⚠️ Alpaca credentials missing. Execution is disabled. Please update .env")

    def execute_signal(self, symbol: str, signal: str, confidence: float, current_price: float):
        """
        Executes a trade based on the portfolio manager's signal.
        """
        if not self.enabled or not self.api:
            logger.info(f"[Paper Trading Mode] Ignoring execution for {symbol} due to missing API keys.")
            return {"status": "skipped", "reason": "execution disabled"}

        # Basic risk management: calculate quantity based on confidence
        # For a full YC project, this links to the DB's multi-tenant User portfolio equity
        if signal not in ["BUY", "SELL"]:
            return {"status": "ignored", "reason": f"Signal is {signal}"}

        try:
            qty = max(1, int(confidence / 10)) # Example positioning logic
            side = 'buy' if signal == 'BUY' else 'sell'

            if side == 'sell':
                # Check if we own the position
                positions = self.api.list_positions()
                owned = any(p.symbol == symbol for p in positions)
                if not owned:
                    return {"status": "skipped", "reason": "No position to sell"}

            # Execute market order (can be upgraded to limit)
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force='gtc'
            )
            
            logger.info(f"✅ Alpaca Order Submitted: {side.upper()} {qty} shares of {symbol}")
            return {"status": "success", "order_id": order.id, "side": side, "qty": qty}
            
        except Exception as e:
            logger.error(f"❌ Execution failed for {symbol}: {e}")
            return {"status": "error", "error": str(e)}

trade_executor = TradeExecutor()
