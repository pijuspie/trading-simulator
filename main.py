import database
import stocks
from app import app

database.initialize()
stocks.initialize()

app.run()