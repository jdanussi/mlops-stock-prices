"""Data model definition."""

from sqlalchemy import Column, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class StockOHLC(Base):
    """Adjusted Stocks OHLCV data model."""

    __tablename__ = "stock_ohlc"
    __table_args__ = (UniqueConstraint("date", "symbol", name="unique_stock_ohlc"),)
    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=False))
    symbol = Column(String)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return (
            f"<StockOHLC(date='{self.date}', "
            f"symbol='{self.symbol}', "
            f"open='{self.open}', "
            f"high='{self.high}', "
            f"low='{self.low}', "
            f"close='{self.close}', "
            f"volume='{self.volume}', "
            f"adj_close='{self.adj_close}', "
            f"timestamp='{self.timestamp}')>"
        )


class StockPrediction(Base):
    """Stocks close price predictions."""

    __tablename__ = "stock_prediction"
    __table_args__ = (
        UniqueConstraint("date", "symbol", name="unique_stock_prediction"),
    )
    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=False))
    symbol = Column(String)
    prediction = Column(Float)
    model = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return (
            f"<StockClosePricePrediction(date='{self.date}', "
            f"symbol='{self.symbol}', "
            f"prediction='{self.prediction}', "
            f"model='{self.model}', "
            f"timestamp='{self.timestamp}')>"
        )


class EvidentlyMetrics(Base):
    """Evidently metrics."""

    __tablename__ = "evidently_metrics"
    __table_args__ = (UniqueConstraint("id", name="unique_evidently_metrics"),)
    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=False))
    symbol = Column(String)
    prediction_drift = Column(Float)
    num_drifted_columns = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return (
            f"<EvidentlyMetrics(date='{self.date}', "
            f"symbol='{self.symbol}', "
            f"prediction_drift='{self.prediction_drift}', "
            f"num_drifted_columns='{self.num_drifted_columns}', "
            f"timestamp='{self.timestamp}')>"
        )
