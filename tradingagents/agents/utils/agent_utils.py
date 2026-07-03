from langchain_core.messages import HumanMessage, RemoveMessage

# Import tools from separate utility files
from tradingagents.agents.utils.core_stock_tools import (
    get_stock_data
)
from tradingagents.agents.utils.technical_indicators_tools import (
    get_indicators
)
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_insider_transactions,
    get_global_news
)

def format_portfolio_context(state, ticker: str = None) -> str:
    """Format portfolio_context from state into a prompt section. Returns empty string if no context."""
    ctx = state.get("portfolio_context") or {}
    if not ctx or not ctx.get("holdings"):
        return ""

    ticker = ticker or state.get("company_of_interest", "")
    member = ctx.get("member", "Unknown")
    total_value = ctx.get("totalPortfolioValue", 0)
    holdings = ctx.get("holdings", [])
    sector_concentrations = ctx.get("sectorConcentrations", {})

    current_holding = None
    for h in holdings:
        if (h.get("ticker") or "").upper() == ticker.upper():
            current_holding = h
            break

    lines = [
        f"\n--- Portfolio Context ({member}'s Managed Account) ---",
        f"Total portfolio value: ${total_value:,.0f}",
        f"Open positions: {len(holdings)}",
    ]

    if current_holding:
        lines.append(
            f"Current {ticker.upper()} position: {current_holding.get('portfolioWeightPct', 0):.1f}% "
            f"(${current_holding.get('currentValue', 0):,.0f})"
        )
    else:
        lines.append(f"No existing {ticker.upper()} position.")

    if sector_concentrations:
        top = sorted(sector_concentrations.items(), key=lambda x: x[1], reverse=True)[:5]
        lines.append("Top sector concentrations: " + ", ".join(f"{n} {p:.1f}%" for n, p in top))

    top_holdings = holdings[:5]
    if top_holdings:
        lines.append("Largest positions: " + ", ".join(
            f"{h.get('ticker', '?')} {h.get('portfolioWeightPct', 0):.1f}%" for h in top_holdings
        ))

    lines.append("Use this context for analytical framing only. Do not prescribe specific share counts or dollar amounts.")
    lines.append("--- End Portfolio Context ---\n")
    return "\n".join(lines)


def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]

        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]

        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")

        return {"messages": removal_operations + [placeholder]}

    return delete_messages


        